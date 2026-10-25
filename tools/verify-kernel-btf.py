#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Check built legacy BTF boundaries, consumer limits and typed iterator identity.

These host checks do not establish successful boot, Android program loading,
accounting accuracy or kernel concurrency safety. They never disable verifier
checks and remain active when Python optimization is enabled.
"""

import argparse
import json
import re
import struct
import subprocess
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(description="Validate the built legacy kernel's BTF boundaries, limits and iterator/helper type identity.")
    parser.add_argument('--kernel-source', type=Path, required=True)
    parser.add_argument('--kernel-out', type=Path, required=True)
    parser.add_argument('--llvm-bin', type=Path, required=True)
    parser.add_argument('--work-dir', type=Path, required=True)
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    k = args.kernel_out.resolve()
    llvm = args.llvm_bin.resolve()
    b = args.work_dir.resolve()
    b.mkdir(parents=True, exist_ok=True)
    source = args.kernel_source.resolve()

    def symbols(path):
        text = subprocess.check_output([str(llvm / 'llvm-nm'), str(path)], text=True)
        if not '_binary__btf_vmlinux_bin' not in text:
            raise ValueError('Obsolete BTF boundaries remain')
        return text
    final = symbols(k / 'vmlinux')
    obj = symbols(k / 'kernel/bpf/btf.o')
    for name in ['__start_BTF', '__stop_BTF']:
        if not name in obj:
            raise ValueError('Parser does not reference actual boundary ' + name)
    values = {}
    for line in final.splitlines():
        fields = line.split()
        if len(fields) == 3 and fields[2] in ['__start_BTF', '__stop_BTF']:
            if not fields[1] not in ['w', 'U']:
                raise ValueError('Kernel BTF validation failed')
            values[fields[2]] = int(fields[0], 16)
    if not set(values) == {'__start_BTF', '__stop_BTF'}:
        raise ValueError('Kernel BTF validation failed')
    size = values['__stop_BTF'] - values['__start_BTF']
    if not (values['__start_BTF'] and size >= 24):
        raise ValueError('Kernel BTF validation failed')
    raw = b / 'vmlinux.BTF'
    subprocess.run([str(llvm / 'llvm-objcopy'), '--dump-section', '.BTF=' + str(raw), str(k / 'vmlinux')], check=True)
    data = raw.read_bytes()
    if not len(data) == size:
        raise ValueError('Kernel BTF validation failed')
    magic, version, flags, hdr, toff, tlen, soff, slen = struct.unpack_from('<HBBIIIII', data)
    if not (magic == 60319 and version == 1 and (hdr >= 24)):
        raise ValueError('Kernel BTF validation failed')
    if not (hdr + max(toff + tlen, soff + slen) <= len(data) and tlen and slen):
        raise ValueError('Kernel BTF validation failed')
    header = (source / 'include/uapi/linux/btf.h').read_text()
    max_types = int(re.search('#define BTF_MAX_TYPE\\s+(0x[0-9a-fA-F]+)', header)[1], 16)
    max_names = int(re.search('#define BTF_MAX_NAME_OFFSET\\s+(0x[0-9a-fA-F]+)', header)[1], 16)
    if not (slen - 1 <= max_names and data[hdr + soff] == 0 and (data[hdr + soff + slen - 1] == 0)):
        raise ValueError('Kernel BTF validation failed')
    strings = data[hdr + soff:hdr + soff + slen]

    def typename(offset):
        return strings[offset:strings.find(b'\x00', offset)].decode()
    table = {0: ('void', 0, 0, 0, b'')}
    cursor = hdr + toff
    end = cursor + tlen
    types = 0
    kinds = set()
    while cursor < end:
        name, info, value = struct.unpack_from('<III', data, cursor)
        kind = info >> 24 & 31
        vlen = info & 65535
        cursor += 12
        types += 1
        kinds.add(kind)
        if not (name < slen and name <= max_names):
            raise ValueError('Kernel BTF validation failed')
        lengths = {1: 4, 2: 0, 3: 12, 4: vlen * 12, 5: vlen * 12, 6: vlen * 8, 7: 0, 8: 0, 9: 0, 10: 0, 11: 0, 12: 0, 13: vlen * 8, 14: 4, 15: vlen * 12}
        if not kind in lengths:
            raise ValueError('Kernel BTF validation failed')
        if kind == 6:
            if not info >> 31 == 0:
                raise ValueError('legacy ENUM kind_flag unsupported')
        if kind == 12:
            if not (vlen <= 1 and info >> 31 == 0):
                raise ValueError('legacy function linkage unsupported')
        table[types] = (typename(name), kind, value, info, data[cursor:cursor + lengths[kind]])
        cursor += lengths[kind]
    if not (cursor == end and types < max_types):
        raise ValueError('Kernel BTF validation failed')
    seq_ids = [i for i, t in table.items() if t[0] == 'seq_file' and t[1] == 4]
    if not len(seq_ids) == 1:
        raise ValueError('Ambiguous seq_file BTF graphs: ' + str(seq_ids))
    meta_ids = [i for i, t in table.items() if t[0] == 'bpf_iter_meta' and t[1] == 4]
    if not len(meta_ids) == 1:
        raise ValueError('Kernel BTF validation failed')

    def find_member(idx, wanted):
        name, kind, value, info, extra = table[idx]
        if not kind in [4, 5]:
            raise ValueError('Kernel BTF validation failed')
        for i in range(info & 65535):
            member, target, offset = struct.unpack_from('<III', extra, i * 12)
            if typename(member) == wanted:
                return target
            if member == 0 and table[target][1] in [4, 5]:
                found = find_member(target, wanted)
                if found:
                    return found
        return None
    ptr = find_member(meta_ids[0], 'seq')
    if not (ptr and table[ptr][1] == 2):
        raise ValueError('Kernel BTF validation failed')
    if not table[ptr][2] == seq_ids[0]:
        raise ValueError('Iterator meta uses another seq_file type')
    helper_address = None
    for line in final.splitlines():
        parts = line.split()
        if len(parts) == 3 and parts[2] == 'btf_seq_file_ids':
            helper_address = int(parts[0], 16)
    if not helper_address:
        raise ValueError('Kernel BTF validation failed')
    sections = subprocess.check_output([str(llvm / 'llvm-readelf'), '-SW', str(k / 'vmlinux')], text=True)
    section_line = next((l for l in sections.splitlines() if ' .BTF_ids ' in l))
    section_base = int(section_line.split('.BTF_ids')[1].split()[1], 16)
    ids_path = b / 'BTF_ids.bin'
    subprocess.run([str(llvm / 'llvm-objcopy'), '--dump-section', '.BTF_ids=' + str(ids_path), str(k / 'vmlinux')], check=True)
    helper_type = struct.unpack_from('<I', ids_path.read_bytes(), helper_address - section_base)[0]
    if not helper_type == seq_ids[0]:
        raise ValueError('Typed helper and iterator pointer BTF IDs differ')
    report = {'parser_uses_actual_linker_boundaries': True, 'obsolete_weak_boundaries_absent': True, 'section_size_matches_boundary_span': True, 'btf_bytes': size, 'header_valid': True, 'types': types, 'string_bytes': slen, 'consumer_type_limit': max_types, 'consumer_string_offset_limit': max_names, 'consumer_limits_fit': True, 'unique_seq_file_type': True, 'seq_file_btf_id': seq_ids[0], 'iterator_and_helper_type_ids_match': True, 'runtime_kernel_type_validation_tested': False}
    rendered = json.dumps(report, indent=2) + '\n'
    if args.output:
        args.output.write_text(rendered)
    print(rendered, end='')
if __name__ == '__main__':
    main()

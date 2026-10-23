#!/usr/bin/env python3
"""Verify installed APK/APEX keys, recovery OTA trust and AVB in signed target files."""
import argparse
import concurrent.futures
import gzip
import hashlib
import importlib.util
import io
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import tempfile
import zipfile

spec = importlib.util.spec_from_file_location('release_signing', Path(__file__).with_name('release-signing.py'))
signing = importlib.util.module_from_spec(spec)
spec.loader.exec_module(signing)


def cpio_files(data):
    pos = 0
    while pos + 110 <= len(data):
        if data[pos:pos + 6] not in (b'070701', b'070702'):
            raise ValueError('Unsupported recovery CPIO')
        size = int(data[pos + 54:pos + 62], 16)
        name_size = int(data[pos + 94:pos + 102], 16)
        name = data[pos + 110:pos + 110 + name_size - 1].decode()
        start = (pos + 110 + name_size + 3) & ~3
        if name == 'TRAILER!!!':
            return
        yield name, data[start:start + size]
        pos = (start + size + 3) & ~3


def signer_digests(output):
    return set(re.findall(r'(?:Signer #\d+:?|V[\d.]+ Signer:) certificate SHA-256 digest: ([0-9a-f]+)', output))


def verify(args):
    android, keys = args.android.resolve(), args.keys.resolve()
    inventory = signing.check_keys(keys, signing.plan(args.target_files)['aliases'])
    release_pin = (Path(__file__).resolve().parent.parent / 'ota/release-cert.sha256').read_text().strip()
    if inventory['certificates']['releasekey'] != release_pin:
        raise ValueError('Release certificate pin mismatch')
    env = os.environ.copy()
    env['JAVA_HOME'] = str(android / 'prebuilts/jdk/jdk21/linux-x86')
    env['PATH'] = str(Path(env['JAVA_HOME']) / 'bin') + ':' + str(android / 'out/host/linux-x86/bin') + ':' + env['PATH']
    args.work_dir.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='verify-release-', dir=args.work_dir) as temp:
        temp = Path(temp)
        with zipfile.ZipFile(args.target_files) as archive:
            for name in archive.namelist():
                path = Path(name)
                if path.is_absolute() or '..' in path.parts:
                    raise ValueError('Unsafe target-files path')
            archive.extractall(temp)
        certs = {x['name']: x['certificate'] for x in signing.rows((temp / 'META/apkcerts.txt').read_text())}
        records = []

        def apk_check(path, alias):
            result = subprocess.check_output(['apksigner', 'verify', '--print-certs', '--min-sdk-version', '37', str(path)], env=env, text=True)
            digests = signer_digests(result)
            if digests != {inventory['certificates'][alias]}:
                raise ValueError('APK/container certificate mismatch: ' + path.name)
            return path.name

        apks = list(temp.rglob('*.apk'))
        jobs = []
        with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
            for path in apks:
                cert = certs[path.name]
                if cert in {'PRESIGNED', 'EXTERNAL'}:
                    continue
                stem = Path(cert).name.removesuffix('.x509.pem')
                alias = stem if stem in signing.BASE_KEYS else 'releasekey'
                jobs.append(pool.submit(apk_check, path, alias))
            for job in jobs:
                records.append(job.result())
        print('Standalone APK signatures verified:', len(records), flush=True)
        apexes = []
        nested_apks = []
        presigned = []
        for path in sorted([*temp.rglob('*.apex'), *temp.rglob('*.capex')]):
            alias = path.name.removesuffix('.apex').removesuffix('.capex')
            if alias == 'com.android.apex.cts.shim':
                presigned.append(path.name)
                continue
            apk_check(path, alias)
            actual = path
            if path.suffix == '.capex':
                actual = temp / (alias + '.decompressed.apex')
                subprocess.run(['deapexer', 'decompress', '--input', str(path), '--output', str(actual)], check=True, env=env, capture_output=True)
                apk_check(actual, alias)
            with zipfile.ZipFile(actual) as archive:
                public_key = temp / 'expected.avbpubkey'
                subprocess.run(['avbtool', 'extract_public_key', '--key', str(keys / (alias + '.pem')), '--output', str(public_key)], check=True, env=env, capture_output=True)
                if archive.read('apex_pubkey') != public_key.read_bytes():
                    raise ValueError('APEX public-key mismatch: ' + alias)
                payload = temp / 'apex_payload.img'
                payload.write_bytes(archive.read('apex_payload.img'))
                subprocess.run(['avbtool', 'verify_image', '--image', str(payload), '--key', str(keys / (alias + '.pem'))], check=True, env=env, capture_output=True)
            extracted = temp / 'apex-extracted'
            subprocess.run(['deapexer', '--debugfs_path', str(android / 'out/host/linux-x86/bin/debugfs_static'),
                            '--fsckerofs_path', str(android / 'out/host/linux-x86/bin/fsck.erofs'),
                            'extract', str(actual), str(extracted)], check=True, env=env, capture_output=True)
            for apk in extracted.rglob('*.apk'):
                cert = certs[apk.name]
                if cert in {'PRESIGNED', 'EXTERNAL'}:
                    raise ValueError('Unexpected externally signed APK inside re-signed APEX: ' + apk.name)
                stem = Path(cert).name.removesuffix('.x509.pem')
                apk_check(apk, stem if stem in signing.BASE_KEYS else 'releasekey')
                nested_apks.append(apk.name)
            shutil.rmtree(extracted)
            apexes.append(alias)
        print('APEX container/payload signatures verified:', len(apexes), flush=True)
        for name in ['vbmeta.img', 'recovery.img']:
            subprocess.run(['avbtool', 'verify_image', '--image', str(temp / 'IMAGES' / name), '--key', str(keys / 'avb.pem')],
                           check=True, env=env, capture_output=True)
        trust = []
        for path in temp.rglob('otacerts.zip'):
            with zipfile.ZipFile(path) as archive:
                for info in archive.infolist():
                    result = subprocess.run(['openssl', 'x509', '-outform', 'DER'], input=archive.read(info), capture_output=True, check=True)
                    if hashlib.sha256(result.stdout).hexdigest() != release_pin:
                        raise ValueError('Old/foreign OTA trust certificate: ' + str(path))
            trust.append(str(path.relative_to(temp)))
        unpacked = temp / 'unpacked-recovery'
        subprocess.run(['unpack_bootimg', '--boot_img', str(temp / 'IMAGES/recovery.img'), '--out', str(unpacked)],
                       check=True, env=env, stdout=subprocess.DEVNULL)
        ramdisk = (unpacked / 'ramdisk').read_bytes()
        if ramdisk.startswith(b'\x1f\x8b'):
            ramdisk = gzip.decompress(ramdisk)
        elif not ramdisk.startswith((b'070701', b'070702')):
            ramdisk = subprocess.check_output(['lz4', '-dc', str(unpacked / 'ramdisk')], env=env)
        embedded_trust = 0
        for name, data in cpio_files(ramdisk):
            if name.endswith('otacerts.zip'):
                with zipfile.ZipFile(io.BytesIO(data)) as archive:
                    for cert in archive.infolist():
                        result = subprocess.run(['openssl', 'x509', '-outform', 'DER'], input=archive.read(cert), capture_output=True, check=True)
                        if hashlib.sha256(result.stdout).hexdigest() != release_pin:
                            raise ValueError('Recovery image trusts an old/foreign OTA key')
                        embedded_trust += 1
        if not embedded_trust:
            raise ValueError('No OTA certificate found in actual recovery ramdisk')
        result = {'standalone_apks_verified': len(records), 'apex_containers_and_payloads_verified': len(apexes),
                  'nested_apks_verified': len(nested_apks),
                  'presigned_cts_shim_retained': presigned, 'ota_trust_archives': trust,
                  'actual_recovery_ota_certificates_verified': embedded_trust,
                  'avb_vbmeta_recovery_signatures_valid': True, 'release_certificate_sha256': release_pin}
        args.output.write_text(json.dumps(result, indent=2) + '\n')
        print(json.dumps(result, indent=2))


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--target-files', type=Path, required=True)
    p.add_argument('--keys', type=Path, required=True)
    p.add_argument('--android', type=Path, required=True)
    p.add_argument('--work-dir', type=Path, required=True)
    p.add_argument('--output', type=Path, required=True)
    args = p.parse_args()
    try:
        verify(args)
    except (ValueError, OSError, KeyError, subprocess.CalledProcessError) as e:
        p.exit(1, f'Release verification failed: {e}\n')


if __name__ == '__main__':
    main()

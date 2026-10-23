#!/usr/bin/env python3
"""Prepare LOS24 v2 update metadata locally; never publish or change signing keys."""
import argparse
import datetime
import hashlib
import json
from pathlib import Path
import re
import struct
import subprocess
from urllib.parse import quote, urlparse
import zipfile

DEVICE = 'gta4xlveu'
VERSION = '24.0'
REPOSITORY = 'tylxr59/lineageos-for-gta4xlveu'
# AOSP build/make/target/product/security/testkey.x509.pem (SHA-256 of DER).
PUBLIC_TEST_CERT = 'a40da80a59d170caa950cf15c18c454d47a39b26989d8b640ecd745ba71bf5dc'


def require(condition, message):
    if not condition:
        raise ValueError(message)


def validate(feed):
    require(isinstance(feed, list), 'LOS24 feed must be a v2 JSON array')
    seen = set()
    previous = float('inf')
    for build in feed:
        require(isinstance(build, dict), 'Build must be an object')
        stamp = build.get('datetime')
        require(type(stamp) is int and stamp > 0, 'datetime must be positive UNIX seconds')
        require(stamp < previous, 'Builds must have unique timestamps, newest first')
        previous = stamp
        require(build.get('version') == VERSION, 'This feed serves LineageOS 24.0 only')
        require(build.get('type') == 'unofficial', 'Build type must be unofficial')
        files = build.get('files')
        require(isinstance(files, list) and len(files) == 1, 'Exactly one full ROM file per build')
        f = files[0]
        require(isinstance(f, dict), 'File must be an object')
        name = f.get('filename', '')
        require(isinstance(name, str) and re.fullmatch(r'lineage-24\.0-\d{8}-UNOFFICIAL-gta4xlveu\.zip', name), 'Unexpected ROM filename/device/version')
        digest = f.get('sha256', '')
        require(isinstance(digest, str) and re.fullmatch('[0-9a-f]{64}', digest), 'Invalid SHA-256')
        require(digest not in seen, 'Duplicate ROM digest')
        seen.add(digest)
        require(type(f.get('size')) is int and f['size'] > 0, 'Invalid ROM byte size')
        require(f.get('os_sdk_level') == 37, 'Expected Android17/API37')
        patch = f.get('os_patch_level', '')
        require(isinstance(patch, str), 'Invalid security patch')
        datetime.date.fromisoformat(patch)
        url = f.get('url', '')
        require(isinstance(url, str), 'Invalid URL')
        parsed = urlparse(url)
        prefix = '/' + REPOSITORY + '/releases/download/'
        require(parsed.scheme == 'https' and parsed.netloc == 'github.com' and
                parsed.path.startswith(prefix) and not parsed.query and not parsed.fragment and
                parsed.path.endswith('/' + name), 'Expected a direct HTTPS release asset in this repository')
        ranges = f.get('ota_property_files')
        require(isinstance(ranges, str) and ranges.strip(), 'Missing OTA metadata byte ranges')
        for token in ranges.strip().split(','):
            require(re.fullmatch(r'[A-Za-z0-9_.-]+:\d+:\d+', token.strip()), 'Invalid OTA property-files range')
    return feed


def file_sha256(path):
    with path.open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def read_pin(path):
    value = path.read_text().strip()
    require(re.fullmatch('[0-9a-f]{64}', value), 'Certificate pin must be one lowercase SHA-256 hex digest')
    require(value != PUBLIC_TEST_CERT, 'Public AOSP test certificate cannot be a release identity')
    return value


def certificate_digest(pem):
    result = subprocess.run(['openssl', 'x509', '-outform', 'DER'], input=pem,
                            capture_output=True, check=True)
    return hashlib.sha256(result.stdout).hexdigest()


def prepare(rom, pin, tag):
    require(re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9._-]*', tag), 'Invalid release tag')
    expected = read_pin(pin)
    with zipfile.ZipFile(rom) as archive:
        require(archive.testzip() is None, 'ZIP CRC check failed')
        names = archive.namelist()
        require(len(names) == len(set(names)), 'Duplicate ZIP entries')
        require('payload.bin' not in names, 'This device requires a non-A/B full OTA')
        metadata = dict(line.split('=', 1) for line in
                        archive.read('META-INF/com/android/metadata').decode().splitlines() if '=' in line)
        require(metadata.get('pre-device') == DEVICE, 'OTA targets a different/multiple devices')
        require(metadata.get('ota-type') == 'BLOCK', 'Expected a block OTA')
        require('pre-build' not in metadata and 'pre-build-incremental' not in metadata, 'Incremental OTA is not supported by this release tool')
        require(metadata.get('post-build', '').endswith('/release-keys'), 'Use release-signed target files, not development/test-key builds')
        require(metadata.get('post-sdk-level') == '37', 'Expected Android17/API37 metadata')
        actual = certificate_digest(archive.read('META-INF/com/android/otacert'))
        require(actual != PUBLIC_TEST_CERT and actual == expected, 'OTA certificate does not match the pinned release identity')
        ranges = metadata.get('ota-property-files', '').strip()
        require(ranges, 'OTA byte-range metadata missing')
        # Verify ranges against the actual ZIP local headers, not filename guesses.
        with rom.open('rb') as raw:
            for token in ranges.split(','):
                name, offset, length = token.strip().split(':')
                matches = [n for n in names if n.rsplit('/', 1)[-1] == name]
                require(len(matches) == 1, 'Ambiguous OTA metadata range')
                info = archive.getinfo(matches[0])
                raw.seek(info.header_offset)
                header = raw.read(30)
                require(header[:4] == b'PK\x03\x04', 'Invalid local ZIP header')
                name_len, extra_len = struct.unpack_from('<HH', header, 26)
                require(info.compress_type == zipfile.ZIP_STORED and
                        int(offset) == info.header_offset + 30 + name_len + extra_len and
                        int(length) == info.file_size, 'OTA byte range does not match ZIP content')
        entry = {'datetime': int(metadata['post-timestamp']), 'files': [{
            'filename': rom.name, 'os_patch_level': metadata['post-security-patch-level'],
            'os_sdk_level': 37, 'ota_property_files': ranges,
            'sha256': file_sha256(rom),
            'size': rom.stat().st_size,
            'url': f'https://github.com/{REPOSITORY}/releases/download/{quote(tag)}/{rom.name}',
        }], 'type': 'unofficial', 'version': VERSION}
    validate([entry])
    return entry


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='command', required=True)
    check = sub.add_parser('validate')
    check.add_argument('feed', type=Path)
    create = sub.add_parser('prepare')
    create.add_argument('rom', type=Path)
    create.add_argument('--tag', required=True)
    create.add_argument('--cert-pin', type=Path, default=Path(__file__).resolve().parent.parent / 'ota/release-cert.sha256')
    create.add_argument('--feed', type=Path, default=Path(__file__).resolve().parent.parent / 'ota/gta4xlveu.json')
    create.add_argument('--output', type=Path, required=True, help='Write a candidate feed outside the live ota directory')
    args = parser.parse_args()
    try:
        if args.command == 'validate':
            feed = validate(json.loads(args.feed.read_text()))
            print(f'Valid LOS24 v2 feed: {len(feed)} build(s)')
        else:
            require(args.output.resolve() != args.feed.resolve(), 'Prepare to a candidate path; publish the live feed only after assets exist')
            entry = prepare(args.rom, args.cert_pin, args.tag)
            feed = validate(json.loads(args.feed.read_text()))
            require(not feed or entry['datetime'] > feed[0]['datetime'], 'Build must be newer than the current release')
            feed = validate([entry, *feed])
            args.output.parent.mkdir(parents=True, exist_ok=True)
            args.output.write_text(json.dumps(feed, indent=2) + '\n')
            print(f'Candidate ready at {args.output}; nothing published. Certificate comparison is not whole-file signature verification.')
    except (ValueError, OSError, KeyError, zipfile.BadZipFile, subprocess.CalledProcessError) as error:
        parser.exit(1, f'Error: {error}\n')


if __name__ == '__main__':
    main()

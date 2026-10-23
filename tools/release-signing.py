#!/usr/bin/env python3
"""Persistent local release keys and Android target-files signing. Never publishes."""
import argparse
import fcntl
import hashlib
import io
import json
import os
from pathlib import Path
import re
import secrets
import shlex
import shutil
import tempfile
import subprocess
import tarfile
import zipfile

BASE_KEYS = ('releasekey', 'platform', 'shared', 'media', 'networkstack', 'bluetooth', 'sdk_sandbox', 'nfc')


def run(argv, **kwargs):
    return subprocess.run(list(map(str, argv)), check=True, **kwargs)


def rows(text):
    return [dict(x.split('=', 1) for x in shlex.split(line))
            for line in text.splitlines() if line.strip()]


def metadata(source, name):
    if source.is_dir():
        return (source / 'META' / name).read_text()
    with zipfile.ZipFile(source) as archive:
        return archive.read('META/' + name).decode()


def plan(source):
    apexes = []
    presigned = []
    for row in rows(metadata(source, 'apexkeys.txt')):
        if row['private_key'] == 'PRESIGNED':
            presigned.append(row['name'])
            continue
        name = row['name'].removesuffix('.apex')
        if not re.fullmatch(r'[A-Za-z0-9_.-]+', name):
            raise ValueError('Unsafe APEX key name')
        apexes.append(name)
    return {'schema': 1, 'aliases': sorted(set(BASE_KEYS) | set(apexes) | {'avb'}),
            'apexes': sorted(apexes), 'presigned_apexes': sorted(presigned)}


def cert_digest(path):
    cert = subprocess.check_output(['openssl', 'x509', '-in', str(path), '-outform', 'DER'])
    return hashlib.sha256(cert).hexdigest()


def check_keys(keys, aliases):
    if keys.stat().st_mode & 0o077:
        raise ValueError('Key directory must have mode 0700')
    inventory = json.loads((keys / 'inventory.json').read_text())
    for name in aliases:
        expected = inventory['certificates'].get(name)
        if not expected or expected != cert_digest(keys / (name + '.x509.pem')):
            raise ValueError('Missing/changed certificate: ' + name)
        for suffix in ['.pem', '.pk8']:
            path = keys / (name + suffix)
            if not path.is_file() or path.stat().st_mode & 0o077:
                raise ValueError('Missing or overly permissive private key: ' + str(path))
        pub = subprocess.check_output(['openssl', 'x509', '-in', str(keys / (name + '.x509.pem')), '-pubkey', '-noout'])
        for suffix, form in [('.pem', 'PEM'), ('.pk8', 'DER')]:
            key_pub = subprocess.check_output(['openssl', 'pkey', '-in', str(keys / (name + suffix)), '-inform', form, '-pubout'])
            if key_pub != pub:
                raise ValueError('Private key/certificate mismatch: ' + name)
    return inventory


def initialize(source, keys):
    info = plan(source)
    keys.mkdir(parents=True, mode=0o700, exist_ok=True)
    if keys.stat().st_mode & 0o077:
        raise ValueError('Key directory must have mode 0700')
    inventory_path = keys / 'inventory.json'
    inventory = json.loads(inventory_path.read_text()) if inventory_path.exists() else {'schema': 1, 'certificates': {}}
    # Refuse partial pairs and changed existing identities. Never regenerate a key.
    for name in info['aliases']:
        paths = [keys / (name + s) for s in ['.pem', '.pk8', '.x509.pem']]
        if any(x.exists() for x in paths):
            if not all(x.exists() for x in paths):
                raise ValueError('Partial key set; recover it before continuing: ' + name)
            digest = cert_digest(paths[2])
            if name in inventory['certificates'] and inventory['certificates'][name] != digest:
                raise ValueError('Existing signing identity changed: ' + name)
        else:
            if name in inventory['certificates']:
                raise ValueError('Previously recorded key is missing; restore backup: ' + name)
            run(['openssl', 'genpkey', '-algorithm', 'RSA', '-pkeyopt', 'rsa_keygen_bits:4096', '-out', paths[0]], stderr=subprocess.DEVNULL)
            run(['openssl', 'pkcs8', '-topk8', '-outform', 'DER', '-in', paths[0], '-out', paths[1], '-nocrypt'])
            run(['openssl', 'req', '-new', '-x509', '-sha256', '-key', paths[0], '-out', paths[2], '-days', '10000',
                 '-subj', '/O=tylxr59/OU=gta4xlveu/CN=' + name])
            digest = cert_digest(paths[2])
            print('Created persistent key:', name, flush=True)
        inventory['certificates'][name] = digest
        inventory['plan'] = info
        inventory_path.write_text(json.dumps(inventory, indent=2) + '\n')
    check_keys(keys, info['aliases'])
    print('Key inventory verified:', len(info['aliases']), 'identities; no private material printed.')


def signing_args(source, keys):
    info = plan(source)
    check_keys(keys, info['aliases'])
    args = ['-o', '-d', str(keys)]
    # Preserve platform/shared/network privilege relationships. Other module/test
    # APK identities (including APKs nested inside APEXes) map to releasekey.
    seen = set()
    for row in rows(metadata(source, 'apkcerts.txt')):
        cert = row['certificate']
        if cert in {'PRESIGNED', 'EXTERNAL'}:
            continue
        old = cert.removesuffix('.x509.pem')
        stem = Path(old).name
        alias = stem if stem in BASE_KEYS else 'releasekey'
        if stem in {'testkey', 'devkey'}:
            alias = 'releasekey'
        mapping = old + '=' + str(keys / alias)
        if mapping not in seen:
            args.extend(['-k', mapping])
            seen.add(mapping)
    # The extra upstream recovery key must not remain as an alternate trust root.
    args.extend(['-k', 'vendor/lineage/build/target/product/security/lineage=' + str(keys / 'releasekey')])
    for name in info['apexes']:
        args.extend(['--extra_apks', name + '.apex=' + str(keys / name),
                     '--extra_apex_payload_key', name + '.apex=' + str(keys / (name + '.pem'))])
    for partition in ['vbmeta', 'recovery']:
        args.extend(['--avb_' + partition + '_key', str(keys / 'avb.pem'),
                     '--avb_' + partition + '_algorithm', 'SHA256_RSA4096'])
    return args



def normalize_ota_extras(misc, ota_keys, key_map):
    """Deduplicate mapped OTA keys before Android creates trust ZIPs.

    Releasetools writes each mapped extra key verbatim, including duplicate ZIP
    names. Recovery's libziparchive rejects that entire archive.
    """
    def mapped(key):
        key = key.removesuffix('.x509.pem')
        return key_map.get(key, key)

    values = dict(line.split('=', 1) for line in misc.splitlines() if '=' in line)
    primary_keys = ota_keys.split() or [values.get('default_system_dev_certificate',
                                                   'build/make/target/product/security/testkey')]
    primary = {mapped(key) for key in primary_keys}
    lines = []
    for line in misc.splitlines():
        name, sep, value = line.partition('=')
        if sep and name in {'extra_recovery_keys', 'extra_ota_keys'}:
            seen = set(primary)
            keep = []
            for key in value.split():
                identity = mapped(key)
                if identity not in seen:
                    keep.append(key)
                    seen.add(identity)
            line = name + '=' + ' '.join(keep)
        lines.append(line)
    return '\n'.join(lines) + '\n'


def sign(source, keys, android, output):
    if not source.is_file() or output.exists():
        raise ValueError('Input ZIP required and output must not exist')
    output.parent.mkdir(parents=True, exist_ok=True)
    args = signing_args(source, keys)
    env = os.environ.copy()
    env['JAVA_HOME'] = str(android / 'prebuilts/jdk/jdk21/linux-x86')
    env['PATH'] = str(Path(env['JAVA_HOME']) / 'bin') + ':' + str(android / 'out/host/linux-x86/bin') + ':' + env['PATH']
    key_map = {root + '/' + name: str(keys / ('releasekey' if name in {'testkey', 'devkey'} else name))
               for root in ['build/make/target/product/security', 'build/target/product/security']
               for name in [*BASE_KEYS, 'testkey', 'devkey']}
    key_map.update(dict(args[i + 1].split('=', 1) for i, arg in enumerate(args) if arg == '-k'))
    misc = metadata(source, 'misc_info.txt')
    normalized = normalize_ota_extras(misc, metadata(source, 'otakeys.txt'), key_map)
    # Keep the unsigned build untouched. Info-ZIP preserves the other compressed
    # entries while replacing metadata, without duplicate target-files entries.
    with tempfile.TemporaryDirectory(prefix='signing-input-', dir=output.parent) as work:
        work = Path(work).resolve()
        prepared = work / 'target-files.zip'
        shutil.copyfile(source, prepared)
        (work / 'META').mkdir()
        (work / 'META/misc_info.txt').write_text(normalized)
        run(['zip', '-q', '-d', prepared, 'META/misc_info.txt'], env=env)
        run(['zip', '-q', prepared, 'META/misc_info.txt'], cwd=work, env=env)
        run([android / 'out/host/linux-x86/bin/sign_target_files_apks', '-p', android / 'out/host/linux-x86',
             '--threads', '8', *args, prepared, output], cwd=android, env=env)


def backup(keys, destination):
    inventory = json.loads((keys / 'inventory.json').read_text())
    check_keys(keys, inventory['certificates'])
    destination.mkdir(parents=True, exist_ok=True, mode=0o700)
    encrypted = destination / 'gta4xlveu-release-keys.tar.gpg'
    password = keys.parent / 'gta4xlveu-backup-passphrase.txt'
    if encrypted.exists():
        raise ValueError('Backup output exists; choose a new directory')
    if not password.exists():
        password.write_text(secrets.token_urlsafe(48) + '\n')
    if password.stat().st_mode & 0o077:
        raise ValueError('Backup passphrase file must have mode 0600')
    payload = io.BytesIO()
    with tarfile.open(fileobj=payload, mode='w') as archive:
        archive.add(keys, arcname='gta4xlveu-release', filter=lambda info: None if info.name.endswith('/.lock') else info)
    home = destination / 'gnupg'
    home.mkdir(mode=0o700)
    command = ['gpg', '--homedir', home, '--batch', '--pinentry-mode', 'loopback', '--passphrase-file', password]
    run([*command, '--symmetric', '--cipher-algo', 'AES256', '--output', encrypted], input=payload.getvalue(), stderr=subprocess.PIPE)
    result = subprocess.check_output(list(map(str, [*command, '--decrypt', encrypted])), stderr=subprocess.DEVNULL)
    if hashlib.sha256(result).digest() != hashlib.sha256(payload.getvalue()).digest():
        raise ValueError('Encrypted backup round-trip failed')
    print('Encrypted key backup verified:', encrypted)
    print('Backup password saved separately; copy archive and password separately to owner-controlled storage.')


def main():
    os.umask(0o077)
    p = argparse.ArgumentParser(description=__doc__)
    sub = p.add_subparsers(dest='action', required=True)
    for action in ['plan', 'init', 'sign']:
        cmd = sub.add_parser(action)
        cmd.add_argument('--target-files', type=Path, required=True)
        if action != 'plan':
            cmd.add_argument('--keys', type=Path, required=True)
        if action == 'sign':
            cmd.add_argument('--android', type=Path, required=True)
            cmd.add_argument('--output', type=Path, required=True)
    cmd = sub.add_parser('backup')
    cmd.add_argument('--keys', type=Path, required=True)
    cmd.add_argument('--output', type=Path, required=True)
    a = p.parse_args()
    try:
        if a.action == 'plan':
            print(json.dumps(plan(a.target_files), indent=2))
            return
        keys = a.keys.resolve()
        pin = Path(__file__).resolve().parent.parent / 'ota/release-cert.sha256'
        if pin.exists():
            certificate = keys / 'releasekey.x509.pem'
            if not certificate.is_file() or cert_digest(certificate) != pin.read_text().strip():
                raise ValueError('Release identity is pinned; restore its keys from backup instead of generating new keys')
        keys.mkdir(parents=True, exist_ok=True, mode=0o700)
        with (keys / '.lock').open('a') as lock:
            fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
            if a.action == 'init':
                initialize(a.target_files.resolve(), keys)
            elif a.action == 'sign':
                sign(a.target_files.resolve(), keys, a.android.resolve(), a.output.resolve())
            else:
                backup(keys, a.output.resolve())
    except (ValueError, OSError, KeyError, subprocess.CalledProcessError) as e:
        p.exit(1, f'Error: {e}\n')


if __name__ == '__main__':
    main()

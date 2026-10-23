"""Persistent identity, private-file permissions and whole-file signature checks."""
import importlib.machinery
import importlib.util
import io
import json
import os
from pathlib import Path
import struct
import subprocess
import tempfile
import unittest
import zipfile

ROOT = Path(__file__).resolve().parents[1]


def load(name, path):
    loader = importlib.machinery.SourceFileLoader(name, str(path))
    spec = importlib.util.spec_from_loader(name, loader)
    module = importlib.util.module_from_spec(spec)
    loader.exec_module(module)
    return module


signing = load('release_signing', ROOT / 'tools/release-signing.py')
verifier = load('verify_ota', ROOT / 'tools/verify-ota')
components = load('verify_release', ROOT / 'tools/verify-release.py')


class SigningTests(unittest.TestCase):
    def test_versioned_and_legacy_apksigner_output(self):
        digest = 'a' * 64
        self.assertEqual(components.signer_digests('Signer #1 certificate SHA-256 digest: ' + digest), {digest})
        self.assertEqual(components.signer_digests('V3.0 Signer: certificate SHA-256 digest: ' + digest), {digest})

    def test_plan_preserves_presigned_shim_and_rejects_traversal(self):
        with tempfile.TemporaryDirectory() as d:
            source = Path(d)
            (source / 'META').mkdir()
            apex = source / 'META/apexkeys.txt'
            apex.write_text('name="com.android.art.apex" private_key="old.pem"\n'
                            'name="shim.apex" private_key="PRESIGNED"\n')
            plan = signing.plan(source)
            self.assertIn('com.android.art', plan['aliases'])
            self.assertNotIn('shim', plan['aliases'])
            self.assertEqual(plan['presigned_apexes'], ['shim.apex'])
            apex.write_text('name="../../bad.apex" private_key="old.pem"')
            with self.assertRaises(ValueError):
                signing.plan(source)

    def test_partial_or_lost_keys_are_not_regenerated(self):
        with tempfile.TemporaryDirectory() as d:
            source = Path(d) / 'source'
            (source / 'META').mkdir(parents=True)
            (source / 'META/apexkeys.txt').write_text('')
            keys = Path(d) / 'keys'
            keys.mkdir(mode=0o700)
            (keys / 'avb.pem').write_text('incomplete-key')
            with self.assertRaises(ValueError):
                signing.initialize(source, keys)
            self.assertEqual((keys / 'avb.pem').read_text(), 'incomplete-key')
            (keys / 'avb.pem').unlink()
            (keys / 'inventory.json').write_text(json.dumps({'certificates': {'avb': '0' * 64}}))
            with self.assertRaises(ValueError):
                signing.initialize(source, keys)
            self.assertFalse((keys / 'avb.pem').exists())


class SignatureTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory()
        cls.root = Path(cls.tmp.name)
        cls.keys = cls.root / 'keys'
        cls.keys.mkdir(mode=0o700)
        cls.pem = cls.keys / 'releasekey.pem'
        cls.cert = cls.keys / 'releasekey.x509.pem'
        subprocess.run(['openssl', 'req', '-x509', '-newkey', 'rsa:2048', '-nodes',
                        '-keyout', str(cls.pem), '-out', str(cls.cert),
                        '-subj', '/CN=unit-test-only', '-days', '1'],
                       check=True, capture_output=True)
        subprocess.run(['openssl', 'pkcs8', '-topk8', '-outform', 'DER', '-in', str(cls.pem),
                        '-out', str(cls.keys / 'releasekey.pk8'), '-nocrypt'], check=True)
        for p in cls.keys.iterdir():
            p.chmod(0o600)
        cls.pin = cls.root / 'pin'
        cls.pin.write_text(signing.cert_digest(cls.cert))
        (cls.keys / 'inventory.json').write_text(json.dumps({'certificates': {'releasekey': cls.pin.read_text()}}))

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def package(self):
        data = io.BytesIO()
        with zipfile.ZipFile(data, 'w') as archive:
            archive.writestr('META-INF/com/android/otacert', self.cert.read_bytes())
            archive.writestr('content.txt', b'payload subject to tampering')
        content = self.root / 'content'
        content.write_bytes(data.getvalue()[:-2])
        signature = subprocess.check_output(['openssl', 'cms', '-sign', '-binary', '-in', str(content),
                                             '-signer', str(self.cert), '-inkey', str(self.pem),
                                             '-outform', 'DER', '-nosmimecap', '-md', 'sha256'])
        length = len(signature) + 6
        rom = self.root / 'test.zip'
        rom.write_bytes(content.read_bytes() + struct.pack('<H', length) + signature +
                        struct.pack('<H2sH', length, b'\xff\xff', length))
        return rom

    def test_whole_file_signature_accepts_valid_and_rejects_tampering(self):
        rom = self.package()
        self.assertTrue(verifier.verify(rom, self.cert, self.pin, self.root)['whole_file_signature_valid'])
        data = bytearray(rom.read_bytes())
        data[data.index(b'payload subject')] ^= 1
        rom.write_bytes(data)
        with self.assertRaises(subprocess.CalledProcessError):
            verifier.verify(rom, self.cert, self.pin, self.root)

    def test_certificate_pin_mismatch_is_rejected(self):
        bad = self.root / 'wrong-pin'
        bad.write_text('0' * 64)
        with self.assertRaises(ValueError):
            verifier.verify(self.package(), self.cert, bad, self.root)

    def test_exposed_private_key_permissions_are_rejected(self):
        signing.check_keys(self.keys, ['releasekey'])
        self.pem.chmod(0o644)
        try:
            with self.assertRaises(ValueError):
                signing.check_keys(self.keys, ['releasekey'])
        finally:
            self.pem.chmod(0o600)


if __name__ == '__main__':
    unittest.main()

"""Metadata/security gates only: synthetic ZIPs are not signed installation tests."""
import copy
import hashlib
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
import zipfile

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
import ota


class FeedTests(unittest.TestCase):
    def entry(self):
        return {'datetime': 1792700000, 'files': [{
            'filename': 'lineage-24.0-20261023-UNOFFICIAL-gta4xlveu.zip',
            'os_patch_level': '2026-10-05', 'os_sdk_level': 37,
            'ota_property_files': 'metadata:69:300,metadata.pb:410:150',
            'sha256': '1' * 64, 'size': 1024,
            'url': 'https://github.com/tylxr59/lineageos-for-gta4xlveu/releases/download/test/lineage-24.0-20261023-UNOFFICIAL-gta4xlveu.zip',
        }], 'type': 'unofficial', 'version': '24.0'}

    def test_empty_and_valid_feed(self):
        self.assertEqual(ota.validate([]), [])
        ota.validate([self.entry()])

    def test_legacy_response_rejected(self):
        with self.assertRaises(ValueError):
            ota.validate({'response': []})

    def test_device_version_hash_size_and_url_gates(self):
        for key, value in [('filename', 'lineage-24.0-20261023-UNOFFICIAL-gta4xlve.zip'),
                           ('sha256', 'wrong'), ('size', True), ('os_sdk_level', 36),
                           ('url', 'https://example.com/rom.zip'), ('ota_property_files', 'bogus')]:
            with self.subTest(key=key), self.assertRaises(ValueError):
                item = self.entry()
                item['files'][0][key] = value
                ota.validate([item])
        item = self.entry()
        item['version'] = '25.0'
        with self.assertRaises(ValueError):
            ota.validate([item])

    def test_unique_newest_first_required(self):
        a = self.entry()
        b = copy.deepcopy(a)
        b['datetime'] += 1
        b['files'][0]['sha256'] = '2' * 64
        ota.validate([b, a])
        for feed in [[a, a], [a, b]]:
            with self.assertRaises(ValueError):
                ota.validate(feed)

    def test_public_test_pin_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            pin = Path(d) / 'pin'
            pin.write_text(ota.PUBLIC_TEST_CERT)
            with self.assertRaises(ValueError):
                ota.read_pin(pin)


class PrepareTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory()
        cls.root = Path(cls.tmp.name)
        cls.cert = cls.root / 'cert.pem'
        subprocess.run(['openssl', 'req', '-x509', '-newkey', 'rsa:2048', '-nodes',
                        '-keyout', str(cls.root / 'ephemeral.key'), '-out', str(cls.cert),
                        '-subj', '/CN=metadata-unit-test', '-days', '1'],
                       check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        cls.pin = cls.root / 'pin'
        cls.pin.write_text(ota.certificate_digest(cls.cert.read_bytes()))

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def make_rom(self, device='gta4xlveu', tags='release-keys', wrong_range=False):
        rom = self.root / 'lineage-24.0-20261023-UNOFFICIAL-gta4xlveu.zip'
        prop = 'metadata:0:0'
        for _ in range(8):
            metadata = (f'ota-type=BLOCK\npre-device={device}\npost-timestamp=1792700000\n'
                        f'post-sdk-level=37\npost-security-patch-level=2026-10-05\n'
                        f'post-build=samsung/gta4xlveu/gta4xlveu:17/BUILD/123:userdebug/{tags}\n'
                        f'ota-property-files={prop}\n').encode()
            with zipfile.ZipFile(rom, 'w', compression=zipfile.ZIP_STORED) as f:
                f.writestr('META-INF/com/android/metadata', metadata)
                f.writestr('META-INF/com/android/otacert', self.cert.read_bytes())
                f.writestr('system.transfer.list', '4\n0\n0\n0\n')
            expected = f'metadata:{30 + len("META-INF/com/android/metadata")}:{len(metadata)}'
            if wrong_range:
                return rom
            if expected == prop:
                return rom
            prop = expected
        raise AssertionError('Fixture range did not converge')

    def test_prepare_reads_actual_package(self):
        rom = self.make_rom()
        entry = ota.prepare(rom, self.pin, 'test-20261023')
        self.assertEqual(entry['datetime'], 1792700000)
        self.assertEqual(entry['files'][0]['size'], rom.stat().st_size)
        self.assertEqual(entry['files'][0]['sha256'], hashlib.sha256(rom.read_bytes()).hexdigest())

    def test_wrong_device_rejected(self):
        with self.assertRaises(ValueError):
            ota.prepare(self.make_rom(device='gta4xl'), self.pin, 'test')

    def test_test_key_build_rejected(self):
        with self.assertRaises(ValueError):
            ota.prepare(self.make_rom(tags='test-keys'), self.pin, 'test')

    def test_mismatched_certificate_rejected(self):
        bad = self.root / 'bad-pin'
        bad.write_text('0' * 64)
        with self.assertRaises(ValueError):
            ota.prepare(self.make_rom(), bad, 'test')

    def test_bad_range_rejected(self):
        with self.assertRaises(ValueError):
            ota.prepare(self.make_rom(wrong_range=True), self.pin, 'test')


if __name__ == '__main__':
    unittest.main()

"""Regression checks for original ZIPs and Kaggle's recursive ZIP extraction."""
from contextlib import redirect_stdout
import hashlib
import io
import json
from pathlib import Path
import runpy
import tempfile
import unittest
import zipfile


HERE = Path(__file__).resolve().parent
RESTORE = runpy.run_path(str(HERE / 'restore_in_kaggle.py'))['restore_student_114']
ARCHIVE = HERE / 'student_114_kaggle_restore.zip'
EXPORT = HERE / 'annotations.zip'


class RestoreTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.input = self.root / 'input'
        self.input.mkdir()
        self.output = self.root / 'output'
        with zipfile.ZipFile(ARCHIVE) as bundle:
            self.manifest = json.loads(bundle.read('student_114_manifest.json'))
            self.expected = {
                name: bundle.read('annotations/' + name)
                for name in self.manifest['files']
            }

    def unpack(self):
        with zipfile.ZipFile(ARCHIVE) as bundle:
            bundle.extractall(self.input)

    def add_legacy_export(self, present=False):
        data = EXPORT.read_bytes()
        manifest = self.input / 'student_114_manifest.json'
        document = json.loads(manifest.read_text(encoding='utf-8'))
        document['files']['annotations.zip'] = {
            'sha256': hashlib.sha256(data).hexdigest(), 'bytes': len(data),
        }
        manifest.write_text(json.dumps(document), encoding='utf-8')
        if present:
            (self.input / 'annotations/annotations.zip').write_bytes(data)
        else:
            with zipfile.ZipFile(EXPORT) as bundle:
                bundle.extractall(self.input / 'annotations/annotations')

    def restore(self):
        with redirect_stdout(io.StringIO()):
            return RESTORE(input_root=self.input, output=self.output)

    def assert_payload(self):
        for name, expected in self.expected.items():
            self.assertEqual((self.output / name).read_bytes(), expected, name)

    def test_zip(self):
        (self.input / ARCHIVE.name).write_bytes(ARCHIVE.read_bytes())
        self.assertEqual(self.restore(), self.output)
        self.assert_payload()

    def test_unpacked(self):
        self.unpack()
        self.restore()
        self.assert_payload()

    def test_legacy_recursively_unpacked_export(self):
        self.unpack()
        self.add_legacy_export()
        self.restore()
        self.assert_payload()
        self.assertFalse((self.output / 'annotations.zip').exists())

    def test_legacy_unpacked_and_hidden_registry_removed(self):
        self.unpack()
        self.add_legacy_export()
        (self.input / 'annotations/.state/content.json').unlink()
        self.restore()
        self.assert_payload()

    def test_intact_legacy_zip(self):
        self.unpack()
        self.add_legacy_export(present=True)
        legacy = self.root / ARCHIVE.name
        with zipfile.ZipFile(legacy, 'w') as bundle:
            for file in self.input.rglob('*'):
                if file.is_file():
                    bundle.write(file, file.relative_to(self.input))
        archive_input = self.root / 'legacy_input'
        archive_input.mkdir()
        legacy.rename(archive_input / legacy.name)
        self.input = archive_input
        self.restore()
        self.assert_payload()
        self.assertEqual((self.output / 'annotations.zip').read_bytes(), EXPORT.read_bytes())

    def test_missing_native_is_not_ignored(self):
        self.unpack()
        self.add_legacy_export()
        (self.input / 'annotations/source_mismatches/17390.json').unlink()
        with self.assertRaises(FileNotFoundError):
            self.restore()
        self.assertFalse(self.output.exists())

    def test_legacy_replacement_source_is_not_restored(self):
        self.unpack()
        relative = '_review/student_114_for_review.json'
        data = b'[]'
        (self.input / 'annotations' / relative).write_bytes(data)
        manifest = self.input / 'student_114_manifest.json'
        document = json.loads(manifest.read_text())
        document['files'][relative] = {
            'sha256': hashlib.sha256(data).hexdigest(), 'bytes': len(data),
        }
        manifest.write_text(json.dumps(document))
        self.restore()
        self.assert_payload()
        self.assertFalse((self.output / relative).exists())

    def test_corrupted_native_is_rejected(self):
        self.unpack()
        (self.input / 'annotations/18591.json').write_bytes(b'corrupt')
        with self.assertRaisesRegex(ValueError, 'checksum failed'):
            self.restore()
        self.assertFalse(self.output.exists())

    def test_corrupted_present_export_is_rejected(self):
        self.unpack()
        self.add_legacy_export(present=True)
        (self.input / 'annotations/annotations.zip').write_bytes(b'corrupt')
        with self.assertRaisesRegex(ValueError, 'checksum failed'):
            self.restore()
        self.assertFalse(self.output.exists())

    def test_repeat_restore_keeps_identical_payload(self):
        self.unpack()
        self.restore()
        self.restore()
        self.assert_payload()

    def test_newer_work_is_not_overwritten(self):
        self.unpack()
        self.restore()
        edited = self.output / '18591.json'
        edited.write_bytes(b'newer user work')
        with self.assertRaisesRegex(RuntimeError, 'No overwrite performed'):
            self.restore()
        self.assertEqual(edited.read_bytes(), b'newer user work')


if __name__ == '__main__':
    unittest.main()

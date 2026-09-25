import json
import tempfile
import unittest
import zipfile
from pathlib import Path

from maeron.core import scan_mods, toggle_enabled, export_json


class ScannerTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)

    def tearDown(self):
        self.temp.cleanup()

    def jar(self, name, entries):
        path = self.root / name
        with zipfile.ZipFile(path, "w") as archive:
            for filename, content in entries.items():
                archive.writestr(filename, content)
        return path

    def test_scans_fabric_metadata_and_missing_dependency(self):
        data = {"id":"demo", "name":"Demo Mod", "version":"1.2", "depends":{"minecraft":"1.20.1", "missing-lib":"*"}}
        self.jar("demo.jar", {"fabric.mod.json": json.dumps(data)})
        mod, = scan_mods(self.root)
        self.assertEqual((mod.name, mod.mod_id, mod.version, mod.loader), ("Demo Mod", "demo", "1.2", "Fabric"))
        self.assertEqual(mod.minecraft_versions, ["1.20.1"])
        self.assertTrue(any("missing-lib" in issue for issue in mod.issues))

    def test_detects_duplicate_id_and_multiple_versions(self):
        for name, version in (("a.jar", "1"), ("b.jar", "2")):
            self.jar(name, {"fabric.mod.json": json.dumps({"id":"same", "version":version})})
        mods = scan_mods(self.root)
        self.assertTrue(all(any("重複" in issue and "複数バージョン" in issue for issue in mod.issues) for mod in mods))

    def test_reports_corrupt_jar_and_scans_disabled(self):
        (self.root / "broken.jar").write_bytes(b"not a zip")
        self.jar("off.jar.disabled", {"fabric.mod.json": json.dumps({"id":"off", "version":"1"})})
        mods = {mod.file:mod for mod in scan_mods(self.root)}
        self.assertTrue(any("読み取りエラー" in issue for issue in mods["broken.jar"].issues))
        self.assertFalse(mods["off.jar.disabled"].enabled)

    def test_toggle_is_reversible_and_export_is_json(self):
        source = self.jar("demo.jar", {"fabric.mod.json": json.dumps({"id":"demo", "version":"1"})})
        disabled = toggle_enabled(source)
        self.assertTrue(disabled.name.endswith(".jar.disabled"))
        enabled = toggle_enabled(disabled)
        self.assertEqual(enabled.name, "demo.jar")
        output = self.root / "out.json"
        export_json(scan_mods(self.root), output)
        self.assertIn('"mod_id": "demo"', output.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()

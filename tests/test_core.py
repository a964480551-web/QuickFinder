import importlib.machinery
import importlib.util
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
LOADER = importlib.machinery.SourceFileLoader(
    "quick_finder_test", str(ROOT / "quick_finder.pyw")
)
SPEC = importlib.util.spec_from_loader("quick_finder_test", LOADER)
APP = importlib.util.module_from_spec(SPEC)
LOADER.exec_module(APP)


class FileIndexTests(unittest.TestCase):
    def setUp(self):
        self.index = APP.FileIndex()
        self.index.entries = [
            ("C:/Docs/report.pdf", "report.pdf", False),
            ("D:/Archive/report-old.pdf", "report-old.pdf", False),
            ("C:/Docs/Reports", "reports", True),
        ]

    def test_search_scope_and_folder_filter(self):
        results = self.index.search("report", scope_roots=["C:/"])
        self.assertEqual(len(results), 2)
        self.assertTrue(all(path.startswith("C:") for path, _ in results))
        self.assertEqual(
            self.index.search("report", scope_roots=["C:/"], dirs_only=True),
            [("C:/Docs/Reports", True)],
        )

    def test_sqlite_cache_round_trip(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            old_cache = APP.CACHE_FILE
            try:
                APP.CACHE_FILE = str(Path(temp_dir) / "index.sqlite3")
                self.index.save_cache(["C:/", "D:/"])
                entries, roots, saved_at = APP.FileIndex.load_cache()
            finally:
                APP.CACHE_FILE = old_cache
        self.assertEqual(entries, [(p, n, int(d)) for p, n, d in self.index.entries])
        self.assertEqual(len(roots), 2)
        self.assertGreater(saved_at, 0)


if __name__ == "__main__":
    unittest.main()

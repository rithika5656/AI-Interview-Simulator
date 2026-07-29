import unittest
from pathlib import Path


class FrontendBootstrapTest(unittest.TestCase):
    def test_runtime_ready_is_dispatched_after_page_load(self) -> None:
        html = Path("frontend/index.html").read_text(encoding="utf-8")

        self.assertIn("function dispatchRuntimeReady()", html)
        self.assertIn("window.addEventListener('load', dispatchRuntimeReady);", html)
        self.assertIn("dispatchRuntimeReady();", html)


if __name__ == "__main__":
    unittest.main()

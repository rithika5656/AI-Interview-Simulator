import unittest
from pathlib import Path


class FrontendBootstrapTest(unittest.TestCase):
    def test_frontend_bootstrap_uses_reliable_react_runtime_urls(self) -> None:
        html = Path("frontend/index.html").read_text(encoding="utf-8")
        router = Path("frontend/router.js").read_text(encoding="utf-8")

        self.assertIn("react.production.min.js", html)
        self.assertIn("react-dom.production.min.js", html)
        self.assertIn("react-router-dom.production.min.js", html)
        self.assertIn("function dispatchRuntimeReady()", html)
        self.assertIn("console.log('[BOOT] React runtime state'", html)
        self.assertIn("console.error('[BOOT] React runtime missing'", html)
        self.assertNotIn("setTimeout(mountRouter, 100);", router)
        self.assertIn("console.error('[ROUTER] React runtime missing'", router)


if __name__ == "__main__":
    unittest.main()

import unittest
from pathlib import Path


class FrontendBootstrapTest(unittest.TestCase):
    def test_frontend_bootstrap_uses_clean_react_18_startup(self) -> None:
        html = Path("frontend/index.html").read_text(encoding="utf-8")
        router = Path("frontend/router.js").read_text(encoding="utf-8")
        app = Path("frontend/app.js").read_text(encoding="utf-8")

        self.assertIn('src="config.js"', html)
        self.assertIn('src="apiClient.js"', html)
        self.assertIn('react.production.min.js', html)
        self.assertIn('react-dom.production.min.js', html)
        self.assertIn('react-router-dom.production.min.js', html)
        self.assertNotIn("dispatchRuntimeReady", html)
        self.assertNotIn("react-runtime-ready", html)
        self.assertNotIn("React not ready yet", html)

        self.assertIn("const root = ReactDOM.createRoot", router)
        self.assertIn("root.render(", router)
        self.assertIn("window.routerReady = true;", router)
        self.assertNotIn("startWhenReady", router)
        self.assertNotIn("setTimeout(", router)
        self.assertNotIn("React not ready yet", router)
        self.assertNotIn("react-runtime-ready", router)

        self.assertIn("window.addEventListener('router-ready', startAuthBootstrap, { once: true });", app)


if __name__ == "__main__":
    unittest.main()

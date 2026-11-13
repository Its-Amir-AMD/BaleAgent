from pathlib import Path
import ast
import unittest

ROOT = Path(__file__).resolve().parents[1]


class SourceIntegrityTests(unittest.TestCase):
    def test_python_sources_parse(self):
        sources = list(ROOT.rglob("*.py"))
        self.assertGreaterEqual(len(sources), 5)
        for source in sources:
            with self.subTest(source=source.relative_to(ROOT)):
                ast.parse(source.read_text(encoding="utf-8"), filename=str(source))

    def test_design_tokens_have_both_palettes(self):
        tree = ast.parse((ROOT / "ui" / "design_tokens.py").read_text(encoding="utf-8"))
        names = {node.targets[0].id for node in tree.body if isinstance(node, ast.Assign) and isinstance(node.targets[0], ast.Name)}
        self.assertIn("LIGHT", names)
        self.assertIn("DARK", names)

    def test_new_window_keeps_existing_controller(self):
        source = (ROOT / "ui" / "main_window.py").read_text(encoding="utf-8")
        self.assertIn("class RebuiltMainWindow(LegacyMainWindow)", source)
        self.assertIn("def _build_dashboard", source)
        self.assertIn("def _build_chats", source)
        self.assertIn("def render_messages", source)
        self.assertTrue((ROOT / "ui" / "pages" / "dashboard.py").is_file())
        self.assertTrue((ROOT / "ui" / "pages" / "chats.py").is_file())

    def test_chat_renderer_imports_shared_components_from_correct_package(self):
        source = (ROOT / "ui" / "pages" / "chats.py").read_text(encoding="utf-8")
        self.assertIn("from ..components import GlassPanel", source)
        self.assertNotIn("from .components import GlassPanel", source)

    def test_launcher_uses_new_entrypoint(self):
        self.assertIn("app.py", (ROOT / "run.bat").read_text(encoding="utf-8"))
        self.assertIn("app.py", (ROOT / "run.sh").read_text(encoding="utf-8"))

    def test_workspace_is_registered_in_root_stack_before_unlock(self):
        source = (ROOT / "ui" / "main_window.py").read_text(encoding="utf-8")
        tree = ast.parse(source)
        window = next(
            node for node in tree.body
            if isinstance(node, ast.ClassDef) and node.name == "RebuiltMainWindow"
        )
        build_shell = next(
            node for node in window.body
            if isinstance(node, ast.FunctionDef) and node.name == "_build_shell"
        )
        calls = [
            node for node in ast.walk(build_shell)
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute)
        ]
        registration = [
            node for node in calls
            if node.func.attr == "addWidget"
            and len(node.args) == 1
            and isinstance(node.args[0], ast.Attribute)
            and node.args[0].attr == "app_shell"
        ]
        self.assertTrue(registration, "app_shell must be added to root_stack")

        legacy_source = (ROOT / "legacy_app.py").read_text(encoding="utf-8")
        legacy_tree = ast.parse(legacy_source)
        legacy_window = next(
            node for node in legacy_tree.body
            if isinstance(node, ast.ClassDef) and node.name == "LegacyMainWindow"
        )
        unlock = next(
            node for node in legacy_window.body
            if isinstance(node, ast.FunctionDef) and node.name == "_unlock_app"
        )
        unlock_source = ast.get_source_segment(legacy_source, unlock) or ""
        self.assertIn("self.root_stack.indexOf(self.app_shell)", unlock_source)
        self.assertIn("self.root_stack.addWidget(self.app_shell)", unlock_source)

    def test_auth_page_does_not_disable_controls_with_automatic_network_check(self):
        source = (ROOT / "legacy_app.py").read_text(encoding="utf-8")
        tree = ast.parse(source)
        legacy = next(node for node in tree.body if isinstance(node, ast.ClassDef) and node.name == "LegacyMainWindow")
        init = next(node for node in legacy.body if isinstance(node, ast.FunctionDef) and node.name == "__init__")
        calls = [
            node.func.attr for node in ast.walk(init)
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute)
        ]
        self.assertNotIn("_check_saved_session", calls)
        self.assertIn("_set_auth_status", calls)

    def test_saved_session_check_uses_bounded_auth_helper(self):
        source = (ROOT / "legacy_app.py").read_text(encoding="utf-8")
        self.assertIn("verify_saved_session", source)
        helper = (ROOT / "ui" / "auth_flow.py").read_text(encoding="utf-8")
        self.assertIn("START_TIMEOUT_SECONDS = 30", helper)
        self.assertIn("client.stop()", helper)
        self.assertIn("finally:", helper)


    def test_auth_validation_requires_remote_account_rpc(self):
        helper = (ROOT / "ui" / "auth_flow.py").read_text(encoding="utf-8")
        self.assertIn("client.dialogs(limit=1)", helper)
        self.assertIn('"authenticated": True', helper)
        self.assertIn('"authenticated": False', helper)
        core = (ROOT / "bale_agent.py").read_text(encoding="utf-8")
        connected = core.split("async def _connected_client(self):", 1)[1].split("async def login(", 1)[0]
        self.assertIn("client.dialogs(limit=1)", connected)

    def test_auth_ui_unlocks_only_after_authenticated_probe(self):
        source = (ROOT / "legacy_app.py").read_text(encoding="utf-8")
        block = source.split("def _check_saved_session", 1)[1].split("def _unlock_app", 1)[0]
        self.assertIn('result.get("authenticated")', block)
        self.assertNotIn('if result.get("connected"):', block)

    def test_login_success_checks_persisted_session(self):
        source = (ROOT / "legacy_app.py").read_text(encoding="utf-8")
        self.assertIn("if not client.is_logged_in", source)
        self.assertIn("after_login=True", source)

    def test_liquid_glass_uses_real_cached_backdrop_blur(self):
        surfaces = (ROOT / "ui" / "components" / "surfaces.py").read_text(encoding="utf-8")
        self.assertIn("ImageFilter.GaussianBlur", surfaces)
        self.assertIn("blurred_region_for", surfaces)
        self.assertIn("_backdrop_image", surfaces)
        self.assertIn('LIQUID_VARIANTS = {"liquid", "dock"}', surfaces)
        requirements = (ROOT / "requirements.txt").read_text(encoding="utf-8")
        self.assertIn("Pillow", requirements)

    def test_content_pages_use_material_surfaces_not_liquid_surfaces(self):
        dashboard = (ROOT / "ui" / "pages" / "dashboard.py").read_text(encoding="utf-8")
        chats = (ROOT / "ui" / "pages" / "chats.py").read_text(encoding="utf-8")
        shell = (ROOT / "ui" / "main_window.py").read_text(encoding="utf-8")
        self.assertIn('variant="material"', dashboard)
        self.assertIn('variant="material"', chats)
        self.assertIn('variant="liquid"', shell)
        self.assertIn('variant="dock"', shell)

    def test_auth_buttons_are_wired_and_initial_state_is_actionable(self):
        source = (ROOT / "ui" / "main_window.py").read_text(encoding="utf-8")
        self.assertIn("self.auth_login_button.clicked.connect(self.start_login)", source)
        self.assertIn("self.auth_check_button.clicked.connect", source)
        self.assertIn("self.auth_fresh_button.clicked.connect(self.start_fresh_session)", source)
        self.assertIn("برای ورود، شماره موبایل را وارد کن", source)


if __name__ == "__main__":
    unittest.main()

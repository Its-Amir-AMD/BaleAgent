from pathlib import Path
import xml.etree.ElementTree as ET
import unittest

ROOT = Path(__file__).resolve().parents[1]


class SvgAssetTests(unittest.TestCase):
    def test_all_icon_assets_are_valid_svg(self):
        icons = list((ROOT / "assets" / "icons").glob("*.svg"))
        self.assertGreaterEqual(len(icons), 8)
        for icon in icons:
            with self.subTest(icon=icon.name):
                root = ET.parse(icon).getroot()
                self.assertTrue(root.tag.endswith("svg"))
                self.assertEqual(root.attrib.get("viewBox"), "0 0 24 24")


if __name__ == "__main__":
    unittest.main()

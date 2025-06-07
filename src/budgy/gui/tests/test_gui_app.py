import os
import sys
import unittest
from unittest.mock import patch

# Configure pygame for headless environment before importing BudgyViewerApp
os.environ['SDL_VIDEODRIVER'] = 'dummy'
os.environ['SDL_AUDIODRIVER'] = 'dummy'

# Skip tests on problematic CI environments
skip_gui_tests = (
    # Skip on Ubuntu Python 3.9 due to pygame compatibility issues
    (sys.platform.startswith('linux') and sys.version_info[:2] == (3, 9)) or
    # Skip on Windows due to pygame/SDL setup issues in CI
    sys.platform == 'win32'
)

if skip_gui_tests:
    import pytest
    pytest.skip(
        f"GUI tests skipped on {sys.platform} Python {sys.version_info[:2]} due to CI environment issues",
        allow_module_level=True
    )

from budgy.gui.viewer import BudgyViewerApp
class GuiAppTestCase(unittest.TestCase):
    gui_app = None
    def test_create(self):
        self.assertIsNotNone(GuiAppTestCase.gui_app)

    def test_setup(self):
        self.gui_app.setup()

    @classmethod
    def setUpClass(cls):
        testargs = ['prog']
        testargs = ['prog']
        with patch.object(sys, 'argv', testargs):
            GuiAppTestCase.gui_app = BudgyViewerApp()
    @classmethod
    def tearDownClass(cls):
        GuiAppTestCase.gui_app = None

if __name__ == '__main__':
    unittest.main()

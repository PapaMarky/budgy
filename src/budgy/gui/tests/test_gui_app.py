import sys
import unittest
from unittest.mock import patch

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

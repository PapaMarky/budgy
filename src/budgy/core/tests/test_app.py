import argparse
import unittest
import logging
from unittest.mock import patch
import sys, io

from budgy.core.app import BudgyApp
logger = logging.getLogger()
class MyTestCase(unittest.TestCase):
    def test_create(self):
        testargs = ['prog']
        with patch.object(sys, 'argv', testargs):
            app = BudgyApp('/my/test/app')
            self.assertIsNotNone(app)
            self.assertIsInstance(app.arg_parser, argparse.ArgumentParser)

            header = app._create_app_header()
            self.assertEqual(len(header.splitlines()), 7)

            with patch('sys.stdout', new = io.StringIO()) as fake_out:
                app.print_app_header()
                header = fake_out.getvalue()
                self.assertEqual(len(header.splitlines()), 7 + 1) # "print" adds a newline

            with patch.object(logger, 'info') as mock_info:
                app.log_app_header()
                mock_info.assert_called_with('##############################')

            app.run()


if __name__ == '__main__':
    unittest.main()

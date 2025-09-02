# test script for Typhon package
import unittest

from unittest.mock import patch
from io import StringIO
from contextlib import redirect_stdout

class TestTyphon(unittest.TestCase):
    def test_bypassMAIN(self):
        with redirect_stdout(StringIO()) as f:
            # case1: some basic WAF
            from Typhon import bypassMAIN
            case1 = bypassMAIN(
            banned_chr=['__builtins__', '__subclasses__'],
            banned_re='.*import.*',
            local_scope={'__builtins__': None},
            max_length=100,
            log_level='TESTING')
            self.assertTrue(any(i in case1 for i in ['OBJECT', 'TYPE']))
            # case2: NO waf
            with patch('builtins.exit') as mock_exit:
                from Typhon import bypassMAIN
                bypassMAIN(log_level='TESTING')
                mock_exit.assert_called_with(0)
            # case3: depth
            with patch('builtins.exit') as mock_exit:
                from Typhon import bypassMAIN
                a = bypassMAIN(depth=0, log_level='TESTING', banned_chr=['help'])
                self.assertFalse('help' in a.values())
            

if __name__ == '__main__':
    unittest.main()
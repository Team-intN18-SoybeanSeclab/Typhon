# test script for Typhon package
import unittest

from unittest.mock import patch
from io import StringIO
from contextlib import redirect_stdout


class TestTyphon(unittest.TestCase):
    def test_bypassMAIN(self):
        with redirect_stdout(StringIO()) as f:
            with patch("builtins.exit") as mock_exit:
                # case1: some basic WAF
                import Typhon

                case1 = Typhon.bypassMAIN(
                    banned_chr=["__builtins__", "__subclasses__"],
                    banned_re=".*import.*",
                    allow_unicode_bypass=True,
                    max_length=150,
                    log_level="TESTING",
                )
                mock_exit.assert_called_with(0)
                del Typhon


if __name__ == "__main__":
    unittest.main()

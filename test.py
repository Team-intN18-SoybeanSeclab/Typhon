import sys  # noqa

sys.path.append("..")  # noqa

# test script for Typhon package
import unittest

from unittest.mock import patch
from io import StringIO
from contextlib import redirect_stdout


class TestTyphonRCE(unittest.TestCase):
    def test_bypassRCE(self):
        with redirect_stdout(StringIO()) as f:
            with patch("builtins.exit") as mock_exit:
                import string
                import Typhon

                Typhon.bypassRCE(
                    cmd="whoami",
                    interactive=True,
                    banned_chr=[a for a in string.ascii_letters],
                    allow_unicode_bypass=True,
                    local_scope={'help':help},
                    log_level="TESTING",
                )
                del Typhon
                mock_exit.assert_called_with(0)
        with redirect_stdout(StringIO()) as f:
            with patch("builtins.exit") as mock_exit:
                import string
                import Typhon

                Typhon.bypassRCE(
                    cmd="whoami",
                    interactive=True,
                    banned_chr=[a for a in string.ascii_letters],
                    allow_unicode_bypass=True,
                    local_scope={'help':help},
                    log_level="TESTING",
                )
                del Typhon
                mock_exit.assert_called_with(0)
        with redirect_stdout(StringIO()) as f:
            with patch("builtins.exit") as mock_exit:
                import Typhon

                Typhon.bypassRCE(
                    cmd="whoami",
                    local_scope={"__builtins__": None},
                    banned_chr=[
                        "__loader__",
                        "__import__",
                        "os",
                        "[:",
                        "\\x",
                        "+",
                        "join",
                    ],
                    interactive=True,
                    recursion_limit=200,
                    depth=5,
                    log_level="TESTING",
                )
                del Typhon
                mock_exit.assert_called_with(0)


class TestTyphonREAD(unittest.TestCase):
    def test_bypassREAD(self):
        with redirect_stdout(StringIO()) as f:
            with patch("builtins.exit") as mock_exit:
                import Typhon

                Typhon.bypassREAD(
                    filepath="/flag",
                    mode="exec",
                    banned_chr=[
                        "__loader__",
                        "__import__",
                        "os",
                        "[:",
                        "\\x",
                        "+",
                        "join",
                    ],
                    interactive=False,
                    recursion_limit=100,
                    local_scope={"__builtins__": None},
                    depth=5,
                    log_level="TESTING",
                )
                del Typhon
                mock_exit.assert_called_with(0)


if __name__ == "__main__":
    unittest.main()

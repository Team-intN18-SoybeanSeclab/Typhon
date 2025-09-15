# test script for Typhon package
import unittest

from unittest.mock import patch
from io import StringIO
from contextlib import redirect_stdout


class TestTyphonRCE(unittest.TestCase):
    def test_bypassRCE(self):
        with redirect_stdout(StringIO()) as f:
            with patch("builtins.exit") as mock_exit:
                import Typhon

                Typhon.bypassRCE(
                    cmd="whoami",
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
                    local_scope={"__builtins__": None, "exc": exec},
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
                    local_scope={"__builtins__": None, "exc": exec},
                    depth=5,
                    log_level="TESTING",
                )
                del Typhon
                mock_exit.assert_called_with(0)


if __name__ == "__main__":
    unittest.main()

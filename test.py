import sys  # noqa

sys.path.append("..")  # noqa

# test script for Typhon package
import unittest

from unittest.mock import patch
from io import StringIO
from contextlib import redirect_stdout


class TestTyphonRCE(unittest.TestCase):
    def tearDown(self):
        print(f"✓ Testcase '{self._testMethodName}' done.")

    def test_bypassRCE(self):
        with redirect_stdout(StringIO()) as f:
            with patch("builtins.exit") as mock_exit:
                mock_exit.side_effect = RuntimeError("Test")
                import string
                import Typhon
                import ast

                with self.assertRaises(RuntimeError):
                    Typhon.bypassRCE(
                        cmd="whoami",
                        interactive=True,
                        banned_chr=''.join([a for a in string.ascii_letters]),
                        allow_unicode_bypass=True,
                        banned_ast=[ast.Import],
                        local_scope={},
                        log_level="TESTING",
                    )
                del Typhon
                mock_exit.assert_called_with(0)
            with patch("builtins.exit") as mock_exit:
                mock_exit.side_effect = RuntimeError("Test")
                import string
                import Typhon

                with self.assertRaises(RuntimeError):
                    Typhon.bypassRCE(
                        cmd="whoami",
                        interactive=False,
                        allow_unicode_bypass=True,
                        local_scope={},
                        log_level="TESTING",
                    )
                del Typhon
                mock_exit.assert_called_with(0)
            with patch("builtins.exit") as mock_exit:
                mock_exit.side_effect = RuntimeError("Test")
                import string
                import Typhon

                with self.assertRaises(RuntimeError):
                    Typhon.bypassRCE(
                        cmd="whoami",
                        interactive=True,
                        banned_chr=["help", "breakpoint", "input"],
                        banned_re=r".*import.*",
                        log_level="TESTING",
                    )
                del Typhon
                mock_exit.assert_called_with(0)
            with patch("builtins.exit") as mock_exit:
                mock_exit.side_effect = RuntimeError("Test")
                import Typhon

                with self.assertRaises(RuntimeError):
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
    def tearDown(self):
        print(f"✓ Testcase '{self._testMethodName}' done.")

    def test_bypassREAD(self):
        with redirect_stdout(StringIO()) as f:
            with patch("builtins.exit") as mock_exit:
                mock_exit.side_effect = RuntimeError("Test")
                import Typhon

                with self.assertRaises(RuntimeError):

                    def b(): pass; b()

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
                        local_scope={"__builtins__": None, "a": lambda x: x, "b": b},
                        depth=5,
                        log_level="TESTING",
                    )
                del Typhon
                mock_exit.assert_called_with(0)

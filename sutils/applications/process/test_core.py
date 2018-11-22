import unittest
from unittest.mock import patch
import os

from . import core

class TestGetFileExtension(unittest.TestCase):
    def setUp(self):
        self._exefilename = "main.exe"
        self._shellfilename = "script.sh"
        self._noextfilename = "program"
        self._pyfilename = "mymodule.py"

        self._path = os.path.join("this", "is", "a", "path")

    def test_exe(self):
        self.assertEqual(core.get_file_extension(self._exefilename), 'exe')

    def test_shell(self):
        self.assertEqual(core.get_file_extension(self._shellfilename), 'sh')

    def test_noext(self):
        self.assertEqual(core.get_file_extension(self._noextfilename), '')
    
    def test_py(self):
        self.assertEqual(core.get_file_extension(self._pyfilename), 'py')
    
    def test_exe_in_path(self):
        filename = os.path.join(self._path, self._exefilename)
        self.assertEqual(core.get_file_extension(filename), 'exe')

    def test_shell_in_path(self):
        filename = os.path.join(self._path, self._shellfilename)
        self.assertEqual(core.get_file_extension(filename), 'sh')

    def test_noext_in_path(self):
        filename = os.path.join(self._path, self._noextfilename)
        self.assertEqual(core.get_file_extension(filename), '')
    
    def test_py_in_path(self):
        filename = os.path.join(self._path, self._pyfilename)
        self.assertEqual(core.get_file_extension(filename), 'py')

class TestIsExecutable(unittest.TestCase):
    @patch("sutils.applications.process.core.os.access")
    def test_calls_os_access(self, mock_access):
        core.is_executable("filename")
        mock_access.assert_called_once_with("filename", os.X_OK)

    @patch("sutils.applications.process.core.os.access")
    def test_returns_os_access(self, mock_access):
        mock_access.return_value = "this is the return value"
        ret = core.is_executable("filename")
        self.assertEqual(ret, mock_access.return_value)

"""
Unit tests for copyright.py
"""

import unittest
import os
try:
    from mock import patch
except ImportError:
    from unittest.mock import patch

from copyright import Module, NOTICE


class TestPythonModule(unittest.TestCase):

    def test_loads_file_correctly(self):
        expected_lines = 11
        expected_line_10 = '[print(add_ten(i)) for i in range(100)]'

        m = Module('test/examples/simple_header.py')
        self.assertEqual(len(m.lines), expected_lines)
        self.assertIn(expected_line_10, m.lines[9])

    def test_finds_copyright_when_exists(self):
        m = Module('test/examples/has_copyright.py')
        self.assertTrue(m.has_copyright())

    def test_no_copyright_when_doesnt_exist(self):
        m = Module('test/examples/simple_header.py')
        self.assertFalse(m.has_copyright())

    def test_identifies_lines_with_comment(self):
        lines = [
            ('# this has a comment', True),
            ('this = 2 # has a comment bus is code', False),
            ('""" this is a docstring', False),
            ("''' so is this '''", False),
            ('from something import something', False),
        ]

        for line, expected in lines:
            actual = Module.line_starts_with_comment(line)
            self.assertEqual(actual, expected, line + ' failed.')
    
    def test_identifies_lines_with_docstrings(self):
        lines = [
            ('# this has a comment', False),
            ('this = 2 # has a comment bus is code', False),
            ('"""', True),
            ("''' so is this '''", True),
            ('from something import something', False),
        ]

        for line, expected in lines:
            actual = Module.line_contains_docstring(line)
            self.assertEqual(actual, expected, line + ' failed.')

    def test_identify_header_correctly(self):
        files = [
            ('test/examples/simple_header.py', 'comment'),
            ('test/examples/comment.py', 'comment'),
            ('test/examples/no_header.py', None),
            ('test/examples/docstring.py', 'docstring'),
        ]

        for file, expected in files:
            m = Module(file)
            self.assertEqual(m.header_type, expected, file + ' failed.')

    def test_add_notice_inserts_lines(self):      
        notice_lines = ['# copyright notice']
        ix = 3
        overwite = False
        expected = [
            '# comment_header.py\n',
            '# This module has a simple comment header\n',
            '# which is wrong but sometimes exists.\n',
            '# copyright notice\n',
            '\n',
            'import os\n',
        ]

        m = Module('test/examples/comment.py')
        m.add_notice(ix, notice_lines, overwite)

        for actual, expected in zip(m.lines[:6], expected):
            self.assertEqual(actual, expected, expected + ' failed.')
    
    def test_add_notice_inserts_lines_and_overwrites(self):      
        notice_lines = ['copyright notice', '"""']
        ix = 2
        overwrite = True
        expected = [
            '"""\n',
            'simple_docstring.py: This file has a docstring.\n',
            'copyright notice\n',
            '"""\n',
            '\n',
            'import os\n',
        ]

        m = Module('test/examples/simple_docstring.py')
        m.add_notice(ix, notice_lines, overwrite)

        for actual, expected in zip(m.lines[:6], expected):
            self.assertEqual(actual, expected, expected + ' failed.')

    def test_detects_importable_module(self):
        pass

    def test_detects_unimportable_module(self):
        m = Module('test/examples/bad_module.py')
        self.assertFalse(m.can_import())

    @patch.object(Module, 'write_changes')
    def test_works_with_docstring(self, mock_write):
        expected = [
            '"""\n',
            'simple_docstring.py: This file has a docstring.\n',
            NOTICE + '\n',
            '"""\n',
            '\n',
            'import os\n',
        ]
        
        m = Module('test/examples/simple_docstring.py')
        m.add_copyright()

        for actual, expected in zip(m.lines[:6], expected):
            self.assertEqual(actual, expected, expected + ' failed.')

        mock_write.assert_called()

    @patch.object(Module, 'write_changes')
    def test_works_with_no_header(self, mock_write):
        expected = [
            '"""\n',
            NOTICE + '\n',
            '"""\n',
            '\n',
            'import os\n',
        ]
        
        m = Module('test/examples/no_header.py')
        m.add_copyright()

        for actual, expected in zip(m.lines[:5], expected):
            self.assertEqual(actual, expected, expected + ' failed.')

        mock_write.assert_called()

    @patch.object(Module, 'write_changes')
    def test_ignores_file_with_copyright(self, mock_write):
        
        m = Module('test/examples/has_copyright.py')
        m.add_copyright()

        mock_write.assert_not_called()
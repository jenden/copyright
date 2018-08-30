"""
Opens a file, adds copyright info to the header of any .py file.
Copyright (C) 2018 Boeing Vancouver.  All Rights Reserved.
"""

import os
import re
import imp
import argparse

EXTENSIONS = ['.py']
NOTICE = "Copyright (C) 2018 Will Jenden. All Rights Reserved."

parser = argparse.ArgumentParser()
parser.add_argument('-d', '--directory', default='.', help='location to walk')

class Module:

    def __init__(self, filepath):
        self.filepath = filepath
        with open(filepath, 'r') as f:
            self.lines = list(f.readlines())
        
        self.original = self.lines.copy()
        
        self.header_type = None
        self.get_file_header()
        
    def add_copyright(self):
        """
        If docstring exists, place copyright in last line of the docstring. If comment exists,
        add commented docstring as last line of comment. If no comment, then place docstring with
        comment at top of file and leave one space before imports.
        """
        
        if self.has_copyright():
            return True
        
        if self.header_type == 'docstring':
            ix, notice_lines, overwrite = self.docstring_insertion()
        # elif self.header_type == 'comment':
        #     ix, notice_lines, overwrite = self.comment_insertion()
        elif self.header_type is None:
            ix, notice_lines, overwrite = self.empty_insertion()
        else:
            raise RuntimeError('Unknown header type {}'.format(self.header_type))

        self.add_notice(ix, notice_lines, overwrite)
        self.write_changes()

    def get_file_header(self):
        # todo: find complex headers (e.g. both types of comments before code)
        # find start of header
        first_line = self.lines[0]
        if self.line_starts_with_comment(first_line):
            self.header_type = 'comment'
        elif self.line_contains_docstring(first_line):
            self.header_type = 'docstring'

    @staticmethod       
    def line_starts_with_comment(line):
        return line.startswith('#')

    @staticmethod
    def line_contains_docstring(line):
        return any([docstring in line for docstring in ['"""', "'''"]])

    def has_copyright(self):
        return any([NOTICE in line for line in self.lines])

    def docstring_insertion(self):
        def docstring_line(lines, start_ix=None):
            start_ix = 0 if start_ix is None else start_ix + 2

            for ix, line in enumerate(self.lines[start_ix:]):
                if self.line_contains_docstring(line):
                    return ix + start_ix
        
        start_ix = docstring_line(self.lines)
        end_ix = docstring_line(self.lines, start_ix)
        insert_ix = end_ix
        notice_lines = [NOTICE]
        overwrite = False
        
        return insert_ix, notice_lines, overwrite

    def empty_insertion(self):
        insert_ix = 0
        notice_lines = ['"""', NOTICE, '"""', '']
        overwite = False

        return insert_ix, notice_lines, overwite
    
    def add_notice(self, ix, notice_lines, overwrite):
        '''
        Adds the list of `notice_lines` into file starting at line number `ix`. If 
        `overwrite` is true, replaces the line at `ix`, otherwise, inserts before.
        '''

        notice_lines = [line if line.endswith('\n') else line + '\n' for line in notice_lines]
        if overwrite:
            self.lines.pop(ix)
        self.lines = self.lines[:ix] + notice_lines + self.lines[ix:]
    
    def write_changes(self):
        with open(self.filepath, 'w') as f:
            f.writelines(self.lines)
        
        if not self.can_import():
            self.revert_changes()
            return False
        else:
            return True
        
    def can_import(self):
        try:
            imp.load_source('test_import', self.filepath)
            return True
        except SyntaxError:
            return False
        
    def revert_changes(self):
        print('Unable to add notice to {}. Reverting file.'.format(self.filepath))
        with open(self.filepath, 'w') as f:
            f.writelines(self.original)

if __name__ == '__main__':

    args = parser.parse_args()
    for root, dirs, files in os.walk(args.directory):
        for file in files:
            if any([file.endswith(extension) for extension in EXTENSIONS]):
                try:
                    success = Module(os.path.join(root, file)).add_copyright()
                    print('[{}] {} in {}'.format('X' if success else ' ', file, root))
                except Exception as e:
                    print('[ ] {} in {} raised error {}'.format(file, root, str(e)))
        
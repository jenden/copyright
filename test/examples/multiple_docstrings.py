"""one_line_docstring.py: This file has a docstring."""

import os
import sys

def add_ten(number):
    """does some stuff"""
    return number + 10

if __name__ == '__main__':
    [add_ten(i) for i in range(100)]

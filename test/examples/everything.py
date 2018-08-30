#!/usr/bin/env python
"""everything.py has no style whatsoever.
"""

import os
import sys

def add_ten(number):
    return number + 10

if __name__ == '__main__':
    [print(add_ten(i)) for i in range(100)]
        
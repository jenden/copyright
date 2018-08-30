"""
Copyright (C) 2018 Will Jenden. All Rights Reserved.
"""

import os
import sys

def add_ten(number):
    return number + 10

if __name__ == '__main__':
    [print(add_ten(i)) for i in range(100)]
        
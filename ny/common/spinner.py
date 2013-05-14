# -*- coding: utf-8 -*-

import sys
import time
import subprocess
import contextlib

def draw_ascii_spinner(delay=0.1):
    for char in '/-\|':
        sys.stdout.write(char)
        sys.stdout.flush()
        time.sleep(delay)
        sys.stdout.write('\b')

def spin_forever():
    while "forever":
        draw_ascii_spinner()


@contextlib.contextmanager
def distraction():
    p = subprocess.Popen(['ny-_spinner'])
    yield
    sys.stdout.write('\b')
    p.terminate()

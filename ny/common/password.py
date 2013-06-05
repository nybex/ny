# -*- coding: utf-8 -*-

# For running the 1pass coffee command
import sys
import time
import getpass
import pexpect

def get_password(key='AWS Access Key'):
    # Get the password
    p = getpass.getpass(prompt='1Password: ', stream=sys.stderr)
    p = False if not len(p) else p

    child = pexpect.spawn('1pass', ['-r', '0', key], timeout=3)
    child.expect('Password: ')
    if child.isalive():
        child.sendline(p)
        try:
            r = child.readlines()
        except:
            return None
    else:
        return None

    return r

# For running the 1pass coffee command
import sys
import getpass
import pexpect

def get_password(key='AWS Access Key'):
    # Get the password
    p = getpass.getpass(prompt='1Password: ', stream=sys.stderr)
    p = False if not len(p) else p

    child = pexpect.spawn('1pass', ['-r', '0', key])
    child.expect('Password: ')
    if child.isalive():
        child.sendline(p)
        r = child.readlines()
    else:
        return None

    return r

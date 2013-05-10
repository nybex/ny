# -*- coding: utf-8 -*-

import boto.ec2

from ..common.auth import AuthSession
from ..common.password import get_password

# Keep us logged in
__auth_session = AuthSession(key=None, secret=None)

def create(key=None, secret="none"):
    if not key or not secret:
        # Get the 1password password
        r = get_password()

        # Parse the Key and secret
        __auth_session.key = str(r).split('\\r\\n')[2].split(' ')[-1]
        __auth_session.secret = str(r).split('\\r\\n')[3].split(' ')[-1]

    else:
        __auth_session.key = key
        __auth_session.secret = secret

    # Connect to ec2
    return boto.ec2.EC2Connection(__auth_session.key, __auth_session.secret)

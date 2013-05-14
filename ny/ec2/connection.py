# -*- coding: utf-8 -*-

import boto.ec2

from ..common.auth import AuthSession
from ..common.password import get_password

# Keep us logged in
__auth_session = AuthSession(key=None, secret=None)

def create(config):
    if 'aws' in config.keys():
        if '1pass' in config['aws'].keys():
            # Get the 1password password
            r = get_password(key=config['aws']['1pass'])

            # Parse the Key and secret
            __auth_session.key = str(r).split('\\r\\n')[2].split(' ')[-1]
            __auth_session.secret = str(r).split('\\r\\n')[3].split(' ')[-1]

        elif ('key' in config['aws'].keys() and
                'secret' in config['aws'].keys()):

            __auth_session.key = config['aws']['key']
            __auth_session.secret = config['aws']['secret']

        else:
            raise

    else:
        raise

    # Connect to ec2
    return boto.ec2.EC2Connection(__auth_session.key, __auth_session.secret)

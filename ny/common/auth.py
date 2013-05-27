# -*- coding: utf-8 -*-

from ..common.password import get_password

class AuthSession(object):
    def __init__(self, key=None, secret=None):
        self.key = key
        self.secret = secret


def get_aws_credentials(config):
    if 'aws' in config.keys():
        if '1pass' in config['aws'].keys():
            # Get the 1password password
            r = get_password(key=config['aws']['1pass'])

            # Parse the Key and secret
            key = str(r).split('\\r\\n')[2].split(' ')[-1]
            secret = str(r).split('\\r\\n')[3].split(' ')[-1]

        elif ('key' in config['aws'].keys() and
                'secret' in config['aws'].keys()):

            key = config['aws']['key']
            secret = config['aws']['secret']

        else:
            raise

    else:
        raise

    return [key, secret]

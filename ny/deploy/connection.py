# -*- coding: utf-8 -*-

from boto.s3.connection import S3Connection

from ..common.auth import AuthSession, get_aws_credentials

# Keep us logged in
__auth_session = AuthSession(key=None, secret=None)

def create(config):
    if not __auth_session.key:
        if 'aws' in config.keys():
            try:
                key, secret = get_aws_credentials(config)
                __auth_session.key = key
                __auth_session.secret = secret
            except:
                raise

    # Connect to s3
    return S3Connection(__auth_session.key, __auth_session.secret)

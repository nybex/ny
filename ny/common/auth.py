# -*- coding: utf-8 -*-

class AuthSession(object):
    def __init__(self, key=None, secret=None):
        self.key = key
        self.secret = secret

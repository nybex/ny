# -*- coding: utf-8 -*-

import os
import time

from envoy import run
from jinja2 import Template
from clint.textui import colored, puts

from . import connection
from ..common import configuration
from ..common.spinner import distraction

def deploy(args, config):
    # Create an s3 connection
    s3 = connection.create(config)

    # Read the config file
    bucket_name = configuration.get_deploy_bucket(config)
    if not bucket_name:
        raise Exception('Please specify a bucket name in your Nyfile')

    # Find the bucket
    bucket = s3.get_bucket(bucket_name)
    if not bucket:
        raise Exception('Unable to find bucket specified in Nyfile')

    config_key = configuration.get_deploy_key(config)
    if not config_key:
        raise Exception('Unable to find bucket key in Nyfile')
    else:
        config_key = Template(config_key)

    for env in args['<env>']:
        env = env.lower()

        # Set the deploy key
        key = config_key.render(env=env)

        with distraction():
            # Remove old files
            run('rm -rf /tmp/__ny_tmp /tmp/__ny_tmp.tar /tmp/__ny_tmp.tar.gz')

            # Lets create an archive of the local branch
            run('git checkout-index -a -f --prefix=/tmp/__ny_tmp/')
            run('tar -cvf /tmp/__ny_tmp.tar /tmp/__ny_tmp/')
            run('gzip -9 /tmp/__ny_tmp.tar')
            run('rm -rf /tmp/__ny_tmp /tmp/__ny_tmp.tar')

            # Remove old deploy
            bucket.delete_key(key)

            # Upload new key
            k = bucket.new_key(key)
            k.set_contents_from_filename("/tmp/__ny_tmp.tar.gz",
                    encrypt_key=True)

            # Remove gzipped file
            run('rm -rf /tmp/__ny_tmp.tar.gz')

        puts(colored.green("Uploaded %s source archive to S3" % env))

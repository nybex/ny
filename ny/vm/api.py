# -*- coding: utf-8 -*-

import os
import time
from collections import Counter

import boto.ec2
import prettytable
from clint.textui import colored, puts
from prettytable import PrettyTable
from jinja2 import Template

from ..ec2 import connection as ec2connection
from ..common import configuration
from ..common.structures import AttrDict
from ..common.spinner import distraction

# A constant
SUBNET_ALTERNATE = 'alternate'

def list(args, config):
    instance_type = args['--type']
    subnet = args['--subnet']

    if not args['<env>']:
        args['<env>'] = configuration.get_all_envs(config)

    # Launch Instances per env
    env_tables = {}
    for env in args['<env>']:
        e = configuration.get_env(env, config)
        if not e:
            puts(colored.red(
                '"%s" is not defined in your Nyfile' % env))
        else:
            ec2 = ec2connection.create(config)

            with distraction():
                filters = AttrDict()
                filters.vpc_id = e.vpc

                if instance_type:
                    filters['tag:ny_type'] = instance_type

                try:
                    reservations = ec2.get_all_instances(filters=filters)
                except:
                    puts(colored.red("Unable to get reservations"))
                    reservations = []

                # Start building the table
                t = PrettyTable(['instance_id', 'tags', 'state'])
                t.align["tags"] = "l"
                t.hrules = prettytable.ALL

                for res in reservations:
                    for instance in res.instances:
                        tags = []
                        for name,value in instance.tags.items():
                            tags.append('%s => %s' % (name,value,))

                        t.add_row([
                            instance.id,
                            '\n'.join(tags),
                            instance.state,
                        ])

                env_tables[env] = t

    for env,table in env_tables.items():
        puts('Instances in %s' % env.upper())
        puts(str(table)) # The str is required for puts to work

def terminate(args, config):
    instances = args['<instance>']

    if instances:
        ec2 = ec2connection.create(config)
        for instance in instances:
            term = ec2.terminate_instances(instance_ids=[instance])

            puts(colored.green("Successfully Terminated: %s" % ', '.join(
                [t.id for t in term])))


def create(args, config):
    instance_type = args['--type']
    subnet = args['--subnet']
    num = int(args['--num'])

    type_template = configuration.get_type_template(instance_type, config)

    # Launch Instances per env
    for env in args['<env>']:
        e = configuration.get_env(env, config)
        if not e:
            print '%s is not defined in your Nyfile' % e
        else:
            ec2 = ec2connection.create(config)

            if not ec2:
                print 'Unable to connect to EC2'
                exit()

            groups = configuration.security_group_names_to_ids(
                        names=type_template.security_groups,
                        env=env,
                        config=config)

            if not groups or not len(groups):
                print 'Unable to determine security groups'
                exit()

            if subnet == SUBNET_ALTERNATE:
                reservations = ec2.get_all_instances()
                instances = [i for r in reservations for i in r.instances]

                all_subnets = configuration.get_env_subnets(env, config)
                subnets = Counter(all_subnets)
                vpc_subnets = []
                if all_subnets:
                    subnets.update([i.subnet_id for i in instances])
                    for s in subnets.items():
                        if s[0] in all_subnets:
                            vpc_subnets.append(s[0])

                subnets = Counter((tuple(vpc_subnets)*num)[:num])
            else:
                subnets = Counter((subnet,)*num)

            reservations = []
            tags = configuration.get_tags(instance_type, config)

            # Try to get a bootscript
            bootscript_paths = configuration.get_bootscript_paths(
                                    instance_type=instance_type,
                                    env=env,
                                    config=config)

            for sub in subnets.items():
                # Parse the bootscripts once per subnet
                parsed_bootscripts = []
                for p in bootscript_paths:
                    with open(p) as tmp:
                        parsed_bootscripts.append(
                                Template(tmp.read()).render(
                                    type=instance_type,
                                    env=env,
                                    subnet=subnet,
                                    security_groups=groups,
                                    image_id=type_template.image_id,
                                    tags=(';'.join(tags) if tags else []),
                                    key=e.key))

                reservations.append(
                    ec2.run_instances(
                        min_count=sub[1],
                        image_id=type_template.image_id,
                        instance_type=type_template.type,
                        key_name=e.key,
                        subnet_id=sub[0],
                        security_group_ids=groups,
                        user_data='\n'.join(parsed_bootscripts)))

            puts(colored.green(
                'Started %s (%i x instance)' % (
                        reservations[-1:][0], int(sub[1]))))

            puts("\n")
            puts("Waiting on instances to start: \n")
            with distraction():
                for reservation in reservations:
                    for instance in reservation.instances:
                        status = instance.update()
                        while status == 'pending':
                            time.sleep(10)
                            status = instance.update()

                        if status == 'running':
                            puts(colored.green(
                                'Instance %s is up' % instance))

                            tags = configuration.get_tags(
                                                instance_type,config)

                            if tags:
                                for key,val in tags.items():
                                    instance.add_tag(key, val)

                            instance.add_tag('ny_env', env)
                            instance.add_tag('ny_type', instance_type)

                        else:
                            puts(colored.red(
                                'Instance status: ' + status))

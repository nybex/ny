# -*- coding: utf-8 -*-

import os
from subprocess import call

from docopt import docopt

from . import server
from .common.configuration import get_config
from .common.cli import exit_if_no_config, exit_with_message

__ny__ = """
usage: ny [<command> <args>...]

The most commonly used `ny` commands are:
    deploy          Deploy to a specified environment
    servers         Manage Servers

See `ny <command> help` for more information on a specific command.

"""

__ny_server__ = """
usage: ny servers [options <command> <env>...]
       ny servers terminate <instance>

The most commonly used snake bootstrap commands are:
    list            List VMs
    create          Spin up a VM
    terminate       Termiante a VM

Generic options
    -h, --help
    -n, --num=<n>       Specify number of VMs to launch [default: 1]
    -t, --type=<t>      Specify the server type (defined in the Nyfile)
    -s, --subnet=<s>    Specify the subnet [Default: alternate]
    -i, --instance=<i>  Instance id

"""

# ny
def ny():
    args = docopt(__ny__, version='Version 0.0.1dev', options_first=True)

    argv = [args['<command>']] + args['<args>']
    if args['<command>'] in 'deploy servers'.split():
        exit(call(['ny-%s' % args['<command>']] + argv))
    elif args['<command>'] in ['help', None]:
        exit(call(['ny', '--help']))
    else:
        exit("%r is not a `ny` command. See 'ny help'." % args['<command>'])

# Ny-deploy
def ny_servers():
    config = get_config()

    # Setup the args
    args = docopt(__ny_server__)

    if args['<command>'] in ('create terminate list').split():
        func = globals()['cli_server_%s' %
                args['<command>'].replace('-', '_')]
        if func is not None:
            if (args['<command>'] in ('create list').split() and
                    not len(args['<env>'])):

                exit_with_message("""
                    Error: An env is required for creation of VMs.
                    For help: `ny server help`
                    """)

            if args['<command>'] == 'create' and not args['--type']:
                exit_with_message("""
                    Error: You must specify `--type`
                    For help: `ny server help`
                    """)

            if args['<command>'] == 'terminate' and not args['--instance']:
                exit_with_message("""
                    Error: You must specify an instance to terminate.
                    For help: `ny server help`
                """)

            exit(func(args, config))

    elif args['<command>'] in ['help', None]:
        exit(call(['ny-server', '--help']))
    else:
        exit("%r is not a `ny` command. See 'ny server help'."
                % args['<command>'])


def ny_deploy():
    pass


####
# Create Cli Commands
####
def cli_server_create(args, config):
    exit(server.create(args, config))

def cli_server_list(args, config):
    exit(server.list(args, config))

def cli_server_terminate(args, config):
    exit(server.terminate(args, config))

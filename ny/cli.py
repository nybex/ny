# -*- coding: utf-8 -*-

import os
import traceback
from subprocess import call

from docopt import docopt
from clint.textui import colored, puts

from . import vm, deploy
from .common.spinner import spin_forever
from .common.configuration import get_config
from .common.cli import exit_if_no_config, exit_with_message

__ny__ = """
usage: ny [<command> <args>...]

The most commonly used `ny` commands are:
    deploy          Deploy to a specified environment
    vm              Manage VMs

See `ny <command> help` for more information on a specific command.

"""

__ny_vm__ = """
usage: ny vm [options <command> <env>...]
       ny vm terminate <instance>

The most commonly used snake bootstrap commands are:
    list            List VMs
    create          Spin up a VM
    terminate       Termiante a VM

Generic options
    -h, --help
    -n, --num=<n>       Specify number of VMs to launch [default: 1]
    -t, --type=<t>      Specify the VM type (defined in the Nyfile)
    -s, --subnet=<s>    Specify the subnet [Default: alternate]

"""

__ny_deploy__ = """
usage: ny deploy [options <env>...]

Generic options
    -h, --help
    -R, --rollback      Rollback to the previous deployed version

"""

# ny
def ny():
    args = docopt(__ny__, version='Version 0.0.1dev', options_first=True)

    argv = [args['<command>']] + args['<args>']
    if args['<command>'] in 'deploy vm'.split():
        exit(call(['ny-%s' % args['<command>']] + argv))
    elif args['<command>'] in ['help', None]:
        exit(call(['ny', '--help']))
    else:
        exit("%r is not a `ny` command. See 'ny help'." % args['<command>'])

# Ny-deploy
def ny_vm():
    config = get_config()

    # Setup the args
    args = docopt(__ny_vm__)

    if args['<command>'] in ('create terminate list').split():
        func = globals()['cli_vm_%s' %
                args['<command>'].replace('-', '_')]
        if func is not None:
            if (args['<command>'] in ('create').split() and
                    not len(args['<env>'])):

                exit_with_message("""
                    Error: An env is required for creation of VMs.
                    For help: `ny vm help`
                    """)

            if args['<command>'] == 'create' and not args['--type']:
                exit_with_message("""
                    Error: You must specify `--type`
                    For help: `ny vm help`
                    """)

            if args['<command>'] == 'terminate' and args['<env>']:
                args['<instance>'] = args['<env>']
                args['<env>'] = None
            elif args['<command>'] == 'terminate' and not args['<env>']:
                exit_with_message("""
                    Error: You must specify an instance to terminate.
                    For help: `ny vm help`
                """)

            exit(func(args, config))

    elif args['<command>'] in ['help', None]:
        exit(call(['ny-vm', '--help']))
    else:
        exit("%r is not a `ny` command. See 'ny vm help'."
                % args['<command>'])


def __spinner():
    spin_forever()

####
# Create Cli Commands
####
def cli_vm_create(args, config):
    try:
        exit(vm.create(args, config))
    except Exception as e:
        puts(traceback.format_exc())
        puts(colored.red(str(e)))

def cli_vm_list(args, config):
    try:
        exit(vm.list(args, config))
    except Exception as e:
        puts(traceback.format_exc())
        puts(colored.red(str(e)))

def cli_vm_terminate(args, config):
    try:
        exit(vm.terminate(args, config))
    except Exception as e:
        puts(traceback.format_exc())
        puts(colored.red(str(e)))

def ny_deploy():
    config = get_config()

    # Setup the args
    args = docopt(__ny_deploy__)

    try:
        deploy.do_deploy(args=args, config=config)
    except Exception as e:
        puts(traceback.format_exc())
        puts(colored.red(str(e)))

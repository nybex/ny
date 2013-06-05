# -*- coding: utf-8 -*-

import os
import sys
import traceback
from subprocess import call

from docopt import docopt
from clint.textui import colored, puts

from . import vm, stage, config
from .common.spinner import spin_forever
from .common.configuration import get_config
from .common.cli import exit_if_no_config, exit_with_message

__ny__ = """
Usage: ny [<command> <args>...]

The most commonly used `ny` commands are:
    vm              Manage VMs
    stage           Stage the current branch to a specified env
    deploy          Deploy the previously staged branch to a specified env
    config          Manage the config variables for a specified env

See `ny <command> help` for more information on a specific command.

"""

__ny_vm__ = """
Usage: ny vm [options <command> <env>...]
       ny vm terminate <instance>

The most commonly used snake bootstrap commands are:
    list            List VMs
    create          Spin up a VM
    terminate       Termiante a VM

Options:
    -h, --help
    -n, --num=<n>       Specify number of VMs to launch [default: 1]
    -t, --type=<t>      Specify the VM type (defined in the Nyfile)
    -s, --subnet=<s>    Specify the subnet [Default: alternate]

"""

__ny_stage__ = """
Usage: ny stage [options <env>...]

Options:
    -h, --help

"""

__ny_config__ = """
Usage: ny config [options <command> <env>...]

The most commonly used snake bootstrap commands are:
    add             Add an item to the config
    remove          Remove an item from the config
    show            Show the config keys

Options:
    -h, --help

"""

__ny_config_add_remove__ = """
Usage: ny config (add|remove) [--value=<pair> --value=<pair> <env>...]

Options:
    -h, --help
    -v, --value=<pair>  Specify params to add in KEY=VALUE format

"""


# ny
def ny():
    args = docopt(__ny__, version='Version 0.0.1dev', options_first=True)
    argv = [args['<command>']] + args['<args>']

    if args['<command>'] in 'stage deploy vm config'.split():
        exit(call(['ny-%s' % args['<command>']] + argv))
    elif args['<command>'] in ['help', None]:
        exit(call(['ny', '--help']))
    else:
        exit("%r is not a `ny` command. See 'ny help'." % args['<command>'])

### Multi Command Commands
# ny-vm
def ny_vm():
    config = get_config()

    # Setup the args
    args = docopt(__ny_vm__, options_first=True)

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

# ny-config
def ny_config():
    config = get_config()

    # Setup the args
    args = docopt(__ny_config__, options_first=True)

    if args['<command>'] in ('add remove').split():
        exit(call(['ny-config-%s' % args['<command>']] + sys.argv[1:]))

    elif args['<command>'] in ('show').split():
        func = globals()['cli_config_%s' %
                args['<command>'].replace('-', '_')]
        if func is not None:
            if not len(args['<env>']):
                exit_with_message("""
                    Error: An env is required.
                    For help: `ny config help`
                    """)

            exit(func(args, config))

    elif args['<command>'] in ['help', None]:
        exit(call(['ny-config', '--help']))
    else:
        exit("%r is not a `ny` command. See 'ny config help'."
                % args['<command>'])


def ny_config_add_remove():
    config = get_config()

    # Setup the args
    args = docopt(__ny_config_add_remove__)

    if (args['add'] or args['remove']) and len(args['--value']) > 0:
        cmd = 'add' if args['add'] else 'remove'
        func = globals()['cli_config_%s' % cmd]
        if func is not None:
            if not len(args['<env>']):
                exit_with_message("""
                    Error: An env is required.
                    For help: `ny config help`
                    """)

            exit(func(args, config))

    else:
        exit(call(['ny-config-add', '--help']))

### Single commands
# ny-stage
def ny_stage():
    config = get_config()

    # Setup the args
    args = docopt(__ny_stage__)

    try:
        stage.do_stage(args=args, config=config)
    except Exception as e:
        puts(traceback.format_exc())
        puts(colored.red(str(e)))

### Stubs
def __spinner():
    spin_forever()

####
# Create Cli Sub Commands
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

def cli_config_add(args, conf):
    try:
        if args['add']:
            exit(config.add(args, conf))
        elif args['remove']:
            exit(config.remove(args, conf))
    except Exception as e:
        puts(traceback.format_exc())
        puts(colored.red(str(e)))

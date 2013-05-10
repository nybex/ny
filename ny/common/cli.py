# -*- coding: utf-8 -*-

# Exit messages
def exit_if_no_config(config):
    if not isinstance(config, dict):
        exit_with_message("""
            Hrm, looks like something is wrong with your config file. Make sure that you
            have a `Nyfile` in your project root and that it is valid TOML. If the file
            is in your root, you may check the syntax with `ny testconfig`
        """)

def exit_with_message(msg):
    exit("\n".join([x.strip() for x in msg.splitlines()]))

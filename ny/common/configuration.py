# -*- coding: utf-8 -*-

import os
from copy import deepcopy

# So we can parse TOML
import toml
from jinja2 import Template

# Import the walk_up command
from .filesystem import walk_up
from .structures import AttrDict

def get_config():
    config = None
    nyrc = None
    try:
        nyrc_path = find_config(name='.nyrc')
        if nyrc_path:
            with open(nyrc_path) as nyrcfile:
                nyrc = toml.loads(nyrcfile.read())

        config_path = find_config()
        with open(config_path) as conffile:
            config = toml.loads(conffile.read())

        if nyrc:
            dict_merge(nyrc, config)
            config = nyrc

    except Exception as e:
        print e
        print 'Configuration is malformed'
        return None

    return AttrDict(config)


def find_config(name="Nyfile"):
    start_path = os.getcwd()
    config = None
    for root, dirs, files in walk_up(start_path):
        # When we find the Snakefile ... #winning
        if name in files:
            config = os.path.join(root, name)
            break

        # if we have reached the project root, stop
        if '.git' in dirs:
            break

    return config


def get_bootscript_paths(instance_type, env, config):
    path = None
    if 'global' in config.keys():
        if 'bootscripts' in config['global'].keys():
            path = os.path.join(os.path.dirname(find_config()),
                    config['global']['bootscripts'])

    if path:
        instance_template = get_type_template(instance_type, config)
        if 'bootscripts' in instance_template.keys():
            paths = []
            for script in instance_template['bootscripts']:
                paths.append(os.path.join(path,
                    Template(script).render(env=env)))

            return paths

    return None


def is_env(string, config):
    if 'envs' in config.keys():
        for x in config['envs']:
            if x == string:
                return True

    return False


def is_type(type, config):
    if 'types' in config.keys():
        for x in config['types']:
            if x == type:
                return True

    return False


def get_env(env, config):
    if is_env(env, config):
        return AttrDict(config['envs'][env])

    return None


def get_type(type, config):
    if is_type(type, config):
        return config['types'][type]

    return None


def get_tags(type, config):
    t = get_type(type, config)
    if t:
        if 'tags' in t:
            tags = {}
            for tag in t['tags']:
                pair = tag.split('=')
                tags[pair[0].rtrim()] = pair[1].ltrim()

            return AttrDict(tags)

    return None


def _get_all_env_security_groups(env, config):
    if is_env(env, config):
        e = get_env(env, config)
        if 'security_groups' in e:
            groups = {}
            for val in e['security_groups']:
                pair = val.split('=>')
                groups[pair[1].lstrip()] = pair[0].rstrip()

            return groups

    return None


def get_env_security_group(name, env, config):
    groups = _get_all_env_security_groups(env, config)
    if groups:
        for id in groups:
            if groups[id] == name:
                return id

    return None


def get_all_envs(config):
    if 'envs' in config.keys():
        return config['envs'].keys()

    return []


def security_group_names_to_ids(names, env, config):
    groups = []
    for n in names:
        id = get_env_security_group(name=n, env=env, config=config)
        if id:
            groups.append(id)

    return groups


def get_type_template(type, config):
    t = get_type(type, config)
    if t:
        return AttrDict(t)
    return None


def get_env_subnets(env, config):
    e = get_env(env, config)
    if e:
        try:
            return e['subnets']
        except:
            pass

    return None

def get_type_subnets(type, env, config):
    e = get_env_subnets(env, config)
    t = get_type_template(type, config)
    if not t:
        try:
            return e['subnets']
        except:
            pass
    else:
        try:
            if e:
                return list(set(t['subnets']).intersection(e))
        except:
            pass

    return None

def get_deploy_bucket(config):
    if 'deploy' in config.keys():
        try:
            return config['deploy']['bucket']
        except:
            pass

    return None

def get_deploy_key(config):
    if 'deploy' in config.keys():
        try:
            return config['deploy']['key']
        except:
            pass

    return None

def dict_merge(target, *args):
  # Merge multiple dicts
  if len(args) > 1:
    for obj in args:
      dict_merge(target, obj)
    return target

  # Recursively merge dicts and set non-dict values
  obj = args[0]
  if not isinstance(obj, dict):
    return obj
  for k, v in obj.iteritems():
    if k in target and isinstance(target[k], dict):
      dict_merge(target[k], v)
    else:
      target[k] = deepcopy(v)
  return target

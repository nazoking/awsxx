# coding: utf-8
import ec2_copy
import boto.ec2
import os
import getpass
from optparse import OptionParser
import yaml
import sys


def create(env=os.environ):
    con = boto.ec2.connect_to_region(
        env.get("AWS_DEFAULT_REGION"),
        aws_access_key_id=env.get("AWS_ACCESS_KEY"),
        aws_secret_access_key=env.get("AWS_SECRET_KEY"))
    t = ec2_copy.EC2Copy(con)
    t.additional_tags["User"] = getpass.getuser()
    return t


def list_get(self, index):
    if len(self) > index:
        return self[index]
    else:
        return None


def parse(usage, options=[], env=os.environ, args=sys.argv, prog=None):
    parser = OptionParser(usage=usage, prog=prog)
    for opt in options:
        parser.add_option(opt)
    parser.add_option('-c', '--config', dest='config',
                      help=u'設定ファイル(yaml)', metavar='FILE')
    parser.add_option("-v", "--verbose",
                      action="store_true", dest="verbose")

    (options, args) = parser.parse_args(args)

    dic = {
        'ssh_settings': {},
        'instance_options': {},
        'verbose': options.verbose,
        'optparse': parser,
        'options': options
    }
    if options.config:
        if options.verbose:
            print "load config file " + options.config
        data = yaml.load(open(options.config).read().decode('utf8'))
        for k, v in data.items():
            dic[k] = v

    return (create(), dic, args)


def module_import(module_name):
    module = __import__(module_name)
    for s in module_name.split(".")[1:]:
        module = getattr(module, s)
    return module


def command_help(prog, prefix):
    modules = []
    from pydoc import ModuleScanner

    def callback(path, module_name, desc):
        if module_name.startswith(prefix):
            module = module_import(module_name)
            if is_command(module):
                modules.append((module_name[len(prefix):], module.__doc__))

    def onerror(modname):
        pass

    ModuleScanner().run(callback, onerror=onerror)
    for name, doc in modules:
        print doc.replace("%prog", prog+" "+name).strip()


def is_command(module):
    names = dir(module)
    if 'main' in names and '__doc__' in names:
        return True
    else:
        return False


def execute(prefix, args=sys.argv[1:], prog=sys.argv[0]):
    cmd = None
    nargs = []
    for arg in args:
        if cmd is None and not(arg[0].startswith('-')):
            cmd = arg
        else:
            nargs.append(arg)

    if cmd is None:
        command_help(prog, prefix)
        sys.exit(-1)

    module_name = prefix+cmd
    try:
        module = module_import(module_name)
    except ImportError, err:
        print "can't import module "+module_name+" "+str(err)
        module = None
    if not(module) or not is_command(module):
        raise Exception("Unknown command "+cmd)
    options = module.options() if 'options' in dir(module) else []
    module.main(*parse(module.__doc__,
                       options=options,
                       args=nargs,
                       prog=prog+" "+cmd))

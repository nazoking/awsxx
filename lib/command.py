# coding: utf-8
import lib.ec2_copy
import boto.ec2
import os
import getpass
from optparse import OptionParser
import yaml


def create(env=os.environ):
    con = boto.ec2.connect_to_region(
        env.get("AWS_DEFAULT_REGION"),
        aws_access_key_id=env.get("AWS_ACCESS_KEY"),
        aws_secret_access_key=env.get("AWS_SECRET_KEY"))
    t = lib.ec2_copy.EC2Copy(con)
    t.additional_tags["User"] = getpass.getuser()
    return t


def list_get(self, index):
    if len(self) > index:
        return self[index]
    else:
        return None


def parse(usage, options=[], env=os.environ):
    parser = OptionParser(usage=usage)
    for opt in options:
        parser.add_option(opt)
    parser.add_option('-c', '--config', dest='config',
                      help=u'設定ファイル(yaml)', metavar='FILE')
    parser.add_option("-v", "--verbose",
                      action="store_true", dest="verbose")

    (options, args) = parser.parse_args()

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

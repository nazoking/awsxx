#!/usr/bin/env python
# vim: fileencoding=utf-8
u"""%prog NEW_INSTANCE_NAME
  インスタンスをコピーして立ち上げる"""

from optparse import make_option
import sys


def options():
    return [
        make_option("--src", type="string", dest="original_instance_name",
                    help=u"コピー元のインスタンス名"),
        make_option("--instance", type="string", dest="new_instance_name",
                    help=u"コピー先のインスタンス名"),
        make_option("--ami", type="string", dest="new_ami_name",
                    help=u"コピー先のami名"),
        ]


def main(self, aopt, args):
    opt = aopt['options']
    if len(args) < 1:
        aopt['optparse'].print_help()
        sys.exit(-1)
    new_ami_name = opt.new_ami_name or args[0]
    new_instance_name = opt.new_instance_name or args[0]

    ins = self.start(original_instance_name=opt.original_instance_name,
                     new_instance_name=new_instance_name,
                     new_ami_name=new_ami_name,
                     instance_options=aopt['instance_options'])
    self.out("OK")
    return ins

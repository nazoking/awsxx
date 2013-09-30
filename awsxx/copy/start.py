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
        make_option("--user_script", type="string", dest="user_script",
                    help=u"インスタンス立ち上げ時のuser_data(bash)"),
        make_option("--user_data", type="string", dest="user_data",
                    help=u"インスタンス立ち上げ時のuser_data"),
        make_option("--role", type="string", dest="role",
                    help=u"インスタンス立ち上げ時のROLE(instance_profile_name)"),
        make_option("--security-groups", type="string", dest="security_groups",
                    help=u"インスタンス立ち上げ時のsecurity_groups"),
        make_option("--tag", type="string", dest="tag", action="append",
                    help=u"インスタンス立ち上げ時のtag (key=name) 複数回指定可能 "),
        ]


def main(self, aopt, args):
    opt = aopt['options']
    if len(args) < 1:
        aopt['optparse'].print_help()
        sys.exit(-1)
    new_ami_name = opt.new_ami_name or args[0]
    new_instance_name = opt.new_instance_name or args[0]
    instance_options = aopt['instance_options']
    if opt.user_script:
        instance_options["user_data"] = "#!/bin/bash -ex\n"+opt.user_script
    else:
        instance_options["user_data"] = opt.user_data
    if opt.role:
        instance_options["instance_profile_name"] = opt.role
    if opt.security_groups:
        instance_options["security_groups"] = opt.security_groups

    ins = self.start(original_instance_name=opt.original_instance_name,
                     new_instance_name=new_instance_name,
                     new_ami_name=new_ami_name,
                     instance_options=instance_options)
    if opt.tag:
        for tag in opt.tag:
            t = tag.split("=", 1)
            if len(t) == 2:
                ins.add_tag(t[0], t[1])
            else:
                ins.add_tag(tag)

    self.out("OK")
    return ins

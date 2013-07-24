#!/usr/bin/env python
# vim: fileencoding=utf-8
u"""%prog NEW_INSTANCE_NAME
  ssh を開く
"""

import lib.command
import start
import fabric.api as fab


def main(self, aopt, args):
    ins = start.main(self, aopt, args)
    aopt['ssh_settings']['host_string'] = ins.public_dns_name
    with fab.settings(**aopt['ssh_settings']):
        fab.open_shell()
    self.out("OK")

if __name__ == '__main__':
    main(*lib.command.parse(__doc__, start.options()))

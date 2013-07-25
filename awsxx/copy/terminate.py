#!/usr/bin/env python
# vim: fileencoding=utf-8
u"""%prog NEW_INSTANCE_NAME
  インスタンスを停止してボリュームを削除する
"""

from lib import command


def main(self, aopt, args):
    self.terminate_instance(args[0])
    self.out("OK")

if __name__ == '__main__':
    main(*command.parse(__doc__))

#!/usr/bin/env python
# vim: fileencoding=utf-8
u"""%prog NEW_INSTANCE_NAME
  (必要なら)インスタンスを終了し、AMIを削除する。
"""

from ..lib import command


def main(self, aopt, args):
    self.unregister(args[0], args[0])
    self.out("OK")

if __name__ == '__main__':
    main(*command.parse(__doc__))

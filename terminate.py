#!/usr/bin/env python
# vim: fileencoding=utf-8 
u"""Usage: %prog NEW_INSTANCE_NAME
    インスタンスを終了する
"""

import lib.command


def main(self, aopt, args):
    self.terminate_instance(args[0])
    self.out("OK")

if __name__ == '__main__':
    main(*lib.command.parse(__doc__))

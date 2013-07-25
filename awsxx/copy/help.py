# coding: utf-8
u"""%prog
  ヘルプの表示
"""

import lib.command
import sys


def main(self, args, options):
    lib.command.command_help(sys.argv[0], __package__+".")

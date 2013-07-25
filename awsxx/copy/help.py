# coding: utf-8
u"""%prog
  ヘルプの表示
"""

from ..lib import command
import sys


def main(self, args, options):
    command.command_help(sys.argv[0], __package__+".")

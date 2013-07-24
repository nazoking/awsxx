# coding: utf-8
u"""%prog
  ヘルプの表示
"""

import lib.command
import sys


def command_help(prog, prefix):
    modules = []
    from pydoc import ModuleScanner

    def callback(path, module_name, desc):
        if module_name.startswith(prefix):
            name = module_name[(module_name.rfind(".")+1):]
            module = getattr(__import__(module_name), name)
            if lib.command.is_command(module):
                modules.append((module_name[len(prefix):], module.__doc__))

    def onerror(modname):
        pass

    ModuleScanner().run(callback, onerror=onerror)
    for name, doc in modules:
        print doc.replace("%prog", prog+" "+name).strip()


def main(self, args, options):
    command_help(sys.argv[0], lib.command.module_prefix)

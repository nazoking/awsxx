# coding: UTF-8
import sys
import datetime
import re


class MessageOutputer():
    u"""
    ログを出力するクラス
    """
    def __init__(self, stdout=sys.stdout):
        self.state = 'out'
        self.stdout = stdout

    def timestamp(self, color="1;30"):
        u"""タイムスタンプ出力"""
        now = datetime.datetime.today()
        self.stdout.write("\033["+color+"m")
        self.stdout.write(now.strftime("[%H:%M:%S]"))
        self.stdout.write("\033[0m")
    bold = re.compile(r'\*(?:\*([^\n\s*]*?)\*|([^\n\s*]*?))\*')

    def _to_bold(self, m):
        if m.group(1):
            return "\033[1;33m"+m.group(1)+"\033[0m"
        return "\033[1;34m"+m.group(2)+"\033[0m"

    def mark(self, msg):
        u"""文字列をマークアップする。"""
        return self.bold.sub(self._to_bold, msg)

    def wait(self, msg):
        u"""改行しない途中経過表示用ログ出力"""
        if self.state == 'wait':
            self.stdout.write("\r\033[2K")
        self.timestamp(color="1;34")
        self.stdout.write(self.mark(msg))
        self.stdout.flush()
        self.state = 'wait'

    def __call__(self, msg):
        u"""改行するログ出力"""
        if self.state == 'wait':
            self.stdout.write("\n")
        self.timestamp()
        self.stdout.write(self.mark(msg)+"\n")
        self.stdout.flush()
        self.state = 'out'

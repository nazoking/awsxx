#!/usr/bin/env python
# vim: fileencoding=utf-8
u"""%prog
  関連するインスタンス、ボリューム、AMI、スナップショットの一覧
"""

import lib.command


def list(self):
    filters = {"tag:Launcher": self.launcher_name}
    for res in self.conn.get_all_instances(filters=filters):
        for ins in res.instances:
            vols = [m.volume_id for m in ins.block_device_mapping.values()]
            print self.out.mark("ins name=" + ins.tags.get("Name")
                                + " id=**" + ins.id + "**"
                                + " state=" + ins.state
                                + " ip=" + ins.public_dns_name
                                + " image=" + ins.image_id
                                + " vols=[" + ", ".join(vols) + "]")
    for vol in self.conn.get_all_volumes(filters=filters):
        print self.out.mark("vol name=%s id=**%s** status=*%s*" %
                            (vol.tags.get("Name"), vol.id, vol.status))
    for ami in self.conn.get_all_images(filters=filters):
        snps = ", ".join(
            [a.snapshot_id for a in ami.block_device_mapping.values()])
        print self.out.mark("ami name=%s id=**%s** state=*%s* snps=[%s]" %
                            (ami.name, ami.id, ami.state, snps))
    for snap in self.conn.get_all_snapshots(owner="self", filters=filters):
        print self.out.mark("snp name=%s id=**%s** status=*%s*" %
                            (snap.tags.get('Name'), snap.id, snap.status))


def main(self, aopt, args):
    list(self)

if __name__ == '__main__':
    main(*lib.command.parse(__doc__))

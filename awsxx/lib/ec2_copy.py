# coding: utf-8
import time
import socket
import out
import fabric.api as fab
import re


class EC2Copy:

    u"""ec2 をコピーしたり
    """

    def __init__(self, con):
        self.conn = con
        self.out = out.MessageOutputer()
        self.launcher_name = "copy_instance"
        self.additional_tags = {
            "Launcher": self.launcher_name
        }

    def find_instances_by_name(self, name):
        u"name と同一の名前を持つインスタンスを返す。戻り値はインスタンスオブジェクトの配列"
        assert not(name is None), "find name is None"
        inss = self.conn.get_all_instances(filters={"tag:Name": name})
        ret = []
        if inss:
            for r in inss:
                for i in r.instances:
                    ret.append(i)
        return ret

    def add_tags(self, i):
        u"オブジェクト i に additional_tags を追加する"
        for k, v in self.additional_tags.items():
            i.add_tag(key=k, value=v)

    def create_image_by_instance(self, instance, new_name):
        u"""インスタンス instance を元に ami (name=new_name)を作成する。

        作成された ami には additional_tags が付与されている
        Returns: amiオブジェクトを返す
        """
        ami_id = self.conn.create_image(instance.id, new_name, no_reboot=True)
        ami = self.conn.get_image(ami_id)
        self.add_tags(ami)
        return ami

    def tag_ami_snapshots(self, ami, new_name):
        """ami のボリュームの元になっているスナップショットにadditional_tags を付与する """
        ids = [dev.snapshot_id for dev in ami.block_device_mapping.values()]
        if ids:
            snaps = self.conn.get_all_snapshots(snapshot_ids=ids, owner="self")
            for snap in snaps:
                self.out("add tag for **" + snap.id + "**")
                self.add_tags(snap)
                snap.add_tag("Name", new_name)

    def tag_instance_volumes(self, ins, new_name):
        u"""インスタンス ins のボリュームにタグを付けます"""
        for d in ins.block_device_mapping.values():
            for v in self.conn.get_all_volumes(d.volume_id):
                if not(self.is_taged_me(v)):
                    self.add_tags(v)
                    v.tags["Name"] = new_name

    def tags_to_str(self, tags):
        """Returns: タグを読みやすい形の文字列にする"""
        return ", ".join([("%s:%s" % t) for t in tags.items()])

    def wait_image_available(self, ami):
        u"""ami の state が available になるまで待つ"""
        while ami.state != "available":
            self.out.wait("**" + ami.id + "** STATUS=*" + ami.state + "*")
            time.sleep(1)
            ami.update()

    def run_instance(self, ami, new_instance_name, instance_options):
        u"""ami からインスタンスを作成する。

        Args:
          ami  -- 起動元のami
          new_instance_name -- インスタンスに付けられる名前
          instance_options -- インスタンスを起動するときのオプション
             ( boto.ec2.image.Image.run の引数 )

        Return: インスタンスオブジェクトを返す
        """
        blocks = ami.block_device_mapping
        blocks[ami.root_device_name].delete_on_termination = True
        instance_options['block_device_map'] = blocks
        r = ami.run(**instance_options)
        if len(r.instances) != 1:
            raise Exception("started instance size !=1 ("+len(r.instance)+")")
        ins = r.instances[0]
        ins.add_tag(key="Name", value=new_instance_name)
        self.add_tags(ins)
        ins.update()
        self.out("Launch Instance from **" +
                 ami.id + "** => **" + ins.id + "**")
        self.wait_instance_state_changing(ins)
        self.tag_instance_volumes(ins, new_instance_name)
        return ins

    def wait_instance_state_changing(self, ins):
        u"""インスタンスの状態が変化中である間待つ。

        変化中で無い状態とは running か stopped か terminated"""
        while ins.state != "running" and ins.state != "stopped" \
                and ins.state != "terminated":
            self.out.wait("**" + ins.id + "** STATUS=*" + ins.state + "*")
            time.sleep(1)
            ins.update()
        return ins.state

    def wait_port_open(self, ip, port):
        u"""ホスト ip の TCP ポート port が反応を返すまで待つ"""
        while True:
            try:
                self.out.wait("CHECK PORT %s " % (port))
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM, 0)
                s.settimeout(1)
                s.connect((ip, port))
                s.close()
                return
            except socket.error:
                pass

    def rename_hostname(self, host, new_hostname, ssh_settings={}):
        u"""ホスト host のホスト名を new_hostname に変更する。

        hostname が ip-xxx-xxx-xxx-xxx の形式(ec2の初期状態)で無ければ変更しない
        """
        ssh_settings['host_string'] = host
        with fab.settings(**ssh_settings):
            with fab.hide('running', 'stdout'):
                hostname = fab.run('hostname')
                if new_hostname == hostname:
                    self.out("already Hostname is " + new_hostname)
                elif re.search(r'^ip(-\d+){4}', hostname):
                    msg = "Rename hostname %s => %s" % (hostname, new_hostname)
                    self.out(msg)
                    fab.sudo('hostname %s' % (new_hostname), pty=True)
                else:
                    msg = "hostname is not expected '%s'" % (hostname)
                    raise Exception(msg)

    def find_image_by_name(self, name):
        u"""ami イメージを名前で探す。

        Returns: ami オブジェクト。見つからない場合は None を返す
        """
        amis = self.conn.get_all_images(filters={"name": name})
        if amis:
            return amis[0]
        else:
            return None

    def check_taged_me(self, obj):
        u"""EC2オブジェクト obj に additional_tags が付与されていなければExceptionを吐いて落ちる
        """
        if not(self.is_taged_me(obj)):
            msg = "%s is not taged me (tags = %s)"
            msg = msg % (str(obj), self.tags_to_str(obj.tags))
            raise Exception(msg)
        self.out(str(obj)+" is mine(tagged)")

    def is_taged_me(self, obj):
        u"""Returns: AWSオブジェクト obj に additional_tags が付与されていなければFalse"""
        for k in self.additional_tags.keys():
            if obj.tags.get(k) != self.additional_tags[k]:
                return False
        return True

    def create_ami_from_instance(self, original_instance_name, new_ami_name):
        u"""original_instance_name から new_ami_name という名前の ami を作成します。

        new_ami_name という名前の ami が既にある場合はそれを返します。
        original_instance_name が複数ある場合は例外を発生します。
        新規作成した場合はスナップショットにその名前を付けます。

        Returns:
          AMI を返します。
        """
        o_inss = self.find_instances_by_name(original_instance_name)
        originals = [s for s in o_inss if s.state != 'terminated']
        if len(originals) != 1:
            msg = "UnExpected instances %s found %d"
            msg = msg % (original_instance_name, len(originals))
            raise Exception(msg)
        original = originals[0]
        self.out("Original instance " + original_instance_name
                 + " ID= **" + original.id + "**")
        ami = self.create_image_by_instance(original, new_ami_name)
        self.out("New AMI ID=**" + ami.id + "**")
        self.wait_image_available(ami)
        self.tag_ami_snapshots(ami, new_ami_name)
        return ami

    def wait_instance_state_running(self, ins):
        u"""インスタンス ins の state が running になるまで待ちます。

        terminated になると例外を発生させます
        """
        while ins.state != 'running':
            self.wait_instance_state_changing(ins)
            if ins.state == 'terminated':
                raise Exception("instance " + ins.id + " is terminated")
            if ins.state == 'stopped':
                self.conn.start_instances([ins.id])
                while ins.state == 'stopped':
                    self.out.wait("instance starting " + ins.id)
                    time.sleep(1)
                    ins.update()
                self.out("instance start **" + ins.id + "**")

    def start(self, original_instance_name, new_instance_name, new_ami_name,
              instance_options={}):
        u"""インスタンスを起動し、ホスト名を書き換えます。

        Args:
          original_instance_name -- ami作成時に元となるインスタンスの名前
          new_instance_name -- 作成されるインスタンスの名前
          new_ami_name -- 作成されるamiの名前
          instance_options -- インスタンスを起動するときのオプション
                          ( boto.ec2.image.Image.run の引数 )
        Returns:
          インスタンスを返します
        """
        inss = [s for s in self.find_instances_by_name(new_instance_name)
                if s.state != 'terminated']
        if inss:
            if len(inss) != 1:
                raise Exception("Instance " + new_instance_name
                                + " (not terminated) are not only one.("
                                + len(inss)
                                + " instances found)")
            ins = inss[0]
            self.out("Alreasy created Instance " +
                     new_instance_name + " => **" + ins.id + "**")
            self.wait_instance_state_running(ins)
        else:
            ami = self.find_image_by_name(new_ami_name)
            if ami:
                self.out("Already created AMI ID=**" + ami.id + "**")
                self.wait_image_available(ami)
            else:
                ami = self.create_ami_from_instance(original_instance_name,
                                                    new_ami_name)
            self.out("ready! **" + ami.id + "** STATUS=*" + ami.state + "*")
            ins = self.run_instance(ami, new_instance_name, instance_options)
        self.out("ready! **" + ins.id + "** STATUS=*" + ins.state + "*")
        self.out("HOST= **" + ins.public_dns_name + "**")
        self.wait_port_open(ins.public_dns_name, 22)
        return ins

    def terminate_instance(self, name):
        u"""インスタンスを終了させます。

        同名のインスタンスが複数ある場合は例外を発生させます。

        Args:
          name -- 停止させるインスタンス名(Nameタグ)

        Returns: 終了させたインスタンスを返します。
          インスタンスが見つからない場合は None を返します。
        """
        inss = [r for r in self.find_instances_by_name(name)
                if r.state != 'terminated']
        if not(inss):
            return None
        if len(inss) != 1:
            raise Exception("UnExpected instances found %d" % (len(inss)))
        ins = inss[0]
        self.check_taged_me(ins)
        self.out("find name=%s id=**%s** state=*%s*" %
                 (name, ins.id, ins.state))
        ins.terminate()
        ins.update()
        self.wait_instance_state_changing(ins)
        return ins

    def unregister(self, new_instance_name, new_ami_name):
        u"""インスタンスを停止し、amiを登録削除します。

        Args:
          new_instance_name -- 停止するインスタンス名
          new_ami_name -- 登録解除するami名
        """
        ins = self.terminate_instance(new_instance_name)
        if ins:
            ami = self.conn.get_image(ins.image_id)
        else:
            self.out("Not running instance %s" % (new_instance_name))
            ami = self.find_image_by_name(new_ami_name)
        if ami:
            self.check_taged_me(ami)
            self.out("Deregister image with snapshot **%s**" % (ami.id))
            ami.deregister(True)
        else:
            self.out("AMI %s is not found" % (new_ami_name))

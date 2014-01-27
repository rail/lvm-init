#!/usr/bin/python

import os
import json
import subprocess
from syslog import openlog, syslog, LOG_ERR, LOG_WARNING

CFG = "/etc/lvm-init/lvm-init.json"
DEFAULT_MOUNT_OPTS = "defaults,noatime"
FSTAB_TMPL = "{dev} {mount_point} {fs_type} {mount_options} 0 0"
openlog("lvm-init")


def run(cmd, include_stderr=False):
    stderr = None
    if include_stderr:
        stderr = subprocess.STDOUT
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=stderr,
                            shell=True)
    proc.wait()
    output = proc.stdout.read()
    if proc.returncode != 0:
        raise subprocess.CalledProcessError(proc.returncode, cmd)
    return output


def add_fstab_entry(dev, mount_point, fs_type, mount_options):
    new_fstab = []
    with open("/etc/fstab") as f:
        for l in f.readlines():
            # Filter out the already existing entry
            if not l.startswith(dev):
                new_fstab.append(l.strip())
        new_fstab.append(FSTAB_TMPL.format(dev=dev, fs_type=fs_type,
                                           mount_point=mount_point,
                                           mount_options=mount_options))
    if new_fstab:
        with open("/etc/fstab", "w") as f:
            f.write("\n".join(new_fstab))
            f.write("\n")


def main():
    if not os.path.exists(CFG):
        syslog(LOG_ERR, "Config %s does not exist, exiting." % CFG)
        return
    try:
        config = json.load(open(CFG))
    except:
        syslog(LOG_ERR, "Error loading config %s" % CFG)
        raise
    if not "lvm" in config:
        syslog(LOG_WARNING, "No lvm section in %s, exiting" % CFG)
        return

    lvm = config["lvm"]
    devs = lvm["pvcreate"].split()
    lvm_setup_done = True
    for dev in devs:
        try:
            out = run("/sbin/blkid -c /dev/null %s" % dev)
            if not "LVM2_member" in out:
                lvm_setup_done = False
        except subprocess.CalledProcessError:
            syslog(LOG_WARNING, "blkid failed, assuming LVM is not configured")
            lvm_setup_done = False
    if lvm_setup_done:
        syslog("LVM is ok, exiting")
        return
    syslog("Creating new physical volumes: %s" % lvm["pvcreate"])
    run("/sbin/pvcreate %s" % lvm["pvcreate"])
    for vg, devices in lvm["vgcreate"].items():
        syslog("Creating new volume group %s using %s" % (vg, devices))
        run("/sbin/vgcreate %s %s" % (vg, devices))
    for lv, lv_config in lvm["lvcreate"].items():
        syslog("Creating new logical volume %s" % lv)
        run("/sbin/lvcreate -n {lv} {params} {vg}".format(
            lv=lv, params=lv_config["params"], vg=lv_config["vg"]))
        if lv_config.get("format_as"):
            fs_type = lv_config["format_as"]
            dev = "/dev/%s/%s" % (lv_config["vg"], lv)
            mount_options = lv_config.get("mount_options", DEFAULT_MOUNT_OPTS)
            mount_point = lv_config["mount_point"]
            syslog("Formatting %s" % dev)
            run('/sbin/mkfs.{fs_type} {dev}'.format(fs_type=fs_type,
                                                    dev=dev))
            add_fstab_entry(dev, mount_point, fs_type, mount_options)
            run("/bin/mkdir -p %s" % mount_point)
            syslog("Mounting %s" % mount_point)
            run("/bin/mount %s" % mount_point)


if __name__ == "__main__":
    main()

# question: how to read arguments from json file?

import os
import sys
import subprocess
from datetime import datetime
import time
import json

config = {}
filename = os.path.dirname(sys.argv[0]) + '/config.json'
with open(filename, 'r', encoding='utf-8') as f_obj:
    config = json.load(f_obj)

log = os.path.expanduser(config['log'])
host = config['host']
shared_dir = config['shareDir']
imagePath = config['imagePath']
imageName = config['imageName']
interval = 7200
path = '/Volumes/' + shared_dir + '/' + imagePath


def isHostOn(host: str):
    command_obj = subprocess.Popen(
        ['smbutil', 'lookup', host], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    stdout = command_obj.communicate()[0]
    yesOrNo = stdout.decode().find('IP') > -1
    try:
        f_obj = open(log, 'a', encoding='utf-8')
    except FileNotFoundError:
        f_obj = open(log, 'x', encoding='utf-8')
    if yesOrNo:
        f_obj.write(str(datetime.now()) + ',' + ' stdout: ' + stdout.decode().rstrip() +
                    ', ' + 'host ' + '"' + host + '"' + ' is already active!\n')
    else:
        f_obj.write(str(datetime.now()) + ',' + ' stdout: ' + stdout.decode().rstrip() +
                    ', ' + 'host ' + '"' + host + '"' + ' is currently inactive!\n')
    f_obj.close()
    return yesOrNo


def isSharedDirMounted(shared_dir: str):
    command_obj = subprocess.Popen(['ls', '/Volumes'], stdout=subprocess.PIPE)
    stdout = command_obj.communicate()[0]
    return stdout.decode().find(shared_dir) > -1


def isImageMounted(img: str):
    command_obj = subprocess.Popen(['mount'], stdout=subprocess.PIPE)
    stdout = command_obj.communicate()[0]
    return stdout.decode().find(img) > -1


def mountSharedDir(host: str, shared_dir: str):
    command_obj = subprocess.Popen(
        ['/usr/bin/osascript', '-e', 'mount volume "smb://' + host + '/' + shared_dir + '"'], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    stdout, stderr = command_obj.communicate()
    f_obj = open(log, 'a', encoding='utf-8')
    if stdout.decode().find(shared_dir) > -1:
        f_obj.write(str(datetime.now()) + ': ' + 'stdout: ' + stdout.decode() +
                    'Successfully mounted remote directory ' + '"' + shared_dir + '"' + '!\n')
    else:
        f_obj.write(str(datetime.now()) + ': ' + 'stdout: ' + stdout.decode().rstrip() + '; stderr: ' +
                    str(stderr) + ': ' + 'Failed to mount remote directory ' + '"' + shared_dir + '"' + '!\n')
    f_obj.close()
    return


def mountImage(path: str):
    command_obj = subprocess.Popen(
        ['open', path], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    stdout, stderr = command_obj.communicate()
    returnCode = command_obj.returncode
    f_obj = open(log, 'a', encoding='utf-8')
    if returnCode == 0:
        f_obj.write(str(datetime.now()) + ': ' + 'stdout: ' + stdout.decode() + ' ' +
                    'Successfully mounted ' + '"' + os.path.basename(path) + '"' + '!')
    else:
        f_obj.write(str(datetime.now()) + ': ' + 'stdout: ' + stdout.decode().strip() + '; stderr: ' +
                    str(stderr) + ': ' + 'Failed to mount ' + '"' + os.path.basename(path) + '"' + '!')
    f_obj.close()
    return


def sayWellDone():
    f_obj = open(log, 'a', encoding='utf-8')
    f_obj.write('Everything for Time Machine is ready, well done! Helper!')
    f_obj.close()
    return


def main():
    while True:
        if isHostOn(host):
            if isSharedDirMounted(shared_dir):
                if isImageMounted(imageName):
                    sayWellDone()
                    pass
                else:
                    mountImage(path)
            else:
                mountSharedDir(host, shared_dir)
                time.sleep(15)
                mountImage(path)
        time.sleep(interval)


if __name__ == "__main__":
    while True:
        main()

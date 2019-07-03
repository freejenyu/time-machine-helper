# question: how to read arguments from json file?

import subprocess
import os
import time
from datetime import datetime
host = 'ld-pc'
shared_dir = 'Data'
imagePath = 'Time Mathine/TimeMachine.sparsebundle'
# the name defined when creating the image file 'TimeMachine.sparsebundle' is the name for the image that will be present in '/volumes'.
imageName = 'TimeMachine'
path = '/Volumes/' + shared_dir + '/' + imagePath
interval = 600
log = os.path.expanduser('~/.TimeMachineHelper.log')


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
                    ', ' + 'host ' + '"' + host + '"' + ' is already active!')
    else:
        f_obj.write(str(datetime.now()) + ',' + ' stdout: ' + stdout.decode().rstrip() +
                    ', ' + 'host ' + '"' + host + '"' + ' is currently inactive!')
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
    if isHostOn(host):
        if isSharedDirMounted(shared_dir):
            if isImageMounted(imageName):
                sayWellDone()
                pass
            else:
                mountImage(path)
        else:
            mountSharedDir(host, shared_dir)
            mountImage(path)


if __name__ == "__main__":
    while True:
        main()
        time.sleep(interval)

import os
import sys
import subprocess
import time
import json


configPath = os.path.join(os.path.dirname(sys.argv[0]), 'config.json')
data = {}
with open(configPath, 'r', encoding='utf-8') as f:
    data = json.load(f)
host = data['host']
share = data['share']
imageFilename = data['imageFilename']
imageName = data['imageName']
mountPoint = '/Volumes'
imageFilepath = os.path.join(mountPoint, share, imageFilename)
interval = data['interval']
log = os.path.expanduser(data['log'])


def timestamp():
    return time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())


def isHostOn(host: str) -> bool:
    cmd = f"smbutil lookup {host}"
    c = subprocess.run(
        cmd, shell=True,
        stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    stdout = c.stdout.decode().replace('\n', ' ', 1)
    with open(log, 'a', encoding='utf-8') as f:
        f.write(f"{timestamp()} {stdout}")
        f.close()
    return c.returncode == 0


def isShareMounted(share: str) -> bool:
    return os.path.isdir(f"{mountPoint}/{share}")


def isImageMounted(image: str) -> bool:
    return os.path.isdir(f"{mountPoint}/{image}")


def mountShare(host: str, share: str):
    cmd = ['osascript', '-e', f'mount volume "smb://{host}/{share}"']
    subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    with open(log, 'a', encoding='utf-8') as f:
        if isShareMounted(share):
            f.write(f"{timestamp()} Successfully mounted '{share}'!\n")
        else:
            f.write(f"{timestamp()} Failed to mount '{share}'!\n")


def mountImage(path: str, image: str):
    cmd = f"open {path}"
    subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    time.sleep(30)
    with open(log, 'a', encoding='utf-8') as f:
        if isImageMounted(image):
            f.write(f"{timestamp()} Successfully mounted '{image}'!\n")
        else:
            f.write(
                f"{timestamp()} Failed to mount '{image}'!\n")


def sayWellDone():
    with open(log, 'a', encoding='utf-8') as f:
        f.write(f'{timestamp()} TimeMachine is ready, well done!\n')


def main():
    while True:
        if isHostOn(host):
            if isShareMounted(share):
                if isImageMounted(imageName):
                    sayWellDone()
                    pass
                else:
                    mountImage(imageFilepath, imageName)
            else:
                mountShare(host, share)
                time.sleep(60)
                mountImage(imageFilepath, imageName)
        time.sleep(interval)


if __name__ == "__main__":
    main()

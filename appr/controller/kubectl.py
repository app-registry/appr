import time
import json
import subprocess


def call(cmd):
    command = ['kubectl'] + cmd
    return subprocess.check_output(command, stderr=subprocess.STDOUT)


def get(kind, name, namespace="default", opts=None):
    if not opts:
        opts = []
    cmd = ['get', kind, name, '-n', namespace] + opts
    return call(cmd)


def delete(kind, name, namespace="default", opts=None):
    if not opts:
        opts = []
    cmd = ['delete', kind, name, '-n', namespace] + opts
    return call(cmd)


def list(kind, namespace="default", opts=None):
    if not opts:
        opts = []
    cmd = ['get', kind, '-o', 'json', '-n', namespace] + opts
    return call(cmd)


def wait(kind, name, namespace="default", retries=3, seconds=1):
    retry_count = 1
    time.sleep(seconds)
    obj = get(kind, name, namespace)
    while retry_count < retries and obj is None:
        retry_count += 1
        time.sleep(seconds)
        obj = get(kind, name, namespace)
    return obj


def exists(kind, name, namespace='default'):
    try:
        get(kind, name, namespace)
        return True
    except subprocess.CalledProcessError:
        return False

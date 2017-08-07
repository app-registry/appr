from __future__ import absolute_import, division, print_function

from tabulate import tabulate

from appr.utils import colorize, get_media_type


def print_packages(packages, registry_host=""):
    header = ['app', 'release', 'downloads', 'manifests']
    table = []
    for package in packages:
        release = package["default"]
        manifests = ", ".join(package['manifests'])
        table.append([
            registry_host + "/" + package['name'], release,
            str(package.get('downloads', '-')), manifests])
    return tabulate(table, header)


def print_package_info(packages, extended=False):
    header = ["release", "manifest", "digest"]
    if extended:
        header = header + ["created_at", "size", "downloads"]
    table = []
    for package in packages:
        row = [
            package['release'],
            get_media_type(package['content']['mediaType']),
            package['content']['digest'], ]
        if extended:
            row = row + [
                package['created_at'],
                package['content']['size'],
                package.get('downloads', '-'), ]
        table.append(row)
    return tabulate(table, header)


def print_channels(channels):
    header = ['channel', 'release']
    table = []
    for channel in channels:
        table.append([channel['name'], channel['current']])
    return tabulate(table, header)


def print_deploy_result(table):
    header = ["package", "release", "type", "name", "namespace", "status"]
    for r in table:
        status = r.pop()
        r.append(colorize(status))

    return tabulate(table, header)

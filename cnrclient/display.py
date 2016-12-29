from tabulate import tabulate

from cnrclient.utils import get_media_type


def print_packages(packages):
    header = ['app', 'release', 'downloads', 'manifests']
    table = []
    for package in packages:
        release = package["default"]
        manifests = ", ".join(package['manifests'])
        table.append([package['name'], release, str(package.get('downloads', '-')), manifests])
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
            package['content']['digest'],
            ]
        if extended:
            row = row + [
                package['created_at'],
                package['content']['size'],
                package.get('downloads', '-'),
            ]
        table.append(row)
    return tabulate(table, header)


def print_channels(channels):
    header = ['channel', 'release']
    table = []
    for channel in channels:
        table.append([channel['name'], channel['current']])
    return tabulate(table, header)

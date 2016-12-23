from tabulate import tabulate


def print_packages(packages):
    header = ['app', 'release', 'downloads', 'manifests']
    table = []
    for package in packages:
        release = package["default"]
        manifests = ", ".join(package['manifests'])
        table.append([package['name'], release, str(package.get('downloads', '-')), manifests])
    return tabulate(table, header)


def print_channels(channels):
    header = ['channel', 'release']
    table = []
    for channel in channels:
        table.append([channel['name'], channel['current']])
    return tabulate(table, header)

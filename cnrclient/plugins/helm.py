import subprocess


__all__ = ['Helm']


class Helm(object):
    def __init__(self):
        pass

    def action(self, cmd, release, helm_opts=None):
        cmd = [cmd]
        if helm_opts:
            cmd = cmd + helm_opts
        cmd = cmd + [release]
        return self._call(cmd)

    def _call(self, cmd):
        command = ['helm'] + cmd
        try:
            return subprocess.check_output(command, stderr=subprocess.STDOUT)
        except subprocess.CalledProcessError as e:
            return e.output

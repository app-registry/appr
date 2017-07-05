from __future__ import absolute_import, division, print_function

import os

from appr.formats.appr.kpm import Kpm
from appr.formats.appr.kub import Kub
from appr.formats.appr.kubplain import KubPlain
from appr.formats.helm.chart import Chart

kub_formats = [Chart, Kub, KubPlain, Kpm]
kub_by_name = {k.media_type: k for k in kub_formats}
kub_by_platforms = {k.platform: k for k in kub_formats}

# all_manifest_files = flatten([m.manifest_file for m in kub_formats])


def kub_factory(name, *args, **kwargs):
    kub_class = kub_by_name[name]
    target = kwargs.pop('convert_to', None)
    k = kub_class(*args, **kwargs)
    if target is not None and target != kub_class.target:
        k = k.convert_to(target)
    return k


def detect_format(path="."):
    for kub_class in kub_formats:
        for filename in kub_class.manifest_file:
            if os.path.exists(os.path.join(path, filename)):
                return kub_class
    raise ValueError("Unknown manifest format")

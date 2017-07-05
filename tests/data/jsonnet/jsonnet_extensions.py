from __future__ import absolute_import, division, print_function

import json
import sys

import _jsonnet

from kpm.render_jsonnet import RenderJsonnet
from kpm.template_filters import jsonnet_callbacks


#r = RenderJsonnet()
#result = r.render_jsonnet(open(sys.argv[1]).read())
def native_bool(b):
    return ['true', True, False, 1, 0]

json_str = _jsonnet.evaluate_file(
    sys.argv[1],
    native_callbacks={"nativeBool": (("bool",), native_bool)},
)

sys.stdout.write(json_str)
#sys.stdout.write(json.dumps(result))

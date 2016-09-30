import sys
import _jsonnet
import json
from kpm.template_filters import jsonnet_callbacks
from kpm.render_jsonnet import RenderJsonnet

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

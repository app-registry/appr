local kpm = import "kpm.libjsonnet";
#local h = import "kpm-utils.libjsonnet";
#local kpm = h + kpmp;
function(
  variables={cookie: "teoto"}
)

{
  env: {
   cookie: variables.cookie
  },
  jinja2: kpm.jinja2("yo: {{cookie}}", self.env),
#   jsonnet: kpm.jsonnet("function(cookie='titi')({cookieT: cookie})", self.env),
  json: kpm.jsonLoads('{"a": "b"}'),
  yaml_obj: kpm.yamlLoads(kpm.to_yaml({"a": "b", "t": [1,2,3,4]})),
  hashsha1: kpm.hash("titi"),
  hashmd5: kpm.hash("titi", 'md5'),
  hashsha256: kpm.hash("titi", 'sha256'),
  yaml: kpm.to_yaml({"a": "b", "t": [1,2,3,4]}),
  rand_alphnum32: kpm.randAlphaNum(),
  rand_alphnum8: kpm.randAlphaNum(8),
  rand_alpha8: kpm.randAlpha(8),
  rand_alpha32: kpm.randAlpha(),
  rand_int32: kpm.randInt(seed="4"),
  rand_int8: kpm.randInt(8),
  rsa: kpm.genPrivateKey("rsa"),
  rsaX: kpm.genPrivateKey("rsa", 'x'),
  rsaZ: kpm.genPrivateKey("rsa", 'z'),
  rsaZ2: kpm.genPrivateKey("rsa", 'z'),
  rsaX2: kpm.genPrivateKey("rsa", 'x'),
  dsa: kpm.genPrivateKey("dsa"),
  ecdsa: kpm.genPrivateKey("ecdsa"),
}

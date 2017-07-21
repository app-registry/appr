{

   # APPR extended std
   local apprnative = self,
   local initSeed = apprnative.randAlpha(256),

   # Returns hash of the string representation of an object.
   hash(data, hashtype='sha1'):: (
      std.native("hash")(std.toString(data), hashtype)
   ),

   # Converts an object to yaml string
   to_yaml(data):: (
      std.native("to_yaml")(std.toString(data))
   ),

   # Read a file
   readfile(filepath, encode=false):: (
      std.native("read")(filepath, encode)
   ),

   # Get a ENV value
   getenv(name, default=null):: (
      std.native("getenv")(name, default)
   ),

   # Random alpha-numeric string of length `size`
   randAlphaNum(size=32, seed=""):: (
      std.native("rand_alphanum")(std.toString(size), seed=seed)
   ),

   # Random alpha string of length `size`
   randAlpha(size=32, seed=""):: (
      std.native("rand_alpha")(std.toString(size), seed=seed)
   ),

   # Random numeric string of length `size`
   randInt(size=32, seed=""):: (
      std.native("randint")(std.toString(size), seed=seed)
   ),

   # Generate privateKeys.
   # Keytype choices: 'rsa', 'ecdsa', 'dsa'.
   # key allows to generate a unique key per run
   genPrivateKey(keytype, key=""):: (
      std.native("privatekey")(keytype, key=key, seed=initSeed)
   ),

   loadObject(data):: (
      std.native("obj_loads")(std.toString(data))
   ),

   # Render jinja2 template
   jinja2(template, env={}):: (
      std.native("jinja2")(template, std.toString(env))
   ),

   # Render jsonnet template
   jsonnet(template, env={}):: (
      std.native("jsonnet")(template, std.toString(env))
   ),

   # Convert json string to object
   jsonLoads(data):: (
      std.native("json_loads")(data)
   ),

   # b64encode
   b64encode(str):: (
      std.native("b64encode")(str)
   ),

   # b64decode
   b64decode(str):: (
      std.native("b64decode")(str)
   ),

   # check if a path exists, optionally check if it's a file
   path_exists(path, isfile=false):: (
      std.native("path_exists")(path, isfile)
   ),

   # recursivly list directoy files
   walkdir(str):: (
      std.native("walkdir")(str)
   ),

   # list directory files
   listdir(str):: (
      std.native("listdir")(str)
   ),

   # Convert yaml string to object
   yamlLoads(data):: (
      std.native("yaml_loads")(data)),

   tests: {
        b64encode: (assert apprnative.b64encode("toto") == "dG90bw=="; true),
        b64decode: (assert apprnative.b64decode(apprnative.b64encode("toto")) == "toto"; true),
        getenv: (assert std.length(apprnative.getenv("HOME")) > 0;
                 assert apprnative.getenv("BAD_ENV_APPR", "default_value") == "default_value"; true),
        },
}

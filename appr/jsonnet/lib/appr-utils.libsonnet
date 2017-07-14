local nativeExt = import "appr-native-ext.libsonnet";

nativeExt + {

   # APPR extended std
   local kpmutils = self,
   local apprutils = self,

   # Generate a sequence array from 1 to i
   seq(i):: (
      [x for x in std.range(1, i)]
   ),

   compact(array):: (
     [x for x in array if x != null]
   ),

  objectFieldsHidden(obj):: (
     std.setDiff(std.objectFieldsAll(obj), std.objectFields(obj))
  ),

  objectFlatten(obj):: (
    // Merge 1 level dict depth into toplevel
    local visible = {[k]: obj[j][k],
                    for j in std.objectFieldsAll(obj)
                    for k in std.objectFieldsAll(obj[j])};

    visible
  ),

  path: {
    basename(path):: (local x = std.split(path, "/"); x[std.length(x) -1]),
   },

   objectValues(obj):: (
     local fields =  std.objectFields(obj);
      [obj[key] for key in fields]
   ),

   objectMap(func, obj):: (
    local fields = std.objectFields(obj);
    {[key]: func(obj[key]) for key in fields}
    ),

   capitalize(str):: (
     std.char(std.codepoint(str[0]) - 32) + str[1:]
   ),

   tests: {
        capitalize: (assert apprutils.capitalize("test") == 'Test'; true),
        b64encode: (assert apprutils.b64encode("toto") == "dG90bw=="; true),
        b64decode: (assert apprutils.b64decode(apprutils.b64encode("toto")) == "toto"; true),
        basename: (assert apprutils.path.basename("/foo/bar/toto") == "toto";
                   assert apprutils.path.basename("foo") == "foo";
                   assert apprutils.path.basename("foo/") == "";
                   assert apprutils.path.basename("/foo") == "foo";
                   assert apprutils.path.basename("") == "";
                   true),
        },

}

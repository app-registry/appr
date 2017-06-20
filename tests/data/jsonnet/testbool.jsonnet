local nativeBool(b) =
    std.native("nativeBool")(b);

{
  "true": nativeBool(true),
  "false": nativeBool(false),
}

local apprstd = import "appr-utils.libsonnet";
apprstd {

   local appr = self,
   local kpm = self,
   utils:: apprstd,

   variables(package, params):: (
   local p = package + {variables: package.variables + std.mergePatch(super.variables, params.variables)};
     p.variables
   ),

   deploy(dep):: (
      dep
   ),

   shards(s, target):: (
      if std.type(target) == 'null' then
         s
      else if std.type(target) == "object" then
         std.mergePatch(s, target)
      else if std.type(target) == "array" then
         if std.length(target) == 0 then
            s
         else
            target
      else if std.type(target) == "number" then
         [{ name: x } for x in appr.seq(target)]
      else
         error "Bad shard type: %s (%s)" % [target, std.type(target)]
   ),

   shard_count(n):: ([{ name: x } for x in std.range(1, n)]),

   shard_list(shard, shards):: (
      if shard == "true" || std.type(shard) == "boolean" then
         shards
      else if std.type(shard) == "string" then
         if std.type(shards[shard]) == "number" then
            appr.shard_count(shards[shard])
         else
            shards[shard]
      else if std.type(shard) == "number" then
         appr.shard_count(shard)
      else
         error "Unknow shard value: %s (%s)" % [shard, std.type(shard)]
   ),


   template_format(resource):: (
      resource { value: appr.loadObject(resource.template % resource.variables) }
   ),

   template_jinja2(resource):: (
      resource { value: appr.loadObject(appr.jinja2(resource.template, resource.variables)) }
   ),

   template_jsonnet(resource):: (
      resource { value: apprstd.jsonnet(resource.template, { variables: std.toString(resource.variables) }) }
   ),

   extra_resource_values(resource):: (
   if resource.format == "kubernetes" then
      {
         namespace: resource.variables.namespace,
         value: { metadata: { [ if std.objectHas(resource, 'name') then 'name' ]: resource.name,
                              namespace: resource.variables.namespace } },
      }
      else {}
   ),

   resource_defaults(resource, package):: (
      local default_expander = if std.objectHas(package, 'expander') then
         package.expander
      else
         'none';
      local default_update = if std.objectHas(package, 'update_mode') then
         package.update_mode
      else
         'update';

      local platform = if std.objectHas(package, 'format') then
         package.format
      else
         'kubernetes';

      {
         update_mode: default_update,
         format: platform,
         expander: default_expander,
         protected: false,
      }
   ),

   template(resource):: (
      local r = if std.objectHas(resource, "value") == true then
         resource
      else if std.objectHas(resource, "expander") == false ||
                   resource.expander == 'none' || resource.expander == null then
         resource { value: appr.loadObject(resource.template) }
      else if resource.expander == "fmt" then
         appr.template_format(resource)
      else if resource.expander == "jinja2" then
         appr.template_jinja2(resource)
      else if resource.expander == "jsonnet" then
         appr.template_jsonnet(resource)
      else
         error "Unknown expander: %s.\n Supported expanders are: [fmt, jinja2, jsonnet, none]" % [resource.expander];
      std.mergePatch(r, appr.extra_resource_values(resource))
   ),

   sharded_resource(resource, shards, variables):: (
      local resource_shards = appr.shard_list(resource.sharded, shards);
      [
         local extra = {
            shard: shard.name,
            name: "%s-%s" % [resource.name, shard.name],
         };

         local var = if std.objectHas(shard, "variables") == true then
            { variables: variables + extra +
                         shard.variables + { shards: resource_shards } }
         else
            { variables: variables + extra + { shards: resource_shards } };

         local r = resource + extra + var;
         appr.template(r) for shard in resource_shards]
   ),

   resources(resources, shards, variables, package):: (
       std.flattenArrays([
         local r = appr.resource_defaults(resource, package) + resource;
         local result = if std.objectHas(resource, "sharded") then
            appr.sharded_resource(r, shards, variables)
         else
            [appr.template(r { variables: {
              [ if std.objectHas(r, 'name') then 'name' ]: r.name } + variables })];
         result for resource in resources if resource != null])
   ),


   ###
   package(pack, env):: (
    local default_params = {
       namespace: "default",
       variables: { namespace: default_params.namespace },
       shards: null,
       };

      local params = std.mergePatch(default_params, env);

      local variables = { variables: { namespace: params.namespace } +
                                     if std.objectHas(pack, "variables") then
         appr.variables(pack, params)
      else
         params.variables };
      local p = pack + variables;

      local shards = if std.objectHas(p, "shards") then
         { shards: appr.shards(p.shards, params.shards) }
      else
         { shards: null };

      local resources = if std.objectHas(p, "resources") then
         { resources: appr.resources(p.resources, shards.shards, variables.variables, p.package) }
      else
         { resources: [] };

      local package = {
         package: p.package,
         deploy: apprstd.compact(p.deploy) } + variables + shards + resources;

      package
   ),
}

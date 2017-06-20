local kpm = import "kpm.libjsonnet";

function(
   namespace="default",
   variables={namespace: namespace},
   shards=null,
   patch={},
)

   {
      package: {
         author: 'Antoine Legrand',
         version: '3.5.6-1',
         description: 'rabbitmq',
         license: 'MIT',
         name: 'rabbitmq/rabbitmq',
      },

      variables: kpm.variables({
         image: "quay.io/ant31/kubernetes-rabbitmq",
         cookie: "Dffds9342",
         data_volume: { emptyDir: { medium: '' }, name: 'varlibrabbitmq' },
      }, variables),

      shards: kpm.shards({
         rmq: [
            { name: 'bunny' },
            { name: 'hare' },
            { name: 'bunny',
              variables: { args: ['--ram'] } },
         ],
         etcd: 5
      }, shards),

      resources: kpm.resources([{
         type: "svc",
         protected: true,
         sharded: 'rmq',
         name: "rabbitmq",
         file: "rabbitmq-svc.yaml",
	 expander: "jsonnet",
         template: (importstr "testkpmtemplate.jsonnet"),
      },
    ], $.shards, $.variables),

      deploy: kpm.deploy([
         {
            name: '$self',
         },

         {
            name: 'coreos/etcd',
            shards: $.shards.etcd,
         }]),

   }

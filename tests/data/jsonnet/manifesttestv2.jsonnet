local kpm = import "kpm.libjsonnet";

function(
  params={}
)

kpm.package({

      package: {
         expander: 'jsonnet',
         author: 'Antoine Legrand',
         version: '3.5.6-1',
         description: 'rabbitmq',
         license: 'MIT',
         name: 'rabbitmq/rabbitmq',
      },

      variables: {
         rand: kpm.hash('titi'),
         image: "quay.io/ant31/kubernetes-rabbitmq",
         cookie: "Dffds9342",
         data_volume: { emptyDir: { medium: '' }, name: 'varlibrabbitmq' },
      },

      shards: {
         rmq: [
            { name: 'bunny' },
            { name: 'hare' },
            { name: 'bunny',
              variables: { args: ['--ram'] } },
         ],
         etcd: 5
      },

      resources: [{
         type: "svc",
         protected: true,
         sharded: 'rmq',
         name: "rabbitmq",
         file: "rabbitmq-svc.yaml",
         template: (importstr "testkpmtemplate.jsonnet"),
      },
    ],

      deploy: [
         {
            name: '$self',
         },

         {
            name: 'coreos/etcd',
            shards: $.shards.etcd,
         }]

   }, params)

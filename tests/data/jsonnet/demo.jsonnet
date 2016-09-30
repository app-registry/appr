local kpm = import "d.libjsonnet";
function(variables={}, namespace='default', shards=null)
  kpm.package(
    {
      name: 'rabbitmq/rabbitmq',
      version: '3.5.6-1',

      meta: {
        author: 'Antoine Legrand',
        description: 'rabbitmq',
        license: 'MIT',
      },

      variables: {
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
        etcd: 5,
      },

      resources: [
        {
          type: "svc",
          protected: true,
          sharded: 'rmq',
          name: "rabbitmq",
          file: "rabbitmq-svc.yaml",
          expander: "jsonnet",
          template: (importstr "testkpmtemplate.jsonnet"),
        },
        {
          type: "svc",
          name: "template",
          template: (importstr "testkpmtemplate.jsonnet"),
        },
      ],

      deploy: [
        {
          name: 'coreos/etcd',
          shards: $.shards.etcd,
        }],

    })

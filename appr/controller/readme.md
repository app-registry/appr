# Offline Descriptor -> Online PackageRelease

- [ ] kubectl packages init-crd  # create crds
- [ ] kubectl packages get  # appr list
- [ ] kubectl packages get xxxx -> appr list --search xxxx
- [ ] kubectl packages get -l mediaType=helm xxx -> appr list -t helm
- [ ] kubectl packages describe xxxx -> appr show xxxx
- [x] kubectl packages generate package --from-descriptor descriptor.yaml --version=x.x.x  # this update descriptor too
- [x] kubectl packages generate descriptor  --name xxx --version=x.x.x --media-type helm   # push
- [x] kubectl packages extract --from-package foo-bar.helm.1.6.0.yaml # pull
- [ ] kubectl packages extract --namespaces apps foo-bar.helm.1.6.0   # fetch from the server  # pull
- [ ] kubectl apply foo-bar.helm.1.6.0.yaml --namespaces apps   # push
- [ ] kubectl packages push --version x.x.x # generate package from-descriptor | kubectl apply
- [ ] kubectl packages push foo-bar.helm.1.6.0.yaml --namespaces apps


#
kubectl packages list-repositories
- local
- quay.io

```
kubectl apply -f new-repo.yaml
spec:
 - endpoint: https://quay.io
   creds:
       basic:
         - username: robot1
           password: token
       secret:
         name: secret
   namespace: '*'
 ---
 spec: endpoint: https://quay.io

   creds:
       basic:
         - username: robot1
           password: token
       secret:
         name: secret2
   namespace: 'ant31'
```

kubectl packages pull quay.io/ns/name

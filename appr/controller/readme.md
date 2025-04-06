# Offline Descriptor -> Online PackageRelease

- [ ] kubectl packages init-crd  # create crds
- [x] kubectl packages get  # appr list
- [x] kubectl packages get xxxx -> appr list --search xxxx
- [x] kubectl packages get -l mediaType=helm xxx -> appr list -t helm
- [x] kubectl packages describe xxxx -> appr show xxxx

- [x] kubectl packages generate package --from-descriptor descriptor.yaml --version=x.x.x  # this update descriptor too
- [x] kubectl packages generate descriptor  --name xxx --version=x.x.x --media-type helm   # push

- [ ] kubectl packages generate descriptor  --name xxx --version=x.x.x --media-type helm   # Generate all fields + documentation as comment
- [ ] kubectl packages generate descriptor  --from-file Chart.yaml   #  detect a Chart.yaml and generate all fields

- [x] kubectl packages extract --from-file foo-bar.helm.1.6.0.yaml # pull
- [x] kubectl packages extract --namespace apps foo-bar.helm.1.6.0   # fetch from the server  # pull
- [x] kubectl packages inspect --from-file foo-bar.helm.1.6.0.yaml # view files
- [x] kubectl packages inspect --namespace apps foo-bar.helm.1.6.0   # view files
- [x] kubectl apply foo-bar.helm.1.6.0.yaml --namespace apps

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

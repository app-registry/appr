## 0.7.0 Released on 2017-07-24

- Introduce client-side deployments handling multiple formats:
  - [ ] [Helm](https://github.com/kubernetes/helm)
  - [x] [appr](https://github.com/coreos/kpm)
  - [ ] Plain kubernetes configuration

- Add jsonnet support for future integration with [ksonnet](https://github.com/ksonnet/ksonnet-lib)

- New commands:

``` shell
# Resolve a jsonnet file, with a set of nativeExtension available
appr jsonnet FILE

# Client side deployment command
appr deploy quay.io/ant31/kube-lego --namespace kube-lego
```

## 0.6.2 Released on 2017-07-10

- Add options to allow unverified certs or custom CA.
```shell
    -k, --insecure        turn off verification of the https certificate
    --cacert [CACERT]     CA certificate to verify peer against (SSL)
```

## 0.4.1 Released on 2017-05-30

- Fixes [issues-23](https://github.com/app-registry/helm-plugin/issues/23)


## 0.4.0 Released on 2017-05-24

- Integration with Helm's dependency file `requirements.yaml`
  command: `helm dep`
- Allow push to any repository name,
  it can be different from the application manifest
  command: `push quay.io/ns/repo-name`
- Display server-error messages


## 0.3.8 Released on 2017-03-28

- Upgrade appr-cli to 0.3.8
- No more registry-host default (localhost:5000)
- Pull command default to 'extract', use `--tarball` to keep the `tar.gz`

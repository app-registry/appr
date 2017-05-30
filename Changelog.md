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

# CNR Command Line Tool

## Install the Helm Registry Plugin

First, Install the latest [Helm release](https://github.com/kubernetes/helm#install).

Next download and install the registry plugin for Helm.

### OSX

```
wget https://github.com/cn-app-registry/cnr-cli/releases/download/v0.3.7-dev/registry-cnr-v0.3.7-dev-osx-x64-helm-plugin.tar.gz
mkdir -p ~/.helm/plugins/
tar xzvf registry-cnr-v0.3.7-dev-osx-x64-helm-plugin.tar.gz  -C ~/.helm/plugins/
```

### Linux

```
wget https://github.com/cn-app-registry/cnr-cli/releases/download/v0.3.7-dev/registry-cnr-v0.3.7-dev-linux-x64-helm-plugin.tar.gz
mkdir -p ~/.helm/plugins/
tar xzvf registry-cnr-v0.3.7-dev-linux-x64-helm-plugin.tar.gz  -C ~/.helm/plugins/
```

## Deploy Jenkins Using Helm from the Quay Registry

Confirm that the Helm registry plugin is working.

```
helm registry version app.quay.io
```

### Creat an alias  (temporary step)

```
helm registry config alias app.quay.io app.quay.io/cnr
```

### Install Jenkins

```
helm init
helm registry list app.quay.io
helm registry install app.quay.io/helm/jenkins
```

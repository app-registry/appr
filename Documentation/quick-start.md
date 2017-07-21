# Appr Command Line Tool
`appr` is the CLI to interact with an app-registry server.
It can be used directly or via the [helm plugin](https://github.com/app-registry/helm-plugin).

note:
The helm plugin `helm registry ...` is calling the `appr`, all commands are equivalents.

## Pull / Download / Install
Pull and install commands have 3 ways to reference a package:

1. By channel:
```
appr pull quay.io/ant31/jenkins:stable -t helm
```

2. By release:
```
appr pull quay.io/ant31/jenkins@0.4.0 -t helm
```

3. By digest:

```
appr registry pull quay.io/ant31/jenkins@sha256:9cdfdcf4bdcf659a576a10f4c18c34fb0543debd695846a971644fedfcc98aee -t helm`
```

## Browse and search packages
To browse a repository The `list` command can be used

```shell
# appr list [REGISTRY]
$ appr list quay.io
quay.io/ant31/rabbitmq     0.0.1      -            docker-compose
quay.io/ant31/mysql        0.1.1      -            helm
quay.io/ant31/jenkins      0.4.1      -            helm
```

### Search
There is multiple search available that can be combined

#### by text
`--search TEXT`, returns only matching apps name
```shell
$ appr list quay.io --search jenkins
app                                release    downloads    manifests
---------------------------------  ---------  -----------  -----------
quay.io/charts/jenkins             0.3.0      -            helm
quay.io/adaptly/jenkins-configmap  0.1.1      -            helm
quay.io/adaptly/jenkins            0.5.2      -            helm
quay.io/praveenr/jenkins-se-demo   0.3.0      -            helm
```

#### by namespace
`--organization NAMESPACE` returns all application under the NAMESPACE
```shell
$ appr list -o ant31 quay.io
app                      release       downloads    manifests
-----------------------  ------------  -----------  -----------
quay.io/ant31/ghost      0.4.6-1       -            helm
quay.io/ant31/cookieapp  0.13.10       -            helm
quay.io/ant31/etcd       0.2.0         -            helm
quay.io/ant31/cookie     0.13.10       -            helm
quay.io/ant31/kube-lego  0.1.5-1       -            kpm
quay.io/ant31/nginx      0.9.0-beta.3  -            kpm

```
### Filter by Media-type
`--media-type` option

```shell
$ appr list quay.io --media-type helm
ant31/mysql        0.1.1      -            helm
ant31/jenkins      0.4.1      -            helm
helm/jenkins       0.3.9      -            helm

$ appr list quay.io --media-type docker-compose
ant31/rabbitmq     0.0.1      -            docker-compose
```

## Releases and channels

### Release
A 'release' is an immutable version of an application, it can be view as an alias to a package digest.
A release name is following the [semver2 format](http://semver.org/).
This immutable constraint is essential to safely pin a particular version

To reference a release, the `@` symbol is used:

```
$ appr pull quay.io/ant31/mysql@0.1.1 -t helm
```

#### List releases
The `show` command lists all available releases

```shell
$ appr show quay.io/ant31/jenkins
Info: ant31/jenkins

release    manifest    digest
---------  ----------  ----------------------------------------------------------------
0.4.1      helm        9cdfdcf4bdcf659a576a10f4c18c34fb0543debd695846a971644fedfcc98aee
0.4.0      helm        a542b37cbd2d719f1851374f34924ebc1f146e7575cb092d62db28fa3a40d2fb

```

#### Channel
Mutable tags are named channels.

A channel is a pointer to a version and the chart/package maintainer can move that pointer.
On version can be referenced by multiple channels
```shell
stable -> 2.4.5
beta -> 2.5.0
stable-1 -> 1.4.3
latest -> 2.5.0
```

To pull/install from a channel, the `:` symbol is used:

```shell
$ appr pull quay.io/ant31/mysql:stable -t helm
```

#### List channels
The `channel` command can be used to manipulate and browse channels

```shell
$ appr channel quay.io/ant31/jenkins
channel    release
---------  ---------
unstable   0.4.1
stable     0.4.0
```

### Set a channel

```shell
$ appr push quay.io/ant31/jenkins --channel unstable
>>> Release '0.4.1' added to 'unstable'

# Or using channel command and the --set-release option

$ appr channel quay.io/ant31/jenkins@0.4.1 --set-release --channel unstable
>>> Release '0.4.1' added to 'unstable'

```

## Create and Push Your Own Chart/Package

First, create an account on https://quay.io and login to the CLI using the username and password

Set an environment for the username created at Quay to use through the rest of these instructions.

```
export USERNAME=ant31
```

Login to Quay with the Helm registry plugin:

```
$ appr registry login -u $USERNAME quay.io
```

Move inside the package directoy and push it to Quay

A helm-chart:
```
$ cd nginx-chart
$ helm registry push quay.io/ant31
package: ant31/jenkins (0.4.2 | helm) pushed
```

The cli try to read the package metadata to set the repo-name, it's possible to explicitly set it:

```shell
$ helm registry push quay.io/ant31/jenkinks-custom-repo-name
package: ant31/jenkins-custom-repo-name (0.4.2 | helm) pushed
```

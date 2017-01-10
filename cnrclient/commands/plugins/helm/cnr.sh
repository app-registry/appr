#!/bin/bash

function pull {
    echo "pull $@"
    release=`cnr pull --media-type helm --tarball ${@}"|tail -n1`
    echo $release
}

function install {
    $(pull $@)
    helm install $release
}

function cnr_helm {
    cnr $@ --media-type=helm
}


case "$1" in
    install)
        install "${@:2}"
        ;;
    pull)
        pull "${@:2}"
        ;;
    push)
        cnr_helm "$@"
        ;;
    list)
         cnr_helm "$@"
        ;;
    show)
        cnr_helm "$@"
        ;;
    delete-package)
        cnr_helm "$@"
        ;;
    inspect)
        cnr_helm "$@"
        ;;
    *)
        cnr $@
        ;;

esac

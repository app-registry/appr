#!/bin/bash

function update_appr {
    echo "wip: install/update appr-cli"
    if [ -e $HELM_PLUGIN_DIR/appr ] ; then
        chmod +x $HELM_PLUGIN_DIR/appr
    fi

}

function pull {
    #echo "pull $@"
    release=`$HELM_PLUGIN_DIR/appr pull --media-type helm --tarball ${@} |tail -n1`
    echo $release
}

function install {
    pull $@ --dest=/tmp
    sleep 1
    helm install $release
}

function appr_helm {
    $HELM_PLUGIN_DIR/appr $@ --media-type=helm
}


case "$1" in
    init-plugin)
        update_appr
        ;;
    install)
        install "${@:2}"
        ;;
    pull)
        pull "${@:2}"
        ;;
    push)
        appr_helm "$@"
        ;;
    list)
        appr_helm "$@"
        ;;
    show)
        appr_helm "$@"
        ;;
    delete-package)
        appr_helm "$@"
        ;;
    inspect)
        appr_helm "$@"
        ;;
    *)
        $HELM_PLUGIN_DIR/appr $@
        ;;

esac

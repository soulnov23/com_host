#!/bin/bash

username=admin
password=sangfor123

function install()
{
    if [ -z "$1" ];then
        echo "error:ip is null"
        exit 1
    fi
    if [ -z "$2" ];then
        echo "error:certs is null"
        exit 1
    fi
    local ip=$1
    local crt=$2
    grep sdwan.io /etc/hosts
    if [ $? -eq 0 ];then
        cp -f /etc/hosts /etc/hosts.temp
        sed -i '/sdwan.io/d' /etc/hosts.temp
        sed -i '$a'${ip}' sdwan.io' /etc/hosts.temp
        cp -f /etc/hosts.temp /etc/hosts
    else
        cp -f /etc/hosts /etc/hosts.temp
        sed -i '$a'${ip}' sdwan.io' /etc/hosts.temp
        cp -f /etc/hosts.temp /etc/hosts
    fi
    mkdir -p /etc/docker/certs.d/sdwan.io:5000
    cp -f ${crt} /etc/docker/certs.d/sdwan.io:5000
    docker login -u ${username} -p ${password} sdwan.io:5000
}

function show()
{
    local image_list=`curl -s --insecure --user ${username}:${password} https://sdwan.io:5000/v2/_catalog \
    | jq .repositories | sed -e 's/"//g;s/[/[]//g;s/]//g;s/,//g'`
    printf "%-30s %-30s\n" REPOSITORY TAG
    for image_name in ${image_list}
    do
        local image_info=`curl -s --insecure --user ${username}:${password} https://sdwan.io:5000/v2/${image_name}/tags/list`
        local tag_list=`echo ${image_info} | jq .tags | sed -e 's/"//g;s/,//g;s/[/[]//g;s/]//g;'`
        for image_tag in ${tag_list}
        do
            if [ null != ${image_tag} ];then
                local name=`echo ${image_info} | jq .name | sed -e 's/"//g'`
                printf "%-30s %-30s\n" ${name} ${image_tag}
            fi
        done
    done
}

#function search()
#{
#   if [ -z "$1" ];then
#       echo "error:image_name is null"
#       exit 1
#   fi
#   if [ -z "$2" ];then
#       echo "error:image_tag is null"
#       exit 1
#   fi
#   image_name=$1
#   image_tag=$2
#   curl --insecure --user ${username}:${password} https://sdwan.io:5000/v2/${image_name}/manifests/${image_tag}
#}

function search_image()
{
    if [ -z "$1" ];then
        echo "error:image_name is null"
        exit 1
    fi
    local image_name=$1
    curl -s --insecure --user ${username}:${password} https://sdwan.io:5000/v2/${image_name}/tags/list
}

function delete()
{
    if [ -z "$1" ];then
        echo "error:image_name is null"
        exit 1
    fi
    if [ -z "$2" ];then
        echo "error:image_tag is null"
        exit 1
    fi
    local image_name=$1
    local image_tag=$2
    sha256=`curl -s --header "Accept: application/vnd.docker.distribution.manifest.v2+json" -I -X HEAD \
    --insecure --user ${username}:${password} https://sdwan.io:5000/v2/"${image_name}"/manifests/"${image_tag}" \
    | grep Docker-Content-Digest | awk -F : '{gsub("\r","");print $3}'`
    ret=`curl -s --insecure --user ${username}:${password} -X DELETE https://sdwan.io:5000/v2/${image_name}/manifests/sha256:${sha256}`
    if [ "${ret}"x = "404 page not found"x ];then
        echo $ret
    else
        echo "delete ${image_name}:${image_tag} success"
    fi
}

function help()
{
    echo ""
    echo "Usage:    sh sdregistry_util.sh [OPTIONS] NAME[IMAGE_NAME|IMAGE_TAG]"
    echo ""
    echo "私有仓库客户端工具脚本"
    echo ""
    echo "Options:"
    echo "-install   安装私有仓库客户端，参数1为私有仓库ip，参数2为registry.crt证书的绝对路径，
            一般需要去私有仓库目录/wns/data/docker_register/certs下拷贝registry.crt到当前主机目录"
    echo "-show      显示私有仓库可用的镜像信息，没有参数"
    echo "-delete    删除私有仓库中的镜像，参数1为镜像名字，参数2为镜像tag"
    echo "--help     Print Usage"
}

case $1 in
install)
    install $2 $3
    ;;
show)
    show
    ;;
#search)
#   search $2 $3
#   ;;
search_image)
    search_image $2
    ;;
delete)
    delete $2 $3
    ;;
--help)
    help
    ;;
*)
    echo "error:argument is null"
    ;;
esac

#!/bin/bash

function set_ip()
{
    if [ -z "$1" ];then
        echo "error:ip is null"
        exit 1
    fi
    if [ -z "$2" ];then
        echo "error:netmask is null"
        exit 1
    fi
    if [ -z "$3" ];then
        echo "error:route is null"
        exit 1
    fi
    local ip=$1
    local netmask=$2
    local route=$3
    #配置eth0给资源使用
    ifconfig eth0 up
    ifconfig eth0 ${ip} netmask ${netmask}
    route add default gw ${route}
    #配置eth1挂到br0下，给容器使用
    ifconfig eth1 up
    brctl addbr br0
    ip link set br0 up
    brctl addif br0 eth1
}

function set_dns()
{
    if [ -z "$1" ];then
        echo "error:dns is null"
        exit 1
    fi
    local dns=$1
    cp -f /etc/resolv.conf /etc/resolv.conf.temp
    sed -i '/nameserver/d' /etc/resolv.conf.temp
    sed -i '$anameserver '${dns}'' /etc/resolv.conf.temp
    cp -f /etc/resolv.conf.temp /etc/resolv.conf
}

function update()
{
    if [ -z "$1" ];then
        echo "error:image is null"
        exit 1
    fi
    local image=$1
    docker pull ${image}
    cp -f /wns/version /wns/version.temp
    sed -i '/com_host=sdwan.io:5000/d' /wns/version.temp
    echo "com_host=${image}" >> /wns/version.temp
    cp -f /wns/version.temp /wns/version
    docker stop -t 10 com_host
}

function clean()
{
    docker system prune -a -f
}

case $1 in
set_ip)
    set_ip $2 $3 $4
    ;;
set_dns)
    set_dns $2
    ;;
update)
    update $2
    ;;
clean)
    clean
    ;;
*)
    echo "error:argument is null"
    ;;
esac

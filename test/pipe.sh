#查看网桥
brctl show
brctl addbr br0
ip link set br0 up
ip addr add 192.168.0.99/24 dev br0
ip addr del 192.168.0.99/24 dev eth0
brctl addif br0 eth0
ip route del default
ip route add default via 192.168.0.254 dev br0
pipework br0 test_pipework 192.168.0.12/24@10.51.0.254

#删除网桥
ip link set dev br0 down
brctl delbr br0

#查看网关
ip route show
route -n
netstat -rn

#增加网关
route add default gw 192.168.0.1
#删除网关
route del default gw 192.168.0.1
#增加路由
route add -net 192.168.10.0 netmask 255.255.255.0 dev eth0
#删除路由
route del -net 192.168.10.0 netmask 255.255.255.0 dev eth0
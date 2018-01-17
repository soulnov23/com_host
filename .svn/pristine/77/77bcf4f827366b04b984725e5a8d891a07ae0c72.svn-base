#!/bin/bash
do_rsync() {
    host_ip=$1
    host_port=$2
    username=$3
    password=$4
    dockername=$5
    /usr/bin/expect <<-EOF
    set timeout -1
    spawn rsync -e "ssh -p $host_port" -az /wns/data/$dockername/ $username@$host_ip:/wns/data/mt_data/$dockername
    expect {
             "(yes/no)?" { send "yes\r"; exp_continue }
             "Password:" { send "$password\r" }
    }
    interact
    expect eof
EOF
}

main() {
    do_rsync $1 $2 $3 $4 $5
}

main $@

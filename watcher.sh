#!/bin/bash

HOME=/home/pi/greenpi
SCRIPT_NAME=GreenPi.py

start () {
    cd $HOME
    if [ "$USER" != "root" ]; then
        echo "root is required. please type 'sudo -E !!'"
        exit 1
    fi
    python $SCRIPT_NAME > watcher.out 2> watcher.err &
    echo "$!" > watcher.pid
}

stop () {
    cd $HOME
    pid=`cat watcher.pid`
    sudo kill $pid
    sudo rm watcher.pid
}
        

case "$1" in
"start")
    start
    ;;
"stop")
    stop
    ;;
"restart")
    stop
    start
    ;;
*)
    help
    ;;
esac

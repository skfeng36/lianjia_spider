#!/bin/sh

NAME="lianjia_spider"
echo "kill Process name : $NAME"
ID=`ps -ef | grep "$NAME" | grep -v "$0" | grep -v "grep" | awk '{print $2}'`
echo $ID
for id in $ID
do
sudo kill -9 $id
echo "killed $id success!"
done
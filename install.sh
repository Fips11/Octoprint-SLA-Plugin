#!/bin/bash

if [ "$EUID" -ne 0 ]
  then echo "Please run as root"
  exit
fi

# /boot/config.txt

#if ! grep -q \'dtoverlay=dwc2\' /boot/config.txt ; then

#    echo "change /boot/config.txt"
 #   echo "dtoverlay=dwc2" >> /boot/config.txt
#fi

#/etc/modules

#if ! grep -q 'dwc2' /etc/modules ; then

#    echo "delete dwc2 in /etc/modules" ###falsch?
#    sed -i '/^dwc2/d' /etc/modules
#fi

#/etc/sudoers

#line="#includedir /etc/sudoers.d"
#
#if ! grep -q "${line}" /etc/sudoers ; then
#  sudo sed '$i'"${line}"'' /etc/sudoers | sudo EDITOR='tee -a' visudo
#fi


#add save control script to /usr/sbin/

echo "add flash script to /usr/sbin/"

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
cp "$DIR/flash" "/usr/sbin/"
chmod +x /usr/sbin/flash


echo "add flash to sudoers"

#add own file to /etc/sudoers.d 
if  grep  -q "$own_sudoers" /etc/sudoers.d/sla_plugin ; then
    echo "/etc/sudoers.d/sla_plugin already existing"
    exit 0    
fi

own_sudoers="pi ALL=NOPASSWD: /usr/sbin/flash * *"
echo "create File: /etc/sudoers.d/sla_plugin"
echo "$own_sudoers" | sudo EDITOR='tee -a' visudo -f /etc/sudoers.d/sla_plugin

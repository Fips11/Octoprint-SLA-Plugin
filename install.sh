if [ "$EUID" -ne 0 ]
  then echo "Please run as root"
  exit
fi

#/boot/config.txt

if ! grep -q 'dtoverlay=dwc2' /boot/config.txt ; then

    echo "change /boot/config.txt"
    echo "dtoverlay=dwc2" >> /boot/config.txt
fi

#/etc/modules

if ! grep -q 'dwc2' /etc/modules ; then

    echo "delete dwc2 in /etc/modules" ###falsch?
    sed -i '/^dwc2/d' /etc/modules
fi

#/etc/sudoers

#line="#includedir /etc/sudoers.d"

#if ! grep -q "${line}" /etc/sudoers ; then
#  sudo sed '$i'"${line}"'' /etc/sudoers | sudo EDITOR='tee -a' visudo
#fi


#add save control script to /usr/sbin/
echo "add script to /usr/sbin/"
new_script="

if ![ -d \"\$2\"  || \$2="" ]; then
  exit 0
fi

updateFStab(){   
  dictionary=\$1
  #Befehle...
}


addMod(){
  dictionary=\$1
}

checkMod(){
  #
}

case \"\$1\" in

  \"updateFStab\") updateFStab(\$2)
            ;;
            
  \"addMod\") updateFStab(\$2)
            ;;

  \"checkMod\") checkMod(\$2)
            ;;


            *) exit 0
            ;;
"

echo "$new_script" > /etc/sbin/control-flash-host

echo "add control-flash-host to sudoers"
#add own file to /etc/sudoers.d 
own_sudoers="pi ALL=NOPASSWD: /usr/sbin/control-flash-host * *"

echo "$own_sudoers" | sudo EDITOR='tee -a' visudo -f /etc/sudoers.d/sla_plugin
# RobotZed
Source code for outdoor robot Zed, that is modular robot designed to be
able to run on many robotic events that takes place in central Europe.

Running on Pine64 and powered by TeaPack & BrickHackers

Currently using Armbian 5.25

# How to setup your system on Pine64:
## Prepare image on Pine
*   Download newest release from https://www.armbian.com/pine64/
*   Extract it to some folder
*   Burn image to some SD card (min 8GB recomended) with https://etcher.io/
*   Unplug and Plug uSD card to your PC and edit file /boot/armbianEnv.txt
    - change line:
        - "pine64_lcd=off" to "pine64_lcd=on"
    - add lines:
        - gmac-tx-delay=3
        - gmac-rx-delay=0
* Also add line to /etc/modules
    - gt9xxf_ts
*   remove uSD from you PC and plug it into Pine

Make sure, that during first boot of pine, there is no aditional device 
connected to it - even the LiPo battery, it prevent Pine from booting
*from version 5.30 and above, powering Pine with LiPo battery prevent booting everytime

## First boot on Pine64
Log in with provided username/password (root/1234)

First of all, you are asked to change root password and than you can make
your own user profile (sudo enabled) than you can directly setup your
 locals and timeZone data:
*   dpkg-reconfigure tzdata
*   dpkg-reconfigure locales

Update cache to install new packages:
*    sudo apt update

Install required packages:
*    sudo apt install git python-zmq python-serial python-numpy

You can also install some usefull packages:
*    sudo apt install terminator htop nmap gitk git-gui rsync

Add your user to group DIALOUT to acces serial ports
*   sudo usermod -a -g dialout $USER

Clone this repository to your Pine:
*   git clone https://github.com/TeaPackCZ/RobotZed.git


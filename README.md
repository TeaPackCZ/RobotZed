# RobotZed
Source code for outdoor robot Zed, that is modular robot designed to be
able to run on many robotic events that takes place in central Europe.

Running on Pine64 and powered by TeaPack & BrickHackers

# How to setup your system on Pine64:
## Prepare image on Pine
*   Download newest release from https://github.com/ayufan-pine64/linux-build/releases
*   Extract it to some folder
*   Burn image to some SD card (min 8GB recomended) with https://etcher.io/
*   Unplug and Plug uSD card to your PC and at partition /boot in file ### uncoment line xxxx to enable LCD
*   remove uSD from you PC and plug it into Pine

## First boot on Pine64
Log in with provided username/password (pine64/pine64)

Setup your locals and timeZone data:
*   sudo dpkg-reconfigure tzdata
*   sudo dpkg-reconfigure locales

Update cache to install new packages:
*    sudo apt update

Install required packages:
*    sudo apt install git python-zmq python-serial python-numpy

You can also install some usefull packages:
*    sudo apt install terminator htop nmap gitk git-gui

Add your user to group DIALOUT to acces serial ports
*   sudo usermod -a -g dialout $USER

Clone this repository to your Pine:
*   git clone https://github.com/TeaPackCZ/RobotZed.git


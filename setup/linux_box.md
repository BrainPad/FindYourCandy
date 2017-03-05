Linux Setup
===

## OS installation
- Ubuntu 16.04.1 LTS Server   
- Choose “standard system utilities” and “OpenSSH server” as software selection
- Create user:  brainpad (group is also brainpad by default)

## Basic setup
```
$ sudo apt-get update && sudo apt-get upgrade -y && sudo reboot
$ sudo apt-get install ubuntu-desktop
$ sudo apt-get install -y vim git build-essential
$ sudo apt-get install python-dev
$ sudo apt-get install nginx
```
You should also install `gsutil` along with [this instuction](https://cloud.google.com/sdk/docs/quickstart-linux).

## pip installation
```
$ wget https://bootstrap.pypa.io/get-pip.py
$ sudo python get-pip.py
$ sudo pip install numpy==1.12.0
```

## OpenCV3.2 installation
```
$ sudo apt-get install cmake git libgtk2.0-dev pkg-config libavcodec-dev libavformat-dev libswscale-dev
$ sudo apt-get install libtbb2 libtbb-dev libjpeg-dev libpng-dev libtiff-dev libgtk2.0-dev
$ mkdir ~/opencv_from_git
$ cd ~/opencv_from_git
$ git clone https://github.com/opencv/opencv.git
$ git clone https://github.com/opencv/opencv_contrib.git
$ git clone https://github.com/opencv/opencv_extra.git
$ cd ~/opencv_from_git/opencv/
$ mkdir build
$ cd build
$ cmake -D CMAKE_BUILD_TYPE=Release -D CMAKE_INSTALL_PREFIX=/usr/local -D OPENCV_EXTRA_MODULES_PATH=../../opencv_contrib/modules/ -D BUILD_DOCS=ON -D WITH_TBB=ON ..
$ make -j7
$ sudo make install
```

## Permisions
```
$ sudo chmod 777 /dev/ttyUSB0
  (* You may have the robot at /dev/ttyUSB1 instead of /dev/ttyUSB0, depending on your hardware. ;-)
$ sudo chmod 777 /dev/video0
  (* If you have two or more web cameras, it may be /dev/video1 or else. )
```
Note: After you re-plugin usb or reboot the system, you need to repeat the above steps.

## Install app
```
$ cd ~
$ git clone git@github.com:BrainPad/FindYourCandy.git
$ cd ~/FindYourCandy
$ sudo pip install -r robot-arm/requirements.txt
$ sudo pip install -r webapp/requirements.txt
```

## Nginx setup
This is not mandatory, but this setup senario is based on nginx.
If you don't install, you have to figure out how to setup by yourself.
```
$ sudo cp ./setup/nginx_config_example/webapp.conf /etc/nginx/conf.d/
$ sudo cp ./setup/nginx_config_example/robot.conf /etc/nginx/conf.d/

$ sudo mkdir /etc/uwsgi
$ sudo cp webapp.ini /etc/uwsgi/
  (* You must edit webapp.ini and change the entry of GOOGLE_APPLICATION_CREDENTIALS later, after you create your credentials in following steps.)
$ sudo cp robot.ini /etc/uwsgi/
  (* You need to modify robot.ini according to your environment.)

$ sudo mkdir -m 775 /var/run/uwsgi
$ sudo chown brainpad:brainpad /var/run/uwsgi
$ sudo mkdir -m 775 /var/log/uwsgi
$ sudo chown brainpad:brainpad /var/log/uwsgi

$ sudo cp uwsgi-webapp.service /etc/systemd/system/
$ sudo cp uwsgi-robot.service /etc/systemd/system/
```

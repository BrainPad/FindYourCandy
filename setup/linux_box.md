Linux Setup
===

## OS installation
- Ubuntu 16.04.1 LTS Server   
- Choose “standard system utilities” and “OpenSSH server” as software selection
- Create user:  brainpad (group is also brainpad by default)

## Base setup
```
$ sudo apt-get update && sudo apt-get upgrade -y && sudo reboot
$ sudo apt-get install ubuntu-desktop
$ sudo apt-get install -y vim git build-essential
$ sudo apt-get install python-dev
```

## pip installation
```
$ wget https://bootstrap.pypa.io/get-pip.py
$ sudo python get-pip.py
$ sudo pip install numpy
$ sudo pip install tensorflow
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
$ cmake -D CMAKE_BUILD_TYPE=Release -D CMAKE_INSTALL_PREFIX=/usr/local -D OPENCV_EXTRA_MODULES_PATH=../../opencv_contrib/modules/ -D BUILD_DOCS=ON -D WITH_TBB=ON ..
$ make -j7
$ sudo make install
```

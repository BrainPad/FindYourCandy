FROM brainpad/fyc-base:latest

RUN set -ex \
  && apt-get update && apt-get install -y \
    build-essential \
    cmake \
    libavcodec-dev \
    libavformat-dev \
    libdc1394-22-dev \
    libcanberra-gtk-module \
    libgtk2.0-dev \
    libjasper-dev \
    libjpeg-dev \
    libpng-dev \
    libswscale-dev \
    libtbb2 \
    libtbb-dev \
    libtiff-dev \
    pkg-config \
    unzip \
    wget \
  && pip install numpy==1.12.0 \
  && apt-get clean \
  && rm -rf /var/lib/apt/lists/* \
  && rm -rf ~/.cache/pip

WORKDIR /opt
RUN set -ex \
  && wget -q https://github.com/opencv/opencv/archive/3.2.0.zip -O opencv-3.2.0.zip \
  && wget -q https://github.com/opencv/opencv_contrib/archive/3.2.0.zip -O opencv_contrib-3.2.0.zip \
  && unzip -q opencv-3.2.0.zip \
  && unzip -q opencv_contrib-3.2.0.zip \
  && mkdir opencv-3.2.0/build \
  && cd opencv-3.2.0/build \
  && cmake \
    -D CMAKE_BUILD_TYPE=Release \
    -D CMAKE_INSTALL_PREFIX=/usr/local \
    -D OPENCV_EXTRA_MODULES_PATH=/opt/opencv_contrib-3.2.0/modules \
    -D BUILD_DOCS=OFF \
    -D BUILD_EXAMPLES=OFF \
    -D BUILD_TESTS=OFF \
    -D BUILD_PERF_TESTS=OFF \
    -D BUILD_opencv_java=OFF \
    -D BUILD_opencv_python2=ON \
    -D WITH_TBB=ON \
    -D WITH_QT=OFF \
    -D WITH_CUDA=OFF \
    -D WITH_FFMPEG=OFF \
    .. \
  && make -j $(nproc) \
  && make install \
  && ldconfig \
  && cp lib/cv2.so /usr/local/lib/python2.7/dist-packages/ \
  && cd ../.. \
  && rm -f opencv-3.2.0.zip opencv_contrib-3.2.0.zip \
  && rm -rf opencv-3.2.0 opencv_contrib-3.2.0 \

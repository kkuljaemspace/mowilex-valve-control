FROM ubuntu:22.04

# Prevent interactive prompts
ENV DEBIAN_FRONTEND=noninteractive
ENV ANDROID_HOME=/opt/android-sdk
ENV ANDROID_SDK_ROOT=/opt/android-sdk
ENV PATH=$PATH:$ANDROID_HOME/tools:$ANDROID_HOME/platform-tools

# Install system dependencies
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    python3-dev \
    build-essential \
    git \
    libffi-dev \
    libssl-dev \
    openjdk-11-jdk \
    autoconf \
    libtool \
    pkg-config \
    zlib1g-dev \
    libncurses5-dev \
    libncursesw5-dev \
    cmake \
    ccache \
    wget \
    unzip \
    && rm -rf /var/lib/apt/lists/*

# Install buildozer and cython
RUN pip3 install --upgrade pip && \
    pip3 install buildozer cython

# Set working directory
WORKDIR /app

# Copy project files
COPY . /app/

# Install Python requirements
RUN pip3 install -r requirements.txt || true

# Prepare project
RUN python3 manage.py collectstatic --noinput || true

# Build APK
CMD ["buildozer", "android", "debug"]

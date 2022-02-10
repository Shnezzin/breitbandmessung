FROM jlesage/baseimage-gui:ubuntu-18.04

ENV DEBIAN_FRONTEND noninteractive
ENV LANG=de_DE.UTF-8

#Install xterm 
RUN apt-get update && \
    apt-get install -y \
            curl jq \
            libasound2 \
            libatk-bridge2.0 \
            libatk1.0 \
            libcurl4 \
            libgbm-dev \
            libgtk-3-0 \
            libjpeg-dev \
            libjq1 \
            libnghttp2-14 \
            libnss3 \
            libonig4 \
            libpython2.7-minimal \
            librtmp1 \
            libxss1 \
            locales \
            nodejs \
            python-minimal \
            python2.7-minimal \
            python3 \
            python3-dev \
            python3-pip \
            python3-tk \
            scrot \
            wget \
            xterm \
            zlib1g-dev \
            && rm -rf /var/lib/apt/lists/*

#Install pyautogui, xlib and apprise
RUN pip3 install --no-cache-dir \
            apprise \
            croniter \
            pyautogui \
            python-xlib

#Install latest Version of Breitbandmessung deb
RUN wget https://download.breitbandmessung.de/bbm/Breitbandmessung-linux.deb && dpkg -i Breitbandmessung-linux.deb

#Generate the DE Locales
RUN locale-gen de_DE.UTF-8

# Create Favicon
RUN \
    APP_ICON_URL=https://breitbandmessung.de/images/breitbandmessung-logo.png && \
    APP_ICON_DESC='{"masterPicture":"/opt/novnc/images/icons/master_icon.png","iconsPath":"/images/icons/","design":{"ios":{"pictureAspect":"backgroundAndMargin","backgroundColor":"#ffffff","margin":"14%","assets":{"ios6AndPriorIcons":false,"ios7AndLaterIcons":false,"precomposedIcons":false,"declareOnlyDefaultIcon":true}},"desktopBrowser":{},"windows":{"pictureAspect":"noChange","backgroundColor":"#2d89ef","onConflict":"override","assets":{"windows80Ie10Tile":false,"windows10Ie11EdgeTiles":{"small":false,"medium":true,"big":false,"rectangle":false}}},"androidChrome":{"pictureAspect":"noChange","themeColor":"#ffffff","manifest":{"display":"standalone","orientation":"notSet","onConflict":"override","declared":true},"assets":{"legacyIcon":false,"lowResolutionIcons":false}},"safariPinnedTab":{"pictureAspect":"silhouette","themeColor":"#5bbad5"}},"settings":{"scalingAlgorithm":"Mitchell","errorOnImageTooSmall":false},"versioning":{"paramName":"v","paramValue":"ICON_VERSION"}}' && \
    install_app_icon.sh "$APP_ICON_URL" "$APP_ICON_DESC"

# Copy the start script
COPY startapp.sh /startapp.sh

#Copy the python script
COPY speedtest.py /opt/
COPY entrypoint.py /opt/

RUN mkdir /export

# Set Application name
ENV APP_NAME="Breitbandmessung"

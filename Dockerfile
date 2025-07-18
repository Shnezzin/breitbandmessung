FROM python:slim-bullseye

ENV RUSTUP_HOME=/usr/local/rustup \
    CARGO_HOME=/usr/local/cargo \
    PATH=/usr/local/cargo/bin:$PATH \
    RUST_VERSION=1.63.0

WORKDIR /usr/src/app

COPY speedtest.py config.shlib geckodriver.sh config.cfg.defaults ./
COPY geckodriver-*.tar.gz ./

COPY entrypoint.sh /usr/local/bin/docker-entrypoint.sh

# Install basic dependencies first
RUN set -eux; \
    apt-get update; \
    apt-get install --no-install-recommends -y \
        firefox-esr \
        tini \
        cron \
        gcc \
        ca-certificates \
        wget \
        curl \
        build-essential \
        libssl-dev \
        libffi-dev \
        python3-dev \
        pkg-config \
    ; \
    rm -rf /var/lib/apt/lists/*

# Install geckodriver
RUN chmod +x /usr/src/app/geckodriver.sh && \
    /bin/bash /usr/src/app/geckodriver.sh

# Install Rust
RUN set -eux; \
    dpkgArch="$(dpkg --print-architecture)"; \
    case "${dpkgArch##*-}" in \
        amd64) rustArch='x86_64-unknown-linux-gnu'; rustupSha256='3dc5ef50861ee18657f9db2eeb7392f9c2a6c95c90ab41e45ab4ca71476b4338' ;; \
        armhf) rustArch='armv7-unknown-linux-gnueabihf'; rustupSha256='67777ac3bc17277102f2ed73fd5f14c51f4ca5963adadf7f174adf4ebc38747b' ;; \
        arm64) rustArch='aarch64-unknown-linux-gnu'; rustupSha256='32a1532f7cef072a667bac53f1a5542c99666c4071af0c9549795bbdb2069ec1' ;; \
        i386) rustArch='i686-unknown-linux-gnu'; rustupSha256='e50d1deb99048bc5782a0200aa33e4eea70747d49dffdc9d06812fd22a372515' ;; \
        *) echo >&2 "unsupported architecture: ${dpkgArch}"; exit 1 ;; \
    esac; \
    url="https://static.rust-lang.org/rustup/archive/1.24.3/${rustArch}/rustup-init"; \
    wget "$url"; \
    echo "${rustupSha256} *rustup-init" | sha256sum -c -; \
    chmod +x rustup-init; \
    ./rustup-init -y --no-modify-path --profile minimal --default-toolchain $RUST_VERSION --default-host ${rustArch}; \
    rm rustup-init; \
    chmod -R a+w $RUSTUP_HOME $CARGO_HOME

# Update Rust and verify installation
RUN set -eux; \
    rustup --version; \
    cargo --version; \
    rustc --version

# Install updated libc6-dev if needed
RUN set -eux; \
    printf "deb http://ftp.debian.org/debian experimental main\ndeb http://ftp.debian.org/debian sid main" > /etc/apt/sources.list.d/experimental.list; \
    apt-get update; \
    apt-get install --no-install-recommends -t experimental -y libc6-dev || true; \
    rm -rf /var/lib/apt/lists/*

# Clean up and prepare Python environment
RUN set -eux; \
    apt-get update; \
    apt-get remove -y --auto-remove wget curl || true; \
    rm -rf /var/lib/apt/lists/*; \
    pip3 install --upgrade pip; \
    pip3 install --no-cache-dir --upgrade setuptools; \
    chmod +x /usr/src/app/speedtest.py; \
    mkdir -p /export; \
    chmod +x /usr/local/bin/docker-entrypoint.sh

RUN --mount=type=tmpfs,target=/usr/local/cargo pip3 install --no-cache-dir \
    cryptography; \
    pip3 install --no-cache-dir \
    selenium \
    apprise \
    psutil \
    influxdb_client \
    influxdb \
    prometheus_client;

ENTRYPOINT ["tini", "--", "docker-entrypoint.sh"]

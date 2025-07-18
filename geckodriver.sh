#!/bin/sh
os=$(uname -s)
arch=$(uname -m)

echo $os
echo $arch

# Function to get latest geckodriver version from GitHub API
get_latest_version() {
    echo "Fetching latest geckodriver version..."
    latest_version=$(curl -s https://api.github.com/repos/mozilla/geckodriver/releases/latest | grep '"tag_name":' | sed -E 's/.*"([^"]+)".*/\1/')
    if [ -z "$latest_version" ]; then
        echo "Warning: Could not fetch latest version, using fallback v0.36.0"
        latest_version="v0.36.0"
    fi
    echo "Latest version: $latest_version"
    echo "$latest_version"
}

# Try to use local files first
local_file=""
if [ $os = "Linux" ] ; then
    case "$arch" in
        i386 | i486 | i786 | x86)
            local_file="geckodriver-v0.30.0-linuxarm32.tar.gz"
            platform="linux32"
            ;;        
        x86_64 | x86-64 | x64 | amd64)
            platform="linux64"
            ;;
        aarch64)
            local_file="geckodriver-v0.31.0-linux-aarch64 .tar.gz"
            platform="linux-aarch64"
            ;;
        xscale | arm | armv61 | armv71 | armv81 | armv7l )
            local_file="geckodriver-v0.31.0-linuxarm32.tar.gz"
            platform="linux32"
            ;;
        *)
            echo Architecture not supported: $arch
            exit 1
            ;;
    esac
elif [ $os = "Darwin" ] ; then
    platform="macos"
fi

if [ -z "$platform" ] ; then
    echo OS not supported: $os
    exit 1
fi

# Try local file first
if [ -n "$local_file" ] && [ -f "/usr/src/app/$local_file" ]; then
    echo "Using local geckodriver file: $local_file"
    tar -xzf "/usr/src/app/$local_file"
else
    # Get latest version and construct download URL
    latest_version=$(get_latest_version)
    url="https://github.com/mozilla/geckodriver/releases/download/${latest_version}/geckodriver-${latest_version}-${platform}.tar.gz"
    
    echo "Downloading geckodriver from: $url"
    
    # Try to download with curl
    if ! curl -s -L "$url" | tar -xz; then
        echo "Download failed, trying alternative approach..."
        # Fallback: download to file first, then extract
        if curl -s -L -o geckodriver.tar.gz "$url"; then
            tar -xzf geckodriver.tar.gz
            rm geckodriver.tar.gz
        else
            echo "Error: Failed to download geckodriver"
            exit 1
        fi
    fi
fi

if [ ! -f "geckodriver" ]; then
    echo "Error: geckodriver binary not found after extraction"
    exit 1
fi

chmod +x geckodriver
mv geckodriver /usr/bin
echo "Geckodriver installed successfully"
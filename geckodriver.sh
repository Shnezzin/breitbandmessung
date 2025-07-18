#!/bin/sh
os=$(uname -s)
arch=$(uname -m)

echo "OS: $os"
echo "Architecture: $arch"

# Function to get latest geckodriver version from GitHub API
get_latest_version() {
    echo "Fetching latest geckodriver version..." >&2
    latest_version=$(curl -s https://api.github.com/repos/mozilla/geckodriver/releases/latest | grep '"tag_name":' | sed -E 's/.*"([^"]+)".*/\1/')
    if [ -z "$latest_version" ]; then
        echo "Warning: Could not fetch latest version, using fallback v0.36.0" >&2
        latest_version="v0.36.0"
    fi
    echo "Latest version found: $latest_version" >&2
    echo "$latest_version"
}

# Try to use local files first
local_file=""
if [ "$os" = "Linux" ] ; then
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
            echo "Architecture not supported: $arch" >&2
            exit 1
            ;;
    esac
elif [ "$os" = "Darwin" ] ; then
    platform="macos"
fi

if [ -z "$platform" ] ; then
    echo "OS not supported: $os" >&2
    exit 1
fi

echo "Platform: $platform"

# Try local file first
if [ -n "$local_file" ] && [ -f "/usr/src/app/$local_file" ]; then
    echo "Using local geckodriver file: $local_file"
    if tar -xzf "/usr/src/app/$local_file"; then
        echo "Local file extracted successfully"
    else
        echo "Failed to extract local file, trying download..." >&2
        local_file=""
    fi
fi

# If no local file or local file failed, download
if [ -z "$local_file" ] || [ ! -f "geckodriver" ]; then
    # Get latest version and construct download URL
    latest_version=$(get_latest_version)
    
    # Clean up any potential whitespace or newlines
    latest_version=$(echo "$latest_version" | tr -d '\n\r ')
    
    url="https://github.com/mozilla/geckodriver/releases/download/${latest_version}/geckodriver-${latest_version}-${platform}.tar.gz"
    
    echo "Download URL: $url"
    
    echo "Downloading geckodriver..."
    if curl -s -L -f -o geckodriver.tar.gz "$url"; then
        echo "Download successful, extracting..."
        if tar -xzf geckodriver.tar.gz; then
            echo "Extraction successful"
            rm geckodriver.tar.gz
        else
            echo "Error: Failed to extract downloaded file" >&2
            rm -f geckodriver.tar.gz
            exit 1
        fi
    else
        echo "Error: Failed to download geckodriver from $url" >&2
        exit 1
    fi
fi

# Verify geckodriver binary exists
if [ ! -f "geckodriver" ]; then
    echo "Error: geckodriver binary not found after extraction" >&2
    exit 1
fi

# Install geckodriver
chmod +x geckodriver
mv geckodriver /usr/bin/geckodriver

# Verify installation
if [ -f "/usr/bin/geckodriver" ]; then
    echo "Geckodriver installed successfully to /usr/bin/geckodriver"
    /usr/bin/geckodriver --version
else
    echo "Error: Failed to install geckodriver" >&2
    exit 1
fi
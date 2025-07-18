#!/bin/sh
os=$(uname -s)
arch=$(uname -m)

echo "OS: $os"
echo "Architecture: $arch"

# Function to get latest geckodriver version from GitHub API
get_latest_version() {
    echo "Fetching latest geckodriver version..." >&2
    json_response=$(curl -s https://api.github.com/repos/mozilla/geckodriver/releases/latest)
    latest_version=""
    
    # Method 1: Using grep and cut
    latest_version=$(echo "$json_response" | grep '"tag_name":' | head -n1 | cut -d'"' -f4)
    
    # Method 2: Using sed (fallback)
    if [ -z "$latest_version" ]; then
        latest_version=$(echo "$json_response" | sed -n 's/.*"tag_name": *"\([^"]*\)".*/\1/p' | head -n1)
    fi
    
    # Method 3: Using awk (another fallback)
    if [ -z "$latest_version" ]; then
        latest_version=$(echo "$json_response" | awk -F'"' '/"tag_name":/ {print $4; exit}')
    fi
    
    if [ -z "$latest_version" ] || ! echo "$latest_version" | grep -q '^v[0-9]'; then
        echo "Warning: Could not fetch valid version, using fallback v0.36.0" >&2
        latest_version="v0.36.0"
    fi
    
    echo "Latest version found: $latest_version" >&2
    echo "$latest_version"
}

# Determine platform based on OS and architecture
if [ "$os" = "Linux" ] ; then
    case "$arch" in
        i386 | i486 | i786 | x86)
            platform="linux32"
            ;;        
        x86_64 | x86-64 | x64 | amd64)
            platform="linux64"
            ;;
        aarch64)
            platform="linux-aarch64"
            ;;
        xscale | arm | armv61 | armv71 | armv81 | armv7l )
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

# Get latest version and construct download URL
latest_version=$(get_latest_version)

# Clean up any potential whitespace or newlines
latest_version=$(echo "$latest_version" | tr -d '\n\r ')

url="https://github.com/mozilla/geckodriver/releases/download/${latest_version}/geckodriver-${latest_version}-${platform}.tar.gz"

echo "Download URL: $url"

# Download and extract geckodriver
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
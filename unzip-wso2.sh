#! /bin/bash
#usage: unzip-wso2.sh <product name and version without wso2 part> <target unzip location>
ROOT_DIR="/home/kalpa/Resources/wso2"
PRODUCT="$1"
TARGET="$2"

unzip "$ROOT_DIR/wso2$PRODUCT.zip" -d "$TARGET"

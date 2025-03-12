#!/bin/bash

# Get the directory of this script
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Run the Python script using the absolute path
python "$SCRIPT_DIR/automake.py" "$SCRIPT_DIR/JavaSrc/MainFile.java"

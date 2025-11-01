#!/bin/bash
set -e

# Line 4: Run the application with module path
echo "🚀 Running Java Module System Example..."
echo

java --module-path com.example.core/bin:com.example.service/bin:com.example.app/bin \
    --module com.example.app/com.example.app.Main

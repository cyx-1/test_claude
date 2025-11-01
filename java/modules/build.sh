#!/bin/bash
set -e

echo "🔨 Building Java Module System Example..."
echo

# Line 6: Compile core module
echo "📦 Compiling com.example.core..."
javac -d com.example.core/bin \
    com.example.core/src/module-info.java \
    com.example.core/src/com/example/core/util/Logger.java \
    com.example.core/src/com/example/core/model/User.java \
    com.example.core/src/com/example/core/internal/Helper.java

# Line 15: Compile service module (requires core)
echo "📦 Compiling com.example.service..."
javac --module-path com.example.core/bin \
    -d com.example.service/bin \
    com.example.service/src/module-info.java \
    com.example.service/src/com/example/service/UserService.java

# Line 23: Compile app module (requires core and service)
echo "📦 Compiling com.example.app..."
javac --module-path com.example.core/bin:com.example.service/bin \
    -d com.example.app/bin \
    com.example.app/src/module-info.java \
    com.example.app/src/com/example/app/Main.java

echo
echo "✅ Build completed successfully!"

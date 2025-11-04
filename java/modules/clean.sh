#!/bin/bash

echo "🧹 Cleaning compiled files..."
rm -rf com.example.core/bin/*
rm -rf com.example.service/bin/*
rm -rf com.example.app/bin/*
echo "✅ Clean completed!"

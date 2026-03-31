#!/bin/zsh

# Build
docker build -t uml-now-mcp-server .

# Run
docker run -p 8000:8000 uml-now-mcp-server:latest 

#!/bin/bash
# Setup script to pull Llama3 model in Ollama container

echo "Waiting for Ollama service to be ready..."
sleep 5

echo "Pulling llama3 model..."
ollama pull llama3

echo "Llama3 model is ready!"
ollama list

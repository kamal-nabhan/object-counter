#!/bin/bash
# Generate .env file with the number of physical cores
echo "NUM_PHYSICAL_CORES=$(($(lscpu | grep "Core(s) per socket:" | awk '{print $4}') * $(lscpu | grep "Socket(s):" | awk '{print $2}')))" &> .env

# Start Docker Compose
sudo docker-compose up --build
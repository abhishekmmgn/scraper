#!/bin/bash

while true; do
    echo "Timestamp: $(date)"
    wc -l output.csv output-1.csv
    sleep 300  # Wait for 60 seconds before running again
done

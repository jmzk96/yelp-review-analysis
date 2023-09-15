#!/bin/bash

echo "Downloading weather data and station data"
wget "https://www1.ncdc.noaa.gov/pub/data/ghcn/daily/ghcnd_hcn.tar.gz"
wget "https://www1.ncdc.noaa.gov/pub/data/ghcn/daily/ghcnd-stations.txt"
echo "Unzipping weather data"
tar -xf ghcnd_hcn.tar.gz
echo "Deleting gz weather data"
rm ghcnd_hcn.tar.gz
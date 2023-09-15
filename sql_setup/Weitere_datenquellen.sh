#!/bin/bash
#update bash with curl and wget
apt-get update
apt-get -qq -y install curl
apt-get install wget

#Download Data from Homeland Infrastructure Foundation-Level Data https://hifld-geoplatform.opendata.arcgis.com/datasets/intermodal-passenger-connectivity-database-ipcd?page=10&selectedAttribute=point_id
echo "Downloading data now..."
wget -O ipcd.csv https://opendata.arcgis.com/datasets/a316a953272a4faf8ae74b426c88d543_0.csv?outSR=%7B%22latestWkid%22%3A3857%2C%22wkid%22%3A102100%7D
sleep 5

#Download Data from https://github.com/evangambit/JsonOfCounties/blob/master/counties.json
echo "Downloading data now..."
wget -O https://github.com/evangambit/JsonOfCounties/raw/master/counties.json

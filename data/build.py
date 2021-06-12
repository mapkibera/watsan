#!/usr/bin/python

import os
import logging
from utils import url2file
from images import cache_images
from data_manipulation import sync_osm, convert_geojson, merge_geojson

logging.basicConfig(level=logging.INFO)

locations = {
  'kibera' : {
    'bbox': '36.7716,-1.3199,36.8066,-1.3046'
  },
  'mathare' : {
    'bbox': '36.8389,-1.2680,36.8786,-1.2489'
  }
}
tag = '"amenity"="water_point"'
startdate = '2021-04-01T00:00:00Z'

sync_osm(locations, tag, startdate)
convert_geojson(locations)
merge_geojson(locations)
##Store images locally, and produce modified XML for upload with new image locations
cache_images(locations, "https://mapkibera.github.io/watsan/data/")

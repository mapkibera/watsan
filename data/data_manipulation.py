#!/usr/bin/python

import os
import csv
import geojson
import logging
from utils import readfile, writefile, url2file, centroid, midpoint

def sync_osm(locations, tag, startdate):
  logging.info("sync_osm start")

  for l in locations:

    url_base = "http://overpass-api.de/api/interpreter?data=[bbox];node[" + tag + "](newer:'" + startdate + "');out%20meta;&bbox="
    url2file(url_base + locations[l]['bbox'],"build/" + l + "-features-osm.xml")

  logging.info("sync_osm complete")

def convert_geojson(locations):
  logging.info("convert_geojson start")

  for l in locations:
    os.system("osmtogeojson -e build/" + l + "-features-osm.xml > build/" + l + "-features-osm.geojson")

  logging.info("convert_geojson complete")

def merge_geojson(locations):
  logging.info("merge_geojson start")

  result = {}
  result['type'] = 'FeatureCollection'
  result['features'] = []

  for l in locations:
    g = geojson.loads(readfile('build/' + l + '-features-osm.geojson'))
    for feature in g.features:
     result['features'].append( feature )

  dump = geojson.dumps(result, sort_keys=True, indent=2)
  writefile("site/features-osm.geojson",dump)

  logging.info("merge_geojson complete")


def build_centroid(infile, outfile):
  result = {}
  result['type'] = 'FeatureCollection'
  result['features'] = []

  g = geojson.loads(readfile(infile))

  for feature in g.features:
    if feature['geometry']['type'] == "Polygon":
        result['features'].append( { "type": "Feature", "id": feature["id"], "properties": feature.properties, "geometry": centroid(feature.geometry) })
    if feature['geometry']['type'] == "LineString":
        result['features'].append( { "type": "Feature", "id": feature["id"], "properties": feature.properties, "geometry": midpoint(feature.geometry) })

  dump = geojson.dumps(result, sort_keys=True, indent=2)
  writefile(outfile,dump)

def ways_only(infile, outfile):
  result = {}
  result['type'] = 'FeatureCollection'
  result['features'] = []

  g = geojson.loads(readfile(infile))

  for feature in g.features:
    if feature['geometry']['type'] != "Point":
        result['features'].append( feature )

  dump = geojson.dumps(result, sort_keys=True, indent=2)
  writefile(outfile,dump)

#!/usr/bin/python

import os
import string
import geojson
from PIL import Image
from utils import readfile, writefile, url2file

import xml.etree.ElementTree as ET


def slug_image(img_url):
  valid_chars = "%s%s" % (string.ascii_letters, string.digits)
  slug = ''.join(c for c in img_url if c in valid_chars)
  return slug

def get_cache_dir(osm_id,img_url):
  slug = slug_image(img_url)
  return "images/cache/" + osm_id + '/' + slug + '/'

def get_file_path(cache_dir, img_url, size):
  fileName, fileExtension = os.path.splitext(img_url)

  if not fileExtension:
    fileExtension = ".png"

  return cache_dir + size + fileExtension

def cache_image(osm_id, img_url, prefix):
  if osm_has_cache(img_url, prefix):
    return

  if os.path.exists('cookies.txt'):
    cookies = readfile('cookies.txt').rstrip()

  cache_dir = get_cache_dir(osm_id, img_url)
  if not os.path.exists(cache_dir):
    os.makedirs(cache_dir)

  file_path = get_file_path(cache_dir, img_url, 'orig')

  if not os.path.exists(file_path):
    url2file(img_url, file_path, cookies)

  if os.path.exists(file_path):
    try:
      im = Image.open(file_path)
    except IOError:
      print "IMAGE ERROR, can't open image, http://www.osm.org/" + osm_id + ", " + img_url
      return

    size = 1200, 900
    if not os.path.exists(get_file_path(cache_dir, img_url, 'large')):
      try:
        im.thumbnail(size)
        im.save(get_file_path(cache_dir, img_url, 'large'))
      except KeyError:
        print "IMAGE ERROR,unknown extension,http://www.osm.org/" + osm_id + ", " + img_url
        return

    size = 300, 225
    if not os.path.exists(get_file_path(cache_dir, img_url, 'med')):
      try:
        im.thumbnail(size)
        im.save(get_file_path(cache_dir, img_url, 'med'))
      except KeyError:
        print "IMAGE ERROR,unknown extension,http://www.osm.org/" + osm_id + ", " + img_url
        return

  else:
    print "IMAGE ERROR,orig missing,http://www.osm.org/" + osm_id + ", " + img_url

def get_image_cache(osm_id, img_url, cache_size, prefix):
  slug = slug_image(img_url)
  cache_path = prefix + osm_id + '/' + slug + '/'
  fileName, fileExtension = os.path.splitext(img_url)
  return cache_path + cache_size + fileExtension

def osm_has_cache(img_url, prefix):
  return img_url.find(prefix) == 0

def cache_images(locations,prefix):
  _cache_images(prefix)
  for l in locations:
    xml_with_cache(l, prefix)

def _cache_images(prefix):
  combined = geojson.loads(readfile("site/features-osm.geojson"))
  for index, feature in enumerate(combined.features):
    images = []
    large_images = []
    if "image" in feature['properties']:
      cache_image(feature['id'], feature['properties']['image'], prefix)

def xml_with_cache(location, prefix):
  tree = ET.parse('build/' + location + '-features-osm.xml')
  nodes = tree.findall('node')
  for node in nodes:
    tag = node.find('.//tag[@k="image"]')
    if tag != None:
      cache_dir = get_cache_dir("node/" + node.attrib['id'], tag.attrib['v'])
      file_path = get_file_path(cache_dir, tag.attrib['v'], 'orig')
      if os.path.exists(file_path):
        tag.attrib['v'] = prefix + file_path
        node.attrib['action'] = 'modify'


  writefile('build/' + location + '-features-osm-images.xml',ET.tostring(tree.getroot()))

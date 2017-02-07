#! /usr/bin/python3

import bottle
from   PIL      import Image
import tweepy
import tweepy.parsers
import yaml

import os
import sys
import tempfile
import shutil


pwd = os.path.dirname(os.path.abspath(__file__))
os.chdir(pwd)

conf = yaml.load(open(sys.argv[1] if len(sys.argv) > 1 else os.path.join(pwd, 'conf.yml')))

ah = tweepy.OAuthHandler(conf['consumer']['key'], conf['consumer']['secret'])
ah.set_access_token(conf['access_token']['key'], conf['access_token']['secret'])
api = tweepy.API(ah, parser = tweepy.parsers.JSONParser())

def jpeg_fitsize(org, size = 3000000, trial_limit = 5):
  res = tempfile.NamedTemporaryFile('rb+')
  org.seek(0)
  img = Image.open(org)
  n = 1
  for i in range(trial_limit + 1):
    tmp = tempfile.NamedTemporaryFile('rb+')
    img.resize((val * n // (2 ** i) for val in img.size)).save(tmp.name, 'jpeg', quality = 95)
    if tmp.tell() > size:
      n *= 2
      n -= 1
    else:
      print('write', n, 2 ** i)
      shutil.copy(tmp.name, res.name)
      if n == 2 ** 1:
        break
      n *= 2
      n += 1
  res.read()
  if res.tell() > size:
    raise Exception('もうだめ')
  res.seek(0)
  return res

@bottle.route('/')
def index():
  return bottle.static_file('index.html', pwd)

@bottle.post('/tweet')
def tweet():
  print(list(bottle.request.POST.allitems()))
  if bottle.request.files.get('media', None):
    media_ids = [api.media_upload(file = elem, filename = '%.jpg' % i) for i, elem in enumerate((lambda f: item.save(f.name) or f)(tempfile.NamedTemporaryFile('rb+')) for item in bottle.request.files.getall('media'))]
  else:
    media_ids = None
  return api.update_status(bottle.request.forms.get('text'), media_ids = media_ids)

@bottle.route('/latest')
def latest():
  return {'statuses': api.user_timeline(count = 200)}

@bottle.get('/destroy')
def destroy():
  target_id = int(bottle.request.query.get('id'))
  print(target_id)
  return api.destroy_status(target_id)

bottle.run(host = conf['bind']['host'], port = conf['bind']['port'])

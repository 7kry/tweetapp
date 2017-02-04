#! /usr/bin/python3

import bottle
import tweepy
import tweepy.parsers
import yaml

import os
import sys

pwd = os.path.dirname(os.path.abspath(__file__))
os.chdir(pwd)

conf = yaml.load(open(sys.argv[1] if len(sys.argv) > 1 else os.path.join(pwd, 'conf.yml')))

ah = tweepy.OAuthHandler(conf['consumer']['key'], conf['consumer']['secret'])
ah.set_access_token(conf['access_token']['key'], conf['access_token']['secret'])
api = tweepy.API(ah, parser = tweepy.parsers.JSONParser())

@bottle.route('/')
def index():
  return bottle.static_file('index.html', pwd)

@bottle.post('/tweet')
def tweet():
  return api.update_status(bottle.request.forms.decode().get('text'))

bottle.run(host = conf['bind']['host'], port = conf['bind']['port'])
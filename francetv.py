#!/usr/bin/python3
# coding: utf8

import argparse
import requests
import sys
#import os

URL1 = 'http://pluzz.webservices.francetelevisions.fr/pluzz/liste/type/replay/nb/10000'
URL2 = 'http://webservices.francetelevisions.fr/tools/getInfosOeuvre/v2/?idDiffusion={0}&catalogue=Pluzz'

parser = argparse.ArgumentParser(add_help=False)
parser.add_argument('-q', type=int, nargs='?', choices=range(0,4), default=1, help='Qualité (0=basse à 3=haute)')
parser.add_argument('keyword', nargs='?')

opt = parser.parse_args()

if opt.keyword is None:
  parser.print_help()

else:

  js = requests.get(URL1).json()

  liste = [] 
  for emission in js['reponse']['emissions']:
    if emission['titre'].lower().find(opt.keyword.lower()) != -1:
      liste.append(emission)

  for cpt in range(len(liste)):
    em = liste[cpt]
    print(u'{0}) [{1} {2}] : {3} ({4})'.format(cpt+1,em['date_diffusion'].replace('T',' '),em['chaine_id'],em['titre'],em['soustitre']))
  print("0) QUITTER")

  while True:
    indice = int(input("Choix => "))
    if indice == 0:
      break
    if indice <= len(liste):
      js = requests.get(URL2.format(liste[indice-1]['id_diffusion'])).json()
      url = ''
      for vid in js['videos']:
        if vid['format'] == 'm3u8-download':
          url = vid['url']
          break
      liste_m3u8 = requests.get(url).text
      for m3u8 in liste_m3u8.splitlines():
        if m3u8.find('index_{0}_av'.format(opt.q)) != -1:
           segments = requests.get(m3u8).text
           nomfich = '{0}_{1}.mp4'.format(liste[indice-1]['code_programme'],liste[indice-1]['id_diffusion'])
           with open(nomfich, 'wb') as fd:
             print('> {0} '.format(nomfich),end='')
             sys.stdout.flush()
             for seg in segments.splitlines():
                if seg.find('http:') != -1:
                  chunk = requests.get(seg).content
                  print('.',end='')
                  sys.stdout.flush()
                  fd.write(chunk)
             print(' OK')

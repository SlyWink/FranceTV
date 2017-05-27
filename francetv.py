#!/usr/bin/python3
# coding: utf8

import requests
import sys
import os

URL1 = 'http://pluzz.webservices.francetelevisions.fr/pluzz/liste/type/replay/nb/10000'
URL2 = 'http://webservices.francetelevisions.fr/tools/getInfosOeuvre/v2/?idDiffusion={0}&catalogue=Pluzz'

if len(sys.argv) != 2:
  print('Syntaxe : {0} <émission à rechercher>'.format(os.path.basename(sys.argv[0])))

else:

  js = requests.get(URL1).json()

  liste = [] 
  for emission in js['reponse']['emissions']:
    if emission['titre'].lower().find(sys.argv[1].lower()) != -1:
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
        if m3u8.find('index_3_av') != -1:
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

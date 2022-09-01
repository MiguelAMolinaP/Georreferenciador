import pandas as pd
import numpy as np
from re import split
import urllib.request, urllib.parse, urllib.error
import json
import ssl

import folium
from folium import plugins


def process_string_db(df_usuario):
  
  def processString5(txt):                #La función processString5 se encarga de eliminar tildes y símbolos y cambia los carateres a mayúsculas
    try:
        transTable = txt.maketrans("ÁÉÍÓÚáéíóúabcdefghijklmnñopqrstuvwxyz", "AEIOUAEIOUABCDEFGHIJKLMNÑOPQRSTUVWXYZ",)
        txt = txt.translate(transTable)
        return txt
    except:
        return txt  
  df_usuario = df_usuario.copy()

  for column in df_usuario.columns: 
    
    try:
      u=list(df_usuario[column].unique())
      d=dict(zip([i for i in u],[processString5(i) for i in u]))
      df_usuario[column]=df_usuario[column].map(d)
    
    except:
      continue
  return df_usuario


def del_names(df_usuario):
  df_usuario = df_usuario.copy()
  for column in df_usuario.columns:
    try:
      #Se borran posibles siglas con el fin de encontrar solamente el nombre de la zona.
      df_usuario[column] =df_usuario[column].str.replace(r"VEREDAS ","")
      df_usuario[column] =df_usuario[column].str.replace(r"VEREDA ","")
      df_usuario[column] =df_usuario[column].str.replace(r"VDAS ","")
      df_usuario[column] =df_usuario[column].str.replace(r"VDA ","")
      df_usuario[column] =df_usuario[column].str.replace(r"VS ","")
      df_usuario[column] =df_usuario[column].str.replace(r"V. ","")
      df_usuario[column] =df_usuario[column].str.replace(r"CORREGIMIENTOS ","")
      df_usuario[column] =df_usuario[column].str.replace(r"CORREGIMIENTO ","")
      df_usuario[column] =df_usuario[column].str.replace(r"CGTO ","")
      df_usuario[column] =df_usuario[column].str.replace(r"CTO ","")
      df_usuario[column] =df_usuario[column].str.replace(r"C. ","")   
      df_usuario[column] =df_usuario[column].str.replace(r"SITIO ","")
      df_usuario[column] =df_usuario[column].str.replace(r"ZONA ","")
      df_usuario[column] =df_usuario[column].str.replace(r"I.P.","")
      df_usuario[column] =df_usuario[column].str.replace(r"\W","")
      
    except:
      continue
  return df_usuario



def delete_spaces_db(df_usuario):
  
  def deletespaces(txt):     #La función deletespaces borra los espacios del parametro ingresado.
    try:
        transTable = txt.maketrans("", ""," ")
        txt = txt.translate(transTable)
        return txt
    except:
        return txt
  
  df_usuario = df_usuario.copy()
  for column in df_usuario.columns:  

    try:
      u=list(df_usuario[column].unique())
      d=dict(zip([i for i in u],[deletespaces(i) for i in u]))
      df_usuario[column]=df_usuario[column].map(d)
      
    except:
      continue
  return df_usuario


def georreferenciar(df_usuario, df_veredas, df_poblados, df_departamentos):

  df=df_usuario.merge(df_veredas, how='left' , left_on=['DEPARTAMENTO','MUNICIPIO','ZONA'] , right_on=['DEPARTAMENTO','MUNICIPIO','VEREDA'], suffixes=('','_x')).drop(['VEREDA'],axis=1)
  df=df.merge(df_poblados, how='left' , left_on=['DEPARTAMENTO','MUNICIPIO','ZONA'] , right_on=['DEPARTAMENTO','MUNICIPIO','POBLADO'], suffixes=('','_1')).drop(['POBLADO'],axis=1)
  df=df.merge(df_poblados, how='left' , left_on=['DEPARTAMENTO','MUNICIPIO','MUNICIPIO'] , right_on=['DEPARTAMENTO','MUNICIPIO','POBLADO'], suffixes=('','_2')).drop(['POBLADO'],axis=1)
  df=df.merge(df_departamentos, how='left' , left_on=['DEPARTAMENTO'] , right_on=['DEPARTAMENTO'], suffixes=('','_3'))

  df['RANGO']=[1 if i==i else np.nan for i in df['LONGITUD']]       
  df['RANGO_1']=[1 if i==i else np.nan for i in df['LONGITUD_1']]
  df['RANGO_2']=[2 if i==i else np.nan for i in df['LONGITUD_2']]
  df['RANGO_3']=[3 if i==i else np.nan for i in df['LONGITUD_3']]
  for i in ['1','2','3']:
    df['LONGITUD']=df['LONGITUD'].fillna(df['LONGITUD_{}'.format(i)])    
    df['LATITUD']=df['LATITUD'].fillna(df['LATITUD_{}'.format(i)])
    df['RANGO']=df['RANGO'].fillna(df['RANGO_{}'.format(i)])
    df=df.drop('LONGITUD_{}'.format(i), axis=1)
    df=df.drop('LATITUD_{}'.format(i), axis=1)
    df=df.drop('RANGO_{}'.format(i), axis=1)
  df['RANGO']=df['RANGO'].fillna(4)
  df['LATITUD']=df['LATITUD'].fillna(0)
  df['LONGITUD']=df['LONGITUD'].fillna(0)

  return df

def merge_df_salida(df_salida, df):
  df_salida=df_salida.merge(df[['LATITUD','LONGITUD','RANGO']], how='left', left_index=True, right_index=True)
  return df_salida


def geocode(location):

  # If you have a Google Places API key, enter it here
  api_key = False
  # https://developers.google.com/maps/documentation/geocoding/intro

  if api_key is False:
      api_key = 42
      serviceurl = 'http://py4e-data.dr-chuck.net/json?'
  else :
      serviceurl = 'https://maps.googleapis.com/maps/api/geocode/json?'

  # Ignore SSL certificate errors
  ctx = ssl.create_default_context()
  ctx.check_hostname = False
  ctx.verify_mode = ssl.CERT_NONE

  address = location.strip()
  parms = dict()
  parms['address'] = address
  if api_key is not False: parms['key'] = api_key
  url = serviceurl + urllib.parse.urlencode(parms)

  #print('Retrieving', url)
  uh = urllib.request.urlopen(url, context=ctx)
  data = uh.read().decode()
  #print('Retrieved', len(data), 'characters')

  try:
      js = json.loads(data)
  except:
      js = None

  if not js or 'status' not in js or js['status'] != 'OK':
    return [0,0]
  lat = js['results'][0]['geometry']['location']['lat']
  lng = js['results'][0]['geometry']['location']['lng']

  return [lat, lng]

def georreferenciar_google(df_usuario):
  lat=[]
  lng=[]
  df_usuario=df_usuario.fillna(' ')
  df_usuario['CONCAT']=df_usuario['DEPARTAMENTO'] + ', ' + df_usuario['MUNICIPIO'] + ', ' + df_usuario['ZONA']
  
  for location in df_usuario['CONCAT']:
    coordinate= geocode(location)
    lat.append(coordinate[0])
    lng.append(coordinate[1])
  
  df_usuario['LATITUD']=lat
  df_usuario['LONGITUD']=lng
  df_usuario=df_usuario.drop(['CONCAT'], axis=1)

  return df_usuario

def create_map():
  # map
  m = folium.Map(location=[6.2443382, -75.573553], zoom_start=5, control_scale=True, width='70%',height='90%')
  # add tiles to map
  folium.raster_layers.TileLayer('Open Street Map').add_to(m)
  folium.raster_layers.TileLayer('Stamen Terrain').add_to(m)
  folium.raster_layers.TileLayer('Stamen Toner').add_to(m)
  folium.raster_layers.TileLayer('Stamen Watercolor').add_to(m)
  folium.raster_layers.TileLayer('CartoDB Positron').add_to(m)
  folium.raster_layers.TileLayer('CartoDB Dark_Matter').add_to(m)
  # add layer control to show different maps
  folium.LayerControl().add_to(m)
  # mini map, scroll zoom toggle button, full screen
  # map
  map_with_mini= folium.Map(location=[6.2443382, -75.573553], zoom_start=8, control_scale=True, width='70%',height='90%')
  # plugin for mini map
  minimap = plugins.MiniMap(toggle_display=True, width= 80, height= 100 )
  # add minimap to map
  m.add_child(minimap)
  # add scroll zoom toggler to map
  plugins.ScrollZoomToggler().add_to(m)
  # add full screen button to map
  plugins.Fullscreen(position='topright').add_to(m)

  return m

def map_pandas(df, df_usuario_2, m):

  lat=[i for i in df['LATITUD']]
  lng=[i for i in df['LONGITUD']]
  rango=[i for i in df['RANGO']]
  zona=[i for i in df_usuario_2['ZONA'].fillna(df_usuario_2['MUNICIPIO']).fillna(df_usuario_2['DEPARTAMENTO']).fillna(' ')]
  municipio=[i for i in df_usuario_2['MUNICIPIO'].fillna(df_usuario_2['DEPARTAMENTO']).fillna(' ')]
  departamento=[i for i in df_usuario_2['DEPARTAMENTO'].fillna(' ')]

  for i in range(len(lat)):    
    if rango[i]==1:
      c="green"
    elif rango[i]==2:
      c="yellow"
    elif rango[i]==3:
      c="red"
    else:
      continue
    a= zona[i]+", "+ municipio[i]+", "+departamento[i]
    tooltip=a
    folium.Circle(radius=10,location=[lat[i], lng[i]],
              color=c,weight=10,tooltip=tooltip).add_to(m)

  return m

def map_google (df_usuario_2, m):

  lat=[i for i in df_usuario_2['LATITUD']]
  lng=[i for i in df_usuario_2['LONGITUD']]
  zona=[i for i in df_usuario_2['ZONA'].fillna(df_usuario_2['MUNICIPIO']).fillna(df_usuario_2['DEPARTAMENTO']).fillna(' ')]
  municipio=[i for i in df_usuario_2['MUNICIPIO'].fillna(df_usuario_2['DEPARTAMENTO']).fillna(' ')]
  departamento=[i for i in df_usuario_2['DEPARTAMENTO'].fillna(df_usuario_2['MUNICIPIO']).fillna(' ')]
  for i in range(len(lat)):
    
    a= zona[i]+", "+ municipio[i]+", "+departamento[i]
    c="blue"    
    tooltip=a
    folium.Circle(radius=10,location=[lat[i], lng[i]],
              color=c,weight=10,tooltip=tooltip).add_to(m)

  return m
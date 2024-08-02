# -*- coding: utf-8 -*-
"""
Created on Wed Jul 31 14:12:45 2024

@author: Usuario
"""
#print(df.iloc[0])

import pandas as pd
import requests
import geopandas as gpd
from shapely.geometry import Point
from pyproj import Proj, transform

url = 'https://sigel.aneel.gov.br/arcgis/rest/services/PORTAL/WFS/MapServer/0/query'

params = {
    'where': '1=1',
    'outFields': '*',
    'f': 'json',
    'resultOffset': 0,
    'resultRecordCount': 1000
}

all_records = []
while True:
    response = requests.get(url, params=params)
    data = response.json()
    
    if 'features' in data:
        all_records.extend(data['features'])
    
    # Se o número de registros retornados for menor que o solicitado, termina
    if len(data['features']) < params['resultRecordCount']:
        break
    
    params['resultOffset'] += params['resultRecordCount']

# Transformando em DataFrame
df = pd.DataFrame([record['attributes'] for record in all_records])

# Convertendo o campo de data
df['DATA_ATUALIZACAO'] = pd.to_datetime(df['DATA_ATUALIZACAO'], unit='ms')
df['DATA_ATUALIZACAO'] = df['DATA_ATUALIZACAO'].dt.strftime('%Y-%m-%d')

print(df.head())

# Converte X e Y para GeoDataFrame
##if 'X' in df.columns and 'Y' in df.columns:
    
utm_proj = Proj(proj='utm', zone=23, south=True, ellps='WGS84')
wgs84_proj = Proj(proj='latlong', datum='WGS84')

# Convertendo as coordenadas 
df['geometry'] = df.apply(
    lambda row: Point(transform(utm_proj, wgs84_proj, row['X'], row['Y'])), axis=1)

# Criando o GeoDataFrame com a geometria convertida
gdf = gpd.GeoDataFrame(df, geometry='geometry', crs="EPSG:4326")

# Adiciona colunas de latitude e longitude
gdf['Latitude'] = gdf['geometry'].apply(lambda p: p.y)
gdf['Longitude'] = gdf['geometry'].apply(lambda p: p.x)

# Exportar o resultado para um arquivo CSV
gdf.to_csv('C:/Users/Usuario/Documents/outputs/resultado_geodata.csv', index=False)
print('Dados exportados para resultado_geodata.csv')
            
#else:
#    print('A chave "features" não foi encontrada no JSON.')
   
#    print(data)  # ou processar os dados conforme necessário

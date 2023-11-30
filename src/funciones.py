# Funcion de limpieza y guardado de archivos

import pandas as pd
pd.set_option('display.max_columns', None)
import os
import numpy as np
import json

import warnings
warnings.filterwarnings('ignore')

def limpiar_guardar_lineas_ventas(ruta_archivo, carpeta_destino):
    df = pd.read_excel(ruta_archivo)

    df = df.rename(columns={
        df.columns[3]: 'operacion',
        df.columns[5]: 'Codigo',
        df.columns[6]: 'Denominacion',
        df.columns[8]: 'Cantidad',
        df.columns[10]: 'Pvp_facturado',
        df.columns[11]: 'Importe_bruto',
        df.columns[13]: 'Importe_neto',
        df.columns[15]: 'perfil',
        df.columns[18]: 'Puesto',
        df.columns[19]: 'Existencias_anteriores',
        df.columns[20]: 'Existencias_posteriores'
    })

    df = df.rename(columns={df.columns[0]: 'columna_vacia'})
    columna_vacia = 'columna_vacia'
    df = df.drop(columns=[columna_vacia], errors='ignore')
    df = df.drop(columns=['operacion', 'Empresa', 'Cliente', 'perfil', 'Aporta.Subv.'], errors='ignore')


    df['Fecha'] = pd.to_datetime(df['Fecha'], format='%d/%m/%y')
    df['Ticket'] = df.groupby(['Puesto', 'Vendedor', 'Fecha', 'Hora'])['Pvp_facturado'].transform('sum')

    if not os.path.exists(carpeta_destino):
        os.makedirs(carpeta_destino)

    nombre_archivo = os.path.basename(ruta_archivo)
    ruta_destino = os.path.join(carpeta_destino, nombre_archivo)

    df.to_excel(ruta_destino, index=False)


carpeta_origen = '/ruta/donde/estan/tus/archivos'
carpeta_destino = '/ruta/donde/guardar/archivos/limpios'

for archivo in os.listdir(carpeta_origen):
    if archivo.endswith('.xlsx', 'xls'):
        ruta_archivo = os.path.join(carpeta_origen, archivo)
        limpiar_guardar_lineas_ventas(ruta_archivo, carpeta_destino)
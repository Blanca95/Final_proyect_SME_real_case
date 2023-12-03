import pandas as pd
pd.set_option('display.max_columns', None)
import os
import numpy as np
import json
import warnings
warnings.filterwarnings('ignore')
from sqlalchemy import create_engine

# Clase de limpieza, guardado de archivos y subida a MySQL

class ExcelManager:
    """
    Clase para limpiar excels, según el nombre del archivo y el tipo de datos que contiene internamente, además de transformar los documentos en dataframes para luego cortar las columnas según las necesidades de MySQL. 
    Guardar los dfs restantes y subir los archivos a MySQL.
    """
    def __init__(self, carpeta_origen):
        """
        Iniciador. Primera función necesaria de cualquier clase. 
        self.data_frames ➡ sirve para agrupar en diccionarios los dataframes según el nombre y tipo de archivo excel. 
        self.data_frames_to_sql ➡ sirve para agrupar en diccionarios los dataframes cortados según las necesidades de la base de datos.
        self.carpeta_origen ➡ es la ruta de donde obtenemos todos los archivos.
        self.excels ➡ mirar def extraerExcels().

        Args:
            carpeta_origen: ruta principal donde se encuentran todos los archivos que queremos trabajar.
        """ 
        self.data_frames = {
                "lineas_ventas": [],
                "facturacion_familias": [],
                "facturacion": [],
        }
        self.data_frames_to_sql = {
            "Stock": None,
            "Ventas":None,
            "Medicamentos": None,
            "Empleados": None,
        }
        self.carpeta_origen = carpeta_origen
        self.excels  = self.extraerExcels(self.carpeta_origen)
        self.filtrarExcels(self.excels)
    

    def extraerExcels(self, carpeta):
        """
        Función para extraer todos los excel de todas las carpetas.

        Args:
            carpeta: ruta de los archivos.

        Returns:
            Los excels de las carpetas.
        """    
        excels = [] # lista
        for root, dirs, files in os.walk(carpeta): # root, es la ruta de las carpetas. dirs, son los directorios, es decir, cada una de las carpetas sin la ruta, osea el nombre. files, son los nombres de los archivos.
            for archivo in files:
                if (archivo.endswith('.xlsx') or archivo.endswith('.xls')): # me quedo solo con los excels
                    ruta_archivo = os.path.join(root, archivo)
                    excels.append(ruta_archivo) # añado los strings de las rutas de los excels a la lista inicial
        return excels
    

    def filtrarExcels(self, excels):
        """
        Función para filtrar y agrupar en dataframes todos los excels, por nombre y tipo de datos que contienen: "lineas_ventas", "facturacion_familia" o "facturacion".

        Args:
            excels: lista de los strings de las rutas de los excels.
        """
        for rutaExcel in excels:
            if "lineas_ventas" in os.path.basename(rutaExcel):
                data_frame = self.lineasVentasToDataFrame(rutaExcel)
                data_frame._ruta_excel = rutaExcel
                self.data_frames["lineas_ventas"].append(data_frame)
                          
            if "facturacion_familia" in os.path.basename(rutaExcel):
                data_frame = self.facturacionFamiliaToDataFrame(rutaExcel)
                data_frame._ruta_excel = rutaExcel
                self.data_frames["facturacion_familias"].append(data_frame)

            if "facturacion" in os.path.basename(rutaExcel):
                data_frame = self.facturacionToDataFrame(rutaExcel)
                data_frame._ruta_excel = rutaExcel
                self.data_frames["facturacion"].append(data_frame)
            

    def lineasVentasToDataFrame(self, excel):
        """
        Función para abrir un excel que contiene en su ruta "lineas_ventas", convertirlo en dataframe y limpiarlo a necesidad.

        Args:
            excel: es un string de la ruta de los excels. Es decir, un solo excel.

        Returns:
            El dataframe creado limpio.
        """
        df = pd.read_excel(excel)
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

        #df['Fecha'] = pd.to_datetime(df['Fecha'], format='%d/%m/%y')
        df['Ticket'] = df.groupby(['Puesto', 'Vendedor', 'Fecha', 'Hora'])['Pvp_facturado'].transform('sum')
        return df


    def facturacionFamiliaToDataFrame(self, excel):
        """
        Función para abrir un excel que contiene en su ruta "facturacion_familia", convertirlo en dataframe y limpiarlo a necesidad.

        Args:
            excel: es un string de la ruta de los excels. Es decir, un solo excel.

        Returns:
            El dataframe creado limpio.
        """
        return 


    def facturacionToDataFrame(self, excel):
        """
        Función para abrir un excel que contiene en su ruta "facturacion", convertirlo en dataframe y limpiarlo a necesidad.

        Args:
            excel: es un string de la ruta de los excels. Es decir, un solo excel.

        Returns:
            El dataframe creado limpio.
        """
        return


    def exportarDfsToExcels(self, carpeta_destino):
        """
        Para abrir un archivo xml, indicándole desde que ruta lo queremos

        Args:
            filepath: ruta del archivo que queremos abrir y leer

        Returns:
            El archivo xml leido en python
        """
    # Guardar a excel los df limpios    
        for nombreExcel, dfList in self.data_frames.items():
            # nombreExcel = lineas_ventas o facturacion o facturacion_familias
            for df in dfList:
                ruta_final = os.path.join(carpeta_destino, os.path.basename(df._ruta_excel).replace('.xls', '.xlsx'))
                df.to_excel(ruta_final, index=False, engine='openpyxl')


    def cortarDFsforMySQL(self, data_frame):
        """
        Para abrir un archivo xml, indicándole desde que ruta lo queremos

        Args:
            filepath: ruta del archivo que queremos abrir y leer

        Returns:
            El archivo xml leido en python
        """
    # Descargas e importaciones    
        for key, value in self.data_frames.items():

        #for meterse en cada dfgde lineas ventas
     

    def exportarExceltoMySQl(self, excel):
        """
        Para abrir un archivo xml, indicándole desde que ruta lo queremos

        Args:
            filepath: ruta del archivo que queremos abrir y leer

        Returns:
            El archivo xml leido en python
        """
    # Descargas e importaciones        
        pass 


#------------------------------------------------


excel_manager = ExcelManager(r"C:\Users\blanx\ironhack\Final_proyect_SME_real_case\Final_proyect_SME_real_case\data\data_raw")

#print(excel_manager.data_frames)
excel_manager.exportarDfsToExcels(r'C:\Users\blanx\ironhack\Final_proyect_SME_real_case\Final_proyect_SME_real_case\data\data_clean')


#------------------------------------------------


def cargar_a_sql(ruta_carpeta, patron_nombre, nombre_base_datos, nombre_tabla):
    """
    -

    Args:
        -: -

    Returns:
        -
    """
    # Conectar a la base de datos
    engine = create_engine(f'sqlite:///{nombre_base_datos}')

    # Iterar sobre los archivos en la carpeta
    for archivo in os.listdir(ruta_carpeta):
        if archivo.startswith(patron_nombre) and archivo.endswith('.xlsx'):
            ruta_archivo = os.path.join(ruta_carpeta, archivo)

            # Leer el archivo Excel
            df = pd.read_excel(ruta_archivo)

            # Limpieza de datos (añadir aquí el código de limpieza si es necesario)

            # Cargar datos a la base de datos
            df.to_sql(nombre_tabla, engine, if_exists='append', index=False)
            print(f"Datos de {archivo} cargados a la tabla {nombre_tabla} en {nombre_base_datos}")

# Ruta de la carpeta que contiene los archivos Excel
carpeta_origen = '/ruta/donde/estan/tus/archivos'

# Patrón de nombre de archivos a considerar
patron_nombre_archivo = 'lineas_ventas'

# Nombre de la base de datos
nombre_db = 'tu_base_de_datos.db'

# Nombre de la tabla en la base de datos
nombre_tabla_sql = 'nombre_de_tabla_sql'

# Llamada a la función para cargar datos
cargar_a_sql(carpeta_origen, patron_nombre_archivo, nombre_db, nombre_tabla_sql)

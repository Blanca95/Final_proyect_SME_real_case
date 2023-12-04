import pandas as pd
pd.set_option('display.max_columns', None)
import os
import numpy as np
import json
import warnings
warnings.filterwarnings('ignore')
from sqlalchemy import create_engine
import configparser
import mysql.connector as conn
import pymysql


# Clase para abrir, limpiar, guardar archivos y subirlos a MySQL

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
            df.columns[20]: 'Existencias'
        })
        df = df.rename(columns={df.columns[0]: 'columna_vacia'})
        columna_vacia = 'columna_vacia'
        df = df.drop(columns=[columna_vacia], errors='ignore')
        df = df.drop(columns=['operacion', 'Empresa', 'Cliente', 'perfil', 'Aporta.Subv.', 'Existencias_anteriores'], errors='ignore')

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
        Función para guardar los dataframes limpios a excels, en una carpeta determinada.

        Args:
            carpeta_destino: ruta donde quiero guardar todos los archivos que he trabajado.
        """  
        for nombreExcel, dfList in self.data_frames.items():
            # nombreExcel = lineas_ventas o facturacion o facturacion_familias
            for df in dfList:
                ruta_final = os.path.join(carpeta_destino, os.path.basename(df._ruta_excel).replace('.xls', '.xlsx'))
                df.to_excel(ruta_final, index=False, engine='openpyxl')


    def obtenerDFstoMySQL(self):
        """
        Función para filtrar y guardar los dataframes en un diccionario, según el tipo de data_frames: "lineas_ventas", "facturacion_familia" o "facturacion".
        self.data_frames_to_sql = {
            "Ventas":None,
            "Medicamentos": None,
            "Empleados": None,
        }
        Returns:
            El diccionario con los dataframes cortados según cada key: "Stock", "Ventas", "Medicamentos" y "Empleados".
        """   
        for key, value in self.data_frames.items(): # key = tipo excel, value = dataframe limpio, filas y columnas
            if key == "lineas_ventas":
                self.data_frames_to_sql["Empleados"] = self.obtenerEmpleadosLineasVentas(value)
                self.data_frames_to_sql["Ventas"] = self.obtenerVentasLineasVentas(value)
                self.data_frames_to_sql["Medicamentos"] = self.obtenerMedicamentosLineasVentas(value)
            '''   
            if key == "facturacion_familia":
                empleados = self. ()
                self.data_frames_to_sql["x"] = 

                
            if key == "facturacion":
                empleados = self. ()
                self.data_frames_to_sql["y"] =     
            '''  

    def obtenerEmpleadosLineasVentas(self, data_frames):
        """
        Función para obtener unicamente los valores de la columna Vendedor.

        Args:
            data_frames: lista de dataframe limpio con nombre 'lineas_ventas'.

        Returns:
            Dataframe que replesentará la tabla de MySQL llamada Empleados.
        """  
        empleados = pd.concat(data_frames, axis=1)    
        empleados = empleados['Vendedor']
        empleados = empleados.drop_duplicates()
        empleados = empleados.reset_index(drop=True)
        empleados.index += 1
        return empleados
    

    def obtenerMedicamentosLineasVentas(self, data_frames):
        """
        Función para obtener los valores de las columnas 'Codigo', 'Denominacion' y 'Pvp'.

        Args:
            data_frames: lista de dataframe limpio con nombre 'lineas_ventas'.

        Returns:
            Dataframe que replesentará la tabla de MySQL llamada Medicamentos.
        """ 
        medicamentos = pd.concat(data_frames, axis=1)  
        medicamentos = medicamentos[['Codigo', 'Denominacion', 'Pvp']]
        medicamentos = medicamentos.drop_duplicates()
        medicamentos = medicamentos.reset_index(drop=True)
        medicamentos.index += 1
        return medicamentos 


    def obtenerVentasLineasVentas(self, data_frames):       
        """
        Función para obtener todos los valores del dataframe.

        Args:
            data_frames: lista de dataframe limpio con nombre 'lineas_ventas'.

        Returns:
            Dataframe que replesentará la tabla de MySQL llamada Ventas.
        """  
        archivos = pd.read_excel(r'C:\Users\blanx\ironhack\Final_proyect_SME_real_case\Final_proyect_SME_real_case\data\data_clean\archivos.xlsx')
        ventas = pd.concat(data_frames, axis=1)
        ventas = pd.merge(ventas, archivos[['Código', 'Familia', 'Mínimo']], left_on='Codigo', right_on='Código', how='left')
        ventas = ventas.drop(columns=['Código'])
        return ventas

    def exportarMySQl(self):
        """
        Función para crear el engine de conexión, crear la base de datos y subir los dataframes.

        Args:
            filepath: ruta del archivo que queremos abrir y leer

        Returns:
            El archivo xml leido en python
        """
        config = configparser.ConfigParser()
        config.read('src/config.ini')
        host = config['mysql']['host']
        user = config['mysql']['user']
        password = config['mysql']['password']

        conexion = conn.connect(host=host, 
                                user=user, 
                                password=password)

        cursor = conexion.cursor() 
        cursor


        c = cursor.execute

        c('create database if not exists Farmacia;')

        engine = create_engine("mysql+pymysql://{user}:{pw}@localhost/{db}"
                            .format(user=user,
                                    pw=password,
                                    db="Farmacia"))

        for key, value in self.data_frames_to_sql.items():
            value.to_sql(name=key,      
                    con=engine,          
                    if_exists='append',  
                    index=True)

        # empleados.to_sql(name='empleados',      
        #             con=engine,          
        #             if_exists='append',  
        #             index=True
        #         )

        # medicamentos.to_sql(name='medicamentos',      
        #             con=engine,          
        #             if_exists='append',  
        #             index=True
        #         )

        # ventas.to_sql(name='ventas',      
        #             con=engine,          
        #             if_exists='append',  
        #             index=True
        #         )
    # Descargas e importaciones        
        pass 


#------------------------------------------------


if __name__ == "__main__":
    carpeta_origen = r"C:\Users\blanx\ironhack\Final_proyect_SME_real_case\Final_proyect_SME_real_case\data\data_raw"
    excelManager = ExcelManager(carpeta_origen)

    # exportar excels entre medias
    carpeta_destino_excel = r"C:\Users\blanx\ironhack\Final_proyect_SME_real_case\Final_proyect_SME_real_case\data\data_clean"
    excelManager.exportarDfsToExcels(carpeta_destino_excel )

    
    excelManager.obtenerDFstoMySQL()
    excelManager.exportarMySQl()
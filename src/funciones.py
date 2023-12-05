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
import mysql
import pymysql


# Clase para abrir, limpiar, guardar archivos y subirlos a MySQL

class ExcelManager:
    """
    Clase para limpiar excels, según el nombre del archivo y el tipo de datos que contiene internamente, además de transformar los documentos en dataframes para luego cortar las columnas según las necesidades de MySQL. 
    Guardar los dfs restantes y subir los archivos a MySQL.
    """
    # -----------------------------------------------------------------------------------------# ETL #------------------------------------------------------------------------------------------------------------------
    def __init__(self):
        """
        Iniciador. Primera función necesaria de cualquier clase. 
        self.data_frames ➡ sirve para agrupar en diccionarios los dataframes según el nombre y tipo de archivo excel. 

        Args:
            carpeta_origen: ruta principal donde se encuentran todos los archivos que queremos trabajar.
        """ 
        self.data_frames = {
                "lineas_ventas": [],
                "facturacion_familias": [],
                "facturacion": [],
        }


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
            El dataframe lineas_ventas creado limpio.
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


    #------------------------------------------------------------------------------------------------------# SQL #----------------------------------------------------------------------------------------------------
    def obtenerDFstoMySQL(self):
        """
        Función para filtrar y guardar los dataframes en un diccionario, según el tipo de data_frames: "lineas_ventas", "facturacion_familia" o "facturacion".

        Returns:
            El diccionario con los dataframes cortados según cada key: "Stock", "Ventas", "Medicamentos" y "Empleados".
        """ 
        # IMPORTANTE: Rellenar primero empleados y medicamentos para que se rellenen los FKs.   
        data_frames_to_sql = {} 
        for key, value in self.data_frames.items(): # key = tipo excel, value = dataframe limpio, filas y columnas
            if key == "lineas_ventas":
                data_frames_to_sql["Empleados"] = self.obtenerEmpleadosLineasVentas(value)
                data_frames_to_sql["Medicamentos"] = self.obtenerMedicamentosLineasVentas(value)
                data_frames_to_sql["Ventas"] = self.obtenerVentasLineasVentas(value, data_frames_to_sql["Medicamentos"], data_frames_to_sql["Empleados"])
                
        return data_frames_to_sql
           

    def obtenerEmpleadosLineasVentas(self, data_frames):
        """
        Función para obtener unicamente los valores de la columna Vendedor.

        Args:
            data_frames: lista de dataframe limpio con nombre 'lineas_ventas'.

        Returns:
            Dataframe que replesentará la tabla de MySQL llamada Empleados.
        """
        # IMPORTANTE: Rellenar primero empleados y medicamentos para que se rellenen los FKs.  
        empleados = pd.concat(data_frames, axis=1)    
        empleados = empleados[['Vendedor']]
        empleados = empleados.drop_duplicates()
        empleados['index'] = range(1, len(empleados) + 1)

        return empleados
    

    def obtenerMedicamentosLineasVentas(self, data_frames):
        """
        Función para obtener los valores de las columnas 'Codigo', 'Denominacion' y 'Pvp'.

        Args:
            data_frames: lista de dataframe limpio con nombre 'lineas_ventas'.

        Returns:
            Dataframe que replesentará la tabla de MySQL llamada Medicamentos.
        """ 
        # IMPORTANTE: Rellenar primero empleados y medicamentos para que se rellenen los FKs.  
        medicamentos = pd.concat(data_frames, axis=1)  
        medicamentos = medicamentos[['Codigo', 'Denominacion', 'Pvp']]
        medicamentos = medicamentos.drop_duplicates()
        medicamentos['index'] = range(1, len(medicamentos) + 1)

        return medicamentos 


    def obtenerVentasLineasVentas(self, data_frames, df_medicamentos, df_empleados):       
        """
        Función para obtener todos los valores del dataframe, además de añadir 2 columnas ['Familia', 'Mínimo'] de otro archivo excel.

        Args:
            data_frames: lista de dataframe limpio con nombre 'lineas_ventas'.

        Returns:
            Dataframe que replesentará la tabla de MySQL llamada Ventas.
        """  
        archivos = pd.read_excel(r'C:\Users\blanx\ironhack\Final_proyect_SME_real_case\Final_proyect_SME_real_case\data\data_clean\archivos.xlsx')
        ventas = pd.concat(data_frames, axis=1)

        ventas = pd.merge(ventas, df_medicamentos[["Codigo", "index"]], on='Codigo', how='left')
        ventas.rename(columns={'index':'medicamentos_index'}, inplace=True)

        ventas = pd.merge(ventas, df_empleados[["Vendedor", "index"]], on='Vendedor', how='left')
        ventas.rename(columns={'index': 'empleados_index'}, inplace=True)
        
        # Metemos df archivos
        ventas = pd.merge(ventas, archivos[['Código', 'Familia', 'Mínimo']], left_on='Codigo', right_on='Código', how='left')
   
        ventas = ventas.drop(columns=['Código','Vendedor','Codigo'])
        ventas.rename(columns={'Mínimo':'Ex_minimas'}, inplace=True)

        return ventas


    def configuracionMySQL(self):
        """
        Función para generar el host, user y password de MySQL y que no me reporte github. 
        
        Returns:
            El host, user y password, necesarios para conectarme a MySQL.
        """
        config = configparser.ConfigParser()
        config.read('src/config.ini')
        host = config['mysql']['host']
        user = config['mysql']['user']
        password = config['mysql']['password']
        return host, user, password


    def conectarMySQL(self):
        """
        Función para crear el engine de conexión de la base de datos.
        
        Returns:
            El cursor de conexión.
        """
        host, user, password = self.configuracionMySQL()
        self.conn = conn.connect(host=host, 
                                user=user, 
                                password=password)
        self.cursor = self.conn.cursor() 
        return self.cursor


    def crearBDMySQL(self):
        """
        Función para crear la base de datos.

        """

        try:
            self.conectarMySQL()
            with open(r"C:\Users\blanx\ironhack\Final_proyect_SME_real_case\Final_proyect_SME_real_case\src\create.sql", 'r') as sqlFile:
                data = sqlFile.read()
                self.cursor.execute(data)
        except mysql.connector.Error as err:
            print(f"Error: {err}")
        finally:
            # Cierra el cursor y la conexión después de usarlos
            if self.cursor:
                self.cursor.close()
            if self.conn:
                self.conn.close()


    def crearEngineMySQL(self):
        """
        Función para crear el engine de conexión de la base de datos.
        
        Returns:
            El engine.
        """
        host, user, password = self.configuracionMySQL()
        engine = create_engine("mysql+pymysql://{user}:{pw}@{host}/{db}"
                            .format(user=user,
                                    pw=password,
                                    host=host,
                                    db="Farmacia"))
        return engine
    

    def volcarDatosMySQL(self, data_frames_sql):
        """
        Función para subir los dataframes con toda la información de la base de datos.
        
        Args:
            engine:
            data_frame:

        Returns:
        """
        # IMPORTANTE: Rellenar primero empleados y medicamentos para que se rellenen los FKs.
        engine = self.crearEngineMySQL()

        data_frames_sql["Medicamentos"].to_sql(name='medicamentos',      
            con=engine,          
            if_exists='append',  
            index=True
        )
        data_frames_sql["Empleados"].to_sql(name='empleados',      
            con=engine,          
            if_exists='append',  
            index=True
        )
        data_frames_sql["Ventas"].to_sql(name='ventas',      
            con=engine,          
            if_exists='append',  
            index=True
        )


    def ejecutarSQL(self, query):
        """
        Función para crear el engine de conexión, crear la base de datos y subir los dataframes.
        
        """
        cursor = self.conectarMySQL()
        cursor.execute(query)
        



consulta_sql = ''' 
SELECT * FROM medicamentos
'''

#------------------------------------------------


if __name__ == "__main__":

    excelManager = ExcelManager()

    # # excels
    carpeta_origen = r"C:\Users\blanx\ironhack\Final_proyect_SME_real_case\Final_proyect_SME_real_case\data\data_raw"
    excels  = excelManager.extraerExcels(carpeta_origen)
    excelManager.filtrarExcels(excels)

    # # exportar excels entre medias
    # carpeta_destino = r"C:\Users\blanx\ironhack\Final_proyect_SME_real_case\Final_proyect_SME_real_case\data\data_clean"
    # excelManager.exportarDfsToExcels(carpeta_destino)

    #test bd
    #excelManager.crearBDMySQL()



    data_frames_sql = excelManager.obtenerDFstoMySQL()
    excelManager.volcarDatosMySQL(data_frames_sql)


# 1º saber ejecutar querie desde python
# 2º hacer 2 metodos
    #- crear base de datos si no existe
    #- volcar los datos test
    #- añadir modificar datos
# 3º subir todos los datos

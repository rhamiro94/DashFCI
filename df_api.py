
#Creo dataframe sobre el cual se estructura mi pryoecto de Dash.
import requests
from urllib.parse import urljoin
import pandas as pd
import requests
import openpyxl
#Aqui funciona la api

import pandas as pd

# URL del archivo Excel
url_archivo = "https://api.cafci.org.ar/pb_get"

# Leo el archivo Excel directamente desde su URL
try:
    df = pd.read_excel(url_archivo,header=None,skiprows=10)
    # Ahora puedes trabajar con el DataFrame df como lo harías normalmente
    print(df.head())  # Muestra las primeras filas del DataFrame como ejemplo
except Exception as e:
    print("Error al leer el archivo desde la URL:")

#Ahora que tengo el archivo descargado voy a categorizar los fondos para luego analizarlos en funcion de las mismas.
categorias=["Renta Variable Peso Argentina","Renta Variable Dolar Estadounidense Billete","Renta Variable Dolar Estadounidense", "Renta Fija Peso Argentina","Renta Fija Dolar Estadounidense","Renta Fija Dolar Estadounidense Billete","Renta Mixta Peso Argentina","Renta Mixta Dolar Estadounidense","Renta Mixta Dolar Estadounidense Billete","PyMes Peso Argentina","PyMes Dolar Estadounidense","Infraestructura Peso Argentina","Infraestructura Dolar Estadounidense","Retorno Total Peso Argentina","Retorno Total Dolar Estadounidense","RG900 Peso Argentina","Mercado de Dinero Peso Argentina","Mercado de Dinero Dolar Estadounidense"]

#Incorporo las categorias del cafci
categorias_separadas = []
datos_separados = []

# Inicializo la categoría actual
categoria_actual = None

# Itero sobre cada entrada de la primera columna
for entrada in df.iloc[:, 0]:
    # Verifico si la entrada coincide con alguna de las categorías
    for categoria in categorias:
        if categoria in entrada:
            # Si coincide, actualiza la categoría actual
            categoria_actual = categoria
            break

    # Agrego la categoría actual a la lista de categorías
    categorias_separadas.append(categoria_actual)

    # Agrego la entrada a la lista de datos
    datos_separados.append(entrada.replace(categoria_actual, "").strip())

# Agrego las listas separadas como nuevas columnas al DataFrame
df["Categoria"] = categorias_separadas
df["Datos"] = datos_separados

# Ahora el DataFrame contiene una nueva columna "Categoria" con las categorías separadas
# y una nueva columna "Datos" con los datos separado

#Previo a eliminar valores nulos elimino variables que no considero utiles
col_r = df.columns[24:44]
#Elimino columnas
datos_limpio = df.drop(columns=col_r)

#Ahora si el momento de borrar nulls
# Eliminar filas con valores nulos
datos_sin_nulos = datos_limpio.dropna()
#Ahora tengo como les asigno nombre a estas columnas
nombres_columnas = ['Nombre','Moneda', 'Región','Horizonte','Fecha', 'VCT0', 'VCT-1', 'Var%', 'Reexp.Pesos', 'VarCt-15', 'VarCt-104', 'VarCanual', 'QC', 'QC-1', 'PN0', 'PNt-1','MS','SD','CNV','CAL','CODCAF','CSG','CSD','SG','Categoria','Datos']

# Asigno los nombres a las columnas del DataFrame
datos_sin_nulos.columns = nombres_columnas
#Tratamos de scarnos de encima los outliers para variables numericas de rendimiento
columnas_a_transformar = ['VarCt-15', 'Var%', 'VarCt-104','VarCanual']

# Iteramos sobre las columnas especificadas
for columna in columnas_a_transformar:
    Q1 = datos_sin_nulos[columna].quantile(0.25)
    Q3 = datos_sin_nulos[columna].quantile(0.75)
    IQR = Q3 - Q1

    umbral_inferior = Q1 - 3 * IQR
    umbral_superior = Q3 + 3 * IQR

    # Filtramos los valores que están dentro del rango intercuartílico para la columna actual
    df_filt = datos_sin_nulos[(datos_sin_nulos[columna] >= umbral_inferior) & (datos_sin_nulos[columna] <= umbral_superior)]

#Guardo el archivo en un csv.
df_filt["Variación_Patrimonial"]=((df_filt["PN0"]-df_filt["PNt-1"])/df_filt["PNt-1"]) * 100
df_filt.to_csv('datos_fci.csv', index=False)




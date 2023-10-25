"""
Nombre del Script: Análisis de Clientes
Descripción: Este script limpia, transforma y visualiza un dataset de clientes, y ejecuta consultas SQL específicas.
Autor: Kimberly Negrette
Fecha de Creación: 25/10/2023
"""
"""NOTA: Antes de ejecutar este script asegurarse de que todas las dependiencias están instaladas.
Puede ejecutar 'pip install -r requirements.txt'."""

import pandas as pd
import numpy as np
import sqlite3
import matplotlib.pyplot as plt
import seaborn as sns

def clean_column_names(df):
    """
    Clean column names by replacing spaces with underscores, removing special characters, 
    and converting to lowercase.
    """
    # Reemplazar espacios con guiones bajos y convertir a minúsculas
    df.columns = df.columns.str.replace(' ', '_', regex=True).str.lower()
    
    # Remover caracteres especiales
    df.columns = df.columns.str.replace(r'[^a-zA-Z0-9_]', '', regex=True)

    # Renombrar manualmente las columnas de annual_income, spending_score y customerid
    df.rename(columns={
                    'customerid':'customer_id',
                    'annual_income_': 'annual_income',
                    'spending_score_1100': 'spending_score'
                    }, inplace=True)    
    
    return df


def check_missing_values(df):
    """
    Check for missing values in the dataframe.
    """
    missing_values = df.isnull().sum()
    return missing_values


def replace_values_age(df):
    """
    Replace values with 0 for null in the column age
    """
    df['age'] = df['age'].replace(0, np.nan)
    return df


def impute_missing_values(df, column_name):
    """
    Impute missing values in the specified column with the mode of the column.
    """
    mode_value = df[column_name].mode()[0]
    df[column_name].fillna(mode_value, inplace=True)
    return df


def remove_duplicates(df):
    """
    Remove duplicated rows from the dataframe.
    """
    df.drop_duplicates(inplace=True)
    return df


def correct_data_types(df):
    """
    Correct the data types of columns if necessary.
    """
    # Asegurarse de que 'CustomerID' es de tipo string (object)
    df['customer_id'] = df['customer_id'].astype(str)
    
    # Asegurarse de que 'Gender' y 'Profession' son de tipo string (object)
    df['gender'] = df['gender'].astype('category')
    df['profession'] = df['profession'].astype('category')
    
    return df


def columns_to_lowercase(df, columns):
    """
    Convert the values in the specified columns to lowercase.
    """
    for column in columns:
        df[column] = df[column].str.lower()
    
    return df


def clean_data(df):
    """
    Execute the cleaning and transformation steps.
    """
    print("Formatting column names...")
    df = clean_column_names(df)

    print("\nRemoving duplicates...")
    df = remove_duplicates(df)
    print(f"\nNumber of rows after removing duplicates: {len(df)}")
    
    print("\nCorrecting data types...")
    df = correct_data_types(df)
    print("Data types after correction:")
    print(df.dtypes)
    
    print("\nFormatting values in categorical columns...")
    columns = ['profession', 'gender']
    df = columns_to_lowercase(df, columns)

    print("\nChecking for missing values...")
    print(check_missing_values(df))

    print("\nImputing missing values in column 'profession' with the mode... ")
    df = impute_missing_values(df, 'profession')

    print("\nImputting missing values in column 'age' with the mode...")
    df = replace_values_age(df)
    df = impute_missing_values(df, 'age')
    
    print("\nCleaning done!")

    return df


def create_connection_and_load_data(df):
    conn = sqlite3.connect(":memory:")
    df.to_sql("customers_table", conn, index=False)
    return conn

def consulta1(conn):
    """1.Calcular el número y porcentaje sobre el total absoluto de Mujeres monoparentales 
    que han gastado más de 15.000 dólares. """
    # Acá asumiré que una familia monoparental es la que tiene family_size = 1
    # Además, asumiré que intentan preguntar sobre en annual income y no los gastos
    query = """
            SELECT COUNT(*) AS total_mujeres_monoparentales, 
            (COUNT(*)*100/(SELECT COUNT(*) FROM customers_table)) AS porcentaje
            FROM customers_table 
            WHERE gender = 'female' 
            AND family_size = 1 
            AND annual_income > 15000
            """

    resultado_df = pd.read_sql_query(query, conn)
    return resultado_df


def consulta2(conn):
    """2. Calcular cuántos abogados (M/F) hay en el dataset que tengan mayor experiencia 
    laboral que la media de ingenieros hombres."""

    query = """
            SELECT COUNT(*) AS num_abogados
            FROM customers_table
            WHERE profession = 'lawyer'
                AND work_experience > (SELECT AVG(work_experience) AS avg_exp_ing
                                        FROM customers_table
                                        WHERE profession = 'engineer' 
                                            AND gender = 'male'
                                        )
            """

    resultado_df = pd.read_sql_query(query, conn)
    return resultado_df


def consulta3(conn):
    """3. Dibuja la distribución de abogados en función de su gasto anual (utiliza franjas de gasto)
    y de su sexo."""

    query = """ 
            SELECT 
                gender,
                CASE
                    WHEN spending_score <= 20 THEN '0-20'
                    WHEN spending_score <= 40 THEN '21-40'
                    WHEN spending_score <= 60 THEN '41-60'
                    WHEN spending_score <= 80 THEN '61-80'
                    ELSE '81-100'
                END as spending_bracket,
                COUNT(*) as num_lawyers
            FROM 
                customers_table
            WHERE 
                profession = 'lawyer'
            GROUP BY 
                gender, spending_bracket
            ORDER BY 
                gender, spending_bracket;
            """

    resultado_df = pd.read_sql_query(query, conn)
    print(resultado_df)

    # Crear un gráfico de barras
    # Definir colores
    colors = {
        'male': 'lightblue',  
        'female': 'darkgray'  
    }
    plt.figure(figsize=(10, 6))
    for gender in resultado_df['gender'].unique():
        plt.bar(resultado_df[resultado_df['gender'] == gender]['spending_bracket'], 
                resultado_df[resultado_df['gender'] == gender]['num_lawyers'], 
                label=f'{gender}',
                color=colors.get(gender))

    plt.xlabel('Puntaje de Gasto')
    plt.ylabel('Número de Abogados')
    plt.title('Distribución de Abogados por Gasto y Género')
    plt.legend()
    plt.show()


def consulta4(conn):
    """¿Cuál es la relación entre la profesión y el puntaje de gasto?
    """

    query = """
            SELECT profession, ROUND(AVG(spending_score),2) AS avg_spending_score
            FROM customers_table
            GROUP BY profession
            ORDER BY avg_spending_score DESC
            """
    resultado_df = pd.read_sql_query(query, conn)
    print(resultado_df)

    # Graficar boxplot
    query = """
        SELECT profession, spending_score 
        FROM customers_table
    """
    resultado_2 = pd.read_sql_query(query, conn)

    # Crear un boxplot utilizando Seaborn
    plt.figure(figsize=(10, 6))
    sns.boxplot(x='profession', y='spending_score', data=resultado_2)

    # Rotar las etiquetas del eje x para mejor legibilidad
    plt.xticks(rotation=35)

    # Añadir títulos y etiquetas
    plt.title('Relación entre la Profesión y el Puntaje de Gasto')
    plt.xlabel('Profesión')
    plt.ylabel('Puntaje de Gasto')

    # Mostrar el boxplot
    plt.show()
    

# Carga de los datos desde github
dataset_url = "https://raw.githubusercontent.com/kimnegrette3/Python-SQL-Customer-Analysis/main/customers.csv"
customers = pd.read_csv(dataset_url)

# Limpieza y transformación de los datos
print('*'*50)
print('Cleaning and Transforming Data\n')
customers_clean = clean_data(customers.copy())
print('*'*50)

# Consultas
print('\nConsultas SQL y visualizaciones\n')
print('*'*50)
conn = create_connection_and_load_data(customers_clean)

print("\nConsulta 1: El número y porcentaje sobre el total absoluto de Mujeres \nmonoparentales que han gastado más de 15.000 dólares es:\n")
print(consulta1(conn))
print('*'*50)

print("\nConsulta 2: El número de abogados (M/F) que tienen mayor experiencia \nlaboral que la media de ingenieros hombres es:\n")
print(consulta2(conn))
print('*'*50)

print("\nConsulta 3: La distribución de abogados en función de su gasto anual y de su sexo se ve así:\n")
consulta3(conn)
print('*'*50)

print("\nConsulta 4: ¿Cuál es la relación entre la profesión y el puntaje de gasto?. \nExisten ciertas profesiones que tienden a tener un puntaje de gasto más alto o más bajo\n")
consulta4(conn)
print('\nSe puede observar que no existe una diferencia demasiado notoria en el puntaje \nde gasto entre las diferentes profesiones, aunque hay una variación muy amplia. \nSolo se destaca que las personas "Homemaker" tienen los rangos más bajos.')
print('*'*50)

conn.close()


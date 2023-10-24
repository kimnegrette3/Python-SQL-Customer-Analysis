
import pandas as pd
import numpy as np

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
    Replace values with 0.00 for null values in the column Age
    """
    df['age'] = df['age'].replace(0.00, np.nan)
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
    columns_to_lowercase = ['profession', 'gender']
    df = columns_to_lowercase(df, columns_to_lowercase)

    print("Checking for missing values...")
    print(check_missing_values(df))

    print("\nImputing missing values in column 'profession' with the mode... ")
    df = impute_missing_values(df, 'profession')

    print("\nImputting missing values in column 'age' with the mode...")
    df = replace_values_age(df)
    df = impute_missing_values(df, 'age')
    
    return df

# Carga de los datos desde github
dataset_url = "https://raw.githubusercontent.com/kimnegrette3/Python-SQL-Customer-Analysis/main/customers.csv"
customers = pd.read_csv(dataset_url)

# Limpieza y transformación de los datos
cleaned_data = clean_data(customers.copy())
cleaned_data.head()
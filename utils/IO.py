import pandas as pd
import os
import unicodedata

class IO:
    def __init__(self):
        i = 0

    def read_csv(self, file_path, separator, decimal, encoding):
        """
        Read CSV file from given path
        """
        return pd.read_csv(file_path, sep=separator, decimal=decimal, encoding=encoding)
    

    def create_csv(self, output_df, file_name):
        """
        Creates CSV or Excel from dataframe
        """
        try:
            output_df.to_csv(file_name + '.csv', sep=';', index=False, encoding='latin-1', columns=output_df.columns, decimal=',')
        except UnicodeEncodeError as ex:
            print("ERROR al crear CSV, intentamos con excel...", ex)
            output_df.to_excel(file_name + '.xlsx') 


    def create_CSV_from_list(self, list_of_objects, columns_name, file_name):
        """Crea un archivo CSV usando a partir de una lista de objetos usando pandas. Utiliza ';' como separador.

        Parametros:
        list_of_objects -- Lista de objetos que se exportaran en el fichero CSV
        columns_name -- Nombres para las columnas del CSV
        file_name -- Nombre del fichero CSV (sin incluir la terminacion .csv)
        """
        output_data = self.create_dataframe(list_of_objects, columns_name)
        try:
            output_data.to_csv(file_name + '.csv', sep=';', index=False, encoding='latin-1', columns=columns_name, decimal=',')
        except UnicodeEncodeError:
            print("ERROR al crear CSV, intentamos con excel...")
            output_data.to_excel(file_name + '.xlsx') 
        return output_data


    def create_dataframe(self, list_of_objects, columns_name):
        """
        Creates Datafame

        Parametros:
        list_of_objects -- Lista de objetos que se exportaran en el fichero CSV
        columns_name -- Nombres para las columnas del CSV

        Output:
        Dataframe Object
        """
        return pd.DataFrame(list_of_objects, columns=columns_name)
    

    def cluster_dataframe_by_condition(self, input_dataframe, condition):
        """Crea una lista con los DataFrame que cumplen una condicion dada.

        Parametros:
        input_dataframe -- Objeto DataFrame de entrada sobre el que se itera para conformar la lista
        condition -- Condicion por la que filtrar los elementos que se a�aden a la lista

        Devuelve:
        Una lista con los DataFrame que cumplen la condicion.
        """
        clustered_dataframes_list = list()
        for i in input_dataframe[condition].unique():
            clustered_dataframes_list.append(input_dataframe[input_dataframe[condition] == i])
        return clustered_dataframes_list
    

    def remove_accents(self, input_str):
        """
        Removes accents from a string.

        Parameters:
        input_str (str): The string from which accents are to be removed.

        Returns:
        str: The string without accents.
        """
        # Normalize the string and then remove diacritic marks
        nfkd_form = unicodedata.normalize('NFKD', input_str)
        return "".join([c for c in nfkd_form if not unicodedata.combining(c)])

    
    def remove_non_alpha_numeric_str(self, input_string):
        """Remove all non alphanumeric character in string

        Parametros:
        input_string -- String con caracteres no alfanumericos
        """
        mod_string = ""
        for elem in input_string:
            if elem.isalnum() or elem == ' ':
                mod_string += elem
        result_string = mod_string
        result_string = result_string.replace('  ', ' ')
        return result_string


    def create_folder_if_not_exist(self, folder_path):
        """
        Create Folder if not exists in given folder_path
        """
        path = os.path.join(folder_path)
        isExist = os.path.exists(path)
        if not isExist:
            os.mkdir(path)
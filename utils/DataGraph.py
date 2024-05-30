import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np
import base64
from io import BytesIO

class DataGraph:
    def __init__(self):
        i = 0

    def create_matplotlib_graph(self, routes_ids, routes_items, max_width_pop_up):
        """Crea un gráfico generado con matplotlib y seaborn
        que muestra el peso por ruta en un gráfico de barras horizontal.

        Inputs:
        routes_ids -- (list) Contiene la información de los ids de las rutas.
        routes_items -- (list) Contiene la información del peso de las rutas.
        max_width_pop_up -- (int) Valor que representa en pixeles el ancho del gráfico.

        Return:
        matplotlib_img_html -- (str) Imagen codificada en base64 en formato html.
        """
        # Organizar los datos
        data = pd.DataFrame({
            'Route ID': routes_ids,
            'Items': routes_items
        })

        # Ordenar y limitar a las rutas más pesadas
        top_n = 100
        data_sorted = data.sort_values('Items', ascending=False)
        top_data = data_sorted.head(top_n)
        other_weight = data_sorted.tail(len(data_sorted) - top_n)['Items'].sum()
        other_data = pd.DataFrame({'Route ID': ['Other'], 'Items': [other_weight]})
        top_data = pd.concat([top_data, other_data], ignore_index=True)

        # Crear gráfico de barras horizontal
        plt.figure(figsize=(10, 14))  # Aumentar el segundo valor según sea necesario.
        bar_plot = sns.barplot(
            x='Items',
            y='Route ID',
            data=top_data,
            hue='Route ID',  # Asignar hue a la variable 'Route ID'
            dodge=False,     # Esto mantiene las barras del mismo color juntas sin espaciado entre ellas
            legend=False,    # No mostrar la leyenda ya que hue se usa solo para la coloración
            palette='tab20'  # Usar el mismo esquema de colores como antes
        )

        # Añadir el peso total en las barras
        for index, value in enumerate(top_data['Items']):
            plt.text(value, index, f'{value} Items')

        # Configurar detalles del gráfico
        plt.xlabel('Paradas totales')
        plt.ylabel('Rutas')
        plt.title('Distribución de Peso por Ruta')
        plt.tight_layout()

        # Guardar el gráfico en un buffer
        buffer = BytesIO()
        plt.savefig(buffer, format='png')
        buffer.seek(0)

        # Convertir el PNG buffer a una cadena codificada en base64
        data_uri = base64.b64encode(buffer.read()).decode('utf-8')
        matplotlib_img_html = f'<img src="data:image/png;base64,{data_uri}" style="max-width:{max_width_pop_up}px;"/>'

        # Cerrar el buffer y la figura de matplotlib
        buffer.close()
        plt.close()

        return matplotlib_img_html


    def create_matplotlib_graph5(self, routes_ids, routes_items, max_width_pop_up):
        # Organizar los datos
        data = pd.DataFrame({
            'Route ID': routes_ids,
            'Weight': routes_items
        })

        # Ordenar por peso de forma descendente
        data_sorted = data.sort_values('Weight', ascending=False)

        # Calcular el peso acumulativo
        cumulative_weight = np.cumsum(data_sorted['Weight'])

        # Crear el gráfico de líneas acumulativo
        plt.figure(figsize=(14, 7))  # Tamaño más grande para mejorar la legibilidad
        plt.plot(data_sorted['Route ID'], cumulative_weight, marker='o', color='blue')

        # Añadir etiquetas en puntos clave (puedes ajustar esto según sea necesario)
        for i, (idx, val) in enumerate(zip(data_sorted['Route ID'], cumulative_weight)):
            if i % 10 == 0:  # Añadir una etiqueta cada 10 rutas
                plt.text(idx, val, f'{val:.0f}', fontsize=8)

        plt.xticks(rotation=90, fontsize=8)  # Rotar etiquetas del eje x para mejorar la legibilidad
        plt.xlabel('Rutas', fontsize=20)
        plt.ylabel('Peso acumulado', fontsize=20)
        plt.title('Peso Acumulativo por Ruta')
        plt.tight_layout()

        # Guardar el gráfico en un buffer
        buffer = BytesIO()
        # plt.savefig(buffer, format='png', bbox_inches='tight')  # 'bbox_inches' para incluir etiquetas
        plt.savefig(buffer, format='png')  # 'bbox_inches' para incluir etiquetas
        buffer.seek(0)

        # Convertir el buffer PNG a cadena codificada en base64
        data_uri = base64.b64encode(buffer.read()).decode('utf-8')
        matplotlib_img_html = f'<img src="data:image/png;base64,{data_uri}" style="max-width:{max_width_pop_up}px;"/>'

        # Cerrar buffer y figura
        buffer.close()
        plt.close()

        return matplotlib_img_html


    def create_matplotlib_graph4(self, routes_ids, routes_items, max_width_pop_up):
        # Organizar los datos
        data = pd.DataFrame({
            'Route ID': routes_ids,
            'Items': routes_items
        })

        # Ordenar los datos por peso para el gráfico acumulativo
        data_sorted = data.sort_values('Items', ascending=False)
        data_sorted['Cumulative Weight'] = data_sorted['Items'].cumsum()

        # Crear gráfico acumulativo
        plt.figure(figsize=(12, 8))
        plt.barh(data_sorted['Route ID'], data_sorted['Cumulative Weight'], color='skyblue')
        plt.xlabel('Peso acumulado')
        plt.ylabel('Ruta')

        # Añadir anotaciones de peso en las barras
        for index, value in enumerate(data_sorted['Cumulative Weight']):
            plt.text(value, index, f'{value} Kg')

        plt.title('Peso Acumulado por Ruta')
        plt.gca().invert_yaxis()  # Invierte el eje y para mostrar la barra con mayor peso en la parte superior
        plt.tight_layout()

        # Guardar el gráfico en un buffer
        buffer = BytesIO()
        plt.savefig(buffer, format='png')
        buffer.seek(0)

        # Convertir el PNG buffer a una cadena codificada en base64
        data_uri = base64.b64encode(buffer.read()).decode('utf-8')
        matplotlib_img_html = f'<img src="data:image/png;base64,{data_uri}" style="max-width:{max_width_pop_up}px;"/>'

        # Cerrar el buffer y la figura de matplotlib
        buffer.close()
        plt.close()

        return matplotlib_img_html

    def create_matplotlib_graph2(self, routes_ids, routes_items, max_width_pop_up):
        """Crea un grafico generado con matplolib y/o seaborn
        
        Inputs:
        routes_ids -- (list) Contiene la informacion de los ids de las rutas
        routes_items -- (list) Contiene la informacion de los items de las rutas
        max_width_pop_up -- Valor que representa en pixeles el ancho del grafico

        Return:
        matplotlib_img_html -- (str) Imagen codificada en base64 en formato html
        """
        total_weight = sum(routes_items)  # Calcula el peso total

        # Crear gráfico de dona
        fig, ax = plt.subplots()
        ax.pie(routes_items, labels=routes_ids, autopct='%1.1f%%', startangle=90, pctdistance=0.85, colors=plt.cm.tab20.colors)

        # Dibuja un círculo en el centro para convertir el gráfico de pastel en dona
        centre = plt.Circle((0,0),0.70,fc='white')
        fig = plt.gcf()
        fig.gca().add_artist(centre)

        # Opcional: Añadir el peso total en el centro
        plt.text(0, 0, f'Total\n{total_weight} Items', ha='center', va='center')

        # Save the chart to a BytesIO buffer
        buffer = BytesIO()
        plt.savefig(buffer, format='png')
        buffer.seek(0)

        # Convert the PNG buffer to a base64 encoded string
        data_uri = base64.b64encode(buffer.read()).decode('utf-8')
        matplotlib_img_html = f'<img src="data:image/png;base64,{data_uri}" style="max-width:{max_width_pop_up}px;"/>'
        
        # Cerramos buffer, sin esta linea, la segunda imagen tendra el contenido de la segunda mas el de la primera, la tercera el de la tercera, la segunda y la primera...
        buffer.close() 
        plt.close()
        return matplotlib_img_html
            

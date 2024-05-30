# Meta-Heuristic Optimization Framework for CVRP
The Meta-Heuristic Optimization Framework is an advanced, Python-based software library designed to address the complexities of the Capacitated Vehicle Routing Problem (CVRP). By integrating state-of-the-art optimization strategies and heuristic algorithms, this tool facilitates the development of optimized routing solutions that meticulously observe vehicle capacity limitations and customer requirements.

## Key Features
- Sophisticated Heuristics: Incorporates cutting-edge algorithms such as Nearest Neighbor, Or-Tools and own heuristics to construct initial and viable solutions.
- Clustering Techniques: Contains various clustering techniques such as K-means Clustering and  Hierarchical Clustering.
- Advanced Optimization Techniques: Employs enhanced route optimization methodologies, including Clarke y Wright, 2-opt, 3-opt, and Lin-Kernighan heuristics, to refine solutions.
- Interactive Web Application: Features a built-in Flask web application for dynamic visualization of routing plans and distribution of nodes on interactive maps.
- High Scalability: Optimized for processing extensive datasets, capable of efficiently managing thousands of nodes with multiple constraints.
- Comprehensive Data Visualization: Utilizes a wide array of visualization libraries such as Matplotlib, Seaborn, and Plotly for in-depth data analysis.
- Geospatial Analysis Tools: Integrates Folium for creating engaging map visuals, along with GeoPy and Shapely for detailed geospatial data analysis.

## Installation Guide
To install the Meta-Heuristic Optimization Framework, please follow these steps:

```bash
git clone https://github.com/artuloda/meta-tool-test.git
cd meta-tool-test
pip install -r requirements.txt
```

## Flask Application
This framework includes a Flask-based web application for the interactive exploration and management of CVRP solutions.

#### Key Web Application Features:
- Home: Basic introduction and navigation.
- Clients: Displays customer details.
- Vehicles: Displays vehicles details.
- Map: Interactive map for route visualization.
- Graph: Dynamic graph representation of routing solutions.

```python
# app.py
from flask import Flask, render_template, jsonify
import main

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/clientes')
def clientes():
    return render_template('clientes.html', data=main.nodes_df)

@app.route('/vehiculos')
def vehiculos():
    return render_template('vehiculos.html', vehicle_data=main.fleet_df)

@app.route('/mapa')
def mapa():
    return render_template('map.html')

@app.route('/graph')
def graph():
    return render_template('graph.html')

@app.route('/graph/data')
def graph_data():
    return jsonify(main.result_graph_json)

if __name__ == '__main__':
    nodes_df, fleet_df, result_df, result_graph_json = main.main()
    app.run()
````

Running the Flask Application:
```bash
python app.py
```
Navigate to http://localhost:5000/ in your web browser to access the application.

## License
Distributed under the MIT License. See LICENSE for more information.

## Contact
Should you have any inquiries or require further information, please contact Arturo López-Damas Oliveres via - [@artuloda](https://github.com/artuloda)

Explore the project on GitHub: [Meta-Heuristic Optimization Framework for CVRP](https://github.com/artuloda/meta-tool-test)

## Python Libraries Used
- [Flask](https://flask.palletsprojects.com/en/3.0.x/)
- [NumPy](https://numpy.org/doc/stable/)
- [Pandas](https://pandas.pydata.org/docs/)
- [Scikit-Learn](https://scikit-learn.org/stable/auto_examples/index.html)
- [NetworkX](https://networkx.org/documentation/stable/reference/index.html)
- [Folium](https://python-visualization.github.io/folium/latest/user_guide.html)
- [Matplotlib](https://matplotlib.org/stable/plot_types/basic/index.html)
- [Seaborn](https://seaborn.pydata.org/)
- [Plotly](https://plotly.com/examples/)
- [Shapely](https://shapely.readthedocs.io/en/stable/)
- [GeoPy](https://geopy.readthedocs.io/en/stable/)
- [OR-Tools CVRP](https://developers.google.com/optimization/routing/routing_options?hl=es-419)



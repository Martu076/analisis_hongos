from http.server import BaseHTTPRequestHandler, HTTPServer
import json
import pandas as pd
import sklearn
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
import os

# Ruta al archivo CSV
ruta = r'D:\mushrooms\hongos.csv'

class RequestHandler(BaseHTTPRequestHandler):

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

    def do_POST(self):
        # Permitir CORS
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Content-Type', 'application/json')
        self.end_headers()

        # Obtener los datos enviados (en formato JSON)
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        data = json.loads(post_data)

        # Cargar el dataset
        hongos = pd.read_csv(ruta, sep= ";")
    
        # Realizar One-Hot Encoding usando pandas
        hongos_codificado = pd.get_dummies(hongos, drop_first=False)

        # Descatar la columna 'clase_Comestible'
        hongos_codificado.drop('clase_Comestible', axis=1, inplace=True)

        # Separar las características (X) de la etiqueta (y)
        X = hongos_codificado.drop('clase_Venenoso', axis=1)  # Todo menos si es venenoso o no
        y = hongos_codificado['clase_Venenoso']  # Clase a predecir

        # Dividir en entrenamiento y prueba
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42)

        # Crear un modelo (puedes usar otros como SVM, KNN, etc.)
        model = RandomForestClassifier(n_estimators=100, random_state=42)

        # Entrenar el modelo
        model.fit(X_train, y_train)

        # Función para convertir las respuestas del usuario a One-Hot Encoding
        def generar_one_hot(respuestas):
            one_hot_columns = {
                'forma-del-sombrero': ['Abultada', 'Campana', 'Conica', 'Convexa', 'Hundida', 'Plana'],
                'superficie-del-sombrero': ['Con surcos', 'Escamosa', 'Fibrosa', 'Lisa'],
                'color-del-sombrero': ['Amarillo', 'Amarillo claro', 'Blanco', 'Canela', 'Gris', 'Marron', 'Morado', 'Rojo', 'Rosa', 'Verde'],
                'lastimaduras': ['No', 'Si'],
                'olor': ['Almendra', 'Anis', 'Cresol', 'Especiado', 'Fetido', 'Mofeta', 'Ninguno', 'Pescado', 'Pungente'],
                'union-laminas': ['Libres', 'Unidas' ],
                'separacion-laminas': ['Aglomeradas', 'Cercanas'],
                'tamano-laminas': ['Anchas', 'Estrechas'],
                'color-laminas': ['Amarillo', 'Amarillo claro', 'Blanco', 'Chocolate', 'Gris', 'Marron', 'Morado', 'Naranja', 'Negro', 'Rojo', 'Rosa', 'Verde'],
                'forma-tallo': ['Agrandado', 'Enflaquecido'],
                'raiz-tallo': ['Bulbosa', 'Clava', 'Con raiz', 'Desaparecida' ,'Igual'],
                'superficie-tallo-arriba-del-anillo': ['Escamosa', 'Fibrosa', 'Lisa', 'Sedosa'],
                'superficie-tallo-debajo-del-anillo': ['Escamosa', 'Fibrosa', 'Lisa', 'Sedosa'],
                'color-tallo-arriba-del-anillo': ['Amarillo', 'Amarillo claro', 'Blanco', 'Canela', 'Gris', 'Marron', 'Naranja', 'Rojo', 'Rosa'],
                'color-tallo-debajo-del-anillo': ['Amarillo', 'Amarillo claro', 'Blanco', 'Canela', 'Gris', 'Marron', 'Naranja', 'Rojo', 'Rosa'],
                'tipo-de-velo': ['Parcial', 'Universal'],
                'color-del-velo': ['Amarillo' , 'Blanco', 'Marron', 'Naranja'],
                'numero-de-anillos': ['Dos', 'Ninguno', 'Uno'],
                'tipo-de-anillos': ['Colgante', 'En expansion','Evanescente',  'Grande', 'Ninguno'],
                'color-impresion-de-esporas': [ 'Amarillo', 'Amarillo claro' , 'Blanco' , 'Chocolate', 'Marron', 'Morado' , 'Naranja'  , 'Negro' ,   'Verde'],
                'poblacion': ['Abundante', 'Agrupada', 'Dispersa', 'Numerosa', 'Solitaria' , 'Varia'],
                'habitat': ['Basura',  'Bosques', 'Caminos', 'Hierbas', 'Hojas', 'Praderas',  'Urbano'],
            }

            one_hot_data = {}
            for columna, opciones in one_hot_columns.items():
                for opcion in opciones:
                    one_hot_data[f'{columna}_{opcion}'] = [1 if respuestas.get(columna) == opcion else 0 for _ in range(1)]

            return pd.DataFrame(one_hot_data)

        # Convertir las respuestas del usuario a One-Hot Encoding
        nuevos_datos = generar_one_hot(data)

        nuevos_datos.columns = nuevos_datos.columns.str.replace('tamaÃ±o', 'tamaño')

        # Guardar las respuestas One-Hot Encoding como un archivo CSV
        def guardar_respuestas_csv(respuestas_one_hot):
            # Definir la ruta donde guardar el CSV
            carpeta_data = os.path.dirname(ruta)  # Carpeta de la data del modelo
            ruta_csv = os.path.join(carpeta_data, 'respuestas_one_hot.csv')
            # Guardar las respuestas One-Hot como CSV
            respuestas_one_hot.to_csv(ruta_csv, index=False)
            return ruta_csv

        # Guardar el CSV
        csv_path = guardar_respuestas_csv(nuevos_datos)

        # Obtener las columnas del modelo
        columnas_esperadas = X.columns

        # Reindexar los datos nuevos para que coincidan con las columnas del modelo
        nuevos_datos = nuevos_datos.reindex(columns=columnas_esperadas, fill_value=0)

        # Realizar la predicción con el modelo entrenado
        prediccion = model.predict(nuevos_datos)

        # Devolver la predicción al frontend
        if prediccion[0] == 1:
            resultado = "El hongo es venenoso"
        else:
            resultado = "El hongo es comestible"
        
        # Enviar el resultado y la ruta del archivo CSV al frontend
        response = json.dumps({
            'prediction': resultado,
            'csv_file': csv_path  # Esto incluirá la ruta del archivo CSV generado
        })
        self.wfile.write(response.encode())

# Configurar el servidor
server_address = ('', 8080)
httpd = HTTPServer(server_address, RequestHandler)
print("Servidor corriendo en http://localhost:8080")
httpd.serve_forever()

# Usar una imagen base de Python
FROM python:3.9-slim

# Establecer el directorio de trabajo dentro del contenedor
WORKDIR /app

# Copiar los archivos necesarios (scripts y archivo CSV) al contenedor
COPY . .

# Instalar las dependencias de Python desde requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Exponer el puerto 8080, donde escuchará el servidor
EXPOSE 8080

# Comando para ejecutar el servidor HTTP
CMD ["python", "app.py"]

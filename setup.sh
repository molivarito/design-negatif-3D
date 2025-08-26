#!/bin/bash

ENV_NAME="cq-env"
PYTHON_CMD="python3"

echo "Buscando Python 3..."
if ! command -v $PYTHON_CMD &> /dev/null
then
    echo "Error: Python 3 no está instalado o no se encuentra en el PATH."
    exit 1
fi

echo "Creando entorno virtual '$ENV_NAME'..."
if [ ! -d "$ENV_NAME" ]; then
    $PYTHON_CMD -m venv $ENV_NAME
    echo "Entorno virtual creado."
else
    echo "El entorno virtual '$ENV_NAME' ya existe."
fi

echo "Instalando dependencias desde requirements.txt..."
./$ENV_NAME/bin/pip install -r requirements.txt

echo ""
echo "--------------------------------------------------"
echo "¡Instalación completada!"
echo ""
echo "Para activar el entorno virtual, ejecuta:"
echo "source $ENV_NAME/bin/activate"
echo "--------------------------------------------------"
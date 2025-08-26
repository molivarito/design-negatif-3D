# Generador 3D de Resonadores con GUI

Este proyecto es una aplicación de escritorio con una Interfaz Gráfica de Usuario (GUI) para el diseño paramétrico de resonadores cilíndricos con un objeto interno de forma compleja. La aplicación permite al usuario definir las dimensiones del resonador, seleccionar la forma y el tamaño del objeto interno, y visualizar el modelo 3D en tiempo real. Además, ofrece la funcionalidad de exportar las geometrías generadas a formato STL para su uso en software de simulación o para impresión 3D.

 

 
## Características Principales

- **Diseño Paramétrico:** Todos los aspectos de la geometría se controlan mediante parámetros numéricos en la GUI.
- **Resonador Principal:** Genera un resonador cilíndrico hueco definiendo su largo, diámetro interno y espesor de pared.
- **Objeto Interno Complejo:** Permite insertar un objeto a lo largo del resonador con diferentes formas de sección transversal:
  - Elipse
  - Estrella
  - Polígono Regular
- **Control de Área:** El tamaño del objeto interno se define por la relación entre su área de sección transversal (S2) y el área de la cavidad interna del resonador (S1).
- **Tapa a Medida:** Genera una tapa que encaja en el resonador, con parámetros para el espesor de pared y la profundidad de la cavidad.
- **Análisis de Sección Transversal:** Calcula y muestra en tiempo real las áreas de material del resonador, del objeto interno y el área neta resultante.
- **Cilindro Equivalente:** Genera un cilindro hueco simple cuya geometría está relacionada con el área de material neta del diseño complejo, útil para análisis comparativos.
- **Visualización 3D Interactiva:** Utiliza PyVista para renderizar los modelos 3D, permitiendo rotar, hacer zoom y panear. Los diferentes componentes (resonador, objeto interno, tapa, etc.) se muestran por separado para mayor claridad.
- **Exportación a STL:** Guarda todos los componentes generados como archivos `.stl` individuales con un solo clic, listos para ser utilizados en otros programas.

## Tecnologías Utilizadas

- **Python 3:** Lenguaje de programación principal.
- **PyQt5:** Para la construcción de la interfaz gráfica de usuario.
- **CadQuery 2:** Para el modelado CAD paramétrico y robusto de las geometrías 3D.
- **PyVista:** Para la visualización 3D de alto rendimiento integrada en la aplicación Qt.
- **NumPy:** Para los cálculos numéricos y geométricos.

## Instalación

Este proyecto utiliza un entorno virtual de Python para gestionar las dependencias de forma aislada. Se han incluido scripts para automatizar la configuración.

1.  **Clona o descarga el repositorio.**

2.  **Ejecuta el script de instalación correspondiente a tu sistema operativo:**

    -   **En Windows:**
        Haz doble clic en el archivo `setup.bat`.

    -   **En macOS o Linux:**
        Abre una terminal, dale permisos de ejecución al script y córrelo:
        ```bash
        chmod +x setup.sh
        ./setup.sh
        ```
    Estos scripts crearán automáticamente un entorno virtual llamado `cq-env` e instalarán todas las librerías necesarias listadas en `requirements.txt`.

## Uso

1.  **Activa el entorno virtual.**
    -   En Windows: `.\cq-env\Scripts\activate`
    -   En macOS/Linux: `source cq-env/bin/activate`

Para ejecutar la aplicación, simplemente corre el script de Python desde tu terminal:

```bash
python generador_3d_gui.py
```

### Interfaz de Usuario

La interfaz se divide en varias secciones:

- **Parámetros del Resonador:** Define las dimensiones principales del cilindro hueco exterior.
- **Objeto Interno:**
  - **Forma:** Selecciona entre "Elipse", "Estrella" o "Polígono". Los paneles de parámetros específicos para cada forma aparecerán o desaparecerán automáticamente.
  - **Ratio de Área (S2/S1):** Controla el tamaño del objeto interno relativo al hueco del resonador.
- **Parámetros de la Tapa:** Define las dimensiones de la tapa que se ajusta al diámetro exterior del resonador.
- **Análisis de Sección Transversal:** Muestra los valores calculados de las áreas, lo que permite verificar el diseño antes de exportarlo.
- **Botones de Acción:**
  - **Actualizar Vista 3D:** Aplica todos los parámetros actuales, regenera las geometrías y actualiza el visor 3D.
  - **Guardar Archivos STL...:** Abre un diálogo para guardar. Se generará un conjunto de archivos STL basados en el nombre que elijas (e.g., `diseño_resonador_hueco.stl`, `diseño_tapa_sola.stl`, etc.).

## Estructura del Código (`generador_3d_gui.py`)

- **Clase `App(QMainWindow)`:** La clase principal que contiene toda la lógica de la aplicación.
  - `__init__(self)`:
    - Inicializa la ventana principal.
    - Crea y organiza todos los widgets de la GUI (spin boxes, botones, selectores) usando layouts de PyQt5.
    - Instancia el `QtInteractor` de PyVista para la visualización 3D.
    - Conecta las señales de los widgets (e.g., `clicked` de un botón) a los slots (métodos) correspondientes.
  - `_on_shape_change(self)`: Método para actualizar la visibilidad de los paneles de parámetros según la forma del objeto interno seleccionada.
  - `_generate_geometry_cq(self)`:
    - Es el corazón del programa. Lee todos los valores de los widgets de la GUI.
    - Realiza los cálculos matemáticos para determinar las dimensiones de las formas (e.g., radios de la elipse, puntas de la estrella).
    - Utiliza `CadQuery` para construir los objetos 3D (`resonator_cq`, `inner_object_cq`, `cap_cq`, etc.).
    - Calcula y actualiza las etiquetas de área en la GUI.
  - `update_plot(self)`:
    - Llama a `_generate_geometry_cq` para crear o actualizar los modelos.
    - Limpia el visor de PyVista.
    - Muestra cada objeto `CadQuery` en el visor. Para ello, exporta temporalmente cada objeto a un archivo STL que PyVista puede leer. Los objetos se trasladan en el espacio para que no se superpongan en la vista.
  - `save_stl(self)`:
    - Abre un diálogo de guardado de archivos.
    - Exporta cada uno de los objetos `CadQuery` a un archivo STL con un nombre descriptivo.

## Licencia

Este proyecto no especifica una licencia. Puedes añadir un archivo `LICENSE` si lo deseas (e.g., MIT, GPL).
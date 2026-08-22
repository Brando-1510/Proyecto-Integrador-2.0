# Documentación del Proyecto Integrador 2.0
## 1. Estructura del Proyecto
La organización de directorios del proyecto es la siguiente:

```
Proyecto-Integrador-2.0/
├── .vscode/
│   └── tasks.json
├── app/
│   ├── resources/
│   │   ├── resources.qrc
│   │   ├── images/
│   │   └── icons/
│   ├── generated/
│   │   └── resources_rc.py
│   └── main.py
├── requirements.txt
└── indications.md
```
## 2. Preparación del Entorno
Entorno Virtual: Antes de trabajar, asegúrate de activar el entorno virtual. En Windows PowerShell: 
`.\venv\Scripts\Activate.ps1.`

Dependencias: Si es la primera vez que configuras el proyecto, instala las dependencias necesarias ejecutando: ```pip install -r requirements.txt```

## 3. Ejecución
Existen dos formas de iniciar la aplicación:

VS Code (Recomendado): Presiona Ctrl + Shift + B y selecciona "Ejecutar Proyecto".

Terminal: Ejecuta manualmente el comando: python -m app.main.

## 4. Gestión de Recursos (Qt)
Los iconos e imágenes utilizados por la interfaz se gestionan a través de archivos .qrc.

Flujo para agregar nuevos recursos
Cuando necesites añadir un icono o imagen:

Coloca el archivo en el directorio correspondiente dentro de app/resources/ (ya sea en icons/ o images/).

Añade la ruta del nuevo archivo al archivo app/resources/resources.qrc.

Regenera el archivo de recursos ejecutando en la terminal:

```
pyside6-rcc app/resources/resources.qrc -o app/generated/resources_rc.py
```
**Reglas para recursos**
Archivo Autogenerado: El archivo app/generated/resources_rc.py es generado automáticamente por pyside6-rcc. Nunca lo modifiques manualmente.

Modificaciones: Cualquier cambio en los recursos debe realizarse editando app/resources/resources.qrc y posteriormente ejecutando el comando de regeneración mencionado arriba.

Git: Al realizar cambios, asegúrate de incluir tanto resources.qrc como el nuevo resources_rc.py en tus commits (git add .).

5. Configuración de VS Code (.vscode/tasks.json)
Para que el comando Ctrl + Shift + B funcione, el archivo .vscode/tasks.json debe tener la siguiente configuración:

```
{
    "version": "2.0.0",
    "tasks": [
        {
            "label": "Ejecutar Proyecto",
            "type": "shell",
            "command": "python -m app.main",
            "group": {
                "kind": "build",
                "isDefault": true
            },
            "presentation": {
                "reveal": "always",
                "panel": "shared",
                "focus": false
            },
            "problemMatcher": []
        }
    ]
}
```
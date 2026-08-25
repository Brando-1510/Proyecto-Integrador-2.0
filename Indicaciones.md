# Indicaciones del Proyecto Integrador 2.0

## 1. Estructura del Proyecto
La organización principal de directorios del proyecto es la siguiente:
```text
Proyecto-Integrador-2.0/
│
├── .vscode/
│   └── tasks.json
│
├── app/
│   ├── resources/
│   │   ├── resources.qrc
│   │   ├── images/
│   │   └── icons/
│   │
│   ├── generated/
│   │   └── resources_rc.py
│   │
│   └── main.py
│
├── requirements.txt
│
└── indications.md
```

### Descripción de los directorios principales

* `.vscode/`: contiene configuraciones y tareas específicas de Visual Studio Code.
* `app/`: contiene el código principal de la aplicación.
* `app/resources/`: contiene los recursos utilizados por la interfaz gráfica, como imágenes e iconos.
* `app/generated/`: contiene archivos generados automáticamente, como `resources_rc.py`.
* `requirements.txt`: contiene las dependencias necesarias para ejecutar el proyecto.
* `indications.md`: contiene las instrucciones generales para configurar y ejecutar el proyecto.

---

## 2. Preparación del Entorno

### 2.1. Crear el entorno virtual

Se recomienda trabajar utilizando un entorno virtual para mantener aisladas las dependencias del proyecto.

Desde la raíz del proyecto, en Windows PowerShell:

```powershell
python -m venv venv
```

### 2.2. Activar el entorno virtual

En Windows PowerShell:

```powershell
.\venv\Scripts\Activate.ps1
```

Una vez activado, debería aparecer `(venv)` al inicio de la terminal.

### 2.3. Instalar las dependencias

Si es la primera vez que se configura el proyecto, instalar las dependencias mediante:

```powershell
pip install -r requirements.txt
```

---

## 3. Gestión de Dependencias

Todas las librerías externas utilizadas por el proyecto deben registrarse en `requirements.txt`.

### 3.1. Cuando se agregue un nuevo paquete

Cada vez que un integrante instale una nueva dependencia necesaria para el proyecto, debe actualizar `requirements.txt`.

Por ejemplo, si se instala un paquete mediante:

```powershell
pip install sqlalchemy
```

se debe actualizar posteriormente el archivo `requirements.txt`.

La forma recomendada es:

```powershell
pip freeze > requirements.txt
```

Esto actualizará el archivo con las dependencias instaladas en el entorno virtual.

### 3.2. Antes de realizar un commit

Si se agregó, eliminó o actualizó alguna dependencia:

1. Verificar que el paquete esté incluido en `requirements.txt`.
2. Comprobar que el proyecto continúe funcionando.
3. Incluir `requirements.txt` en el commit.

Ejemplo:

```powershell
git add requirements.txt
git commit -m "chore: actualizar dependencias"
```

### 3.3. Regla importante

**No se debe instalar una dependencia nueva y realizar un commit sin actualizar `requirements.txt`.**

Esto permite que cualquier integrante pueda configurar el proyecto ejecutando únicamente:

```powershell
pip install -r requirements.txt
```

---

## 4. Ejecución del Proyecto

Existen dos formas principales de iniciar la aplicación.

### 4.1. Desde Visual Studio Code

Se recomienda ejecutar el proyecto desde Visual Studio Code mediante:

**Ctrl + Shift + B**

Luego seleccionar:

```text
Ejecutar Proyecto
```

Esta tarea ejecutará:

```powershell
python -m app.main
```

### 4.2. Desde la terminal

También es posible ejecutar manualmente el proyecto desde la raíz:

```powershell
python -m app.main
```

Antes de ejecutar, asegúrate de que el entorno virtual esté activado.

---

## 5. Gestión de Recursos de Qt

Los iconos e imágenes utilizados por la interfaz gráfica se administran mediante archivos `.qrc` de Qt.

El archivo principal de recursos es:

```text
app/resources/resources.qrc
```

Los recursos se encuentran organizados principalmente en:

```text
app/resources/
├── images/
└── icons/
```

### 5.1. Agregar un nuevo recurso

Cuando se necesite agregar una nueva imagen o icono:

1. Colocar el archivo dentro del directorio correspondiente:

   * `app/resources/images/` para imágenes.
   * `app/resources/icons/` para iconos.

2. Agregar la ruta del archivo en:

```text
app/resources/resources.qrc
```

3. Regenerar el archivo de recursos ejecutando:

```powershell
pyside6-rcc app/resources/resources.qrc -o app/generated/resources_rc.py
```

4. Verificar que la aplicación continúe funcionando correctamente.

### 5.2. Reglas para los recursos

El archivo:

```text
app/generated/resources_rc.py
```

es un archivo **generado automáticamente** por `pyside6-rcc`.

**Nunca debe modificarse manualmente.**

Cualquier modificación relacionada con imágenes o iconos debe realizarse en:

```text
app/resources/
```

y/o:

```text
app/resources/resources.qrc
```

Posteriormente se debe ejecutar nuevamente:

```powershell
pyside6-rcc app/resources/resources.qrc -o app/generated/resources_rc.py
```

### 5.3. Git

Cuando se agreguen o modifiquen recursos, se deben incluir en el commit:

```text
resources.qrc
```

y

```text
resources_rc.py
```

Además, deben incluirse los nuevos archivos de imágenes o iconos.

Ejemplo:

```powershell
git add app/resources/ app/generated/resources_rc.py
git commit -m "feat: agregar nuevos recursos gráficos"
```

---

## 6. Configuración de Visual Studio Code

Para que la combinación:

```text
Ctrl + Shift + B
```

ejecute automáticamente el proyecto, el archivo:

```text
.vscode/tasks.json
```

debe contener una configuración similar a la siguiente:

```json
{
    "version": "2.0.0",
    "tasks": [
        {
            "label": "Ejecutar Proyecto",
            "type": "shell",
            "command": "${workspaceFolder}\\venv\\Scripts\\python.exe",
            "args": [
                "-m",
                "app.main"
            ],
            "options": {
                "cwd": "${workspaceFolder}"
            },
            "group": {
                "kind": "build",
                "isDefault": true
            },
            "problemMatcher": []
        }
    ]
}
```

La tarea configurada como `isDefault: true` será la que se ejecute al utilizar:

```text
Ctrl + Shift + B
```

---

## 7. Flujo de Trabajo Recomendado

Para evitar problemas entre los integrantes del equipo, se recomienda seguir este flujo al realizar cambios:

### Si se modifica el código

1. Realizar los cambios.
2. Ejecutar y probar la aplicación.
3. Verificar que no existan errores.
4. Realizar el commit.

### Si se agrega un recurso

1. Agregar la imagen o icono.
2. Modificar `resources.qrc`.
3. Regenerar `resources_rc.py`.
4. Probar la aplicación.
5. Realizar el commit incluyendo los archivos correspondientes.

### Si se agrega una dependencia

1. Instalar el paquete dentro del entorno virtual.
2. Probar la aplicación.
3. Actualizar `requirements.txt`.
4. Realizar el commit incluyendo `requirements.txt`.

---

## 8. Recomendaciones Importantes

* Trabajar siempre dentro del entorno virtual `venv`.
* No modificar manualmente archivos generados automáticamente.
* Mantener actualizado `requirements.txt`.
* Probar la aplicación antes de realizar un commit.
* No eliminar recursos utilizados por otras partes de la aplicación sin verificar sus referencias.
* Mantener una estructura de carpetas organizada.
* Evitar subir archivos innecesarios al repositorio, como archivos temporales o el entorno virtual `venv`.
* Realizar commits pequeños y relacionados con un cambio específico.

### Archivos que no deben modificarse manualmente

```text
app/generated/resources_rc.py
```

Este archivo debe ser regenerado mediante `pyside6-rcc` cuando cambien los recursos.

---

## 9. Comandos de Referencia

### Activar entorno virtual

```powershell
.\venv\Scripts\Activate.ps1
```

### Instalar dependencias

```powershell
pip install -r requirements.txt
```

### Actualizar requirements.txt

```powershell
pip freeze > requirements.txt
```

### Regenerar recursos Qt

```powershell
pyside6-rcc app/resources/resources.qrc -o app/generated/resources_rc.py
```

### Ejecutar proyecto

```powershell
python -m app.main
```

### Ejecutar desde VS Code

```text
Ctrl + Shift + B
```

# Estructura del proyecto --- Proyecto Integrador 2.0

Este documento explica de manera general la estructura actual del
proyecto y la responsabilidad que se espera que tenga cada carpeta y
archivo.
------------------------------------------------------------------------

## 1. Estructura general

``` text
Proyecto-Integrador-2.0/
│
├── app/
│   ├── __pycache__/
│   │
│   ├── config/
│   │   └── settings.py
│   │
│   ├── core/
│   │
│   ├── database/
│   │
│   ├── generated/
│   │
│   ├── models/
│   │   ├── business.py
│   │   ├── recovery.py
│   │   └── users.py
│   │
│   ├── resources/
│   │
│   ├── ui/
│   │
│   ├── utils/
│   │   ├── __pycache__/
│   │   ├── recoveryCode.py
│   │   └── validators.py
│   │
│   ├── views/
│   │   ├── createAccount/
│   │   └── login/
│   │
│   └── main.py
│
├── venv/
│
├── .env
├── .env.example
└── .gitignore
```

------------------------------------------------------------------------

# 2. Carpeta `app/`

`app/` contiene el código principal de la aplicación.

La idea es evitar colocar todo el código en un único archivo y separar
las responsabilidades según su función.

Dentro de `app/` se encuentran las configuraciones, modelos, acceso a
base de datos, interfaces, vistas, utilidades y el punto de entrada de
la aplicación.

------------------------------------------------------------------------

# 3. Carpeta `config/`

``` text
config/
└── settings.py
```

Esta carpeta contiene la **configuración de la aplicación**.

## `settings.py`

Su función general es centralizar valores de configuración que pueden
ser utilizados por diferentes partes del proyecto.

Por ejemplo:

-   Variables relacionadas con la base de datos.
-   Configuración del correo electrónico.
-   Claves o configuraciones de servicios externos.
-   Rutas importantes.
-   Configuraciones generales de la aplicación.

Cuando sea posible, los valores sensibles deberían obtenerse desde
variables de entorno en lugar de escribirlos directamente en el código.

------------------------------------------------------------------------

# 4. Carpeta `core/`

``` text
core/
```

Esta carpeta está destinada a contener elementos **centrales de la
aplicación**.

Aquí podrían colocarse componentes que son utilizados por diferentes
módulos y que representan reglas o funcionalidades generales del
sistema.

Por ejemplo:

-   Configuraciones internas de la aplicación.
-   Excepciones personalizadas.
-   Clases base.
-   Servicios generales.
-   Lógica que sea compartida por diferentes módulos.

La idea es que `core/` contenga elementos fundamentales que no
pertenezcan exclusivamente a una vista, modelo o utilidad específica.

------------------------------------------------------------------------

# 5. Carpeta `database/`

``` text
database/
```

Esta carpeta está destinada a todo lo relacionado con la **base de
datos**.

Como el proyecto utiliza SQLAlchemy, aquí puede mantenerse separada la
lógica relacionada con la conexión y configuración del ORM.

Por ejemplo:

-   Configuración del engine de SQLAlchemy.
-   Creación de la sesión.
-   Configuración de la base de datos.
-   Base declarativa de los modelos.
-   Inicialización de tablas.
-   Funciones auxiliares relacionadas con la persistencia.

Una posible organización futura podría ser:

``` text
database/
├── connection.py
├── session.py
└── base.py
```

La estructura exacta dependerá de cómo vaya creciendo el proyecto.

------------------------------------------------------------------------

# 6. Carpeta `generated/`

``` text
generated/
```

Esta carpeta contiene archivos **generados automáticamente** a partir de
otros recursos.

Por ejemplo, cuando se utilizan archivos `.qrc` de Qt, `pyside6-rcc`
puede generar un archivo Python que contiene los recursos compilados.

Por ejemplo:

``` text
resources.qrc
      ↓
pyside6-rcc
      ↓
generated/resources_rc.py
```

La principal idea es que los archivos dentro de esta carpeta normalmente
**no se editan manualmente**, sino que se vuelven a generar cuando
cambian los recursos originales.

------------------------------------------------------------------------

# 7. Carpeta `models/`

``` text
models/
├── business.py
├── recovery.py
└── users.py
```

Esta carpeta contiene los **modelos de datos de la aplicación**.

En un proyecto que utiliza SQLAlchemy, normalmente estos archivos
contienen clases que representan tablas de la base de datos.

## `users.py`

Representa el modelo relacionado con los **usuarios o cuentas**.

Podría contener información como:

-   Identificador del usuario.
-   Nombre.
-   Correo electrónico.
-   Contraseña almacenada de forma segura.
-   Fecha de creación.
-   Relaciones con otras entidades.

Por ejemplo, conceptualmente:

``` text
Usuario
├── id
├── nombre
├── correo
├── contraseña
└── created_at
```

## `business.py`

Representa el modelo relacionado con los **negocios**.

En el contexto del proyecto, un usuario puede estar asociado con un
negocio.

Conceptualmente podría representar información como:

``` text
Business
├── id
├── nombre
├── información del negocio
└── usuario propietario
```

Los campos concretos dependerán del diseño definitivo de la base de
datos.

## `recovery.py`

Representa la información necesaria para gestionar la **recuperación de
cuentas o contraseñas**.

Por ejemplo, podría almacenar:

-   Código de recuperación.
-   Usuario relacionado.
-   Fecha de creación.
-   Fecha de expiración.
-   Estado del código.

Esto permite que la recuperación de contraseña tenga una parte
persistente en la base de datos.

------------------------------------------------------------------------

# 8. Carpeta `resources/`

``` text
resources/
```

Contiene los **recursos utilizados por la interfaz gráfica**.

Por ejemplo:

-   Imágenes.
-   Logos.
-   Iconos.
-   Fuentes.
-   Archivos `.qrc`.
-   Otros recursos visuales.

En una aplicación PySide6, esta carpeta permite mantener separados los
recursos gráficos del código Python.

Por ejemplo:

``` text
resources/
├── images/
├── icons/
├── fonts/
└── resources.qrc
```

La estructura exacta puede cambiar conforme se agreguen más recursos.

------------------------------------------------------------------------

# 9. Carpeta `ui/`

``` text
ui/
```

Esta carpeta está destinada a los archivos relacionados con el **diseño
de las interfaces creadas con Qt Designer**.

Normalmente aquí pueden almacenarse archivos:

``` text
.ui
```

Estos archivos describen visualmente ventanas, formularios y componentes
de la interfaz.

Por ejemplo:

``` text
ui/
├── createAccount.ui
├── login.ui
└── dashboard.ui
```

La idea es separar el **diseño visual** de la lógica Python.

------------------------------------------------------------------------

# 10. Carpeta `utils/`

``` text
utils/
├── recoveryCode.py
└── validators.py
```

Esta carpeta contiene **funciones auxiliares y reutilizables**.

Son funciones que pueden ser utilizadas por diferentes partes de la
aplicación y que no pertenecen directamente a un modelo o a una ventana
específica.

## `recoveryCode.py`

Contiene la lógica relacionada con la generación o manejo de **códigos
de recuperación**.

Por ejemplo:

``` text
Usuario solicita recuperar contraseña
              ↓
Generar código
              ↓
Guardar código / asociarlo al usuario
              ↓
Enviar código por correo
              ↓
Usuario introduce código
```

## `validators.py`

Contiene funciones para **validar información introducida por el
usuario**.

Por ejemplo:

-   Validar correos electrónicos.
-   Comprobar campos obligatorios.
-   Validar contraseñas.
-   Comprobar formatos.
-   Validar otros datos de formularios.

La ventaja es que la validación puede reutilizarse en diferentes
ventanas sin duplicar código.

------------------------------------------------------------------------

# 11. Carpeta `views/`

``` text
views/
├── createAccount/
└── login/
```

Esta carpeta contiene las **vistas o ventanas de la aplicación**.

En PySide6, cada vista normalmente representa una ventana, formulario o
pantalla con la que interactúa el usuario.

## `createAccount/`

Contiene los elementos relacionados con la pantalla de **creación de
cuenta**.

Aquí podría existir, por ejemplo:

``` text
createAccount/
├── createAccount.py
└── ...
```

La lógica de esta vista puede encargarse de:

-   Leer los datos introducidos.
-   Ejecutar validaciones.
-   Solicitar la creación del usuario.
-   Mostrar mensajes de error.
-   Cambiar a otra ventana después del registro.

## `login/`

Contiene los elementos relacionados con la pantalla de **inicio de
sesión**.

La vista puede encargarse de:

-   Obtener correo y contraseña.
-   Validar los campos.
-   Solicitar la autenticación.
-   Mostrar errores.
-   Permitir recuperar la contraseña.
-   Cambiar a la ventana principal después de iniciar sesión
    correctamente.

------------------------------------------------------------------------

# 12. Archivo `main.py`

``` text
app/
└── main.py
```

`main.py` funciona como **punto de entrada de la aplicación**.

Es decir, es el archivo que inicia el programa.

Una ejecución típica puede ser:

``` bash
python -m app.main
```

Generalmente `main.py` se encarga de:

1.  Crear la aplicación de PySide6.
2.  Inicializar configuraciones necesarias.
3.  Inicializar recursos.
4.  Crear la primera ventana.
5.  Mostrar la interfaz.
6.  Iniciar el ciclo de eventos de Qt.

Conceptualmente:

``` text
main.py
   │
   ├── Inicializa la aplicación
   │
   ├── Carga configuraciones
   │
   ├── Inicializa recursos
   │
   ├── Abre Login
   │
   └── Inicia el evento principal de PySide6
```

------------------------------------------------------------------------

# 13. `__pycache__/`

``` text
__pycache__/
```

Es una carpeta generada automáticamente por Python.

Python puede almacenar allí archivos compilados (`.pyc`) para acelerar
determinadas cargas posteriores.

**No es código fuente del proyecto.**

Normalmente debe incluirse en `.gitignore` para evitar subirla al
repositorio.

------------------------------------------------------------------------

# 14. `venv/`

``` text
venv/
```

Contiene el **entorno virtual de Python** del proyecto.

El entorno virtual permite instalar las dependencias del proyecto de
forma aislada del Python global del sistema.

Por ejemplo, el proyecto utiliza actualmente herramientas y librerías
como:

``` text
Python
PySide6
SQLAlchemy
```

y otras dependencias que se vayan agregando.

Normalmente `venv/` tampoco se sube al repositorio, porque cada
desarrollador puede crear su propio entorno virtual a partir de las
dependencias del proyecto.

------------------------------------------------------------------------

# 15. `.env`

``` text
.env
```

Contiene **variables de entorno locales**.

Puede utilizarse para almacenar información que no debería escribirse
directamente en el código fuente.

Por ejemplo:

``` text
DATABASE_URL=...
EMAIL=...
PASSWORD=...
SECRET_KEY=...
```

El archivo `.env` puede contener información sensible, por lo que
normalmente **no debe subirse a GitHub**.

------------------------------------------------------------------------

# 16. `.env.example`

``` text
.env.example
```

Es una plantilla del archivo `.env`.

A diferencia de `.env`, no debería contener contraseñas o secretos
reales.

Por ejemplo:

``` text
DATABASE_URL=
EMAIL=
PASSWORD=
SECRET_KEY=
```

Su objetivo es mostrarle a otro desarrollador qué variables necesita
configurar para ejecutar el proyecto.

------------------------------------------------------------------------

# 17. `.gitignore`

``` text
.gitignore
```

Indica a Git qué archivos y carpetas debe **ignorar**.

Por ejemplo:

``` text
venv/
__pycache__/
.env
*.pyc
```

Esto evita subir al repositorio archivos temporales, entornos virtuales
y datos sensibles.

------------------------------------------------------------------------

# 18. Flujo general de las partes

Una forma sencilla de entender la arquitectura actual es la siguiente:

``` text
                    ┌───────────────┐
                    │    main.py    │
                    │ Punto entrada │
                    └───────┬───────┘
                            │
                            ▼
                    ┌───────────────┐
                    │     views     │
                    │  Interfaz UI  │
                    └───────┬───────┘
                            │
                            ▼
                    ┌───────────────┐
                    │     utils     │
                    │ Validaciones  │
                    │ Funciones     │
                    └───────┬───────┘
                            │
                            ▼
                    ┌───────────────┐
                    │    models     │
                    │ Datos/ORM     │
                    └───────┬───────┘
                            │
                            ▼
                    ┌───────────────┐
                    │   database    │
                    │ SQLAlchemy/BD │
                    └───────────────┘

       ┌──────────────┐
       │    config    │
       │ Configuración│
       └──────────────┘

       ┌──────────────┐
       │   resources  │
       │ Iconos/Fotos │
       │ Fuentes/QRC  │
       └──────────────┘

       ┌──────────────┐
       │      ui      │
       │ Qt Designer  │
       │    .ui       │
       └──────────────┘
```

------------------------------------------------------------------------

# 19. Idea principal de la arquitectura

La intención de esta estructura es aplicar una separación de
responsabilidades.

En términos sencillos:

  Parte            Responsabilidad
  ---------------- --------------------------------------
  `config/`        Configuración
  `core/`          Componentes centrales
  `database/`      Conexión y manejo de BD
  `models/`        Modelos de datos / SQLAlchemy
  `views/`         Ventanas y lógica de interfaz
  `ui/`            Diseños de Qt Designer
  `utils/`         Funciones auxiliares reutilizables
  `resources/`     Imágenes, iconos, fuentes y recursos
  `generated/`     Archivos generados automáticamente
  `main.py`        Inicio de la aplicación
  `.env`           Configuración sensible local
  `.env.example`   Plantilla de variables
  `.gitignore`     Archivos ignorados por Git
  `venv/`          Entorno virtual de Python

Esta separación permitirá que el proyecto pueda crecer sin convertir
`main.py` o las ventanas en archivos demasiado grandes.

Por ejemplo, una ventana no debería encargarse directamente de construir
consultas SQL complejas. La vista puede solicitar una operación y
delegar la persistencia a la capa correspondiente.

De forma conceptual:

``` text
Usuario
   ↓
Vista (`views/`)
   ↓
Lógica / servicios
   ↓
Modelo (`models/`)
   ↓
Base de datos (`database/`)
   ↓
SQLite / MySQL / PostgreSQL
```

La estructura puede evolucionar conforme aparezcan nuevas
funcionalidades como movimientos financieros, categorías, reportes,
análisis, indicadores y recomendaciones.

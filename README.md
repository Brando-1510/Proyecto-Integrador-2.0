<div align="center">

# Finanzen — Sistema de Análisis Financiero

**Transforma los registros de tu negocio en información útil para tomar mejores decisiones.**

Finanzen es una aplicación de escritorio desarrollada en Python que permite a micro y pequeños negocios importar información financiera desde archivos Excel, analizar sus ventas, ingresos y gastos, visualizar indicadores y obtener recomendaciones basadas en reglas de negocio.

La aplicación busca facilitar la comprensión del comportamiento financiero de un negocio mediante gráficos, estadísticas, comparaciones entre períodos y reportes financieros en PDF, sin requerir conocimientos avanzados de contabilidad o análisis de datos.

<br>

![Python](https://img.shields.io/badge/Python-3.x-3776AB?style=for-the-badge&logo=python&logoColor=white)
![PySide6](https://img.shields.io/badge/PySide6-Qt-41CD52?style=for-the-badge&logo=qt&logoColor=white)
![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-ORM-D71F00?style=for-the-badge&logo=sqlalchemy&logoColor=white)
![MySQL](https://img.shields.io/badge/MySQL-Database-4479A1?style=for-the-badge&logo=mysql&logoColor=white)
![Pandas](https://img.shields.io/badge/Pandas-Data_Analysis-150458?style=for-the-badge&logo=pandas&logoColor=white)
![NumPy](https://img.shields.io/badge/NumPy-Numerical_Computing-013243?style=for-the-badge&logo=numpy&logoColor=white)
![Matplotlib](https://img.shields.io/badge/Matplotlib-Visualization-11557C?style=for-the-badge)
![Jinja2](https://img.shields.io/badge/Jinja2-Templates-B41717?style=for-the-badge)
![WeasyPrint](https://img.shields.io/badge/WeasyPrint-PDF_Reports-2B5797?style=for-the-badge)
![OpenPyXL](https://img.shields.io/badge/OpenPyXL-Excel_Processing-217346?style=for-the-badge&logo=microsoftexcel&logoColor=white)

</div>

---

## Descripción

Los pequeños negocios generan información diariamente mediante sus ventas, ingresos y gastos. Sin embargo, registrar estos datos en hojas de cálculo no siempre es suficiente para comprender su comportamiento financiero y tomar decisiones fundamentadas.

**Finanzen** busca cerrar esa brecha mediante una herramienta que procesa los registros del negocio y los convierte en indicadores, gráficos, comparaciones y observaciones fáciles de interpretar.

La aplicación permite centralizar la información importada, consultar los movimientos registrados, evaluar variaciones entre períodos e identificar situaciones que podrían requerir atención.

Finanzen está orientado al análisis financiero operativo y al apoyo en la toma de decisiones. No pretende sustituir un sistema contable, un ERP ni los servicios de un profesional de contabilidad.

## Problema que aborda

Muchos micro y pequeños negocios utilizan hojas de cálculo para almacenar sus registros, pero tienen dificultades para aprovechar esa información de manera sistemática.

Entre los problemas que busca abordar el proyecto se encuentran:

- Dificultad para interpretar la evolución de las ventas.
- Falta de claridad sobre el comportamiento de los ingresos y gastos.
- Complicaciones para comparar resultados entre diferentes períodos.
- Dificultad para identificar categorías con variaciones relevantes.
- Errores e inconsistencias en los registros importados.
- Falta de herramientas accesibles para generar informes financieros.
- Toma de decisiones basada principalmente en la intuición y no en datos organizados.

## Objetivo general

Desarrollar una aplicación de escritorio que permita importar, almacenar, analizar y visualizar información financiera de micro y pequeños negocios, generando indicadores, comparaciones, recomendaciones y reportes que faciliten la interpretación de sus resultados y apoyen la toma de decisiones.

## Funcionalidades principales

### 1. Importación y validación de archivos Excel

Permite importar información financiera desde archivos `.xlsx`, validando su estructura y los datos contenidos en las hojas correspondientes.

Entre sus funcionalidades se encuentran:

- Validación de columnas y registros.
- Comprobación de tipos y valores.
- Normalización de datos y nombres de categorías.
- Identificación de errores y advertencias.
- Detección de importaciones duplicadas mediante la identificación del archivo.
- Identificación de categorías que necesitan crearse o corregirse.
- Almacenamiento de la información validada en la base de datos.

### 2. Gestión de usuarios y negocios

Permite administrar el acceso a la aplicación y organizar la información según los negocios registrados.

Incluye funcionalidades relacionadas con:

- Registro e inicio de sesión.
- Administración de usuarios.
- Gestión de negocios.
- Asignación de roles y permisos.
- Asociación de usuarios con sus negocios.

Los permisos determinan las operaciones disponibles para cada usuario dentro de la aplicación.

### 3. Panel principal

Presenta un resumen de la actividad financiera del negocio mediante indicadores, gráficos y tablas.

Permite consultar información relevante, como:

- Total de ventas de un período.
- Ingresos y gastos registrados.
- Evolución de las ventas.
- Transacciones recientes.
- Resumen de la actividad del negocio.

### 4. Análisis financiero

Procesa los registros almacenados para ofrecer una visión más detallada del comportamiento financiero del negocio.

Incluye:

- Análisis de ingresos y gastos.
- Comparaciones entre períodos.
- Análisis de variaciones porcentuales.
- Estadísticas descriptivas.
- Análisis de categorías.
- Evaluación de la variabilidad de las ventas.
- Indicadores como el ticket promedio.
- Visualización de tendencias y distribución de los datos.

Los períodos de análisis pueden seleccionarse mediante filtros disponibles en la interfaz, según las opciones implementadas.

### 5. Recomendaciones financieras

Genera observaciones y sugerencias a partir de reglas de negocio definidas y resultados estadísticos.

Estas recomendaciones pueden ayudar a identificar:

- Incrementos relevantes en los gastos.
- Variaciones importantes en las ventas.
- Cambios en los ingresos.
- Comportamientos que merecen una revisión.
- Oportunidades de mejora a partir de los registros disponibles.

Las recomendaciones se basan en condiciones y cálculos verificables. No constituyen predicciones infalibles ni sustituyen el criterio del responsable del negocio.

### 6. Generación de reportes PDF

Permite generar informes financieros a partir de la información procesada por la aplicación.

La generación de documentos utiliza plantillas HTML y CSS para estructurar la presentación de los resultados y convertirlos en archivos PDF.

Las tecnologías empleadas para este proceso son:

- **Jinja2:** construcción de documentos HTML mediante plantillas dinámicas.
- **WeasyPrint:** conversión de documentos HTML y CSS a PDF.

Este enfoque permite organizar los informes en secciones y presentar indicadores, tablas, gráficos y resultados de manera estructurada.

## Flujo general del sistema

```text
        Archivo Excel (.xlsx)
                 |
                 v
       Lectura del archivo
                 |
                 v
     Validación de estructura
       y contenido de los datos
                 |
                 v
     Limpieza y normalización
                 |
                 v
      Almacenamiento en MySQL
                 |
                 v
       Consultas a la base
            de datos
                 |
                 v
       Análisis financiero
                 |
                 v
   Indicadores, gráficos y reglas
          de recomendación
                 |
                 v
       Visualización de datos
                 |
                 v
        Generación de PDF
```

## Tecnologías utilizadas

| Tecnología | Propósito |
|---|---|
| Python | Lenguaje principal de desarrollo. |
| PySide6 | Desarrollo de la interfaz gráfica de escritorio. |
| SQLAlchemy | Mapeo objeto-relacional y acceso a la base de datos. |
| MySQL | Almacenamiento persistente de la información. |
| Pandas | Lectura, transformación y procesamiento tabular de datos. |
| NumPy | Cálculos y operaciones estadísticas. |
| OpenPyXL | Lectura y procesamiento de archivos Excel. |
| Matplotlib | Generación de gráficos financieros. |
| Jinja2 | Renderizado de plantillas HTML para los reportes. |
| WeasyPrint | Generación de archivos PDF desde HTML y CSS. |
| Git y GitHub | Control de versiones y colaboración en el desarrollo. |

## Arquitectura del proyecto

Finanzen organiza sus componentes en módulos y capas para separar las responsabilidades del sistema y facilitar su mantenimiento.

La arquitectura contempla las siguientes responsabilidades:

- **Interfaz de usuario:** interacción con el usuario y presentación de los resultados.
- **Controladores:** coordinación de las acciones solicitadas desde la interfaz y orquestación de los procesos correspondientes.
- **Servicios:** ejecución de los casos de uso, coordinación de operaciones y gestión de sesiones de base de datos.
- **Repositorios:** consultas y operaciones de persistencia mediante SQLAlchemy.
- **Modelos:** representación de las entidades almacenadas en la base de datos.
- **Funciones de análisis:** cálculos estadísticos, comparaciones y generación de hallazgos.
- **Utilidades:** funciones auxiliares para fechas, formatos y otras operaciones comunes.
- **Plantillas de reportes:** estructura y presentación de los documentos PDF.

Esta separación permite mantener la lógica de análisis independiente de la interfaz y de los mecanismos de almacenamiento.

## Usuarios objetivo

Finanzen está dirigido principalmente a micro y pequeños negocios, entre ellos:

- Pulperías y tiendas de barrio.
- Cafeterías y pequeños restaurantes.
- Tiendas de ropa.
- Ferreterías.
- Emprendimientos y negocios familiares.
- Pequeños comercios que administran sus registros mediante Excel.

La aplicación busca presentar la información de manera comprensible, incluso para usuarios sin conocimientos avanzados de estadística o contabilidad.

## Alcance del proyecto

El sistema se enfoca en el análisis de información financiera registrada y almacenada en la aplicación.

Dentro de su alcance se encuentran la importación de archivos Excel, la gestión de usuarios y negocios, la consulta de transacciones, el análisis de ventas, ingresos y gastos, la visualización de indicadores, las recomendaciones basadas en reglas y la generación de reportes financieros en PDF.

### Fuera del alcance

Finanzen no pretende ofrecer, como parte de su alcance actual:

- Contabilidad empresarial completa.
- Facturación electrónica.
- Declaraciones fiscales.
- Gestión integral de inventarios.
- Administración de nóminas.
- Integraciones bancarias automáticas.
- Sustitución de un sistema ERP.
- Predicciones basadas en modelos de aprendizaje automático entrenados.

## Instalación y ejecución

Los pasos exactos de instalación dependen de la configuración del proyecto y de los archivos de dependencias incluidos en el repositorio.

En términos generales, se requiere:

- Python compatible con las dependencias del proyecto.
- Un servidor MySQL.
- Las bibliotecas de Python utilizadas por la aplicación.
- La configuración de conexión a la base de datos.

Una vez preparado el entorno, el proceso general consiste en instalar las dependencias, configurar la conexión a MySQL, preparar el esquema de la base de datos y ejecutar el punto de entrada de la aplicación.

Consulta los archivos de configuración y las instrucciones de instalación del repositorio para conocer los comandos y requisitos específicos.

## Contexto académico

Finanzen se desarrolla como proyecto integrador de Ingeniería en Sistemas, con el propósito de aplicar conocimientos de programación orientada a objetos, interfaces gráficas, bases de datos relacionales, procesamiento de archivos, análisis de datos y arquitectura de software.

El proyecto integra estas áreas en una aplicación orientada a resolver una necesidad práctica de los micro y pequeños negocios.

## Equipo de desarrollo

| Integrante | Correo electrónico | GitHub |
|---|---|---|
| **Brandon Reynaldo Rodríguez Téllez** | `brandonbrt2020@gmail.com` | [@Brando-1510](https://github.com/Brando-1510) |
| **Leonardo Antonio Tellería Trujillo** | `telleriatrujilloleonardoanti@gmail.com` | [@LeonardoTelleria](https://github.com/LeonardoTelleria) |
| **Jorge Luis Antón Henández** | `luisjorgeantonhernandez@gmail.com` | [@luis-hdz7](https://github.com/luis-hdz7) |
| **Luis Carlos Castillo Gómez** | `luis1284ufd4@gmail.com` | [@luiscastillo-18c](https://github.com/luiscastillo-18c) |

---

<div align="center">

**Finanzen — Información financiera para tomar mejores decisiones.**

*Proyecto académico en desarrollo.*

</div>

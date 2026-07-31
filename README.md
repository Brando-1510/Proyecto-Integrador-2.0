<div align="center">

#  Sistema de Análisis Financiero

### Desarrollo de una aplicación de escritorio en Python y PySide6 enfocada en la visualización, analisis  y comparación de información financiera de pequeños negocios mediante un modelo predictivo basado en Pandas y  Numpy además de la gestión de datos mediante SQLAlchemy.

<br>

![Python](https://img.shields.io/badge/Python-3.x-3776AB?style=for-the-badge\&logo=python\&logoColor=white)
![PySide6](https://img.shields.io/badge/PySide6-Qt-41CD52?style=for-the-badge\&logo=qt\&logoColor=white)
![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-ORM-D71F00?style=for-the-badge)
![MySQL](https://img.shields.io/badge/MySQL-Database-4479A1?style=for-the-badge\&logo=mysql\&logoColor=white)
![Estado](https://img.shields.io/badge/Estado-En%20definición-yellow?style=for-the-badge)

</div>

---

## 📖 Descripción

Este proyecto consiste en una aplicación de escritorio orientada al análisis de información financiera y comercial de pequeños negocios.

La aplicación permitirá importar registros almacenados en archivos de Microsoft Excel, validar y procesar su contenido, para posteriormente presentar indicadores, estadísticas, gráficos y observaciones que faciliten la comprensión del comportamiento del negocio.

El sistema está dirigido principalmente a pequeños comercios, emprendimientos y negocios familiares que actualmente utilizan hojas de cálculo como medio principal para registrar ventas, ingresos y gastos, pero que no cuentan con herramientas accesibles para analizar esa información.

> El proyecto no busca reemplazar un sistema contable ni un sistema de gestión empresarial. Su propósito es convertir datos existentes en información comprensible y útil para apoyar la toma de decisiones.

---

## 🎯 Problema identificado

Muchos pequeños negocios utilizan Excel únicamente para almacenar registros, sin aprovechar los datos para:

* Identificar tendencias de ventas.
* Evaluar el crecimiento de ingresos y gastos.
* Detectar productos con mayor o menor rendimiento.
* Reconocer variaciones importantes entre periodos.
* Identificar posibles inconsistencias en los registros.
* Tomar decisiones basadas en evidencia.

Como consecuencia, numerosas decisiones se realizan utilizando únicamente la experiencia, la intuición o percepciones subjetivas.

---

## 💡 Objetivo general

Desarrollar una aplicación de escritorio que permita importar, procesar, analizar y visualizar información financiera básica almacenada en hojas de cálculo, facilitando la interpretación de los datos y apoyando la toma de decisiones en pequeños negocios.

---

## 👥 Usuarios objetivo

El sistema está pensado principalmente para:

* Pulperías.
* Cafeterías.
* Pequeños restaurantes.
* Tiendas de ropa.
* Ferreterías.
* Emprendimientos.
* Negocios familiares.
* Personas que están iniciando una actividad comercial.

No será necesario que los usuarios posean conocimientos avanzados de contabilidad, estadística o análisis de datos.

---

## 🧩 Módulos previstos

<table>
  <thead>
    <tr>
      <th>Módulo</th>
      <th>Descripción</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td><strong>Importación de datos</strong></td>
      <td>Carga, validación y procesamiento de archivos Excel.</td>
    </tr>
    <tr>
      <td><strong>Gestión de usuarios</strong></td>
      <td>Registro, inicio de sesión y administración de la información de cada negocio.</td>
    </tr>
    <tr>
      <td><strong>Análisis financiero</strong></td>
      <td>Cálculo de indicadores, estadísticas, tendencias y comparaciones entre periodos.</td>
    </tr>
    <tr>
      <td><strong>Visualización</strong></td>
      <td>Presentación de resultados mediante gráficos, tablas y tarjetas informativas.</td>
    </tr>
    <tr>
      <td><strong>Recomendaciones</strong></td>
      <td>Generación de observaciones y sugerencias mediante reglas de negocio verificables.</td>
    </tr>
  </tbody>
</table>

---

## 🔄 Flujo general

```text
Archivo Excel
      ↓
Validación de estructura
      ↓
Limpieza y normalización
      ↓
Almacenamiento de datos
      ↓
Análisis financiero
      ↓
Gráficos, indicadores y observaciones
```

---

## 🛠️ Tecnologías previstas

| Área                      | Tecnología   |
| ------------------------- | ------------ |
| Lenguaje principal        | Python       |
| Interfaz gráfica          | PySide6      |
| ORM                       | SQLAlchemy   |
| Base de datos             | MySQL        |
| Procesamiento de datos    | Pandas       |
| Lectura de archivos Excel | OpenPyXL     |
| Visualización de datos    | Matplotlib   |
| Control de versiones      | Git y GitHub |

La selección tecnológica podrá ajustarse conforme se definan los requisitos funcionales, el volumen de datos y la arquitectura definitiva del sistema.

---

## 📌 Alcance inicial

La primera versión contempla:

* Importación de archivos `.xlsx`.
* Validación básica de columnas y registros.
* Almacenamiento de datos procesados.
* Consulta y filtrado de transacciones.
* Análisis de ventas, ingresos y gastos.
* Comparación entre periodos.
* Generación de indicadores.
* Visualización mediante gráficos y tablas.
* Creación de observaciones basadas en reglas.
* Gestión básica de usuarios y negocios.

---

## 🚫 Fuera del alcance inicial

En esta etapa el sistema no incluirá:

* Facturación electrónica.
* Declaraciones fiscales.
* Nómina.
* Gestión de inventarios.
* Integraciones bancarias.
* Contabilidad empresarial completa.
* Sincronización en la nube.
* Aplicación web o móvil.

---

## 🚧 Estado actual

El proyecto se encuentra en la etapa de:

* Definición de la problemática.
* Justificación inicial.
* Delimitación del alcance.
* Identificación de usuarios.
* Selección preliminar de tecnologías.
* Definición inicial de módulos.

La arquitectura, el modelo de datos, los requisitos funcionales y el diseño de interfaz todavía se encuentran en proceso de análisis.

---

## 📂 Estructura provisional

```text
project/
├── app/
│   ├── core/
│   ├── models/
│   ├── repositories/
│   ├── services/
│   ├── analytics/
│   ├── ui/
│   └── utils/
├── tests/
├── resources/
├── requirements.txt
├── README.md
└── main.py
```

---

## 🎓 Contexto académico

Este proyecto se desarrolla como examen final, con el propósito de integrar conocimientos relacionados con:

* Programación orientada a objetos.
* Desarrollo de interfaces gráficas.
* Bases de datos relacionales.
* Procesamiento de archivos.
* Análisis de datos.
* Visualización de información.
* Arquitectura modular de software.

---

<div align="center">

### Proyecto en construcción

La documentación y las funcionalidades serán actualizadas conforme avance el análisis y desarrollo del sistema.

</div>

# Finanzen — Mapa de lógica de negocio y reglas del sistema

## 1. Propósito del documento

Este documento define las decisiones funcionales y reglas de negocio acordadas para **Finanzen**.

Debe utilizarse como referencia durante el desarrollo de:

* modelos SQLAlchemy;
* repositories;
* services;
* controllers;
* importación y validación de Excel;
* edición y eliminación de datos;
* análisis financiero;
* recomendaciones;
* gestión de categorías;
* permisos por rol;
* futuras migraciones de base de datos.

Las reglas descritas aquí representan decisiones ya tomadas. Si durante la implementación aparece una situación que contradice alguna de estas reglas, no se debe modificar silenciosamente el comportamiento: primero debe revisarse la decisión con el equipo.

---

# 2. Alcance general

Finanzen es una aplicación de análisis financiero para pequeños y medianos negocios.

El objetivo principal es permitir registrar/importar información financiera y posteriormente analizar el comportamiento de:

* ingresos;
* gastos;
* ventas.

Finanzen **no pretende ser un sistema contable completo**.

## 2.1. Funcionalidades fuera del alcance

No se manejarán:

* contabilidad de partida doble;
* inventario;
* cuentas por cobrar;
* cuentas por pagar;
* proveedores;
* clientes;
* nómina;
* facturación;
* cuentas bancarias;
* deudas;
* otros módulos propios de un sistema contable/ERP completo.

---

# 3. Usuarios y negocios

## 3.1. Usuarios

Un usuario puede pertenecer a uno o varios negocios.

Los usuarios se relacionan con los negocios mediante `USER_BUSINESS`.

Un usuario también puede crear varios negocios.

Por ello:

* `USERS → BUSINESS` representa quién creó originalmente el negocio mediante `creator_id`.
* `USERS ↔ BUSINESS` representa pertenencia y rol mediante `USER_BUSINESS`.

`creator_id` **no significa que el usuario sea el único gerente actual del negocio**.

---

# 4. Roles

Los roles definidos actualmente son:

```text
MANAGER
FINANCIAL_ANALYST
EMPLOYEE
```

Correspondencia:

```text
MANAGER            → Gerente
FINANCIAL_ANALYST  → Analista Financiero
EMPLOYEE           → Empleado
```

## 4.1. Gerente

El Gerente tiene acceso a todas las funciones financieras de la aplicación, incluyendo:

* importar Excel;
* consultar información;
* analizar información;
* generar informes;
* consultar recomendaciones;
* modificar datos financieros;
* eliminar datos financieros;
* gestionar categorías de ventas.

## 4.2. Analista Financiero

Puede:

* importar Excel;
* consultar información;
* realizar análisis;
* generar informes;
* consultar recomendaciones.

No puede modificar ni eliminar datos financieros después de la importación.

## 4.3. Empleado

Puede:

* acceder a las funciones permitidas para su rol;
* importar archivos Excel.

No puede modificar ni eliminar datos financieros después de la importación.

> Todos los roles pueden importar Excel. La diferencia está en lo que pueden hacer posteriormente con los datos.

---

# 5. Importación de Excel

El Excel utilizado por Finanzen tendrá dos hojas:

```text
Movimientos
Ventas
```

## 5.1. Hoja Movimientos

Contendrá:

```text
Fecha
Tipo
Categoría
Descripción
Monto
Método de pago
```

## 5.2. Hoja Ventas

Contendrá:

```text
Fecha
Producto/Servicio
Categoría
Cantidad
Precio unitario
Total
```

Cada fila de ventas representa una venta/producto-servicio independiente.

No se manejarán múltiples productos dentro de una misma venta.

---

# 6. Validación del Excel

La validación debe distinguir entre:

* errores estructurales;
* errores de datos.

Si existe cualquier error, **el Excel completo debe rechazarse**.

Ejemplo:

```text
500 registros
3 registros con errores
        ↓
RECHAZAR TODO EL ARCHIVO
```

No se deben importar parcialmente los 497 registros correctos.

El usuario debe recibir información suficiente para identificar exactamente los errores encontrados.

Debe existir una opción para descargar/utilizar una plantilla oficial de Excel.

---

# 7. Importaciones y `IMPORT`

Cada importación exitosa genera un registro en `IMPORT`.

`IMPORT` permite identificar:

* qué archivo fue importado;
* qué usuario realizó la importación;
* a qué negocio perteneció;
* cuándo fue importado;
* qué archivo era mediante `file_hash`.

Los registros de `MOVEMENTS` y `SALE` generados por el Excel mantienen una referencia hacia `IMPORT`.

Esto permite tratar una importación completa como una unidad.

## 7.1. Importaciones fallidas

Si el Excel contiene errores:

```text
Excel
  ↓
Validación
  ↓
ERROR
  ↓
NO crear movimientos
NO crear ventas
NO guardar importación exitosa
```

No debe quedar información financiera parcialmente importada.

## 7.2. Excel duplicado

Se utilizará `file_hash` para identificar si exactamente el mismo archivo ya fue importado.

Si el hash indica que el archivo ya fue importado, la aplicación debe rechazar la nueva importación como duplicada.

---

# 8. Movimientos financieros

`MOVEMENTS` representa los movimientos financieros generales del negocio.

Existen únicamente dos tipos:

```text
INCOME  → Ingreso
EXPENSE → Gasto
```

No deben agregarse otros tipos de movimiento sin modificar previamente la definición funcional del sistema.

---

# 9. Categorías de movimientos

Las categorías de movimientos son **fijas**.

El Gerente no puede crear ni eliminar categorías de movimientos.

## 9.1. Categorías de ingresos

```text
Ventas
Servicios
Otros ingresos
```

## 9.2. Categorías de gastos

```text
Compras
Personal
Servicios básicos
Alquiler
Transporte
Mantenimiento
Publicidad
Impuestos
Otros
```

## 9.3. Regla de compatibilidad

La categoría debe corresponder al tipo de movimiento.

Ejemplos válidos:

```text
INCOME  + Ventas
INCOME  + Servicios
INCOME  + Otros ingresos

EXPENSE + Compras
EXPENSE + Alquiler
EXPENSE + Publicidad
EXPENSE + Otros
```

Ejemplos inválidos:

```text
INCOME  + Alquiler
INCOME  + Compras
EXPENSE + Ventas
EXPENSE + Servicios
```

Esta validación debe realizarse en la lógica de negocio y no depender únicamente de la interfaz.

---

# 10. Métodos de pago

Los métodos de pago disponibles son:

```text
CASH
CARD
TRANSFER
OTHER
```

Correspondencia:

```text
Efectivo
Tarjeta
Transferencia
Otro
```

No se diferenciará entre:

* tarjeta de crédito;
* tarjeta de débito.

El método de pago puede ser opcional. Cuando no pueda especificarse, se utilizará `Otro/sin especificar`.

---

# 11. MOVEMENTS y SALE son independientes

No existe una relación directa entre:

```text
MOVEMENTS
```

y:

```text
SALE
```

Una venta no tiene que convertirse obligatoriamente en un ingreso dentro de `MOVEMENTS`.

Por ejemplo:

```text
Ventas registradas = C$10,000
Ingresos registrados = C$8,500
```

La aplicación no debe considerar automáticamente esto como un error de importación.

Puede mostrar la diferencia durante el análisis, pero **no debe bloquear la información por esta razón**.

Además, no todos los ingresos provienen de ventas:

```text
Ventas
Servicios
Otros ingresos
```

---

# 12. Ventas

`SALE` contiene:

```text
date
product_service
category_id
quantity
unit_price
total
created_by
updated_by
created_at
updated_at
```

El total de una venta se determina mediante:

```text
total = quantity × unit_price
```

El sistema debe validar que el `total` proporcionado en el Excel sea consistente con estos valores.

Una discrepancia debe considerarse un error de datos durante la importación.

---

# 13. Categorías de ventas

A diferencia de las categorías de movimientos, las categorías de ventas son dinámicas y pertenecen a cada negocio.

Se utiliza la entidad:

```text
CATEGORY
```

Cada categoría pertenece a un único `BUSINESS`.

Un negocio puede tener muchas categorías.

---

# 14. Categorías genéricas iniciales

Al crear un negocio, Finanzen debe crear automáticamente estas categorías iniciales:

```text
General
Novedades
Promociones
Servicios
Combos
Misceláneos
Otros
Productos
```

Estas categorías se crean mediante la lógica de la aplicación, no mediante inserciones manuales en Workbench.

La creación del negocio y la creación de sus categorías iniciales debe formar parte de una operación consistente.

---

# 15. `CATEGORY.is_system`

`CATEGORY` posee:

```text
is_system
```

Este campo identifica categorías protegidas por las reglas del sistema.

La categoría:

```text
Otros
```

es una categoría del sistema y debe tener:

```text
is_system = True
```

Las demás categorías genéricas no necesitan ser protegidas simplemente por haber sido creadas inicialmente.

Por tanto:

```text
Otros       → is_system = True
General     → is_system = False
Novedades   → is_system = False
Promociones → is_system = False
Servicios   → is_system = False
Combos      → is_system = False
Misceláneos → is_system = False
Productos   → is_system = False
```

---

# 16. Regla especial de `Otros`

`Otros` es una categoría obligatoria para cada negocio.

No puede:

* eliminarse;
* renombrarse.

La protección debe existir en la lógica de negocio.

El `QMessageBox` solamente comunica la restricción al usuario; **no es la única protección**.

La aplicación debe rechazar cualquier operación que intente eliminar o renombrar una categoría protegida.

---

# 17. Categorías creadas por el Gerente

El Gerente puede crear categorías específicas para su negocio.

Ejemplo:

```text
Farmacia
├── Productos
├── Analgésicos
├── Antibióticos
├── Vitaminas
└── Otros
```

Otro negocio puede tener:

```text
Ferretería
├── Productos
├── Herramientas
├── Electricidad
├── Plomería
└── Otros
```

Las categorías pertenecen al negocio y no son compartidas globalmente entre negocios.

---

# 18. Categorías duplicadas

Dentro de un mismo negocio no pueden existir dos categorías con el mismo nombre.

Ejemplo inválido:

```text
Farmacia
├── Analgésicos
└── Analgésicos
```

Por tanto, la base de datos debe garantizar la unicidad de:

```text
business_id + name
```

Esto debe protegerse tanto en la base de datos como en la lógica de aplicación.

Dos negocios diferentes sí pueden tener categorías con el mismo nombre.

Ejemplo válido:

```text
Farmacia       → Analgésicos
Otra Farmacia  → Analgésicos
```

---

# 19. Eliminación de categorías de ventas

El Gerente puede eliminar categorías que no sean del sistema.

Si una categoría no está siendo utilizada por ninguna venta:

```text
CATEGORY
    ↓
eliminar
```

Si existen ventas asociadas a esa categoría:

```text
Analgésicos
      ↓
Ventas relacionadas
      ↓
category_id = Otros
      ↓
Eliminar categoría
```

Las ventas históricas **no deben eliminarse** solamente porque se elimine su categoría.

Ejemplo:

```text
Antes:

Paracetamol → Analgésicos
Ibuprofeno  → Analgésicos

Después:

Paracetamol → Otros
Ibuprofeno  → Otros
```

Después de reasignar las ventas, la categoría original puede eliminarse.

Esta operación debe realizarse de manera transaccional para evitar estados inconsistentes.

---

# 20. Gestión de categorías desde Configuración

La interfaz de configuración puede utilizar un `QListWidget` para mostrar las categorías del negocio.

Se contemplan acciones como:

```text
Agregar
Eliminar
Guardar cambios
```

Las modificaciones no deberían escribirse inmediatamente en la base de datos por cada interacción visual.

La operación final de guardar debe validar las reglas y persistir los cambios correctamente.

`Otros` debe aparecer como categoría protegida.

---

# 21. Edición de datos financieros

Todos los usuarios pueden importar.

Después de la importación:

```text
Gerente
    → puede modificar
    → puede eliminar

Analista Financiero
    → no puede modificar
    → no puede eliminar

Empleado
    → no puede modificar
    → no puede eliminar
```

El Gerente podrá corregir registros individualmente.

También podrá eliminar/revertir una importación completa cuando sea necesario.

---

# 22. Edición mediante tabla

La interfaz de datos podrá utilizar un modelo basado en `QAbstractTableModel`.

El modelo de Qt no debe convertirse en el lugar donde se coloque toda la lógica de persistencia.

La arquitectura esperada es conceptualmente:

```text
QTableView
    ↓
QAbstractTableModel
    ↓
Controller
    ↓
Service
    ↓
Repository
    ↓
Database
```

La edición debe pasar por validaciones antes de persistirse.

No se debe hacer que `setData()` escriba directamente en la base de datos sin pasar por la capa correspondiente.

---

# 23. Auditoría básica

No se necesita un historial completo de cambios.

Para `MOVEMENTS` y `SALE` únicamente se conservará:

```text
created_by
updated_by
created_at
updated_at
```

Esto permite saber:

* quién creó el registro;
* quién realizó la última modificación;
* cuándo fue creado;
* cuándo fue modificado.

No se creará una tabla de versiones o historial detallado de cada modificación.

---

# 24. Eliminación/reversión de importaciones

Una importación exitosa puede haber generado:

```text
MOVEMENTS
SALE
```

relacionados mediante:

```text
import_id
```

El Gerente puede eliminar una importación completa.

La operación debe afectar a los registros financieros pertenecientes a esa importación.

Debe evitarse dejar registros huérfanos o información financiera parcialmente eliminada.

---

# 25. Análisis

La aplicación debe conservar los datos históricos.

No se reemplazará el historial cada vez que se importe un nuevo Excel.

Los análisis deben poder trabajar con distintos períodos:

```text
Esta semana
Este mes
Mes anterior
Últimos 3 meses
Este año
Rango personalizado
```

También se podrán comparar períodos.

---

# 26. Indicadores principales

El módulo de análisis debe contemplar como mínimo:

```text
Total de ingresos
Total de gastos
Balance
Promedio de ingresos
Promedio de gastos
```

También debe poder analizar información por:

* fecha;
* mes;
* categoría;
* método de pago.

---

# 27. Análisis de ventas

El sistema debe poder obtener información como:

* producto/servicio más vendido;
* producto/servicio que genera mayor ingreso;
* ingresos por categoría de venta.

También se contemplan porcentajes como:

```text
% de gastos por categoría
% de ingresos provenientes de ventas
```

---

# 28. Recomendaciones

Las recomendaciones se generan a partir de los datos analizados.

No deben ser un módulo independiente que invente información sin relación con los resultados del análisis.

Está previsto utilizar herramientas de Machine Learning, incluyendo `scikit-learn`, para una parte del sistema de recomendaciones.

Las recomendaciones estarán en una página independiente de la página de análisis.

---

# 29. Arquitectura y separación de responsabilidades

La lógica debe mantenerse separada por capas.

Conceptualmente:

```text
UI
 ↓
Controller
 ↓
Service
 ↓
Repository
 ↓
SQLAlchemy
 ↓
MySQL
```

## UI

Responsable de:

* mostrar información;
* recibir acciones;
* mostrar mensajes;
* actualizar widgets.

No debe contener reglas de negocio complejas.

## Controller

Responsable de:

* recibir acciones de la interfaz;
* coordinar el flujo;
* llamar a los servicios correspondientes.

## Service

Responsable de:

* reglas de negocio;
* validaciones;
* permisos;
* transacciones;
* coordinación de múltiples operaciones.

Ejemplos:

```text
BusinessService
CategoryService
ImportService
MovementService
SaleService
AnalysisService
```

## Repository

Responsable de operaciones de acceso a datos.

Debe encargarse de:

* consultar;
* crear;
* actualizar;
* eliminar;
* buscar entidades.

No debe contener reglas de negocio complejas que pertenezcan al Service.

---

# 30. Transacciones

Las operaciones que modifican varias entidades relacionadas deben ejecutarse de manera transaccional.

Ejemplo: creación de negocio:

```text
crear Business
crear UserBusiness
crear categorías iniciales
```

Si una operación falla:

```text
ROLLBACK
```

Si todo funciona:

```text
COMMIT
```

Lo mismo aplica a operaciones como:

```text
eliminar categoría utilizada
    ↓
reasignar ventas a Otros
    ↓
eliminar categoría
```

No se debe permitir que solamente una parte de la operación quede persistida.

---

# 31. Regla general de consistencia

Las reglas importantes deben protegerse en más de una capa cuando sea necesario.

Por ejemplo, para `Otros`:

```text
UI
 ↓
muestra que no puede eliminarse
 ↓
Service
 ↓
rechaza la operación
 ↓
Database
 ↓
mantiene integridad mediante sus restricciones correspondientes
```

La interfaz nunca debe ser considerada la única barrera de seguridad o integridad.

---

# 32. Principio para futuras decisiones

Cuando aparezca una nueva funcionalidad, primero debe determinarse:

1. ¿Es una regla de negocio?
2. ¿A qué entidad afecta?
3. ¿Debe estar protegida por la base de datos?
4. ¿Debe validarse en Service?
5. ¿Es únicamente comportamiento de UI?
6. ¿Afecta el E-R existente?

No se debe modificar el modelo de datos únicamente para resolver un problema que realmente pertenece a la interfaz o a la lógica de negocio.

---

# 33. Resumen de entidades actuales

El modelo definido actualmente está compuesto por:

```text
USERS
BUSINESS
USER_BUSINESS
RECOVERY
IMPORT
MOVEMENTS
SALE
CATEGORY
```

Relaciones principales:

```text
USERS 1:N BUSINESS
USERS N:M BUSINESS → USER_BUSINESS
USERS 1:N RECOVERY
USERS 1:N IMPORT
BUSINESS 1:N IMPORT
BUSINESS 1:N MOVEMENTS
BUSINESS 1:N SALE
BUSINESS 1:N CATEGORY
IMPORT 1:N MOVEMENTS
IMPORT 1:N SALE
CATEGORY 1:N SALE
USERS 1:N MOVEMENTS → created_by
USERS 1:N MOVEMENTS → updated_by
USERS 1:N SALE → created_by
USERS 1:N SALE → updated_by
```

No existe relación directa:

```text
MOVEMENTS ↔ SALE
```

Este modelo debe considerarse la base funcional actual de Finanzen. Las decisiones futuras pueden ampliarlo, pero no deben contradecir estas reglas sin una revisión explícita del diseño.

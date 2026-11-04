--- Función para demostrar los indices de Finanzen
SELECT
    TABLE_NAME AS Tabla,
    INDEX_NAME AS Indice,
    GROUP_CONCAT(
        COLUMN_NAME
        ORDER BY SEQ_IN_INDEX
        SEPARATOR ', '
    ) AS Columnas
FROM INFORMATION_SCHEMA.STATISTICS
WHERE TABLE_SCHEMA = 'finanzen'
AND INDEX_NAME IN (
    'idx_sales_business_date',
    'idx_movements_business_date',
    'idx_import_business_date',
    'uq_import_business_hash',
    'uq_user_business',
    'uq_category_business_name'
)
GROUP BY TABLE_NAME, INDEX_NAME
ORDER BY TABLE_NAME;


-- Consulta para evaluar las reglas de integridad referencial
SELECT
    k.TABLE_NAME,
    k.CONSTRAINT_NAME,
    k.COLUMN_NAME,
    k.REFERENCED_TABLE_NAME,
    k.REFERENCED_COLUMN_NAME,
    r.DELETE_RULE,
    r.UPDATE_RULE
FROM INFORMATION_SCHEMA.KEY_COLUMN_USAGE AS k
JOIN INFORMATION_SCHEMA.REFERENTIAL_CONSTRAINTS AS r
    ON k.CONSTRAINT_SCHEMA = r.CONSTRAINT_SCHEMA
    AND k.CONSTRAINT_NAME = r.CONSTRAINT_NAME
    AND k.TABLE_NAME = r.TABLE_NAME
WHERE k.CONSTRAINT_SCHEMA = 'finanzen'
  AND k.REFERENCED_TABLE_NAME IS NOT NULL
ORDER BY k.TABLE_NAME, k.CONSTRAINT_NAME;
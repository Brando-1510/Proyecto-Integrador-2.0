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
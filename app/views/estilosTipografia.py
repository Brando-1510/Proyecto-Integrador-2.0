def estilos_fuentes(source_family,manrope_family):
    return f"""
    /* =========================
    FUENTE GENERAL
    ========================= */
        QWidget {{
            font-family: "{source_family}";
        }}
    /* =========================
        TÍTULOS PRINCIPALES
    ========================= */
        QLabel[texto="Principal"], QLabel[texto="TituloPrincipal"],
        QLabel[texto="Destacado"], {{
            font-family: "{manrope_family}";
            font-weight: bold;
        }}
    /* =========================
    BOTONES
    ========================= */
        QPushButton {{
            font-family: "{source_family}";
        }}
    /* =========================
    TÍTULOS DE SECCIÓN
    ========================= */
        QLabel[texto="InputTexto"],QPushButton[boton="BotonTexto"] {{
            font-family: "{manrope_family}";
            font-weight: bold;
        }}
    /* =========================
    TÍTULOS SECUNDARIOS
    ========================= */
        QLabel[styleClass="tituloSecundario"] {{
            font-family: "{source_family}";
        }}
    /* =========================
    LABELS GENERALES
    ========================= */
        QLabel {{
            font-family: "{source_family}";
        }}
    /* =========================
    INPUTS
    ========================= */
        QLineEdit,QDateEdit,QComboBox {{
            font-family: "{source_family}";
            font-size: 14px;
        }}
"""
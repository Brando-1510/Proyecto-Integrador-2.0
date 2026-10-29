def estilos_fuentes(source_family, manrope_family):
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
    QLabel[texto="Principal"],
    QLabel[texto="TituloPrincipal"],
    QLabel[texto="Destacado"],
    QLabel[texto="DestacadoArriba"] {{
        font-family: "{manrope_family}";
        font-weight: bold;
    }}

    /* =========================
       BOTONES DE QMESSAGEBOX
    ========================= */
    QMessageBox QPushButton,
    QInputDialog QPushButton{{
        font-family: "{source_family}";
        font-size: 12px;
        font-weight: bold;

        color: #F7F7F7;
        background-color: #5D38BB;

        border: none;
        border-radius: 5px;

        min-width: 80px;
        max-width: 120px;

        min-height: 28px;
        max-height: 28px;

        padding: 0px;
    }}

    QMessageBox QPushButton:hover 
    QInputDialog QPushButton:hover{{
        background-color: #744BCC;
    }}

    QMessageBox QPushButton:pressed 
    QInputDialog QPushButton:pressed{{
        background-color: #472A8F;
    }}

    /* =========================
       TÍTULOS DE SECCIÓN
    ========================= */
    QLabel[texto="InputTexto"],
    QPushButton[boton="BotonTexto"] {{
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
    QLineEdit,
    QDateEdit,
    QComboBox {{
        font-family: "{source_family}";
        font-size: 14px;
    }}

    /* =========================
       QMESSAGEBOX
    ========================= */
    QMessageBox,QInputDialog {{
        background-color: #F7F7F7;
    }}

    QMessageBox QLabel,
    QInputDialog QLabel{{
        color: #0E042F;
        font-family: "{source_family}";
        font-weight: 600;
    }}
    """

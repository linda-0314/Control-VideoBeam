"""Semana 7. Tabla de decisión de registrar_prestamo (HU-02, HU-03 y HU-08).

Esperados: criterios de aceptación de HU-02, HU-03 y HU-08 y las decisiones de
la tabla de ambigüedades (registro_pruebas.md, función 3).
"""

from datetime import datetime
from zoneinfo import ZoneInfo

import pytest

from prestamos.registro import Prestamo, registrar_prestamo
from prestamos.reglas import DatoInvalido, VideobeamNoExiste, VideobeamYaPrestado

BOGOTA = ZoneInfo("America/Bogota")
SALIDA = datetime(2026, 11, 21, 18, 40, tzinfo=BOGOTA)
PRESTADO_VB01 = [Prestamo("VB-01", "Mateo Díaz", "Redes", "Andrés Ruiz", SALIDA)]

FALTA_QUIEN = "^Escribe el nombre de quien lleva el videobeam$"
FALTA_CLASE = "^Falta la clase$"
FALTA_PROFESOR = "^Falta el nombre del profesor$"


# ----- Tabla de decisión: una fila por regla R1 a R5 -----


@pytest.mark.parametrize(
    ("quien", "clase", "profesor", "codigo", "error", "mensaje"),
    [
        ("", "Redes", "Andrés Ruiz", "VB-02", DatoInvalido, FALTA_QUIEN),  # R1: C1 no
        ("Laura Gómez", "", "Andrés Ruiz", "VB-02", DatoInvalido, FALTA_CLASE),  # R2: C2 no
        ("Laura Gómez", "Redes", "", "VB-02", DatoInvalido, FALTA_PROFESOR),  # R3: C3 no
        ("Laura Gómez", "Redes", "Andrés Ruiz", "VB-09", VideobeamNoExiste,
         "^El VB-09 no existe$"),  # R4: C4 no
        ("Laura Gómez", "Redes", "Andrés Ruiz", "VB-01", VideobeamYaPrestado,
         "^El VB-01 ya está prestado$"),  # R5: C5 no (HU-08 escenario 2)
    ],
)
def test_reglas_que_no_guardan(quien, clase, profesor, codigo, error, mensaje):
    with pytest.raises(error, match=mensaje):
        registrar_prestamo(codigo, PRESTADO_VB01, quien, clase, profesor, SALIDA)


# ----- El «—» de la tabla: si fallan varias condiciones, gana la primera regla -----


@pytest.mark.parametrize(
    ("quien", "clase", "profesor", "codigo", "mensaje"),
    [
        ("", "", "", "VB-01", FALTA_QUIEN),  # R1: fallan C1, C2, C3 y C5
        ("", "Redes", "Andrés Ruiz", "VB-09", FALTA_QUIEN),  # R1: fallan C1 y C4
        ("Laura Gómez", "", "", "VB-09", FALTA_CLASE),  # R2: fallan C2, C3 y C4
        ("Laura Gómez", "Redes", "", "VB-01", FALTA_PROFESOR),  # R3: fallan C3 y C5
    ],
)
def test_si_fallan_varias_condiciones_gana_la_primera(quien, clase, profesor, codigo, mensaje):
    with pytest.raises(DatoInvalido, match=mensaje):
        registrar_prestamo(codigo, PRESTADO_VB01, quien, clase, profesor, SALIDA)


def test_si_c4_y_c5_fallan_gana_que_no_existe():
    # R4 antes que R5: un código que no existe no puede estar prestado.
    with pytest.raises(VideobeamNoExiste):
        registrar_prestamo("VB-09", PRESTADO_VB01, "Laura Gómez", "Redes", "Andrés Ruiz", SALIDA)


def test_r6_prestamo_valido_guarda_todos_los_datos():
    # R6, HU-02 escenario 1: VB-02, Laura Gómez, Bases de datos, Andrés Ruiz, 6:40 p. m.
    prestamo = registrar_prestamo(
        "VB-02", PRESTADO_VB01, "Laura Gómez", "Bases de datos", "Andrés Ruiz", SALIDA
    )
    assert prestamo == Prestamo("VB-02", "Laura Gómez", "Bases de datos", "Andrés Ruiz", SALIDA)
    assert prestamo.fecha_hora_devolucion is None


# ----- Particiones inválidas de cada texto (P4, P5 y P6) -----


@pytest.mark.parametrize("vacio", ["", "   ", None])  # P4 vacío, P5 solo espacios, P6 None
@pytest.mark.parametrize(
    ("campo", "mensaje"),
    [
        ("quien_lleva", FALTA_QUIEN),  # HU-03 escenario 2
        ("clase", FALTA_CLASE),  # decisión: mismo estilo de HU-02
        ("profesor", FALTA_PROFESOR),  # HU-02 escenario 2
    ],
)
def test_texto_vacio_en_cada_campo(campo, mensaje, vacio):
    datos = {"quien_lleva": "Laura Gómez", "clase": "Redes", "profesor": "Andrés Ruiz"}
    datos[campo] = vacio
    with pytest.raises(DatoInvalido, match=mensaje):
        registrar_prestamo(
            "VB-02", [], datos["quien_lleva"], datos["clase"], datos["profesor"], SALIDA
        )


# ----- Particiones válidas y límites de longitud -----


@pytest.mark.parametrize(
    ("entrada", "guardado"),
    [
        ("Laura Gómez", "Laura Gómez"),  # P1
        ("  Laura Gómez ", "Laura Gómez"),  # P2: se quitan los espacios de los extremos
        ("Íñigo Peña", "Íñigo Peña"),  # P3: tilde y ñ
        ("Ana D'Ángelo", "Ana D'Ángelo"),  # P3: apóstrofo
        ("A", "A"),  # límite inferior: 1 carácter, primero válido
        ("x" * 100, "x" * 100),  # límite superior: 100 caracteres, último válido
        (" " + "x" * 100 + " ", "x" * 100),  # 102 con espacios: cuenta sin los extremos
    ],
)
def test_textos_validos_de_quien_lleva(entrada, guardado):
    prestamo = registrar_prestamo("VB-02", [], entrada, "Redes", "Andrés Ruiz", SALIDA)
    assert prestamo.quien_lleva == guardado


@pytest.mark.parametrize(
    ("campo", "mensaje"),
    [
        (
            "quien_lleva",
            "^El nombre de quien lleva el videobeam no puede tener más de 100 caracteres$",
        ),
        ("clase", "^La clase no puede tener más de 100 caracteres$"),
        ("profesor", "^El nombre del profesor no puede tener más de 100 caracteres$"),
    ],
)
def test_texto_de_101_caracteres_en_cada_campo(campo, mensaje):
    # P7, límite superior: 101 caracteres es el primer valor inválido (defecto D-01).
    datos = {"quien_lleva": "Laura Gómez", "clase": "Redes", "profesor": "Andrés Ruiz"}
    datos[campo] = "x" * 101
    with pytest.raises(DatoInvalido, match=mensaje):
        registrar_prestamo(
            "VB-02", [], datos["quien_lleva"], datos["clase"], datos["profesor"], SALIDA
        )

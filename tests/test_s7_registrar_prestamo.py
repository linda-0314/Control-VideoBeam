"""Semana 7. Tabla de decisión de registrar_prestamo (HU-02, HU-03 y HU-08)."""

from datetime import datetime
from zoneinfo import ZoneInfo

import pytest

from prestamos.registro import Prestamo, registrar_prestamo
from prestamos.reglas import DatoInvalido, VideobeamNoExiste, VideobeamYaPrestado

BOGOTA = ZoneInfo("America/Bogota")
SALIDA = datetime(2026, 11, 21, 18, 40, tzinfo=BOGOTA)
PRESTADO_VB01 = [Prestamo("VB-01", "Mateo Díaz", "Redes", "Andrés Ruiz", SALIDA)]


@pytest.mark.parametrize(
    ("quien", "clase", "profesor", "codigo", "error", "mensaje"),
    [
        ("", "Redes", "Andrés Ruiz", "VB-02", DatoInvalido,
         "Escribe el nombre de quien lleva el videobeam"),  # R1
        ("Laura Gómez", "", "Andrés Ruiz", "VB-02", DatoInvalido, "Falta la clase"),  # R2
        ("Laura Gómez", "Redes", "", "VB-02", DatoInvalido, "Falta el nombre del profesor"),  # R3
        ("Laura Gómez", "Redes", "Andrés Ruiz", "VB-09", VideobeamNoExiste,
         "El VB-09 no existe"),  # R4
        ("Laura Gómez", "Redes", "Andrés Ruiz", "VB-01", VideobeamYaPrestado,
         "El VB-01 ya está prestado"),  # R5
    ],
)
def test_reglas_que_no_guardan(quien, clase, profesor, codigo, error, mensaje):
    with pytest.raises(error, match=mensaje):
        registrar_prestamo(codigo, PRESTADO_VB01, quien, clase, profesor, SALIDA)


def test_r6_prestamo_valido():
    # R6
    prestamo = registrar_prestamo(
        "VB-02", PRESTADO_VB01, "Laura Gómez", "Bases de datos", "Andrés Ruiz", SALIDA
    )
    assert prestamo is not None
    assert prestamo.codigo == "VB-02"


@pytest.mark.parametrize(
    "vacio",
    [
        "",  # P4
        "   ",  # P5
        None,  # P6
    ],
)
def test_textos_vacios_en_profesor(vacio):
    with pytest.raises(DatoInvalido):
        registrar_prestamo("VB-02", [], "Laura Gómez", "Redes", vacio, SALIDA)


@pytest.mark.parametrize(
    "vacio",
    [
        "",  # P4
        "   ",  # P5
        None,  # P6
    ],
)
def test_textos_vacios_en_profesor_otra_vez(vacio):
    with pytest.raises(DatoInvalido, match="Falta el nombre del profesor"):
        registrar_prestamo("VB-02", [], "Laura Gómez", "Redes", vacio, SALIDA)


@pytest.mark.parametrize(
    ("entrada", "guardado"),
    [
        ("Laura Gómez", "Laura Gómez"),  # P1
        ("  Laura Gómez ", "Laura Gómez"),  # P2
        ("Íñigo Peña", "Íñigo Peña"),  # P3 tilde y ñ
        ("Ana D'Ángelo", "Ana D'Ángelo"),  # P3 apóstrofo
        ("A", "A"),  # límite inferior: 1 carácter
        ("x" * 100, "x" * 100),  # límite superior: 100 caracteres
    ],
)
def test_textos_validos_de_quien_lleva(entrada, guardado):
    prestamo = registrar_prestamo("VB-02", [], entrada, "Redes", "Andrés Ruiz", SALIDA)
    assert prestamo.quien_lleva == guardado


def test_texto_de_101_caracteres():
    # P7, límite superior inválido
    with pytest.raises(DatoInvalido):
        registrar_prestamo("VB-02", [], "x" * 101, "Redes", "Andrés Ruiz", SALIDA)

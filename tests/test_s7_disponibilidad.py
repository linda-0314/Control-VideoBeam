"""Semana 7. Tabla de casos de mensaje_disponibilidad (HU-01).

Esperados: criterios de aceptación de HU-01 (registro_pruebas.md, función 1).
"""

from datetime import datetime
from zoneinfo import ZoneInfo

import pytest

from prestamos.registro import Prestamo, mensaje_disponibilidad

BOGOTA = ZoneInfo("America/Bogota")
SALIDA = datetime(2026, 11, 21, 18, 40, tzinfo=BOGOTA)
DEVOLUCION = datetime(2026, 11, 21, 21, 30, tzinfo=BOGOTA)
CODIGOS = ["VB-01", "VB-02", "VB-03", "VB-04", "VB-05"]


def abiertos(cantidad: int) -> list[Prestamo]:
    return [Prestamo(c, "Laura Gómez", "Redes", "Andrés Ruiz", SALIDA) for c in CODIGOS[:cantidad]]


def cerrado(codigo: str) -> Prestamo:
    return Prestamo(codigo, "Laura Gómez", "Redes", "Andrés Ruiz", SALIDA, DEVOLUCION)


@pytest.mark.parametrize(
    ("prestados", "esperado"),
    [
        (0, "5 de 5 videobeams disponibles"),  # P1, límite inferior: ninguno prestado
        (1, "4 de 5 videobeams disponibles"),  # P1, primero después del límite inferior
        (3, "2 de 5 videobeams disponibles"),  # P1, HU-01 escenario 1
        (4, "1 de 5 videobeams disponibles"),  # P1, último antes del borde con P2
        (5, "No hay videobeams disponibles en este momento"),  # P2, HU-01 escenario 2
    ],
)
def test_mensaje_segun_cantidad_de_prestados(prestados, esperado):
    assert mensaje_disponibilidad(abiertos(prestados)) == esperado


@pytest.mark.parametrize(
    ("prestamos", "esperado"),
    [
        ([cerrado("VB-01")], "5 de 5 videobeams disponibles"),  # P3: uno devuelto no cuenta
        (
            [*abiertos(2), cerrado("VB-03"), cerrado("VB-04"), cerrado("VB-05")],
            "3 de 5 videobeams disponibles",
        ),  # P3: mezcla, solo cuentan los 2 abiertos
        (
            [*abiertos(5), cerrado("VB-01"), cerrado("VB-02")],
            "No hay videobeams disponibles en este momento",
        ),  # P3 con P2: préstamos viejos de VB-01 y VB-02 no liberan los abiertos
    ],
)
def test_los_prestamos_devueltos_no_cuentan(prestamos, esperado):
    assert mensaje_disponibilidad(prestamos) == esperado


def test_dos_registros_abiertos_del_mismo_videobeam_cuentan_una_vez():
    # P4 (datos inconsistentes que la base impide): VB-01 no puede estar prestado dos veces.
    duplicado = [*abiertos(1), *abiertos(1)]
    assert mensaje_disponibilidad(duplicado) == "4 de 5 videobeams disponibles"

"""Semana 7. Tabla de casos de mensaje_disponibilidad (HU-01)."""

from datetime import datetime
from zoneinfo import ZoneInfo

import pytest

from prestamos.registro import Prestamo, codigos_prestados, mensaje_disponibilidad

BOGOTA = ZoneInfo("America/Bogota")
SALIDA = datetime(2026, 11, 21, 18, 40, tzinfo=BOGOTA)
CODIGOS = ["VB-01", "VB-02", "VB-03", "VB-04", "VB-05"]


def abiertos(cantidad):
    return [Prestamo(c, "Laura Gómez", "Redes", "Andrés Ruiz", SALIDA) for c in CODIGOS[:cantidad]]


@pytest.mark.parametrize(
    ("prestados", "esperado"),
    [
        (0, "5 de 5 videobeams disponibles"),  # límite inferior de P1
        (1, "4 de 5 videobeams disponibles"),  # primero después del límite inferior
        (2, "3 de 5 videobeams disponibles"),  # P1, valor intermedio
        (3, "2 de 5 videobeams disponibles"),  # HU-01, escenario 1
        (4, "1 de 5 videobeams disponibles"),  # último de P1
        (5, "No hay videobeams disponibles en este momento"),  # P2, HU-01 escenario 2
    ],
)
def test_mensaje_segun_cantidad_de_prestados(prestados, esperado):
    assert mensaje_disponibilidad(abiertos(prestados)) == esperado


def test_mensaje_devuelve_texto():
    assert isinstance(mensaje_disponibilidad(abiertos(2)), str)


def test_prestamos_devueltos_no_cuentan():
    # P3
    cerrado = Prestamo("VB-01", "Laura Gómez", "Redes", "Andrés Ruiz", SALIDA, SALIDA)
    assert mensaje_disponibilidad([cerrado]) == "5 de 5 videobeams disponibles"


def test_codigos_prestados_con_tres():
    assert len(codigos_prestados(abiertos(3))) == 3

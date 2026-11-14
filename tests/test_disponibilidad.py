"""Pruebas de HU-01: consultar disponibilidad."""

from dataclasses import replace
from datetime import datetime

from conftest import prestamo_abierto
from prestamos.registro import codigos_prestados, mensaje_disponibilidad

# ----- Casos normales -----


def test_con_tres_prestados_hay_dos_de_cinco_disponibles(tres_prestados):
    # HU-01, escenario 1.
    assert mensaje_disponibilidad(tres_prestados) == "2 de 5 videobeams disponibles"


def test_sin_prestamos_estan_los_cinco_disponibles():
    assert mensaje_disponibilidad([]) == "5 de 5 videobeams disponibles"


def test_codigos_prestados_solo_trae_los_prestamos_abiertos(tres_prestados):
    assert codigos_prestados(tres_prestados) == frozenset({"VB-01", "VB-02", "VB-03"})


# ----- Casos límite -----


def test_con_cuatro_prestados_queda_uno_disponible():
    cuatro = [prestamo_abierto(c) for c in ("VB-01", "VB-02", "VB-03", "VB-04")]
    assert mensaje_disponibilidad(cuatro) == "1 de 5 videobeams disponibles"


def test_un_prestamo_devuelto_no_cuenta_como_prestado():
    devuelto = replace(
        prestamo_abierto("VB-01"), fecha_hora_devolucion=datetime(2026, 11, 14, 21, 30)
    )
    assert codigos_prestados([devuelto]) == frozenset()
    assert mensaje_disponibilidad([devuelto]) == "5 de 5 videobeams disponibles"


# ----- Caso de error del escenario -----


def test_con_los_cinco_prestados_no_hay_disponibles():
    # HU-01, escenario 2.
    cinco = [prestamo_abierto(f"VB-0{n}") for n in range(1, 6)]
    assert mensaje_disponibilidad(cinco) == "No hay videobeams disponibles en este momento"

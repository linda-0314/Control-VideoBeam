"""Pruebas de HU-05: devolución por otra persona."""

from datetime import datetime

import pytest
from conftest import BOGOTA, SALIDA

from prestamos.registro import Prestamo, codigos_prestados, registrar_devolucion_por
from prestamos.reglas import DatoInvalido, VideobeamNoPrestado

DEVOLUCION = datetime(2026, 11, 14, 21, 30, tzinfo=BOGOTA)
SIN_NOMBRE = "Escribe el nombre de quien devuelve el videobeam"


def prestamo_de_mateo() -> Prestamo:
    """HU-05, escenario 1: Mateo Díaz sacó el VB-01."""
    return Prestamo("VB-01", "Mateo Díaz", "Redes", "Andrés Ruiz", SALIDA)


def test_devuelve_otra_persona_y_se_guardan_los_dos_nombres():
    # HU-05, escenario 1: lo trae Sara López.
    devuelto = registrar_devolucion_por("VB-01", [prestamo_de_mateo()], "Sara López", DEVOLUCION)
    assert devuelto.quien_lleva == "Mateo Díaz"
    assert devuelto.quien_devuelve == "Sara López"
    assert devuelto.fecha_hora_devolucion == DEVOLUCION
    assert codigos_prestados([devuelto]) == frozenset()


def test_puede_devolverlo_la_misma_persona_que_lo_saco():
    devuelto = registrar_devolucion_por("VB-01", [prestamo_de_mateo()], "Mateo Díaz", DEVOLUCION)
    assert devuelto.quien_devuelve == "Mateo Díaz"


@pytest.mark.parametrize(
    "nombre",
    [
        "",  # vacío
        "   ",  # solo espacios
        None,  # no llegó el campo
    ],
)
def test_sin_nombre_de_quien_devuelve_no_se_registra(nombre):
    # HU-05, escenario 2.
    with pytest.raises(DatoInvalido, match=SIN_NOMBRE):
        registrar_devolucion_por("VB-01", [prestamo_de_mateo()], nombre, DEVOLUCION)


def test_se_quitan_los_espacios_de_los_extremos():
    devuelto = registrar_devolucion_por(
        "VB-01", [prestamo_de_mateo()], "  Sara López  ", DEVOLUCION
    )
    assert devuelto.quien_devuelve == "Sara López"


def test_nombre_de_100_caracteres_se_acepta():
    devuelto = registrar_devolucion_por("VB-01", [prestamo_de_mateo()], "a" * 100, DEVOLUCION)
    assert devuelto.quien_devuelve == "a" * 100


def test_nombre_de_101_caracteres_no_se_acepta():
    with pytest.raises(DatoInvalido, match="no puede tener más de 100 caracteres"):
        registrar_devolucion_por("VB-01", [prestamo_de_mateo()], "a" * 101, DEVOLUCION)


def test_primero_se_revisa_el_videobeam_y_despues_el_nombre():
    # El VB-04 no está prestado: ese error gana aunque falte el nombre.
    with pytest.raises(VideobeamNoPrestado, match="El VB-04 no está prestado"):
        registrar_devolucion_por("VB-04", [prestamo_de_mateo()], "", DEVOLUCION)


def test_no_modifica_la_lista_que_recibe():
    prestamos = [prestamo_de_mateo()]
    copia = list(prestamos)
    registrar_devolucion_por("VB-01", prestamos, "Sara López", DEVOLUCION)
    assert prestamos == copia
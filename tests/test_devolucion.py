"""Pruebas de HU-04: registrar devolución."""

from dataclasses import replace
from datetime import datetime

import pytest
from conftest import BOGOTA, SALIDA, prestamo_abierto

from prestamos.registro import codigos_prestados, mensaje_disponibilidad, registrar_devolucion
from prestamos.reglas import DatoInvalido, VideobeamNoExiste, VideobeamNoPrestado

DEVOLUCION = datetime(2026, 11, 14, 21, 30, tzinfo=BOGOTA)

# ----- Casos normales -----


def test_devolucion_normal_guarda_la_hora_y_deja_el_videobeam_disponible():
    # HU-04, escenario 1: el VB-02 salió a las 6:40 p. m. y vuelve a las 9:30 p. m.
    prestamos = [prestamo_abierto("VB-02")]
    devuelto = registrar_devolucion("VB-02", prestamos, DEVOLUCION)
    assert devuelto.fecha_hora_devolucion == DEVOLUCION
    assert devuelto.fecha_hora_salida == SALIDA
    assert codigos_prestados([devuelto]) == frozenset()
    assert mensaje_disponibilidad([devuelto]) == "5 de 5 videobeams disponibles"


def test_devuelve_el_prestamo_abierto_aunque_haya_prestamos_viejos_del_mismo_videobeam():
    ayer = datetime(2026, 11, 13, 21, 0, tzinfo=BOGOTA)
    viejo = replace(prestamo_abierto("VB-02"), fecha_hora_devolucion=ayer)
    abierto = prestamo_abierto("VB-02")
    devuelto = registrar_devolucion("VB-02", [viejo, abierto], DEVOLUCION)
    assert devuelto.fecha_hora_salida == SALIDA
    assert devuelto.fecha_hora_devolucion == DEVOLUCION


def test_no_modifica_el_prestamo_original():
    abierto = prestamo_abierto("VB-02")
    registrar_devolucion("VB-02", [abierto], DEVOLUCION)
    assert abierto.fecha_hora_devolucion is None


# ----- Casos límite -----


def test_se_puede_devolver_en_el_mismo_minuto_de_la_salida():
    devuelto = registrar_devolucion("VB-02", [prestamo_abierto("VB-02")], SALIDA)
    assert devuelto.fecha_hora_devolucion == SALIDA


def test_se_puede_devolver_al_dia_siguiente():
    # HU-06: si no se devolvió en la jornada, igual se debe poder registrar después.
    al_dia_siguiente = datetime(2026, 11, 15, 7, 15, tzinfo=BOGOTA)
    devuelto = registrar_devolucion("VB-02", [prestamo_abierto("VB-02")], al_dia_siguiente)
    assert devuelto.fecha_hora_devolucion == al_dia_siguiente


# ----- Casos de error -----


def test_devolver_uno_que_no_estaba_prestado_muestra_el_mensaje_de_hu04():
    # HU-04, escenario 2: el VB-04 está disponible.
    with pytest.raises(VideobeamNoPrestado, match="El VB-04 no está prestado") as error:
        registrar_devolucion("VB-04", [prestamo_abierto("VB-01")], DEVOLUCION)
    assert error.value.estado_http == 409


def test_no_se_puede_devolver_dos_veces_el_mismo_prestamo():
    ya_devuelto = replace(prestamo_abierto("VB-02"), fecha_hora_devolucion=DEVOLUCION)
    with pytest.raises(VideobeamNoPrestado, match="El VB-02 no está prestado"):
        registrar_devolucion("VB-02", [ya_devuelto], DEVOLUCION)


def test_devolver_un_codigo_que_no_existe():
    with pytest.raises(VideobeamNoExiste, match="El VB-09 no existe"):
        registrar_devolucion("VB-09", [], DEVOLUCION)


def test_la_devolucion_no_puede_ser_anterior_a_la_salida():
    antes = datetime(2026, 11, 14, 18, 0, tzinfo=BOGOTA)
    with pytest.raises(
        DatoInvalido, match="La hora de devolución no puede ser anterior a la de salida"
    ):
        registrar_devolucion("VB-02", [prestamo_abierto("VB-02")], antes)

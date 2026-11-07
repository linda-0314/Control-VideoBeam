"""Pruebas de HU-08: no prestar un videobeam que ya está prestado."""

import pytest

from prestamos.reglas import (
    VideobeamNoExiste,
    VideobeamYaPrestado,
    prestar_videobeam,
)


# ----- Casos normales -----

def test_prestar_uno_disponible_lo_agrega_a_los_prestados():
    # HU-08, escenario 1: el VB-04 está disponible y pasa a prestado.
    resultado = prestar_videobeam("VB-04", frozenset({"VB-01"}))
    assert resultado == frozenset({"VB-01", "VB-04"})


def test_prestar_cuando_no_hay_ninguno_prestado():
    resultado = prestar_videobeam("VB-02", frozenset())
    assert resultado == frozenset({"VB-02"})


def test_prestar_no_modifica_el_conjunto_que_recibe():
    prestados = frozenset({"VB-01"})
    prestar_videobeam("VB-03", prestados)
    assert prestados == frozenset({"VB-01"})


# ----- Casos límite -----

def test_prestar_el_primer_videobeam():
    assert prestar_videobeam("VB-01", frozenset()) == frozenset({"VB-01"})


def test_prestar_el_ultimo_videobeam():
    assert prestar_videobeam("VB-05", frozenset()) == frozenset({"VB-05"})


def test_prestar_el_ultimo_que_quedaba_libre_deja_los_cinco_prestados():
    cuatro = frozenset({"VB-01", "VB-02", "VB-03", "VB-04"})
    resultado = prestar_videobeam("VB-05", cuatro)
    assert resultado == frozenset({"VB-01", "VB-02", "VB-03", "VB-04", "VB-05"})


def test_con_los_cinco_prestados_no_se_puede_prestar_ninguno():
    cinco = frozenset({"VB-01", "VB-02", "VB-03", "VB-04", "VB-05"})
    with pytest.raises(VideobeamYaPrestado, match="El VB-03 ya está prestado"):
        prestar_videobeam("VB-03", cinco)


# ----- Casos de error -----

def test_prestar_uno_ya_prestado_muestra_el_mensaje_de_hu08():
    # HU-08, escenario 2: el VB-01 está prestado a «Mateo Díaz».
    with pytest.raises(VideobeamYaPrestado, match="El VB-01 ya está prestado"):
        prestar_videobeam("VB-01", frozenset({"VB-01"}))


def test_prestar_un_codigo_que_no_existe():
    with pytest.raises(VideobeamNoExiste, match="El VB-09 no existe"):
        prestar_videobeam("VB-09", frozenset())


def test_codigo_en_minusculas_se_trata_como_inexistente():
    # Supuesto del contrato: el código llega exacto desde la lista del formulario.
    with pytest.raises(VideobeamNoExiste):
        prestar_videobeam("vb-02", frozenset())


def test_el_error_de_ya_prestado_no_cambia_los_prestados():
    prestados = frozenset({"VB-01", "VB-02"})
    with pytest.raises(VideobeamYaPrestado):
        prestar_videobeam("VB-02", prestados)
    assert prestados == frozenset({"VB-01", "VB-02"})

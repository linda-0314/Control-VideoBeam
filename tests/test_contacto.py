"""Pruebas de HU-09: identificación y celular de quien lleva el videobeam."""

import pytest

from prestamos.registro import validar_contacto
from prestamos.reglas import DatoInvalido

FALTA_ID = "Escribe el número de identificación de quien lleva el videobeam"
ID_INVALIDA = "La identificación debe tener entre 6 y 10 dígitos"
CELULAR_INVALIDO = "El celular debe tener 10 dígitos y empezar por 3"


def test_identificacion_y_celular_validos():
    assert validar_contacto("1075123456", "3001234567") == ("1075123456", "3001234567")


def test_el_celular_es_opcional():
    assert validar_contacto("1075123456", "") == ("1075123456", "")
    assert validar_contacto("1075123456", None) == ("1075123456", "")


def test_se_quitan_espacios_y_guiones():
    assert validar_contacto(" 1075 123 456 ", "300 123-4567") == ("1075123456", "3001234567")


@pytest.mark.parametrize("identificacion", ["", "   ", None])
def test_sin_identificacion_no_se_acepta(identificacion):
    with pytest.raises(DatoInvalido, match=FALTA_ID):
        validar_contacto(identificacion, "3001234567")


@pytest.mark.parametrize(
    "identificacion",
    [
        "12345",  # límite: 5 dígitos, uno menos del mínimo
        "12345678901",  # límite: 11 dígitos, uno más del máximo
        "10751A3456",  # tiene una letra
        "²²²²²²",  # dígitos que no son 0-9
    ],
)
def test_identificacion_invalida(identificacion):
    with pytest.raises(DatoInvalido, match=ID_INVALIDA):
        validar_contacto(identificacion, "")


@pytest.mark.parametrize(
    "identificacion",
    [
        "123456",  # límite: 6 dígitos
        "1234567890",  # límite: 10 dígitos
    ],
)
def test_identificacion_en_los_limites(identificacion):
    assert validar_contacto(identificacion, "")[0] == identificacion


@pytest.mark.parametrize(
    "celular",
    [
        "300123456",  # 9 dígitos
        "30012345678",  # 11 dígitos
        "6001234567",  # no empieza por 3 (fijo)
        "300123456a",  # tiene una letra
    ],
)
def test_celular_invalido(celular):
    with pytest.raises(DatoInvalido, match=CELULAR_INVALIDO):
        validar_contacto("1075123456", celular)
"""Semana 7. Tabla de casos de registrar_devolucion (HU-04)."""

from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

import pytest

from prestamos.registro import Prestamo, registrar_devolucion
from prestamos.reglas import DatoInvalido, VideobeamNoExiste, VideobeamNoPrestado

BOGOTA = ZoneInfo("America/Bogota")
SALIDA = datetime(2026, 11, 21, 18, 40, tzinfo=BOGOTA)
ABIERTO_VB02 = Prestamo("VB-02", "Laura Gómez", "Bases de datos", "Andrés Ruiz", SALIDA)


@pytest.mark.parametrize(
    "devolucion",
    [
        SALIDA,  # límite: misma hora
        SALIDA + timedelta(minutes=1),  # un minuto después
        datetime(2026, 11, 21, 21, 30, tzinfo=BOGOTA),  # HU-04 escenario 1
        datetime(2026, 11, 21, 23, 59, tzinfo=BOGOTA),  # último minuto del día
        datetime(2026, 11, 22, 0, 0, tzinfo=BOGOTA),  # día siguiente (HU-06)
    ],
)
def test_devoluciones_validas(devolucion):
    devuelto = registrar_devolucion("VB-02", [ABIERTO_VB02], devolucion)
    assert devuelto.fecha_hora_devolucion == devolucion


def test_devolucion_un_minuto_antes_de_la_salida():
    with pytest.raises(DatoInvalido):
        registrar_devolucion("VB-02", [ABIERTO_VB02], SALIDA - timedelta(minutes=1))


@pytest.mark.parametrize(
    ("codigo", "prestamos", "error"),
    [
        ("VB-04", [ABIERTO_VB02], VideobeamNoPrestado),  # P2, HU-04 escenario 2
        ("VB-02", [], VideobeamNoPrestado),  # P2 sin préstamos
        ("VB-09", [ABIERTO_VB02], VideobeamNoExiste),  # P4
    ],
)
def test_devoluciones_invalidas(codigo, prestamos, error):
    with pytest.raises(error):
        registrar_devolucion(codigo, prestamos, SALIDA)


def test_no_modifica_el_prestamo_original():
    registrar_devolucion("VB-02", [ABIERTO_VB02], SALIDA)
    assert ABIERTO_VB02.fecha_hora_devolucion is None

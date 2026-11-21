"""Semana 7. Tabla de casos de registrar_devolucion (HU-04).

Esperados: criterios de aceptación de HU-04, HU-06 y la decisión de la
bitácora, entrada 12 (registro_pruebas.md, función 4).
"""

from dataclasses import replace
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
        SALIDA,  # límite: la misma hora de la salida, primer valor válido
        datetime(2026, 11, 21, 21, 30, tzinfo=BOGOTA),  # P1, HU-04 escenario 1 (9:30 p. m.)
        datetime(2026, 11, 21, 23, 59, tzinfo=BOGOTA),  # límite de día: último minuto del día
        datetime(2026, 11, 22, 0, 0, tzinfo=BOGOTA),  # límite de día: día siguiente (HU-06)
    ],
)
def test_devolucion_valida_cierra_el_mismo_prestamo(devolucion):
    devuelto = registrar_devolucion("VB-02", [ABIERTO_VB02], devolucion)
    assert devuelto == replace(ABIERTO_VB02, fecha_hora_devolucion=devolucion)


def test_devolucion_un_minuto_antes_de_la_salida():
    # P5, límite: 6:39 p. m. es el último valor inválido.
    with pytest.raises(
        DatoInvalido, match="^La hora de devolución no puede ser anterior a la de salida$"
    ):
        registrar_devolucion("VB-02", [ABIERTO_VB02], SALIDA - timedelta(minutes=1))


def test_con_prestamos_viejos_cierra_el_abierto():
    # P6: VB-02 se prestó y devolvió ayer, y hoy está prestado otra vez.
    ayer = datetime(2026, 11, 20, 18, 40, tzinfo=BOGOTA)
    viejo = Prestamo("VB-02", "Sara López", "Redes", "Andrés Ruiz", ayer, ayer + timedelta(hours=2))
    devolucion = datetime(2026, 11, 21, 21, 30, tzinfo=BOGOTA)
    devuelto = registrar_devolucion("VB-02", [viejo, ABIERTO_VB02], devolucion)
    assert devuelto == replace(ABIERTO_VB02, fecha_hora_devolucion=devolucion)


@pytest.mark.parametrize(
    ("codigo", "prestamos", "error", "mensaje"),
    [
        ("VB-04", [ABIERTO_VB02], VideobeamNoPrestado,
         "^El VB-04 no está prestado$"),  # P2, HU-04 escenario 2
        ("VB-02", [replace(ABIERTO_VB02, fecha_hora_devolucion=SALIDA)], VideobeamNoPrestado,
         "^El VB-02 no está prestado$"),  # P3: ya se devolvió, no se devuelve dos veces
        ("VB-09", [ABIERTO_VB02], VideobeamNoExiste, "^El VB-09 no existe$"),  # P4
    ],
)
def test_devoluciones_invalidas(codigo, prestamos, error, mensaje):
    with pytest.raises(error, match=mensaje):
        registrar_devolucion(codigo, prestamos, SALIDA + timedelta(hours=1))

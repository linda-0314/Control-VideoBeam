"""Pruebas de HU-06: videobeams pendientes de días anteriores."""

from dataclasses import replace
from datetime import datetime, timezone

from conftest import BOGOTA, prestamo_abierto

from prestamos.registro import prestamos_pendientes

AHORA = datetime(2026, 11, 25, 8, 0, tzinfo=BOGOTA)
AYER = datetime(2026, 11, 24, 18, 0, tzinfo=BOGOTA)


def test_sin_prestamos_no_hay_pendientes():
    assert prestamos_pendientes([], AHORA) == []


def test_prestamo_de_hoy_no_es_pendiente():
    hoy = prestamo_abierto("VB-01", datetime(2026, 11, 25, 7, 0, tzinfo=BOGOTA))
    assert prestamos_pendientes([hoy], AHORA) == []


def test_prestamo_de_ayer_sin_devolver_es_pendiente():
    ayer = prestamo_abierto("VB-02", AYER)
    assert prestamos_pendientes([ayer], AHORA) == [ayer]


def test_prestamo_de_ayer_devuelto_no_es_pendiente():
    devuelto = replace(
        prestamo_abierto("VB-02", AYER),
        fecha_hora_devolucion=datetime(2026, 11, 24, 21, 0, tzinfo=BOGOTA),
    )
    assert prestamos_pendientes([devuelto], AHORA) == []


# ----- Valores límite: el cambio de día -----


def test_salida_a_las_11_59_pm_de_ayer_es_pendiente():
    ultimo_minuto = prestamo_abierto("VB-03", datetime(2026, 11, 24, 23, 59, tzinfo=BOGOTA))
    assert prestamos_pendientes([ultimo_minuto], AHORA) == [ultimo_minuto]


def test_salida_a_las_12_00_am_de_hoy_no_es_pendiente():
    primer_minuto = prestamo_abierto("VB-03", datetime(2026, 11, 25, 0, 0, tzinfo=BOGOTA))
    assert prestamos_pendientes([primer_minuto], AHORA) == []


# ----- Zona horaria: la base guarda en UTC -----


def test_salida_de_las_7_pm_guardada_en_utc_cuenta_como_de_ese_dia():
    # 7:00 p. m. del 25 en Neiva son las 12:00 a. m. del 26 en UTC.
    siete_pm = prestamo_abierto("VB-04", datetime(2026, 11, 26, 0, 0, tzinfo=timezone.utc))
    nueve_pm = datetime(2026, 11, 25, 21, 0, tzinfo=BOGOTA)
    assert prestamos_pendientes([siete_pm], nueve_pm) == []


# ----- Varios préstamos -----


def test_solo_trae_los_pendientes_ordenados_del_mas_antiguo():
    hoy = prestamo_abierto("VB-01", datetime(2026, 11, 25, 7, 0, tzinfo=BOGOTA))
    ayer = prestamo_abierto("VB-02", AYER)
    anteayer = prestamo_abierto("VB-03", datetime(2026, 11, 23, 18, 0, tzinfo=BOGOTA))
    prestamos = [hoy, ayer, anteayer]
    assert prestamos_pendientes(prestamos, AHORA) == [anteayer, ayer]


def test_no_modifica_la_lista_que_recibe():
    prestamos = [prestamo_abierto("VB-02", AYER)]
    copia = list(prestamos)
    prestamos_pendientes(prestamos, AHORA)
    assert prestamos == copia
"""Pruebas de los préstamos de hoy (HU-10) y los HDMI por recuperar (HU-07)."""

from dataclasses import replace
from datetime import datetime, timezone

from conftest import BOGOTA, prestamo_abierto

from prestamos.registro import hdmi_por_recuperar, prestamos_del_dia

AHORA = datetime(2026, 11, 25, 20, 0, tzinfo=BOGOTA)


def test_solo_trae_los_prestamos_de_hoy_en_el_orden_en_que_salieron():
    tarde = prestamo_abierto("VB-01", datetime(2026, 11, 25, 18, 40, tzinfo=BOGOTA))
    manana = prestamo_abierto("VB-02", datetime(2026, 11, 25, 7, 0, tzinfo=BOGOTA))
    ayer = prestamo_abierto("VB-03", datetime(2026, 11, 24, 18, 0, tzinfo=BOGOTA))
    assert prestamos_del_dia([tarde, ayer, manana], AHORA) == [manana, tarde]


def test_los_devueltos_de_hoy_tambien_aparecen():
    devuelto = replace(
        prestamo_abierto("VB-01", datetime(2026, 11, 25, 7, 0, tzinfo=BOGOTA)),
        fecha_hora_devolucion=datetime(2026, 11, 25, 9, 0, tzinfo=BOGOTA),
    )
    assert prestamos_del_dia([devuelto], AHORA) == [devuelto]


def test_una_salida_de_las_7_pm_guardada_en_utc_es_de_hoy():
    # 7:00 p. m. del 25 en Neiva son las 12:00 a. m. del 26 en UTC.
    siete_pm = prestamo_abierto("VB-04", datetime(2026, 11, 26, 0, 0, tzinfo=timezone.utc))
    assert prestamos_del_dia([siete_pm], AHORA) == [siete_pm]


def test_sin_prestamos_hoy_la_lista_esta_vacia():
    assert prestamos_del_dia([], AHORA) == []


def test_hdmi_por_recuperar_solo_trae_los_devueltos_sin_hdmi():
    salida = datetime(2026, 11, 25, 7, 0, tzinfo=BOGOTA)
    sin_hdmi = replace(
        prestamo_abierto("VB-05", salida),
        fecha_hora_devolucion=datetime(2026, 11, 25, 9, 0, tzinfo=BOGOTA),
        con_hdmi=True,
        hdmi_devuelto=False,
        observacion="Devuelto sin HDMI",
    )
    con_hdmi = replace(sin_hdmi, codigo="VB-01", hdmi_devuelto=True, observacion="")
    assert hdmi_por_recuperar([con_hdmi, sin_hdmi]) == [sin_hdmi]
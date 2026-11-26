"""Pruebas de HU-07: control del HDMI."""

from dataclasses import replace
from datetime import datetime

from conftest import BOGOTA, SALIDA

from prestamos.registro import Prestamo, registrar_devolucion_por, registrar_hdmi

DEVOLUCION = datetime(2026, 11, 14, 21, 30, tzinfo=BOGOTA)


def devuelto(con_hdmi: bool) -> Prestamo:
    """El VB-05 de Mateo Díaz, ya devuelto por Sara López."""
    abierto = replace(
        Prestamo("VB-05", "Mateo Díaz", "Redes", "Andrés Ruiz", SALIDA), con_hdmi=con_hdmi
    )
    return registrar_devolucion_por("VB-05", [abierto], "Sara López", DEVOLUCION)


def test_sale_y_vuelve_con_hdmi_queda_sin_observaciones():
    # HU-07, escenario 1.
    resultado = registrar_hdmi(devuelto(con_hdmi=True), hdmi_devuelto=True)
    assert resultado.hdmi_devuelto is True
    assert resultado.observacion == ""


def test_sale_con_hdmi_y_vuelve_sin_el_queda_la_observacion():
    # HU-07, escenario 2: queda devuelto, con la observación y quién lo llevó.
    resultado = registrar_hdmi(devuelto(con_hdmi=True), hdmi_devuelto=False)
    assert resultado.hdmi_devuelto is False
    assert resultado.observacion == "Devuelto sin HDMI"
    assert resultado.quien_lleva == "Mateo Díaz"
    assert resultado.fecha_hora_devolucion == DEVOLUCION


def test_si_salio_sin_hdmi_no_hay_observacion():
    resultado = registrar_hdmi(devuelto(con_hdmi=False), hdmi_devuelto=False)
    assert resultado.hdmi_devuelto is None
    assert resultado.observacion == ""


def test_si_salio_sin_hdmi_no_importa_si_marcan_hdmi_devuelto():
    resultado = registrar_hdmi(devuelto(con_hdmi=False), hdmi_devuelto=True)
    assert resultado.hdmi_devuelto is None
    assert resultado.observacion == ""
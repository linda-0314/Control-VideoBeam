"""Pruebas de HU-07: control del HDMI."""

from dataclasses import replace
from datetime import datetime

import pytest
from conftest import BOGOTA, SALIDA

from prestamos.registro import (
    Prestamo,
    hdmi_por_recuperar,
    recuperar_hdmi,
    registrar_devolucion_por,
    registrar_hdmi,
)
from prestamos.reglas import DatoInvalido

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


# ----- El HDMI que faltaba vuelve después -----

RECUPERADO = datetime(2026, 11, 26, 11, 40, tzinfo=BOGOTA)


def test_al_recuperar_el_hdmi_sale_de_la_lista_por_recuperar():
    sin_hdmi = registrar_hdmi(devuelto(con_hdmi=True), hdmi_devuelto=False)
    recuperado = recuperar_hdmi(sin_hdmi, RECUPERADO)
    assert recuperado.hdmi_devuelto is True
    assert hdmi_por_recuperar([recuperado]) == []


def test_la_observacion_guarda_cuando_se_recupero():
    sin_hdmi = registrar_hdmi(devuelto(con_hdmi=True), hdmi_devuelto=False)
    recuperado = recuperar_hdmi(sin_hdmi, RECUPERADO)
    assert recuperado.observacion == "HDMI recuperado el 26/11/2026 11:40"
    assert recuperado.quien_lleva == "Mateo Díaz"
    assert recuperado.fecha_hora_devolucion == DEVOLUCION


def test_no_se_puede_recuperar_un_hdmi_que_no_faltaba():
    con_hdmi = registrar_hdmi(devuelto(con_hdmi=True), hdmi_devuelto=True)
    with pytest.raises(DatoInvalido, match="Ese préstamo no tiene un HDMI por recuperar"):
        recuperar_hdmi(con_hdmi, RECUPERADO)
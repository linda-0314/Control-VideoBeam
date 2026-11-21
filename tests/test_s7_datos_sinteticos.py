"""Semana 7. Pruebas con los datos sintéticos del fixture datos_sinteticos.

Esperados: los mismos de la tabla de decisión de registrar_prestamo
(registro_pruebas.md, función 3): un préstamo válido guarda los textos sin los
espacios de los extremos, y uno inválido da el mensaje de su regla.
"""

import html
from datetime import datetime
from zoneinfo import ZoneInfo

import pytest

from prestamos.models import Prestamo as PrestamoGuardado
from prestamos.registro import Prestamo, registrar_prestamo
from prestamos.reglas import DatoInvalido

SALIDA = datetime(2026, 11, 21, 18, 40, tzinfo=ZoneInfo("America/Bogota"))
CAMPOS = ("quien_lleva", "clase", "profesor")


def test_los_datos_sinteticos_tienen_los_casos_dificiles(datos_sinteticos):
    # Si alguien edita el archivo y quita un caso difícil, esta prueba lo avisa.
    textos = " ".join(d[c] for d in datos_sinteticos["validos"] for c in CAMPOS)
    for caracter in ("á", "Á", "ñ", "Ñ", "ü", "'", "-"):
        assert caracter in textos
    assert any(d["clase"] == "0" for d in datos_sinteticos["validos"])
    largos = {len(d["quien_lleva"]) for g in ("validos", "invalidos") for d in datos_sinteticos[g]}
    assert {0, 100, 101} <= largos


def test_cada_prestamo_valido_guarda_sus_textos_sin_espacios_en_los_extremos(datos_sinteticos):
    for dato in datos_sinteticos["validos"]:
        prestamo = registrar_prestamo(
            dato["codigo"], [], dato["quien_lleva"], dato["clase"], dato["profesor"], SALIDA
        )
        esperado = Prestamo(dato["codigo"], *(dato[c].strip() for c in CAMPOS), SALIDA)
        assert prestamo == esperado, dato["caso"]


def test_cada_prestamo_invalido_da_el_mensaje_de_su_regla(datos_sinteticos):
    for dato in datos_sinteticos["invalidos"]:
        with pytest.raises(DatoInvalido) as error:
            registrar_prestamo(
                "VB-02", [], dato["quien_lleva"], dato["clase"], dato["profesor"], SALIDA
            )
        assert str(error.value) == dato["mensaje"], dato["caso"]


def test_la_pagina_muestra_los_cinco_prestamos_con_sus_caracteres(cliente, datos_sinteticos):
    # Los 5 préstamos válidos por la aplicación web: tildes, ñ y apóstrofo
    # se guardan en SQLite y se muestran iguales (el HTML escapa el apóstrofo).
    for dato in datos_sinteticos["validos"]:
        formulario = {"codigo": dato["codigo"], **{c: dato[c] for c in CAMPOS}}
        respuesta = cliente.post("/prestamos/", formulario)
        assert respuesta.status_code == 302, dato["caso"]
    pagina = html.unescape(cliente.get("/").content.decode())
    assert "No hay videobeams disponibles en este momento" in pagina
    for dato in datos_sinteticos["validos"]:
        guardado = PrestamoGuardado.objects.get(videobeam__codigo=dato["codigo"])
        assert (guardado.quien_lleva, guardado.clase, guardado.profesor) == tuple(
            dato[c].strip() for c in CAMPOS
        ), dato["caso"]
        assert dato["quien_lleva"].strip() in pagina, dato["caso"]

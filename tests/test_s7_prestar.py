"""Semana 7. Tabla de casos de prestar_videobeam (HU-08).

Esperados: criterios de aceptación de HU-08 y tabla de la API del diseño
(registro_pruebas.md, función 2).
"""

import pytest

from prestamos.reglas import VideobeamNoExiste, VideobeamYaPrestado, prestar_videobeam

CINCO = frozenset({"VB-01", "VB-02", "VB-03", "VB-04", "VB-05"})


@pytest.mark.parametrize(
    ("codigo", "prestados", "esperado"),
    [
        ("VB-04", frozenset({"VB-01"}), frozenset({"VB-01", "VB-04"})),  # P1, HU-08 escenario 1
        ("VB-01", frozenset(), frozenset({"VB-01"})),  # límite inferior: primer código válido
        ("VB-05", frozenset(), frozenset({"VB-05"})),  # límite superior: último código válido
        ("VB-05", CINCO - {"VB-05"}, CINCO),  # límite: se presta el último libre, quedan 5
    ],
)
def test_prestar_un_videobeam_libre(codigo, prestados, esperado):
    assert prestar_videobeam(codigo, prestados) == esperado


@pytest.mark.parametrize(
    ("codigo", "prestados"),
    [
        ("VB-01", frozenset({"VB-01"})),  # P2, HU-08 escenario 2
        ("VB-03", CINCO),  # límite: con los 5 prestados no se presta ninguno
    ],
)
def test_prestar_uno_ya_prestado(codigo, prestados):
    with pytest.raises(VideobeamYaPrestado, match=f"^El {codigo} ya está prestado$"):
        prestar_videobeam(codigo, prestados)


@pytest.mark.parametrize(
    ("codigo", "mensaje"),
    [
        ("VB-00", "^El VB-00 no existe$"),  # límite inferior: último código inválido
        ("VB-06", "^El VB-06 no existe$"),  # límite superior: primer código inválido
        ("VB-09", "^El VB-09 no existe$"),  # P3, ejemplo de la tabla de la API
        ("vb-02", "^El vb-02 no existe$"),  # P4, minúsculas: no se convierten
        (" VB-02", "^El  VB-02 no existe$"),  # P4, espacio adelante: no se recorta
        ("VB2", "^El VB2 no existe$"),  # P4, sin guion ni cero
        ("", "^El  no existe$"),  # P5, vacío
        (None, "^El None no existe$"),  # P5, sin valor
    ],
)
def test_prestar_un_codigo_que_no_es_de_la_biblioteca(codigo, mensaje):
    with pytest.raises(VideobeamNoExiste, match=mensaje):
        prestar_videobeam(codigo, frozenset())

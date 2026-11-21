"""Semana 7. Tabla de casos de prestar_videobeam (HU-08)."""

import pytest

from prestamos.reglas import VideobeamNoExiste, VideobeamYaPrestado, prestar_videobeam


@pytest.mark.parametrize(
    ("codigo", "prestados", "esperado"),
    [
        ("VB-04", frozenset({"VB-01"}), frozenset({"VB-01", "VB-04"})),  # P1, HU-08 escenario 1
        ("VB-01", frozenset(), frozenset({"VB-01"})),  # límite inferior válido
        ("VB-05", frozenset(), frozenset({"VB-05"})),  # límite superior válido
        ("VB-05", frozenset({"VB-01", "VB-02", "VB-03", "VB-04"}), frozenset(
            {"VB-01", "VB-02", "VB-03", "VB-04", "VB-05"})),  # último libre
    ],
)
def test_prestar_codigos_validos(codigo, prestados, esperado):
    assert prestar_videobeam(codigo, prestados) == esperado


@pytest.mark.parametrize(
    "codigo",
    [
        "VB-00",  # límite inferior inválido
        "VB-06",  # límite superior inválido
        "VB-09",  # P3
        "vb-02",  # P4 minúsculas
        " VB-02",  # P4 espacio
        "VB2",  # P4 sin guion
        "",  # P5 vacío
        None,  # P5 None
    ],
)
def test_prestar_codigo_que_no_existe(codigo):
    with pytest.raises(Exception):
        prestar_videobeam(codigo, frozenset())


def test_prestar_uno_ya_prestado():
    # P2, HU-08 escenario 2
    with pytest.raises(VideobeamYaPrestado):
        prestar_videobeam("VB-01", frozenset({"VB-01"}))


def test_prestar_con_los_cinco_prestados():
    cinco = frozenset({"VB-01", "VB-02", "VB-03", "VB-04", "VB-05"})
    with pytest.raises(VideobeamYaPrestado):
        prestar_videobeam("VB-02", cinco)


def test_mensaje_codigo_inexistente():
    with pytest.raises(VideobeamNoExiste) as error:
        prestar_videobeam("VB-09", frozenset())
    assert "no existe" in str(error.value)

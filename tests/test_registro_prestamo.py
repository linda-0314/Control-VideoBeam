"""Pruebas de HU-02: registrar préstamo."""

import pytest

from conftest import SALIDA
from prestamos.registro import Prestamo, mensaje_disponibilidad, registrar_prestamo
from prestamos.reglas import DatoInvalido, VideobeamNoExiste, VideobeamYaPrestado


def registrar(codigo="VB-02", prestamos=(), quien="Laura Gómez", clase="Bases de datos",
              profesor="Andrés Ruiz"):
    return registrar_prestamo(codigo, list(prestamos), quien, clase, profesor, SALIDA)


# ----- Casos normales -----


def test_prestamo_completo_guarda_los_datos_sin_devolucion():
    # HU-02, escenario 1: VB-02, Laura Gómez, Bases de datos, Andrés Ruiz, 6:40 p. m.
    prestamo = registrar()
    assert prestamo == Prestamo("VB-02", "Laura Gómez", "Bases de datos", "Andrés Ruiz", SALIDA)
    assert prestamo.fecha_hora_devolucion is None


def test_despues_del_prestamo_la_disponibilidad_baja_de_cinco_a_cuatro():
    prestamo = registrar()
    assert mensaje_disponibilidad([prestamo]) == "4 de 5 videobeams disponibles"


def test_quita_los_espacios_alrededor_de_los_nombres():
    prestamo = registrar(quien="  Laura Gómez ", profesor=" Andrés Ruiz")
    assert prestamo.quien_lleva == "Laura Gómez"
    assert prestamo.profesor == "Andrés Ruiz"


def test_no_modifica_la_lista_de_prestamos_que_recibe():
    prestamos = []
    registrar_prestamo("VB-02", prestamos, "Laura Gómez", "Bases de datos", "Andrés Ruiz", SALIDA)
    assert prestamos == []


# ----- Casos de error -----


def test_sin_profesor_no_guarda_y_muestra_el_mensaje_de_hu02():
    # HU-02, escenario 2.
    with pytest.raises(DatoInvalido, match="Falta el nombre del profesor") as error:
        registrar(profesor="")
    assert error.value.estado_http == 400


def test_sin_quien_lo_lleva_muestra_el_mensaje_de_hu03():
    with pytest.raises(DatoInvalido, match="Escribe el nombre de quien lleva el videobeam"):
        registrar(quien="")


def test_sin_clase_muestra_que_falta_la_clase():
    with pytest.raises(DatoInvalido, match="Falta la clase"):
        registrar(clase="")


@pytest.mark.parametrize("vacio", ["   ", None])
def test_solo_espacios_o_none_cuentan_como_dato_faltante(vacio):
    with pytest.raises(DatoInvalido, match="Falta el nombre del profesor"):
        registrar(profesor=vacio)


def test_no_presta_uno_que_ya_esta_prestado():
    # Integra la regla de HU-08.
    primero = registrar(codigo="VB-01")
    with pytest.raises(VideobeamYaPrestado, match="El VB-01 ya está prestado"):
        registrar(codigo="VB-01", prestamos=[primero])


def test_no_presta_un_codigo_que_no_existe():
    with pytest.raises(VideobeamNoExiste, match="El VB-09 no existe"):
        registrar(codigo="VB-09")

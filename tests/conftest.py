"""Datos y configuración de prueba compartidos.

Los nombres son ficticios, del documento de requisitos. Este archivo también
prepara Django para pytest: crea una base de datos de prueba en memoria una
sola vez y cada prueba con el fixture `db` corre dentro de una transacción
que se deshace al terminar, así ninguna prueba deja datos para la siguiente.
"""

import json
import os
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

import django
import pytest

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
# Clave solo para pruebas: la real va en .env y nunca en el código.
os.environ.setdefault("DJANGO_SECRET_KEY", "solo-para-pruebas-no-sirve-en-la-biblioteca")
django.setup()

from django.contrib.auth.models import User  # noqa: E402
from django.db import transaction  # noqa: E402
from django.test import Client  # noqa: E402
from django.test.utils import (  # noqa: E402
    setup_databases,
    setup_test_environment,
    teardown_databases,
    teardown_test_environment,
)

from prestamos.registro import Prestamo  # noqa: E402

# Zona horaria de Neiva. Django guarda fechas con zona (USE_TZ = True), así que
# las pruebas también las usan: comparar una fecha con zona y otra sin zona falla.
BOGOTA = ZoneInfo("America/Bogota")

# Jornada de la noche del 14 de noviembre de 2026 (6:30 p. m. a 10:00 p. m.).
SALIDA = datetime(2026, 11, 14, 18, 40, tzinfo=BOGOTA)


def prestamo_abierto(codigo: str, salida: datetime = SALIDA) -> Prestamo:
    """Préstamo sin devolución, con los datos de HU-02."""
    return Prestamo(codigo, "Laura Gómez", "Bases de datos", "Andrés Ruiz", salida)


@pytest.fixture
def tres_prestados() -> list[Prestamo]:
    return [prestamo_abierto("VB-01"), prestamo_abierto("VB-02"), prestamo_abierto("VB-03")]


# ----- Django -----


@pytest.fixture(scope="session")
def base_de_datos_de_prueba():
    """Crea la base de prueba con las migraciones (incluye VB-01 a VB-05)."""
    setup_test_environment()
    configuracion = setup_databases(verbosity=0, interactive=False)
    yield
    teardown_databases(configuracion, verbosity=0)
    teardown_test_environment()


@pytest.fixture
def db(base_de_datos_de_prueba):
    """Cada prueba corre en una transacción que se deshace al final."""
    with transaction.atomic():
        yield
        transaction.set_rollback(True)


@pytest.fixture
def bibliotecario(db) -> User:
    return User.objects.create_user("bibliotecario", password="Clave-de-prueba-2026")


@pytest.fixture
def anonimo(db) -> Client:
    """Navegador sin iniciar sesión."""
    return Client()


@pytest.fixture
def cliente(bibliotecario) -> Client:
    """Navegador con la sesión del bibliotecario iniciada."""
    navegador = Client()
    navegador.force_login(bibliotecario)
    return navegador


# ----- Datos sintéticos (semana 7) -----


@pytest.fixture
def datos_sinteticos() -> dict:
    """Préstamos inventados con casos difíciles, de tests/datos_sinteticos.json.

    Tienen tildes, ñ, diéresis, apóstrofo, guion, espacios, el texto "0" y
    textos de 100 y 101 eñes. Ningún dato es de una persona real.
    """
    ruta = Path(__file__).parent / "datos_sinteticos.json"
    return json.loads(ruta.read_text(encoding="utf-8"))

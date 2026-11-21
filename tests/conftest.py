"""Datos de prueba compartidos: nombres ficticios del documento de requisitos."""

from datetime import datetime
from zoneinfo import ZoneInfo

import pytest

from prestamos.registro import Prestamo

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

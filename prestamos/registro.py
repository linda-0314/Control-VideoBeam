"""Registro de préstamos y devoluciones (HU-01, HU-02 y HU-04)."""

from collections.abc import Iterable
from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class Prestamo:
    codigo: str
    quien_lleva: str
    clase: str
    profesor: str
    fecha_hora_salida: datetime
    fecha_hora_devolucion: datetime | None = None


def codigos_prestados(prestamos: Iterable[Prestamo]) -> frozenset[str]:
    raise NotImplementedError


def mensaje_disponibilidad(prestamos: Iterable[Prestamo]) -> str:
    raise NotImplementedError


def registrar_prestamo(
    codigo: str,
    prestamos: Iterable[Prestamo],
    quien_lleva: str,
    clase: str,
    profesor: str,
    fecha_hora_salida: datetime,
) -> Prestamo:
    raise NotImplementedError


def registrar_devolucion(
    codigo: str, prestamos: Iterable[Prestamo], fecha_hora: datetime
) -> Prestamo:
    raise NotImplementedError

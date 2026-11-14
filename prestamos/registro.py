"""Registro de préstamos y devoluciones (HU-01, HU-02 y HU-04)."""

from collections.abc import Iterable
from dataclasses import dataclass, replace
from datetime import datetime

from prestamos.reglas import (
    VIDEOBEAMS_DE_LA_BIBLIOTECA,
    DatoInvalido,
    VideobeamNoExiste,
    VideobeamNoPrestado,
    prestar_videobeam,
)


@dataclass(frozen=True)
class Prestamo:
    codigo: str
    quien_lleva: str
    clase: str
    profesor: str
    fecha_hora_salida: datetime
    fecha_hora_devolucion: datetime | None = None


def codigos_prestados(prestamos: Iterable[Prestamo]) -> frozenset[str]:
    return frozenset(p.codigo for p in prestamos if p.fecha_hora_devolucion is None)


def mensaje_disponibilidad(prestamos: Iterable[Prestamo]) -> str:
    libres = len(VIDEOBEAMS_DE_LA_BIBLIOTECA) - len(codigos_prestados(prestamos))
    if libres == 0:
        return "No hay videobeams disponibles en este momento"
    return f"{libres} de {len(VIDEOBEAMS_DE_LA_BIBLIOTECA)} videobeams disponibles"


def registrar_prestamo(
    codigo: str,
    prestamos: Iterable[Prestamo],
    quien_lleva: str,
    clase: str,
    profesor: str,
    fecha_hora_salida: datetime,
) -> Prestamo:
    if quien_lleva is None or quien_lleva.strip() == "":
        raise DatoInvalido("Escribe el nombre de quien lleva el videobeam")
    if clase is None or clase.strip() == "":
        raise DatoInvalido("Falta la clase")
    if profesor is None or profesor.strip() == "":
        raise DatoInvalido("Falta el nombre del profesor")
    prestar_videobeam(codigo, codigos_prestados(prestamos))
    return Prestamo(
        codigo, quien_lleva.strip(), clase.strip(), profesor.strip(), fecha_hora_salida
    )


def registrar_devolucion(
    codigo: str, prestamos: Iterable[Prestamo], fecha_hora: datetime
) -> Prestamo:
    if codigo not in VIDEOBEAMS_DE_LA_BIBLIOTECA:
        raise VideobeamNoExiste(codigo)
    for p in prestamos:
        if p.codigo == codigo and p.fecha_hora_devolucion is None:
            if fecha_hora < p.fecha_hora_salida:
                raise DatoInvalido("La hora de devolución no puede ser anterior a la de salida")
            return replace(p, fecha_hora_devolucion=fecha_hora)
    raise VideobeamNoPrestado(codigo)

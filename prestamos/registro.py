"""Registro de préstamos y devoluciones (HU-01, HU-02 y HU-04).

Python puro, sin Django: las vistas de GET /videobeams/disponibilidad,
POST /prestamos y PATCH /prestamos/{id} llaman estas funciones y guardan el
Prestamo que devuelven (documento de diseño, sección 6). Ninguna función
modifica la lista que recibe ni toma la hora del reloj: la hora llega como
parámetro para poder probarla.
"""

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

TOTAL_VIDEOBEAMS = len(VIDEOBEAMS_DE_LA_BIBLIOTECA)

# Máximo de caracteres de quién lo lleva, la clase y el profesor: lo mismo que
# guarda cada campo en models.py y el maxlength del formulario.
LONGITUD_MAXIMA_TEXTO = 100


@dataclass(frozen=True)
class Prestamo:
    """Un préstamo de la planilla, como la entidad Prestamo del modelo de datos.

    Attributes:
        codigo: Código del videobeam, por ejemplo "VB-02".
        quien_lleva: Nombre de quien se lleva el videobeam.
        clase: Clase para la que se presta.
        profesor: Profesor responsable de la clase.
        fecha_hora_salida: Fecha y hora en que salió de la biblioteca.
        fecha_hora_devolucion: Fecha y hora de la devolución, o None si
            todavía no se ha devuelto.
    """

    codigo: str
    quien_lleva: str
    clase: str
    profesor: str
    fecha_hora_salida: datetime
    fecha_hora_devolucion: datetime | None = None

    @property
    def esta_abierto(self) -> bool:
        """True si el videobeam todavía no se ha devuelto."""
        return self.fecha_hora_devolucion is None


def codigos_prestados(prestamos: Iterable[Prestamo]) -> frozenset[str]:
    """Devuelve los códigos de los videobeams que están prestados ahora.

    Args:
        prestamos: Todos los préstamos registrados, abiertos y cerrados.

    Returns:
        frozenset[str]: Códigos con un préstamo sin devolución.
    """
    return frozenset(p.codigo for p in prestamos if p.esta_abierto)


def mensaje_disponibilidad(prestamos: Iterable[Prestamo]) -> str:
    """Arma el mensaje de disponibilidad que ve el bibliotecario (HU-01).

    Args:
        prestamos: Todos los préstamos registrados, abiertos y cerrados.

    Returns:
        str: "2 de 5 videobeams disponibles", o "No hay videobeams
        disponibles en este momento" si los 5 están prestados.
    """
    libres = TOTAL_VIDEOBEAMS - len(codigos_prestados(prestamos))
    if libres == 0:
        return "No hay videobeams disponibles en este momento"
    return f"{libres} de {TOTAL_VIDEOBEAMS} videobeams disponibles"


def registrar_prestamo(
    codigo: str,
    prestamos: Iterable[Prestamo],
    quien_lleva: str,
    clase: str,
    profesor: str,
    fecha_hora_salida: datetime,
) -> Prestamo:
    """Crea el préstamo de un videobeam disponible (HU-02 con la regla de HU-08).

    Primero revisa los datos del formulario, en el orden quién lo lleva,
    clase y profesor, y después el videobeam.

    Args:
        codigo: Código del videobeam, exacto como lo envía la lista del
            formulario, por ejemplo "VB-02".
        prestamos: Todos los préstamos registrados; no se modifica.
        quien_lleva: Nombre de quien se lo lleva; se le quitan los espacios
            de los extremos.
        clase: Nombre de la clase; se le quitan los espacios de los extremos.
        profesor: Nombre del profesor; se le quitan los espacios de los
            extremos.
        fecha_hora_salida: Fecha y hora del préstamo.

    Returns:
        Prestamo: El préstamo nuevo, sin fecha de devolución.

    Raises:
        DatoInvalido: Si quien_lleva, clase o profesor está vacío, tiene solo
            espacios o es None. Mensajes: "Escribe el nombre de quien lleva el
            videobeam", "Falta la clase" o "Falta el nombre del profesor".
            También si alguno tiene más de 100 caracteres sin contar los
            espacios de los extremos, por ejemplo "La clase no puede tener
            más de 100 caracteres".
        VideobeamNoExiste: Si el código no es de la biblioteca.
        VideobeamYaPrestado: Si el videobeam tiene un préstamo abierto.
    """
    quien_lleva = _texto_obligatorio(
        quien_lleva,
        "Escribe el nombre de quien lleva el videobeam",
        "El nombre de quien lleva el videobeam",
    )
    clase = _texto_obligatorio(clase, "Falta la clase", "La clase")
    profesor = _texto_obligatorio(
        profesor, "Falta el nombre del profesor", "El nombre del profesor"
    )
    prestar_videobeam(codigo, codigos_prestados(prestamos))
    return Prestamo(codigo, quien_lleva, clase, profesor, fecha_hora_salida)


def registrar_devolucion(
    codigo: str, prestamos: Iterable[Prestamo], fecha_hora: datetime
) -> Prestamo:
    """Cierra el préstamo abierto de un videobeam con la hora de devolución (HU-04).

    Args:
        codigo: Código del videobeam que se devuelve, por ejemplo "VB-02".
        prestamos: Todos los préstamos registrados; no se modifica.
        fecha_hora: Fecha y hora de la devolución. Puede ser de otro día si
            el videobeam no se devolvió en su jornada (HU-06).

    Returns:
        Prestamo: Una copia del préstamo abierto con fecha_hora_devolucion.

    Raises:
        VideobeamNoExiste: Si el código no es de la biblioteca.
        VideobeamNoPrestado: Si el videobeam no tiene un préstamo abierto.
            Mensaje: "El VB-04 no está prestado".
        DatoInvalido: Si fecha_hora es anterior a la salida. Mensaje: "La hora
            de devolución no puede ser anterior a la de salida".
    """
    if codigo not in VIDEOBEAMS_DE_LA_BIBLIOTECA:
        raise VideobeamNoExiste(codigo)
    abierto = _prestamo_abierto(codigo, prestamos)
    if abierto is None:
        raise VideobeamNoPrestado(codigo)
    if fecha_hora < abierto.fecha_hora_salida:
        raise DatoInvalido("La hora de devolución no puede ser anterior a la de salida")
    return replace(abierto, fecha_hora_devolucion=fecha_hora)


def _texto_obligatorio(valor: str | None, mensaje_si_falta: str, nombre_del_campo: str) -> str:
    """Devuelve el texto sin espacios en los extremos.

    Lanza DatoInvalido si queda vacío o si pasa de LONGITUD_MAXIMA_TEXTO.
    """
    if valor is None or not valor.strip():
        raise DatoInvalido(mensaje_si_falta)
    texto = valor.strip()
    if len(texto) > LONGITUD_MAXIMA_TEXTO:
        raise DatoInvalido(
            f"{nombre_del_campo} no puede tener más de {LONGITUD_MAXIMA_TEXTO} caracteres"
        )
    return texto


def _prestamo_abierto(codigo: str, prestamos: Iterable[Prestamo]) -> Prestamo | None:
    """Busca el préstamo sin devolución de un videobeam; None si no hay."""
    return next((p for p in prestamos if p.codigo == codigo and p.esta_abierto), None)



def prestamos_pendientes(
    prestamos: Iterable[Prestamo], fecha_hora_actual: datetime
) -> list[Prestamo]:
    """Devuelve los préstamos que no se devolvieron en su jornada (HU-06).

    Un préstamo está pendiente si sigue abierto y salió un día anterior al de
    `fecha_hora_actual`. Los días se comparan en la zona horaria de
    `fecha_hora_actual`, para que una salida de las 7:00 p. m. en Neiva no
    cuente como del día siguiente por estar guardada en UTC.

    Args:
        prestamos: Todos los préstamos registrados, abiertos y cerrados.
        fecha_hora_actual: Fecha y hora de la consulta, con zona horaria.

    Returns:
        list[Prestamo]: Los préstamos pendientes, del más antiguo al más reciente.
    """
    hoy = fecha_hora_actual.date()
    zona = fecha_hora_actual.tzinfo
    pendientes = [
        p for p in prestamos if p.esta_abierto and p.fecha_hora_salida.astimezone(zona).date() < hoy
    ]
    return sorted(pendientes, key=lambda p: p.fecha_hora_salida)
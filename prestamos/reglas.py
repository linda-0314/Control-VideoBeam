"""Reglas del préstamo de videobeams.

Python puro, sin Django: la vista de POST /prestamos llama estas funciones
antes de guardar y responde con el `estado_http` del error que se lance
(documento de diseño, sección 6).
"""

from collections.abc import Set

# Los 5 videobeams de la biblioteca de la FET (requisitos de la semana 3).
VIDEOBEAMS_DE_LA_BIBLIOTECA = frozenset({"VB-01", "VB-02", "VB-03", "VB-04", "VB-05"})


class ErrorDePrestamo(Exception):
    """Error de una regla del préstamo, con el código del videobeam afectado.

    Cada subclase define `plantilla` (el mensaje que ve el bibliotecario) y
    `estado_http` (la respuesta de la API), para que la vista de Django
    atrape un solo tipo de error.

    Attributes:
        codigo: Código del videobeam que causó el error, por ejemplo "VB-01".
    """

    plantilla = "Error con el {codigo}"
    estado_http = 400

    def __init__(self, codigo: object) -> None:
        self.codigo = codigo
        super().__init__(self.plantilla.format(codigo=codigo))


class VideobeamNoExiste(ErrorDePrestamo):
    """El código no es uno de los videobeams de la biblioteca (API: 404)."""

    plantilla = "El {codigo} no existe"
    estado_http = 404


class VideobeamYaPrestado(ErrorDePrestamo):
    """El videobeam tiene un préstamo sin devolución (HU-08, escenario 2; API: 409)."""

    plantilla = "El {codigo} ya está prestado"
    estado_http = 409


def prestar_videobeam(codigo: str, prestados: Set[str]) -> frozenset[str]:
    """Marca un videobeam como prestado si existe y está libre (HU-08).

    Args:
        codigo: Código del videobeam que se quiere prestar, exacto como lo
            envía la lista del formulario, por ejemplo "VB-04".
        prestados: Códigos de los videobeams que tienen un préstamo sin
            devolución. Puede ser un set o un frozenset; no se modifica.

    Returns:
        frozenset[str]: Un conjunto nuevo con los prestados más `codigo`.

    Raises:
        VideobeamNoExiste: Si `codigo` no es uno de los 5 videobeams de la
            biblioteca, por ejemplo "VB-09", "vb-02" o None.
        VideobeamYaPrestado: Si `codigo` ya está en `prestados`. El mensaje
            es "El VB-01 ya está prestado".
    """
    if codigo not in VIDEOBEAMS_DE_LA_BIBLIOTECA:
        raise VideobeamNoExiste(codigo)
    if codigo in prestados:
        raise VideobeamYaPrestado(codigo)
    return frozenset(prestados) | {codigo}


class VideobeamNoPrestado(ErrorDePrestamo):
    """Se intenta devolver un videobeam sin préstamo abierto (HU-04, escenario 2; API: 409)."""

    plantilla = "El {codigo} no está prestado"
    estado_http = 409


class DatoInvalido(ErrorDePrestamo):
    """Falta un dato del formulario o no es válido (HU-02, escenario 2; API: 400)."""

    estado_http = 400

    def __init__(self, mensaje: str) -> None:
        self.codigo = None
        Exception.__init__(self, mensaje)

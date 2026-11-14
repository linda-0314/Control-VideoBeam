"""Reglas del préstamo de videobeams.

Python puro, sin Django: la vista de POST /prestamos llama estas funciones
antes de guardar y convierte VideobeamNoExiste en 404 y VideobeamYaPrestado
en 409 (documento de diseño, sección 6).
"""

# Los 5 videobeams de la biblioteca de la FET (requisitos de la semana 3).
VIDEOBEAMS_DE_LA_BIBLIOTECA = frozenset({"VB-01", "VB-02", "VB-03", "VB-04", "VB-05"})


class VideobeamYaPrestado(Exception):
    """El videobeam tiene un préstamo sin devolución (HU-08, escenario 2)."""


class VideobeamNoExiste(Exception):
    """El código no es uno de los videobeams de la biblioteca."""


def prestar_videobeam(codigo: str, prestados: frozenset[str]) -> frozenset[str]:
    """Devuelve los prestados más `codigo`, sin modificar `prestados`.

    Lanza VideobeamNoExiste si el código no es de la biblioteca y
    VideobeamYaPrestado si ya está prestado.
    """
    if codigo not in VIDEOBEAMS_DE_LA_BIBLIOTECA:
        raise VideobeamNoExiste(f"El {codigo} no existe")
    if codigo in prestados:
        raise VideobeamYaPrestado(f"El {codigo} ya está prestado")
    return frozenset(prestados) | {codigo}

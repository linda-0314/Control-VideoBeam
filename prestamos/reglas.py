"""Reglas del préstamo de videobeams (HU-08)."""


class VideobeamYaPrestado(Exception):
    pass


class VideobeamNoExiste(Exception):
    pass


def prestar_videobeam(codigo: str, prestados: frozenset[str]) -> frozenset[str]:
    if codigo not in ["VB-01", "VB-02", "VB-03", "VB-04", "VB-05"]:
        raise VideobeamNoExiste("El " + codigo + " no existe")
    if codigo in prestados:
        raise VideobeamYaPrestado("El " + codigo + " ya está prestado")
    return prestados | {codigo}

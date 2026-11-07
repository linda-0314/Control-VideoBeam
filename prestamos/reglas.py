"""Reglas del préstamo de videobeams (HU-08)."""


class VideobeamYaPrestado(Exception):
    pass


class VideobeamNoExiste(Exception):
    pass


def prestar_videobeam(codigo: str, prestados: frozenset[str]) -> frozenset[str]:
    raise NotImplementedError("Falta implementar prestar_videobeam")

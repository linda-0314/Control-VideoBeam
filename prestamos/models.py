"""Modelo de datos (documento de diseño, sección 5): Videobeam y Prestamo.

Las reglas no van aquí sino en reglas.py y registro.py (Python puro). Estos
modelos solo guardan los datos y convierten un préstamo al formato de esas
reglas con `a_registro`.
"""

from django.db import models
from django.db.models import Q

from prestamos import registro


class Videobeam(models.Model):
    """Uno de los 5 videobeams de la biblioteca (VB-01 a VB-05)."""

    codigo = models.CharField(max_length=5, unique=True)

    class Meta:
        ordering = ["codigo"]

    def __str__(self) -> str:
        return self.codigo


class Prestamo(models.Model):
    """Una fila de la planilla: quién lleva qué videobeam, para qué clase y cuándo."""

    videobeam = models.ForeignKey(Videobeam, on_delete=models.PROTECT, related_name="prestamos")
    quien_lleva = models.CharField(max_length=100)
    clase = models.CharField(max_length=100)
    profesor = models.CharField(max_length=100)
    fecha_hora_salida = models.DateTimeField()
    fecha_hora_devolucion = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-fecha_hora_salida"]
        constraints = [
            # HU-08 en la base de datos: un solo préstamo abierto por videobeam,
            # aunque dos registros lleguen casi al mismo tiempo.
            models.UniqueConstraint(
                fields=["videobeam"],
                condition=Q(fecha_hora_devolucion__isnull=True),
                name="un_prestamo_abierto_por_videobeam",
            ),
        ]

    def __str__(self) -> str:
        return f"{self.videobeam.codigo} - {self.quien_lleva}"

    def a_registro(self) -> registro.Prestamo:
        """Convierte el préstamo guardado al formato de las reglas de registro.py."""
        return registro.Prestamo(
            self.videobeam.codigo,
            self.quien_lleva,
            self.clase,
            self.profesor,
            self.fecha_hora_salida,
            self.fecha_hora_devolucion,
        )

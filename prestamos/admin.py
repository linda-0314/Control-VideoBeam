"""Administración de Django: para consultar la planilla completa de préstamos."""

from django.contrib import admin

from prestamos.models import Prestamo, Videobeam


@admin.register(Videobeam)
class VideobeamAdmin(admin.ModelAdmin):
    list_display = ["codigo"]


@admin.register(Prestamo)
class PrestamoAdmin(admin.ModelAdmin):
    list_display = [
        "videobeam",
        "quien_lleva",
        "clase",
        "profesor",
        "fecha_hora_salida",
        "fecha_hora_devolucion",
        "quien_devuelve",
        "con_hdmi",
        "hdmi_devuelto",
        "observacion",
    ]
    list_filter = ["videobeam", "fecha_hora_salida"]
    search_fields = ["quien_lleva", "profesor", "clase"]

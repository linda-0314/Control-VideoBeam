"""Rutas de la app de préstamos."""

from django.urls import path

from prestamos import views

urlpatterns = [
    path("", views.inicio, name="inicio"),
    path("prestamos/", views.crear_prestamo, name="crear_prestamo"),
    path("devoluciones/", views.registrar_devolucion, name="registrar_devolucion"),
]

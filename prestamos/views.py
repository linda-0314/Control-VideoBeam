"""Pantallas del bibliotecario: disponibilidad, préstamo y devolución.

Las vistas no deciden nada por su cuenta: leen los préstamos de la base, llaman
las reglas de registro.py y, si una regla lanza un ErrorDePrestamo, muestran su
mensaje con su estado_http (400, 404 o 409). Todas exigen sesión (ADR-002).
"""

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError, transaction
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect, render
from django.utils import timezone
from django.views.decorators.http import require_GET, require_POST

from prestamos import registro
from prestamos.models import Prestamo, Videobeam
from prestamos.reglas import ErrorDePrestamo, VideobeamYaPrestado

CAMPOS_PRESTAMO = ("codigo", "quien_lleva", "clase", "profesor")


@login_required
@require_GET
def inicio(request: HttpRequest) -> HttpResponse:
    """HU-01: cuántos videobeams hay disponibles y el estado de cada uno."""
    return _pagina_inicio(request)


@login_required
@require_POST
def crear_prestamo(request: HttpRequest) -> HttpResponse:
    """HU-02 con la regla de HU-08: registra un préstamo o muestra por qué no."""
    datos = {campo: request.POST.get(campo, "") for campo in CAMPOS_PRESTAMO}
    try:
        with transaction.atomic():
            nuevo = registro.registrar_prestamo(
                datos["codigo"],
                _prestamos_abiertos(),
                datos["quien_lleva"],
                datos["clase"],
                datos["profesor"],
                timezone.now(),
            )
            Prestamo.objects.create(
                videobeam=Videobeam.objects.get(codigo=nuevo.codigo),
                quien_lleva=nuevo.quien_lleva,
                clase=nuevo.clase,
                profesor=nuevo.profesor,
                fecha_hora_salida=nuevo.fecha_hora_salida,
            )
    except IntegrityError:
        # Otro préstamo del mismo videobeam se guardó justo antes (restricción de la base).
        return _pagina_inicio(request, VideobeamYaPrestado(datos["codigo"]), datos)
    except ErrorDePrestamo as error:
        return _pagina_inicio(request, error, datos)
    messages.success(request, f"Préstamo registrado: {nuevo.codigo} a {nuevo.quien_lleva}")
    return redirect("inicio")


@login_required
@require_POST
def registrar_devolucion(request: HttpRequest) -> HttpResponse:
    """HU-04: cierra el préstamo abierto del videobeam con la hora actual."""
    codigo = request.POST.get("codigo", "")
    try:
        with transaction.atomic():
            devuelto = registro.registrar_devolucion(codigo, _prestamos_abiertos(), timezone.now())
            Prestamo.objects.filter(
                videobeam__codigo=devuelto.codigo, fecha_hora_devolucion__isnull=True
            ).update(fecha_hora_devolucion=devuelto.fecha_hora_devolucion)
    except ErrorDePrestamo as error:
        return _pagina_inicio(request, error)
    messages.success(request, f"Devolución registrada: {devuelto.codigo}")
    return redirect("inicio")


def _prestamos_abiertos() -> list[registro.Prestamo]:
    """Los préstamos sin devolución, en el formato de las reglas."""
    abiertos = Prestamo.objects.filter(fecha_hora_devolucion__isnull=True)
    return [p.a_registro() for p in abiertos.select_related("videobeam")]


def _pagina_inicio(
    request: HttpRequest, error: ErrorDePrestamo | None = None, datos: dict | None = None
) -> HttpResponse:
    """Arma la página de inicio; con un error, responde con su estado_http."""
    abiertos = {
        p.videobeam.codigo: p
        for p in Prestamo.objects.filter(fecha_hora_devolucion__isnull=True).select_related(
            "videobeam"
        )
    }
    videobeams = [(v.codigo, abiertos.get(v.codigo)) for v in Videobeam.objects.all()]
    contexto = {
        "mensaje_disponibilidad": registro.mensaje_disponibilidad(
            [p.a_registro() for p in abiertos.values()]
        ),
        "videobeams": videobeams,
        "disponibles": [codigo for codigo, prestamo in videobeams if prestamo is None],
        "prestados": [codigo for codigo, prestamo in videobeams if prestamo is not None],
        "error": error,
        "datos": datos or {},
    }
    estado = error.estado_http if error else 200
    return render(request, "prestamos/inicio.html", contexto, status=estado)

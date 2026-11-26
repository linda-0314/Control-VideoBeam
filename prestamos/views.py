"""Pantallas del bibliotecario: disponibilidad, préstamo y devolución.

Las vistas no deciden nada por su cuenta: leen los préstamos de la base, llaman
las reglas de registro.py y, si una regla lanza un ErrorDePrestamo, muestran su
mensaje con su estado_http (400, 404 o 409). Todas exigen sesión (ADR-002).
"""

from datetime import timedelta

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError, transaction
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_GET, require_POST

from prestamos import registro
from prestamos.models import Prestamo, Videobeam
from prestamos.reglas import ErrorDePrestamo, VideobeamYaPrestado

CAMPOS_PRESTAMO = ("codigo", "quien_lleva", "identificacion", "celular", "clase", "profesor")


@login_required
@require_GET
def inicio(request: HttpRequest) -> HttpResponse:
    """HU-01, HU-06, HU-07 y HU-10: disponibilidad, pendientes, HDMI y préstamos de hoy."""
    return _pagina_inicio(request)


@login_required
@require_POST
def crear_prestamo(request: HttpRequest) -> HttpResponse:
    """HU-02, HU-08 y HU-09: registra un préstamo con su contacto o muestra por qué no."""
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
            identificacion, celular = registro.validar_contacto(
                datos["identificacion"], datos["celular"]
            )
            Prestamo.objects.create(
                videobeam=Videobeam.objects.get(codigo=nuevo.codigo),
                quien_lleva=nuevo.quien_lleva,
                clase=nuevo.clase,
                profesor=nuevo.profesor,
                fecha_hora_salida=nuevo.fecha_hora_salida,
                con_hdmi=request.POST.get("con_hdmi") == "on",
                identificacion=identificacion,
                celular=celular,
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
    """HU-04, HU-05 y HU-07: cierra el préstamo con la hora, quién lo trae y el HDMI."""
    codigo = request.POST.get("codigo", "")
    quien_devuelve = request.POST.get("quien_devuelve", "")
    try:
        with transaction.atomic():
            devuelto = registro.registrar_devolucion_por(
                codigo, _prestamos_abiertos(), quien_devuelve, timezone.now()
            )
            devuelto = registro.registrar_hdmi(
                devuelto, request.POST.get("hdmi_devuelto") == "on"
            )
            Prestamo.objects.filter(
                videobeam__codigo=devuelto.codigo, fecha_hora_devolucion__isnull=True
            ).update(
                fecha_hora_devolucion=devuelto.fecha_hora_devolucion,
                quien_devuelve=devuelto.quien_devuelve,
                hdmi_devuelto=devuelto.hdmi_devuelto,
                observacion=devuelto.observacion,
            )
    except ErrorDePrestamo as error:
        return _pagina_inicio(request, error)
    mensaje = f"Devolución registrada: {devuelto.codigo}"
    if devuelto.observacion:
        mensaje += f". {devuelto.observacion}: lo llevó {devuelto.quien_lleva}"
    messages.success(request, mensaje)
    return redirect("inicio")


@login_required
@require_POST
def recuperar_hdmi(request: HttpRequest, pk: int) -> HttpResponse:
    """HU-07: el HDMI que faltaba ya volvió; sale de «HDMI por recuperar»."""
    guardado = get_object_or_404(Prestamo.objects.select_related("videobeam"), pk=pk)
    try:
        recuperado = registro.recuperar_hdmi(guardado.a_registro(), timezone.localtime())
    except ErrorDePrestamo as error:
        return _pagina_inicio(request, error)
    Prestamo.objects.filter(pk=pk).update(
        hdmi_devuelto=recuperado.hdmi_devuelto, observacion=recuperado.observacion
    )
    messages.success(request, f"HDMI recuperado: {recuperado.codigo} de {recuperado.quien_lleva}")
    return redirect("inicio")


def _abiertos_por_codigo() -> dict[str, Prestamo]:
    """Los préstamos sin devolución guardados, por código de videobeam."""
    abiertos = Prestamo.objects.filter(fecha_hora_devolucion__isnull=True)
    return {p.videobeam.codigo: p for p in abiertos.select_related("videobeam")}


def _prestamos_abiertos() -> list[registro.Prestamo]:
    """Los préstamos sin devolución, en el formato de las reglas."""
    return [p.a_registro() for p in _abiertos_por_codigo().values()]


def _pagina_inicio(
    request: HttpRequest, error: ErrorDePrestamo | None = None, datos: dict | None = None
) -> HttpResponse:
    """Arma la página de inicio; con un error, responde con su estado_http."""
    abiertos = _abiertos_por_codigo()
    guardados = Prestamo.objects.select_related("videobeam")
    hace_un_dia = timezone.now() - timedelta(days=1)
    videobeams = [(v.codigo, abiertos.get(v.codigo)) for v in Videobeam.objects.all()]
    contexto = {
        "mensaje_disponibilidad": registro.mensaje_disponibilidad(
            p.a_registro() for p in abiertos.values()
        ),
        "videobeams": videobeams,
        "disponibles": [codigo for codigo, prestamo in videobeams if prestamo is None],
        "prestados": [codigo for codigo, prestamo in videobeams if prestamo is not None],
        "pendientes": registro.prestamos_pendientes(
            (p.a_registro() for p in abiertos.values()), timezone.localtime()
        ),
        "hdmi_por_recuperar": registro.hdmi_por_recuperar(
            p.a_registro() for p in guardados.filter(observacion=registro.DEVUELTO_SIN_HDMI)
        ),
        "prestamos_de_hoy": registro.prestamos_del_dia(
            (p.a_registro() for p in guardados.filter(fecha_hora_salida__gte=hace_un_dia)),
            timezone.localtime(),
        ),
        "error": error,
        "datos": datos or {},
    }
    estado = error.estado_http if error else 200
    return render(request, "prestamos/inicio.html", contexto, status=estado)
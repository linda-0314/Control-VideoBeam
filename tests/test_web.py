"""Pruebas de la aplicación web de Django: HU-01, HU-02, HU-04 y HU-08 con inicio de sesión."""

import time
from datetime import timedelta

import pytest
from django.db import IntegrityError, transaction
from django.utils import timezone

from prestamos.models import Prestamo, Videobeam

DATOS_LAURA = {
    "codigo": "VB-02",
    "quien_lleva": "Laura Gómez",
    "clase": "Bases de datos",
    "profesor": "Andrés Ruiz",
}


def prestar(codigo: str) -> Prestamo:
    """Crea en la base un préstamo abierto, como si ya se hubiera registrado."""
    return Prestamo.objects.create(
        videobeam=Videobeam.objects.get(codigo=codigo),
        quien_lleva="Mateo Díaz",
        clase="Redes",
        profesor="Andrés Ruiz",
        fecha_hora_salida=timezone.now(),
    )


def texto(respuesta) -> str:
    return respuesta.content.decode()


# ----- Datos iniciales -----


def test_la_migracion_crea_los_cinco_videobeams(db):
    codigos = list(Videobeam.objects.order_by("codigo").values_list("codigo", flat=True))
    assert codigos == ["VB-01", "VB-02", "VB-03", "VB-04", "VB-05"]


# ----- Control de acceso (ADR-002: solo el bibliotecario) -----


def test_sin_sesion_la_pagina_de_inicio_manda_a_iniciar_sesion(anonimo):
    respuesta = anonimo.get("/")
    assert respuesta.status_code == 302
    assert respuesta.url.startswith("/cuentas/login/")


def test_abuso_sin_sesion_no_se_puede_registrar_un_prestamo(anonimo):
    respuesta = anonimo.post("/prestamos/", DATOS_LAURA)
    assert respuesta.status_code == 302
    assert respuesta.url.startswith("/cuentas/login/")
    assert Prestamo.objects.count() == 0


def test_abuso_sin_sesion_no_se_puede_registrar_una_devolucion(anonimo):
    prestamo = prestar("VB-01")
    respuesta = anonimo.post("/devoluciones/", {"codigo": "VB-01"})
    assert respuesta.status_code == 302
    prestamo.refresh_from_db()
    assert prestamo.fecha_hora_devolucion is None


def test_registrar_un_prestamo_solo_acepta_post(cliente):
    assert cliente.get("/prestamos/").status_code == 405


def test_la_contrasena_se_guarda_con_scrypt(bibliotecario):
    assert bibliotecario.password.startswith("scrypt$")


# ----- HU-01: consultar disponibilidad -----


def test_sin_prestamos_muestra_cinco_de_cinco(cliente):
    respuesta = cliente.get("/")
    assert respuesta.status_code == 200
    assert "5 de 5 videobeams disponibles" in texto(respuesta)


def test_con_tres_prestados_muestra_dos_de_cinco(cliente):
    # HU-01, escenario 1.
    for codigo in ("VB-01", "VB-02", "VB-03"):
        prestar(codigo)
    assert "2 de 5 videobeams disponibles" in texto(cliente.get("/"))


def test_con_los_cinco_prestados_muestra_que_no_hay(cliente):
    # HU-01, escenario 2.
    for codigo in ("VB-01", "VB-02", "VB-03", "VB-04", "VB-05"):
        prestar(codigo)
    assert "No hay videobeams disponibles en este momento" in texto(cliente.get("/"))


def test_rnf01_la_disponibilidad_responde_en_menos_de_tres_segundos(cliente):
    inicio = time.perf_counter()
    cliente.get("/")
    assert time.perf_counter() - inicio < 3


# ----- HU-02: registrar préstamo -----


def test_prestamo_completo_se_guarda_y_la_disponibilidad_baja_a_cuatro(cliente):
    # HU-02, escenario 1.
    respuesta = cliente.post("/prestamos/", DATOS_LAURA, follow=True)
    assert respuesta.status_code == 200
    prestamo = Prestamo.objects.get()
    assert prestamo.videobeam.codigo == "VB-02"
    assert (prestamo.quien_lleva, prestamo.clase, prestamo.profesor) == (
        "Laura Gómez",
        "Bases de datos",
        "Andrés Ruiz",
    )
    assert prestamo.fecha_hora_devolucion is None
    assert "4 de 5 videobeams disponibles" in texto(respuesta)
    assert "Préstamo registrado: VB-02" in texto(respuesta)


def test_sin_profesor_no_guarda_y_muestra_el_mensaje(cliente):
    # HU-02, escenario 2.
    respuesta = cliente.post("/prestamos/", {**DATOS_LAURA, "profesor": ""})
    assert respuesta.status_code == 400
    assert "Falta el nombre del profesor" in texto(respuesta)
    assert Prestamo.objects.count() == 0
    # Lo que ya escribió el bibliotecario no se pierde.
    assert 'value="Laura Gómez"' in texto(respuesta)


# ----- HU-08: no prestar uno ya prestado -----


def test_prestar_uno_ya_prestado_responde_409_y_no_guarda(cliente):
    # HU-08, escenario 2.
    prestar("VB-01")
    respuesta = cliente.post("/prestamos/", {**DATOS_LAURA, "codigo": "VB-01"})
    assert respuesta.status_code == 409
    assert "El VB-01 ya está prestado" in texto(respuesta)
    assert Prestamo.objects.count() == 1


def test_prestar_un_codigo_que_no_existe_responde_404(cliente):
    respuesta = cliente.post("/prestamos/", {**DATOS_LAURA, "codigo": "VB-09"})
    assert respuesta.status_code == 404
    assert "El VB-09 no existe" in texto(respuesta)


@pytest.mark.parametrize("codigo", ["VB-01' OR '1'='1", "VB-01; DROP TABLE prestamos_prestamo"])
def test_abuso_codigo_manipulado_no_guarda_nada(cliente, codigo):
    respuesta = cliente.post("/prestamos/", {**DATOS_LAURA, "codigo": codigo})
    assert respuesta.status_code == 404
    assert Prestamo.objects.count() == 0
    assert Videobeam.objects.count() == 5


def test_la_base_no_permite_dos_prestamos_abiertos_del_mismo_videobeam(db):
    # Segunda barrera de HU-08, por si dos préstamos llegan al mismo tiempo.
    prestar("VB-03")
    with pytest.raises(IntegrityError), transaction.atomic():
        prestar("VB-03")


def test_abuso_un_nombre_con_html_se_muestra_como_texto(cliente):
    cliente.post("/prestamos/", {**DATOS_LAURA, "quien_lleva": "<script>alert(1)</script>"})
    pagina = texto(cliente.get("/"))
    assert "<script>alert(1)</script>" not in pagina
    assert "&lt;script&gt;alert(1)&lt;/script&gt;" in pagina


# ----- HU-04: registrar devolución -----


def test_devolucion_guarda_la_hora_y_deja_el_videobeam_disponible(cliente):
    # HU-04, escenario 1.
    prestamo = prestar("VB-02")
    respuesta = cliente.post("/devoluciones/", {"codigo": "VB-02", "quien_devuelve": "Mateo Díaz"}, follow=True
    )
    prestamo.refresh_from_db()
    assert prestamo.fecha_hora_devolucion is not None
    assert prestamo.fecha_hora_devolucion >= prestamo.fecha_hora_salida
    assert "5 de 5 videobeams disponibles" in texto(respuesta)
    assert "Devolución registrada: VB-02" in texto(respuesta)


def test_devolver_uno_que_no_estaba_prestado_responde_409(cliente):
    # HU-04, escenario 2.
    respuesta = cliente.post("/devoluciones/", {"codigo": "VB-04"})
    assert respuesta.status_code == 409
    assert "El VB-04 no está prestado" in texto(respuesta)
    
    
    # ----- HU-06: pendientes de días anteriores -----


def test_un_prestamo_de_ayer_aparece_en_pendientes(cliente):
    prestamo = prestar("VB-03")
    prestamo.fecha_hora_salida = timezone.now() - timedelta(days=1)
    prestamo.save()
    respuesta = cliente.get("/")
    assert respuesta.status_code == 200
    assert "No devuelto en su jornada" in texto(respuesta)


def test_un_prestamo_de_hoy_no_aparece_en_pendientes(cliente):
    prestar("VB-03")
    respuesta = cliente.get("/")
    assert "No devuelto en su jornada" not in texto(respuesta)
    
    

# ----- HU-05: devolución por otra persona -----


def test_devuelve_otra_persona_y_se_guardan_los_dos_nombres(cliente):
    # HU-05, escenario 1: Mateo Díaz sacó el VB-01 y lo trae Sara López.
    prestamo = prestar("VB-01")
    respuesta = cliente.post(
        "/devoluciones/", {"codigo": "VB-01", "quien_devuelve": "Sara López"}, follow=True
    )
    prestamo.refresh_from_db()
    assert prestamo.quien_lleva == "Mateo Díaz"
    assert prestamo.quien_devuelve == "Sara López"
    assert prestamo.fecha_hora_devolucion is not None
    assert "5 de 5 videobeams disponibles" in texto(respuesta)


def test_devolucion_sin_nombre_no_guarda_y_muestra_el_mensaje(cliente):
    # HU-05, escenario 2.
    prestamo = prestar("VB-01")
    respuesta = cliente.post("/devoluciones/", {"codigo": "VB-01", "quien_devuelve": ""})
    prestamo.refresh_from_db()
    assert respuesta.status_code == 400
    assert "Escribe el nombre de quien devuelve el videobeam" in texto(respuesta)
    assert prestamo.fecha_hora_devolucion is None

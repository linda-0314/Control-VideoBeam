"""Crea los 5 videobeams de la biblioteca (requisitos de la semana 3)."""

from django.db import migrations

CODIGOS = ["VB-01", "VB-02", "VB-03", "VB-04", "VB-05"]


def crear_videobeams(apps, schema_editor):
    Videobeam = apps.get_model("prestamos", "Videobeam")
    for codigo in CODIGOS:
        Videobeam.objects.get_or_create(codigo=codigo)


def borrar_videobeams(apps, schema_editor):
    Videobeam = apps.get_model("prestamos", "Videobeam")
    Videobeam.objects.filter(codigo__in=CODIGOS, prestamos__isnull=True).delete()


class Migration(migrations.Migration):
    dependencies = [
        ("prestamos", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(crear_videobeams, borrar_videobeams),
    ]

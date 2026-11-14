# Control VideoBeam FET

## 1. Qué es

Aplicación para que el bibliotecario de la Fundación Escuela Tecnológica de Neiva (FET) registre el préstamo y la devolución de los 5 videobeams de la biblioteca (VB-01 a VB-05) y sepa al instante cuántos hay disponibles, en lugar de usar la planilla en papel.

Diseño (semana 4): aplicación web monolítica en Python con Django y SQLite, instalada en el computador de la biblioteca (ADR-001). Solo la usa el bibliotecario (ADR-002).

**Estado actual (semana 6):** está hecha y probada la regla de la HU-08 «No prestar uno ya prestado», en `prestamos/reglas.py`. Las vistas de Django, la base de datos y el inicio de sesión todavía no existen.

## 2. Requisitos

- Python 3.10 o más reciente (probado con Python 3.13).
- Git.
- Dependencias, con versión fijada en `requirements.txt`:
  - `pytest==9.2.0` para las pruebas.
  - `ruff==0.16.9` para el linter.

La regla de `prestamos/` no usa paquetes externos.

## 3. Instalación

En Windows (PowerShell):

```powershell
git clone https://github.com/linda-0314/Control-VideoBeam.git
cd Control-VideoBeam
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

En Linux o macOS, cambia la activación por `source .venv/bin/activate`.

Si PowerShell no deja ejecutar `Activate.ps1`, ejecuta una vez `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned`.

Cuando exista la aplicación de Django, se copiará `.env.example` como `.env` y se llenará `DJANGO_SECRET_KEY`. El archivo `.env` no se sube a Git.

## 4. Ejecución

Todavía no hay interfaz. Para usar la regla de préstamo desde la terminal:

```powershell
python -c "from prestamos.reglas import prestar_videobeam; print(prestar_videobeam('VB-04', {'VB-01'}))"
```

Resultado esperado: `frozenset({'VB-01', 'VB-04'})` (el orden puede variar).

Si el videobeam ya está prestado, la función lanza `VideobeamYaPrestado` con el mensaje «El VB-01 ya está prestado».

## 5. Pruebas

```powershell
pytest
```

Ejecuta las 17 pruebas de `tests/`: casos normales, límite, de error y de abuso (códigos manipulados en el formulario).

Linter con reglas de estilo, errores, errores probables y seguridad (configurado en `pyproject.toml`):

```powershell
ruff check .
```

Auditoría de dependencias:

```powershell
pip install pip-audit
pip-audit -r requirements.txt
```

### Contrato de la funcionalidad (HU-08)

```python
def prestar_videobeam(codigo: str, prestados: Set[str]) -> frozenset[str]
```

| Entrada | Salida |
|---|---|
| `prestar_videobeam("VB-04", frozenset({"VB-01"}))` | `frozenset({"VB-01", "VB-04"})` |
| `prestar_videobeam("VB-05", frozenset({"VB-01", "VB-02", "VB-03", "VB-04"}))` | los 5 prestados |
| `prestar_videobeam("VB-01", frozenset({"VB-01"}))` | `VideobeamYaPrestado`: «El VB-01 ya está prestado» (API: 409) |
| `prestar_videobeam("VB-09", frozenset())` | `VideobeamNoExiste`: «El VB-09 no existe» (API: 404) |

Supuestos: el código llega exacto desde la lista del formulario (`"vb-02"` se trata como inexistente) y `prestados` no se modifica.

## 6. Estructura

```
Control-VideoBeam/
├── prestamos/              # app de préstamos (ADR-001)
│   ├── __init__.py
│   └── reglas.py           # regla de HU-08 en Python puro y errores ErrorDePrestamo
├── tests/
│   └── test_reglas.py      # 17 pruebas con pytest
├── .env.example            # plantilla de variables de entorno (sin valores reales)
├── .gitignore              # ignora .env, cachés y db.sqlite3
├── bitacora_ia.md          # bitácora de uso de IA (semanas 5 y 6)
├── pyproject.toml          # configuración de ruff y pytest
├── requirements.txt        # dependencias con versión fijada
├── revision_seguridad.md   # informe de revisión de código y seguridad (semana 6)
└── README.md
```

## 7. Uso de IA

Usé Claude (claude.ai) como asistente durante todo el proyecto:

- Semana 5: para convertir la HU-08 en contrato y pruebas, con el ciclo rojo, verde y refactor.
- Semana 6: para la segunda revisión de código y seguridad, y como agente de código en la rama `agente/refactor-errores`. Revisé su diff antes de integrarlo.

Cada sugerencia la verifiqué contra el diseño, las pruebas y el linter. Rechacé las que contradecían el ADR-001 o eran falsos positivos. El detalle está en [bitacora_ia.md](bitacora_ia.md) y los hallazgos en [revision_seguridad.md](revision_seguridad.md).

## 8. Autor y licencia

- Autora: Linda Paola Carreño Meneses.
- Seminario en Inteligencia Artificial aplicada al ciclo de vida del software. Docente: Jorge Luis Trujillo. Fundación Escuela Tecnológica FET, 2026.
- Licencia: trabajo académico, todos los derechos reservados por la autora. No tiene licencia de código abierto por ahora.

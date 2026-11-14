# Control VideoBeam FET

## 1. Qué es

Aplicación para que el bibliotecario de la Fundación Escuela Tecnológica de Neiva (FET) registre el préstamo y la devolución de los 5 videobeams de la biblioteca (VB-01 a VB-05) y sepa al instante cuántos hay disponibles, en lugar de usar la planilla en papel.

Diseño (semana 4): aplicación web monolítica en Python con Django y SQLite, instalada en el computador de la biblioteca (ADR-001). Solo la usa el bibliotecario (ADR-002).

**Estado actual:** están hechas y probadas las reglas de las cuatro historias Must: HU-01 «Consultar disponibilidad», HU-02 «Registrar préstamo», HU-04 «Registrar devolución» y HU-08 «No prestar uno ya prestado», en `prestamos/`. Las vistas de Django, la base de datos y el inicio de sesión todavía no existen.

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

Todavía no hay interfaz. Para probar las reglas desde la terminal:

```powershell
python -c "from prestamos.reglas import prestar_videobeam; print(prestar_videobeam('VB-04', {'VB-01'}))"
```

Resultado esperado: `frozenset({'VB-01', 'VB-04'})` (el orden puede variar). Si el videobeam ya está prestado, la función lanza `VideobeamYaPrestado` con el mensaje «El VB-01 ya está prestado».

Un préstamo y la disponibilidad (HU-02 y HU-01):

```powershell
python -c "from datetime import datetime; from prestamos.registro import registrar_prestamo, mensaje_disponibilidad; p = registrar_prestamo('VB-02', [], 'Laura Gómez', 'Bases de datos', 'Andrés Ruiz', datetime(2026, 11, 14, 18, 40)); print(mensaje_disponibilidad([p]))"
```

Resultado esperado: `4 de 5 videobeams disponibles`.

## 5. Pruebas

```powershell
pytest
```

Ejecuta las 43 pruebas de `tests/`: casos normales, límite, de error y de abuso (códigos manipulados en el formulario) de HU-01, HU-02, HU-04 y HU-08.

Linter con reglas de estilo, errores, errores probables y seguridad (configurado en `pyproject.toml`):

```powershell
ruff check .
```

Auditoría de dependencias:

```powershell
pip install pip-audit
pip-audit -r requirements.txt
```

### Contratos de las funciones principales

| Función | Historia | Devuelve | Errores |
|---|---|---|---|
| `mensaje_disponibilidad(prestamos)` | HU-01 | «2 de 5 videobeams disponibles» o «No hay videobeams disponibles en este momento» | Ninguno |
| `registrar_prestamo(codigo, prestamos, quien_lleva, clase, profesor, fecha_hora_salida)` | HU-02 | `Prestamo` nuevo sin devolución | `DatoInvalido` (400): «Escribe el nombre de quien lleva el videobeam», «Falta la clase», «Falta el nombre del profesor»; `VideobeamNoExiste` (404); `VideobeamYaPrestado` (409) |
| `registrar_devolucion(codigo, prestamos, fecha_hora)` | HU-04 | Copia del préstamo abierto con `fecha_hora_devolucion` | `VideobeamNoExiste` (404); `VideobeamNoPrestado` (409): «El VB-04 no está prestado»; `DatoInvalido` (400) si la hora es anterior a la salida |
| `prestar_videobeam(codigo, prestados)` | HU-08 | `frozenset` con los prestados más `codigo` | `VideobeamNoExiste` (404); `VideobeamYaPrestado` (409) |

Ninguna función modifica la lista que recibe ni toma la hora del reloj: la hora llega como parámetro, para poder probarla. El detalle de cada función está en su docstring.

#### HU-08 en detalle

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
│   ├── reglas.py           # regla de HU-08 y errores ErrorDePrestamo (400, 404, 409)
│   └── registro.py         # Prestamo, HU-01 disponibilidad, HU-02 préstamo, HU-04 devolución
├── tests/
│   ├── conftest.py         # datos de prueba compartidos
│   ├── test_reglas.py      # HU-08 (17 pruebas)
│   ├── test_disponibilidad.py   # HU-01 (6 pruebas)
│   ├── test_registro_prestamo.py # HU-02 (11 pruebas)
│   └── test_devolucion.py  # HU-04 (9 pruebas)
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
- Después de la semana 6: para escribir con pruebas primero las reglas de HU-01, HU-02 y HU-04 en la rama `hu-must`.

Cada sugerencia la verifiqué contra el diseño, las pruebas y el linter. Rechacé las que contradecían el ADR-001 o eran falsos positivos. El detalle está en [bitacora_ia.md](bitacora_ia.md) y los hallazgos en [revision_seguridad.md](revision_seguridad.md).

## 8. Autor y licencia

- Autora: Linda Paola Carreño Meneses.
- Seminario en Inteligencia Artificial aplicada al ciclo de vida del software. Docente: Jorge Luis Trujillo. Fundación Escuela Tecnológica FET, 2026.
- Licencia: trabajo académico, todos los derechos reservados por la autora. No tiene licencia de código abierto por ahora.

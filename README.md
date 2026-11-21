# Control VideoBeam FET

## 1. Qué es

Aplicación web para que el bibliotecario de la Fundación Escuela Tecnológica de Neiva (FET) registre el préstamo y la devolución de los 5 videobeams de la biblioteca (VB-01 a VB-05) y sepa al instante cuántos hay disponibles, en lugar de usar la planilla en papel.

Diseño (semana 4): aplicación web monolítica en Python con Django y SQLite, instalada en el computador de la biblioteca (ADR-001). Solo la usa el bibliotecario (ADR-002).

**Estado actual:**

| Parte | Estado |
|---|---|
| HU-01 Consultar disponibilidad (Must) | ✅ Página de inicio |
| HU-02 Registrar préstamo (Must) | ✅ Formulario de préstamo |
| HU-04 Registrar devolución (Must) | ✅ Formulario de devolución |
| HU-08 No prestar uno ya prestado (Must) | ✅ Regla y restricción en la base de datos |
| Inicio de sesión del bibliotecario con scrypt | ✅ |
| HU-03, HU-05 y HU-06 (Should), HU-07 (Could) | Pendientes |
| API en JSON de la sección 6 del diseño | Pendiente: por ahora las pantallas usan formularios HTML |

## 2. Requisitos

- Python 3.10 o más reciente (probado con Python 3.13).
- Git.
- Dependencias, con versión fijada en `requirements.txt`:
  - `Django==5.2.18` (versión LTS con los últimos parches de seguridad). Instala también `asgiref`, `sqlparse` y `tzdata`.
  - `pytest==9.2.0` para las pruebas.
  - `ruff==0.16.9` para el linter.

## 3. Instalación

En Windows (PowerShell):

```powershell
git clone https://github.com/linda-0314/Control-VideoBeam.git
cd Control-VideoBeam
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
copy .env.example .env
```

Abre `.env` y escribe una clave secreta en `DJANGO_SECRET_KEY`. Para generar una:

```powershell
python -c "import secrets; print(secrets.token_urlsafe(50))"
```

Después crea la base de datos (con los 5 videobeams) y el usuario del bibliotecario:

```powershell
python manage.py migrate
python manage.py createsuperuser
```

`createsuperuser` pide un nombre de usuario y una contraseña; el correo se puede dejar vacío. La contraseña se guarda con scrypt.

En Linux o macOS, cambia la activación por `source .venv/bin/activate` y `copy` por `cp`.

Si PowerShell no deja ejecutar `Activate.ps1`, ejecuta una vez `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned`.

## 4. Ejecución

```powershell
python manage.py runserver
```

Abre http://127.0.0.1:8000/ en el navegador del computador de la biblioteca e inicia sesión con el usuario que creaste. En la página de inicio verás:

- Cuántos videobeams hay disponibles («4 de 5 videobeams disponibles») y el estado de cada uno, con quién lo lleva, la clase, el profesor y la hora de salida.
- El formulario **Registrar préstamo**: solo deja escoger videobeams disponibles.
- El formulario **Registrar devolución**: solo deja escoger videobeams prestados y guarda la fecha y la hora del momento.

Si falta un dato o el videobeam ya está prestado, la página muestra el mensaje en rojo («Falta el nombre del profesor», «El VB-01 ya está prestado») y no guarda nada.

La planilla completa, con los préstamos ya devueltos, se consulta en http://127.0.0.1:8000/admin/.

**Copia de seguridad:** todos los préstamos están en el archivo `db.sqlite3`. Para respaldarlos, cierra el servidor y copia ese archivo.

## 5. Pruebas

```powershell
pytest
```

Ejecuta las 132 pruebas de `tests/` (con `pytest -v` se ve cada una):

- Reglas de HU-01, HU-02, HU-04 y HU-08 de las semanas 5 y 6 (43 pruebas).
- Aplicación web (20 pruebas: páginas, inicio de sesión, control de acceso, abuso con códigos manipulados y HTML, contraseña con scrypt y RNF-01).
- Suite de la semana 7 (69 pruebas en `tests/test_s7_*.py`), diseñada con particiones de equivalencia, valores límite y una tabla de decisión, y con datos sintéticos. El diseño de los casos, la revisión de las pruebas generadas por la IA y los errores introducidos a propósito están en [registro_pruebas.md](registro_pruebas.md).

Las pruebas web crean una base de datos en memoria, así que no tocan `db.sqlite3`.

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
def prestar_videobeam(codigo: str, prestados: AbstractSet[str]) -> frozenset[str]
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
├── config/                 # proyecto Django: settings.py (lee .env), urls.py, wsgi.py
├── prestamos/              # app de préstamos (ADR-001)
│   ├── reglas.py           # regla de HU-08 y errores ErrorDePrestamo (400, 404, 409)
│   ├── registro.py         # reglas de HU-01, HU-02 y HU-04 en Python puro
│   ├── models.py           # Videobeam y Prestamo (diseño, sección 5)
│   ├── views.py            # inicio, crear_prestamo y registrar_devolucion
│   ├── urls.py             # rutas /, /prestamos/ y /devoluciones/
│   ├── admin.py            # planilla completa en /admin/
│   ├── migrations/         # tablas y los 5 videobeams iniciales
│   └── templates/          # páginas HTML: inicio y inicio de sesión
├── tests/
│   ├── conftest.py         # datos de prueba y base de datos de prueba de Django
│   ├── test_reglas.py      # HU-08 (17 pruebas)
│   ├── test_disponibilidad.py    # HU-01 (6 pruebas)
│   ├── test_registro_prestamo.py # HU-02 (11 pruebas)
│   ├── test_devolucion.py  # HU-04 (9 pruebas)
│   ├── test_web.py         # aplicación web (20 pruebas)
│   ├── test_s7_*.py        # semana 7: tablas de casos de 4 funciones (69 pruebas)
│   └── datos_sinteticos.json    # datos de prueba inventados (fixture datos_sinteticos)
├── manage.py               # comandos de Django
├── .env.example            # plantilla de variables de entorno (sin valores reales)
├── .gitignore              # ignora .env, cachés y db.sqlite3
├── bitacora_ia.md          # bitácora de uso de IA
├── pyproject.toml          # configuración de ruff y pytest
├── registro_pruebas.md     # reglas, tablas de casos y revisión de las pruebas (semana 7)
├── requirements.txt        # dependencias con versión fijada
├── revision_seguridad.md   # informe de revisión de código y seguridad
└── README.md
```

Las reglas están separadas de Django a propósito: `reglas.py` y `registro.py` deciden si un préstamo o una devolución es válido, y las vistas solo leen la base, llaman esas reglas y guardan el resultado.

## 7. Uso de IA

Usé Claude (claude.ai) como asistente durante todo el proyecto:

- Semana 5: para convertir la HU-08 en contrato y pruebas, con el ciclo rojo, verde y refactor.
- Semana 6: para la segunda revisión de código y seguridad, y como agente de código en la rama `agente/refactor-errores`. Revisé su diff antes de integrarlo.
- Después de la semana 6: para escribir con pruebas primero las reglas de HU-01, HU-02 y HU-04, y después la aplicación de Django (modelos, vistas, pantallas e inicio de sesión) de las cuatro historias Must.
- Semana 7: para proponer los casos de prueba, escribir la suite a partir de mis tablas y generar los datos sintéticos. Revisé cada prueba con las tres preguntas; descarté 8, corregí 8 y una de ellas encontró un defecto real que corregí en el código.

Cada sugerencia la verifiqué contra el diseño, las pruebas y el linter. Rechacé las que contradecían el ADR-001 o eran falsos positivos. El detalle está en [bitacora_ia.md](bitacora_ia.md) y los hallazgos en [revision_seguridad.md](revision_seguridad.md).

## 8. Autor y licencia

- Autora: Linda Paola Carreño Meneses.
- Seminario en Inteligencia Artificial aplicada al ciclo de vida del software. Docente: Jorge Luis Trujillo. Fundación Escuela Tecnológica FET, 2026.
- Licencia: trabajo académico, todos los derechos reservados por la autora. No tiene licencia de código abierto por ahora.

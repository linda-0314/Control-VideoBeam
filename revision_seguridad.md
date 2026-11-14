# Informe de revisión de código y seguridad

Proyecto: Control VideoBeam FET
Estudiante: Linda Paola Carreño Meneses
Fecha: 2026-11-14
Commit revisado: 4051843 (último commit de la semana 5, antes de las correcciones)

## 1. Herramientas y criterios

- **Linter:** ruff 0.16.9 con las reglas E, F, B y S (estilo, errores, errores probables y seguridad). La configuración está en `pyproject.toml`. Primera ejecución: 7 avisos, todos S101 (`assert` en `tests/`).
- **Auditoría de dependencias:** pip-audit sobre `requirements.txt`. Resultado: [pega aquí lo que muestre `pip-audit -r requirements.txt`].
- **Lista de revisión:** la de la semana 6, con tres partes: corrección y pruebas, diseño y legibilidad, y seguridad. Busqué claves en todo el historial con `git log -p --all` y comprobé el `.gitignore` con `git check-ignore -v`.
- **Revisión con IA:** Claude (claude.ai) con el prompt de revisión de la semana (sección 3).

### Puntos de seguridad revisados

| Punto | ¿Aplica? | Resultado |
|---|---|---|
| Inyección (consultas con parámetros) | Todavía no: no hay base de datos ni consultas. La regla compara el código contra un conjunto fijo. | Sin hallazgos. Agregué pruebas de abuso con texto de inyección SQL, un script, un texto vacío y `None` (commit ad44f0b). Cuando haya vistas de Django, se usará solo el ORM, sin `raw()` ni texto pegado. |
| Secretos (código, historial, .gitignore, .env.example) | Sí | No hay claves en el código ni en el historial. Ver H-01: el `.gitignore` ignoraba `.env.example`. |
| Contraseñas (scrypt, bcrypt o argon2 con sal) | Todavía no: el inicio de sesión del bibliotecario (ADR-002) no está implementado. | Queda en pendientes: Django usa PBKDF2 por defecto, así que se pondrá `ScryptPasswordHasher` de primero en `PASSWORD_HASHERS`. |
| Control de acceso (rol verificado y prueba de abuso) | Todavía no: hay un solo rol y no hay vistas. | Queda en pendientes: `login_required` en todas las vistas y una prueba de abuso de una petición sin sesión que debe dar 401. |
| Dependencias (existen, necesarias, versión fijada, pip-audit) | Sí | Ver H-02: `pytest>=8` no tenía versión fija y faltaba ruff. Las dos existen en PyPI y se necesitan para pruebas y linter. |

## 2. Tabla de hallazgos

| Id | Archivo y línea | Problema | Categoría (OWASP o tipo) | Severidad | Corrección | Commit |
|---|---|---|---|---|---|---|
| H-01 | .gitignore:3 | El patrón `.env.*` también ignoraba `.env.example`, y no existía la plantilla de variables. | A05 Configuración insegura (secretos) | Media | Excepción `!.env.example` y plantilla con `DJANGO_SECRET_KEY` vacía. `.env` sigue ignorado. | a6c8f4a |
| H-02 | requirements.txt:1 | `pytest>=8` sin versión fija; ruff no estaba en la lista. | A06 Componentes vulnerables y desactualizados | Media | `pytest==9.2.0` y `ruff==0.16.9` | 838be6a |
| H-03 | prestamos/reglas.py:30 | Si recibía un `set` común, devolvía un `set` y no el `frozenset` del contrato, así que otro código podía modificar el resultado. | Posible error (A04 Diseño inseguro) | Media | `return frozenset(prestados) \| {codigo}` y una prueba nueva | 91fc2b9 |
| H-04 | prestamos/reglas.py:12-29 | Dos excepciones sin una base común y el texto «El {codigo} …» repetido. La vista de Django tendría que atrapar dos errores. | Mantenibilidad (duplicación) | Baja | Clase base `ErrorDePrestamo` con `codigo`, `plantilla` y `estado_http` (404 y 409), y docstrings con Args, Returns y Raises. Lo hizo el agente en una rama propia. | a83a9a3 |
| H-05 | README.md | No tenía las ocho secciones (instalación, ejecución, autor y licencia, etc.). | Documentación | Baja | README con las ocho secciones, probado en un clon limpio | 6f3ee54 |

**Severidad:** alta (permite acceder o cambiar datos sin permiso, o expone secretos), media (error probable o riesgo con condiciones), baja (estilo o mantenibilidad).

### Avisos del linter no corregidos

| Regla | Archivo y línea | Por qué se mantiene |
|---|---|---|
| S101 | tests/test_reglas.py (todas las pruebas) | `assert` es la forma normal de comprobar en pytest. Solo se permite en `tests/` con `per-file-ignores`; en `prestamos/` la regla sigue activa. |

Después de las correcciones, `ruff check .` dice «All checks passed!» y las 17 pruebas pasan (11 de la semana 5 sin cambios, más 6 nuevas).

## 3. Revisión con IA

**Prompt usado:** «Actúa como revisor de código Python con experiencia en seguridad. Contexto: módulo `prestamos/reglas.py` del proyecto Control VideoBeam FET, que será una app Django con SQLite usada solo por el bibliotecario (ADR-001 y ADR-002); te pego el código, las pruebas, el `requirements.txt` y el `.gitignore`. Tarea: revisa corrección, legibilidad y seguridad: inyección, secretos, contraseñas, control de acceso y dependencias. Formato: tabla línea | problema | severidad (alta, media, baja) | corrección sugerida. Restricciones: no reescribas todo el código; separa los problemas seguros de las sospechas que habría que verificar.» Ver la entrada 7 de la bitácora.

| Hallazgo de la IA | ¿Real o falso positivo? | Cómo lo verifiqué |
|---|---|---|
| Seguro: `requirements.txt:1` sin versión fija (media) | Real (H-02) | Abrí el archivo: decía `pytest>=8`. |
| Seguro: `reglas.py:30` devuelve `set` si recibe `set` (media) | Real (H-03) | Lo ejecuté con `{"VB-01"}` y devolvió `set`. La prueba nueva falló antes de la corrección. |
| Seguro: excepciones duplicadas, sin base común (baja) | Real (H-04) | Comparé las líneas 12-29: el mismo texto aparece dos veces. |
| Sospecha: el código del formulario podría causar inyección SQL (alta) | Falso positivo | No hay SQL. El código solo se compara con un conjunto fijo. Las pruebas de abuso con `' OR '1'='1` dan `VideobeamNoExiste`. |
| Sospecha: el mensaje repite el código recibido; posible XSS si se muestra en HTML (media) | Falso positivo por ahora | No hay HTML todavía. Las plantillas de Django escapan el texto y la API responde JSON. Queda en pendientes no usar `\|safe`. |
| Sospecha: `assert` en las pruebas (S101) se desactiva con `python -O` (baja) | Falso positivo | Las pruebas se ejecutan con pytest, no con `-O`. Lo justifiqué en la tabla del linter. |

**Lo que la IA no encontró:** que el `.gitignore` ignoraba `.env.example` (H-01). La IA revisó que `.env` estuviera ignorado y lo dio por bueno. Yo lo encontré al aplicar la lista de revisión: creé el archivo y ejecuté `git check-ignore -v .env.example`, que mostró que lo ignoraba la regla de la línea 3.

## 4. Pendientes

| Pendiente | Por qué no se corrigió todavía | Plan |
|---|---|---|
| Contraseñas con scrypt o argon2 | El inicio de sesión del bibliotecario (ADR-002) no existe todavía. | Al crear el proyecto Django, poner `ScryptPasswordHasher` de primero en `PASSWORD_HASHERS` y probar que el hash guardado empiece con `scrypt$`. |
| Control de acceso y prueba de abuso | Todavía no hay vistas. | `login_required` en todas las vistas y una prueba de abuso: `POST /prestamos` sin sesión debe dar 401 y no guardar nada. |
| No mostrar mensajes con `\|safe` | Todavía no hay plantillas. | Dejarlo en la lista de revisión de la semana en que se hagan las plantillas. |
| Fijar la versión de Django | Django todavía no se usa. | Agregarlo a `requirements.txt` con versión exacta y pasar pip-audit otra vez. |

**Claves expuestas:** Ninguna. Revisé todo el historial con `git log -p --all` y no hay claves, contraseñas ni archivos `.env`.

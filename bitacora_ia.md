# Bitácora de uso de IA

Proyecto: Control VideoBeam FET · Funcionalidad: HU-08, no prestar un videobeam ya prestado
Estudiante: Linda Paola Carreño Meneses
Asistente: Claude (claude.ai), con acceso a un entorno para crear archivos, ejecutar pytest y hacer commits.

## Entradas

### Entrada 1

- **Fecha:** 7 de noviembre de 2026
- **Sugerencia o prompt:** Le pasé al asistente el enunciado de la tarea de la semana 5 y mi documento de diseño de la semana 4. Me propuso trabajar la HU-08 «No prestar uno ya prestado» como primera funcionalidad.
- **Decisión:** Aceptada.
- **Razón:** Es Must, cabe en una sola función y tiene un escenario de error con un mensaje exacto («El VB-01 ya está prestado») que se puede probar. Además protege lo más importante del sistema: que la disponibilidad sea real (N-01).
- **Cómo la verifiqué:** Revisé en el documento de requisitos que la HU-08 es Must, y en el diseño que su error corresponde al 409 de `POST /prestamos`.

### Entrada 2

- **Fecha:** 7 de noviembre de 2026
- **Sugerencia o prompt:** Le pregunté en qué se iba a desarrollar el proyecto. El asistente respondió que era una página en HTML, CSS y JavaScript que guarda los datos en el navegador (localStorage), sin servidor.
- **Decisión:** Rechazada.
- **Razón:** Esa respuesta venía de la sección 9 del documento de la semana 3, que ya no es la decisión vigente. En el diseño de la semana 4 (ADR-001) elegí una aplicación web monolítica en Python con Django y SQLite. Si la hubiera aceptado, habría programado en otro lenguaje y la tarea no respetaría mi diseño.
- **Cómo la verifiqué:** Le pasé el documento de diseño de la semana 4 y comparé con el ADR-001. El asistente reconoció el error y la funcionalidad quedó en Python con pytest.

### Entrada 3

- **Fecha:** 7 de noviembre de 2026
- **Sugerencia o prompt:** Django no estaba instalado en el entorno del asistente y no se podía instalar. El asistente propuso escribir la regla de HU-08 en Python puro, en `prestamos/reglas.py`, para que más adelante la vista de Django la llame antes de guardar.
- **Decisión:** Ajustada.
- **Razón:** La acepté, pero la dejé dentro de la carpeta de la app `prestamos/`, como en el diseño, y con dos excepciones propias que corresponden a los códigos de la API (`VideobeamNoExiste` es 404 y `VideobeamYaPrestado` es 409). Así la regla se prueba con pytest sin base de datos y sigue la estructura de Django.
- **Cómo la verifiqué:** Comparé las excepciones con la tabla de la API (sección 6 del diseño) y ejecuté `pytest` con un solo comando.

### Entrada 4

- **Fecha:** 7 de noviembre de 2026
- **Sugerencia o prompt:** Para el commit en rojo, la primera idea era subir solo las pruebas, sin el archivo `reglas.py`. El asistente propuso además un esqueleto de la función que lanza `NotImplementedError`.
- **Decisión:** Ajustada.
- **Razón:** Sin el archivo, pytest se detiene con un solo error de importación y no se ve qué prueba falla. Con el esqueleto se ejecutan las 11 pruebas y cada una falla por separado, así que el commit en rojo muestra claramente qué falta.
- **Cómo la verifiqué:** Ejecuté `pytest` antes del commit: «11 failed». Después de la implementación: «11 passed». Con `git diff` comprobé que las pruebas no cambiaron entre el commit en rojo y el commit en verde.

### Entrada 5

- **Fecha:** 7 de noviembre de 2026
- **Sugerencia o prompt:** Mientras armábamos los casos de prueba salió la opción de aceptar códigos en minúsculas o con espacios (por ejemplo `"vb-02"`), convirtiéndolos a `"VB-02"` antes de validar.
- **Decisión:** Rechazada.
- **Razón:** En el diseño el bibliotecario escoge el videobeam de una lista del formulario, así que el código siempre llega exacto. Convertir el texto sería una función que nadie pidió y escondería errores. Lo dejé como supuesto del contrato y con una prueba que lo trata como código que no existe.
- **Cómo la verifiqué:** La prueba `test_codigo_en_minusculas_se_trata_como_inexistente` pasa.

### Entrada 6

- **Fecha:** 7 de noviembre de 2026
- **Sugerencia o prompt:** Con las pruebas en verde, le pedí un refactor. Propuso pasar la lista `["VB-01", ..., "VB-05"]`, escrita dentro del `if`, a la constante `VIDEOBEAMS_DE_LA_BIBLIOTECA`, armar los mensajes con f-string y agregar docstrings.
- **Decisión:** Aceptada.
- **Razón:** La lista era un valor mágico. Con la constante se entiende qué es y hay un solo lugar donde cambiarla si la biblioteca compra otro videobeam. El comportamiento no cambia.
- **Cómo la verifiqué:** Ejecuté `pytest` después del refactor: «11 passed». Con `git diff` comprobé que la carpeta `tests/` no cambió.

## Entradas de la semana 6

### Entrada 7

- **Fecha:** 14 de noviembre de 2026
- **Sugerencia o prompt:** Segunda revisión de código con el prompt de la semana: «Actúa como revisor de código Python con experiencia en seguridad. Contexto: módulo `prestamos/reglas.py` de Control VideoBeam FET (Django con SQLite, solo lo usa el bibliotecario, ADR-001 y ADR-002); te pego el código, las pruebas, el requirements.txt y el .gitignore. Tarea: revisa corrección, legibilidad y seguridad: inyección, secretos, contraseñas, control de acceso y dependencias. Formato: tabla línea | problema | severidad | corrección sugerida. Restricciones: no reescribas todo el código; separa los problemas seguros de las sospechas que habría que verificar.» La IA entregó 3 problemas seguros y 3 sospechas.
- **Decisión:** Ajustada.
- **Razón:** Acepté los 3 problemas seguros (versiones sin fijar, el `set` que devolvía la función y las excepciones duplicadas). Las 3 sospechas eran falsos positivos: inyección SQL (no hay SQL), XSS por el mensaje (no hay HTML y Django escapa) y `assert` en las pruebas. Además la IA no vio que el `.gitignore` ignoraba `.env.example`.
- **Cómo la verifiqué:** Revisé cada línea que señaló, ejecuté la función con un `set` y con códigos manipulados, y probé el `.gitignore` con `git check-ignore -v`. El detalle está en la sección 3 de `revision_seguridad.md`.

### Entrada 8

- **Fecha:** 14 de noviembre de 2026
- **Sugerencia o prompt:** Para el hallazgo H-03, la IA propuso cambiar `return prestados | {codigo}` por `return frozenset(prestados) | {codigo}`.
- **Decisión:** Aceptada.
- **Razón:** Con un `set` común la función devolvía un `set` que otro código podía modificar, y el contrato promete un `frozenset`. Como la corrección cambia el comportamiento, primero agregué una prueba nueva en lugar de modificar las existentes.
- **Cómo la verifiqué:** La prueba nueva `test_si_recibe_un_set_comun_devuelve_frozenset_y_no_lo_modifica` falló antes del cambio («1 failed, 11 passed») y pasó después («12 passed»). Commit 91fc2b9.

### Entrada 9

- **Fecha:** 14 de noviembre de 2026
- **Sugerencia o prompt:** Usé la IA como agente de código para el refactor H-04, con esta instrucción delimitada: «Eres un agente que trabaja en la rama agente/refactor-errores. Contexto: proyecto Control VideoBeam FET en Python; módulo prestamos/reglas.py. Tarea: crea una clase base ErrorDePrestamo con el código del videobeam, para que la vista atrape un solo error, y escribe docstrings con Args, Returns y Raises. Formato: al terminar resume los archivos cambiados y el resultado de pytest y ruff. Restricciones: solo toca prestamos/reglas.py; no toques tests/; no instales paquetes; los mensajes de error no pueden cambiar; si tienes que cambiar una prueba, detente y pregunta.»
- **Decisión:** Aceptada después de revisar el diff.
- **Razón:** Quita el texto repetido «El {codigo} …» y deja en cada error su código HTTP (404 y 409), como en la tabla de la API del diseño. Los mensajes que ve el bibliotecario son los mismos.
- **Cómo la verifiqué:** `git diff --stat main..agente/refactor-errores` mostró solo `prestamos/reglas.py` y el diff de `tests/` salió vacío. Comprobé los mensajes y los códigos HTTP de cada error, y que el docstring dice lo mismo que el código (por ejemplo, que `None` da `VideobeamNoExiste`, como prueba el test de abuso). Pasaron las 17 pruebas y ruff dijo «All checks passed!». Integré con `git merge --no-ff` (commit 5996a84).

### Entrada 10

- **Fecha:** 14 de noviembre de 2026
- **Sugerencia o prompt:** La IA sugirió como sospecha de severidad alta que el código del videobeam podía causar inyección SQL.
- **Decisión:** Rechazada como corrección, pero la convertí en pruebas de abuso.
- **Razón:** La función no arma ninguna consulta: compara el código contra el conjunto fijo `VIDEOBEAMS_DE_LA_BIBLIOTECA`. Cambiar el código por esto habría sido una corrección para un problema que no existe. Sí sirve dejar pruebas que lo demuestren, por si alguien cambia la regla.
- **Cómo la verifiqué:** Agregué 5 pruebas de abuso (`' OR '1'='1`, `; DROP TABLE`, un `<script>`, un texto vacío y `None`). Todas dan `VideobeamNoExiste` y no cambian los prestados. Commit ad44f0b.

## Entradas después de la semana 6 (HU-01, HU-02 y HU-04)

### Entrada 11

- **Fecha:** 14 de noviembre de 2026
- **Sugerencia o prompt:** «Actúa como desarrollador Python que trabaja con pruebas primero en la rama hu-must. Contexto: proyecto Control VideoBeam FET; la regla de HU-08 ya está en prestamos/reglas.py con 17 pruebas; te paso los escenarios de HU-01, HU-02 y HU-04 del documento de requisitos y la tabla de API del diseño (400, 404 y 409). Tarea: escribe primero las pruebas de las tres historias, con casos normales, límite y de error, haz un commit en rojo, después la implementación y un refactor. Formato: al terminar resume archivos, pruebas y resultado de pytest y ruff. Restricciones: Python puro sin Django, no cambies las pruebas existentes, la hora llega como parámetro y no inventes mensajes sin avisarme.» La IA escribió 26 pruebas nuevas y propuso el mensaje «Falta la clase», que no está en el documento de requisitos.
- **Decisión:** Ajustada.
- **Razón:** Los mensajes «Falta el nombre del profesor» (HU-02) y «Escribe el nombre de quien lleva el videobeam» (HU-03) sí salen de mis requisitos. «Falta la clase» lo propuso la IA, porque la clase también es obligatoria en el préstamo. Lo dejé, pero como supuesto que hay que confirmar con el bibliotecario.
- **Cómo la verifiqué:** Comparé cada mensaje de las pruebas con los escenarios del documento de requisitos de la semana 3. Commit en rojo 305435f: «26 failed, 17 passed».

### Entrada 12

- **Fecha:** 14 de noviembre de 2026
- **Sugerencia o prompt:** Para HU-04 la IA agregó dos reglas que no estaban en la historia: rechazar una devolución con hora anterior a la salida, y permitir la devolución al día siguiente.
- **Decisión:** Aceptada.
- **Razón:** Una devolución antes de la salida es un dato imposible, seguramente un error al escribir la hora, y guardarlo dañaría el registro. Devolver al día siguiente tiene que ser posible porque HU-06 dice que un videobeam puede quedar sin devolver en su jornada, y por eso en el diseño cambié hora_devolucion por fecha_hora_devolucion.
- **Cómo la verifiqué:** Revisé HU-06 y el modelo de datos de la sección 5 del diseño. Las pruebas `test_la_devolucion_no_puede_ser_anterior_a_la_salida` y `test_se_puede_devolver_al_dia_siguiente` pasan. Commit en verde 31d5b81: «43 passed».

### Entrada 13

- **Fecha:** 14 de noviembre de 2026
- **Sugerencia o prompt:** Refactor con las pruebas en verde. La IA propuso sacar la validación repetida tres veces a `_texto_obligatorio`, la búsqueda del préstamo abierto a `_prestamo_abierto`, crear la propiedad `esta_abierto` y la constante `TOTAL_VIDEOBEAMS`, y escribir docstrings con Args, Returns y Raises.
- **Decisión:** Aceptada.
- **Razón:** Quita duplicación y un for con un if anidado. La función `registrar_devolucion` se lee en el mismo orden de los errores del docstring.
- **Cómo la verifiqué:** Comparé cada docstring con el código: el orden en que se revisan los datos, los mensajes exactos y que no se modifica la lista recibida. Con `git diff --stat` vi que `tests/` no cambió. Pasaron las 43 pruebas y ruff dijo «All checks passed!». Commit 10f17dc.

## Entradas del 21 de noviembre (aplicación de Django)

### Entrada 14

- **Fecha:** 21 de noviembre de 2026
- **Sugerencia o prompt:** «Revisa el código.» La IA revisó la rama `main` y las reglas de HU-01, HU-02 y HU-04 con todas las reglas de ruff. Encontró que las pruebas usaban fechas sin zona horaria (DTZ001), y que con Django (`USE_TZ = True`) comparar una fecha con zona y otra sin zona en `registrar_devolucion` lanza `TypeError`. También encontró los imports sin ordenar (I001) y el nombre `Set`, que se confunde con `set` (PYI025).
- **Decisión:** Aceptada.
- **Razón:** El error de las fechas solo habría aparecido al conectar Django, que era lo siguiente que iba a hacer. Las pruebas cambiaron solo en sus datos (fechas con `ZoneInfo("America/Bogota")`), no en lo que comprueban.
- **Cómo la verifiqué:** `ruff check --select DTZ,I,PYI .` sin avisos y 43 pruebas en verde. Commit «Revisión del 21 de noviembre».

### Entrada 15

- **Fecha:** 21 de noviembre de 2026
- **Sugerencia o prompt:** «Hazme la mitad de lo que falta.» Le pedí a la IA el proyecto Django con los modelos, las pantallas de las cuatro historias Must y el inicio de sesión, con pruebas primero, respetando el ADR-001 (Django y SQLite) y el ADR-002 (solo el bibliotecario). Su entorno no podía instalar Django, así que para probar copió el Django 5.2.1 que tengo instalado en mi computador.
- **Decisión:** Ajustada.
- **Razón:** La IA propuso fijar `Django==5.2.18` en `requirements.txt` porque es la última versión 5.2 con parches de seguridad (la 5.2.1 tiene vulnerabilidades corregidas después). Lo acepté, pero las pruebas se ejecutaron con la 5.2.1. Por eso tengo que instalar las dependencias y correr `pytest` y `pip-audit` en mi computador para confirmar.
- **Cómo la verifiqué:** 20 pruebas web en rojo antes de las vistas y 63 en verde después, sin cambiar ninguna prueba. Además se probó con `runserver`: inicio de sesión, préstamo, «4 de 5 videobeams disponibles», 403 sin token CSRF y contraseña guardada con `scrypt$`.

### Entrada 16

- **Fecha:** 21 de noviembre de 2026
- **Sugerencia o prompt:** La IA propuso proteger HU-08 también en la base de datos, con una restricción única condicional: un solo préstamo sin devolución por videobeam.
- **Decisión:** Aceptada.
- **Razón:** La regla de `reglas.py` revisa y después se guarda. Si dos préstamos del mismo videobeam llegan casi al mismo tiempo, los dos podrían pasar la revisión. Con la restricción, la base rechaza el segundo y la vista responde 409 «El VB-0X ya está prestado».
- **Cómo la verifiqué:** La prueba `test_la_base_no_permite_dos_prestamos_abiertos_del_mismo_videobeam` crea dos préstamos abiertos del VB-03 directamente en la base y comprueba que el segundo da `IntegrityError`.

### Entrada 17

- **Fecha:** 21 de noviembre de 2026
- **Sugerencia o prompt:** En el diseño, una petición sin sesión debe responder 401. La IA hizo que las páginas sin sesión redirijan (302) a la página de inicio de sesión.
- **Decisión:** Ajustada.
- **Razón:** Para las páginas HTML que usa el bibliotecario, mandarlo a iniciar sesión es más útil que una página de error 401. El 401 queda para cuando se haga la API en JSON. Lo anoté en los pendientes de `revision_seguridad.md`.
- **Cómo la verifiqué:** Las pruebas de abuso comprueban que, sin sesión, `POST /prestamos/` y `POST /devoluciones/` redirigen a `/cuentas/login/` y no guardan nada.

## Reflexión de la semana 5

El asistente me ayudó más a convertir la HU-08 en un contrato concreto, con firma, errores, supuestos y casos límite, y a pensar en casos que yo no habría probado, como que la función no modifique el conjunto que recibe o qué pasa cuando los 5 videobeams están prestados. Esta vez las pruebas no atraparon un error en la implementación, porque la primera versión pasó las 11 pruebas. Sí sirvieron para hacer el refactor con tranquilidad: sabía que si algo cambiaba, alguna prueba iba a fallar. El error más importante no lo atrapó una prueba sino la revisión contra mi diseño: el asistente me dijo que el proyecto era en HTML y localStorage, y el ADR-001 dice Django y SQLite. La próxima vez le pasaría el documento de diseño desde el primer mensaje y escribiría yo misma los casos límite antes de pedir sugerencias, para comparar mi lista con la del asistente.

## Reflexión de la semana 6

La revisión con IA fue útil para encontrar problemas reales rápido, pero la mitad de lo que marcó eran falsos positivos. Si hubiera copiado todo, habría «corregido» una inyección SQL en un código que no tiene SQL. Lo más importante, que el `.gitignore` ignoraba la plantilla `.env.example`, no lo encontró la IA: lo encontré con la lista de revisión, probando el archivo. Con el agente aprendí que la instrucción delimitada y el `git diff` antes de integrar son lo que permite confiar en su trabajo: sabía exactamente qué archivos podía tocar y lo comprobé.

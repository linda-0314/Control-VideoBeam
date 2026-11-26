# Bitácora de uso de IA

Proyecto: Control VideoBeam FET · Funcionalidad: HU-08, no prestar un videobeam ya prestado
Estudiante: Linda Paola Carreño Meneses
Asistente: Claude (claude.ai), con acceso a un entorno para crear archivos, ejecutar pytest y hacer commits.

## Entradas

### Entrada 1

- **Fecha:** 7 de noviembre de 2026
- **Sugerencia o prompt:** Le pasé al asistente el enunciado de la tarea de la semana 5 y mi documento de diseño de la semana 4. Me propuso trabajar la HU-08 «No prestar uno ya prestado» como primera funcionalidad.
- **Prompt mejorado (cómo lo pediría la próxima vez):** «Actúa como analista de requisitos con experiencia en desarrollo guiado por pruebas. Contexto: proyecto Control VideoBeam FET (Django y SQLite, solo lo usa el bibliotecario); te paso el enunciado de la tarea de la semana 5 y mi documento de diseño con las historias y su prioridad MoSCoW. Tarea: propón cuál historia Must conviene hacer primero como una sola función con su contrato. Formato: tabla historia | por qué sirve | tamaño | escenario de error que se puede probar, y al final tu recomendación. Restricciones: solo historias Must de mi documento; no inventes requisitos; no escribas código todavía.»
- **Decisión:** Aceptada.
- **Razón:** Es Must, cabe en una sola función y tiene un escenario de error con un mensaje exacto («El VB-01 ya está prestado») que se puede probar. Además protege lo más importante del sistema: que la disponibilidad sea real (N-01).
- **Cómo la verifiqué:** Revisé en el documento de requisitos que la HU-08 es Must, y en el diseño que su error corresponde al 409 de `POST /prestamos`.

### Entrada 2

- **Fecha:** 7 de noviembre de 2026
- **Sugerencia o prompt:** Le pregunté en qué se iba a desarrollar el proyecto. El asistente respondió que era una página en HTML, CSS y JavaScript que guarda los datos en el navegador (localStorage), sin servidor.
- **Prompt mejorado (cómo lo pediría la próxima vez):** «Actúa como arquitecto de software. Contexto: te paso mis documentos de la semana 3 (requisitos) y de la semana 4 (diseño con los ADR). Tarea: dime en qué tecnología se desarrolla el proyecto según la decisión vigente. Formato: lenguaje, framework y base de datos, con el ADR del que sale cada uno. Restricciones: si los dos documentos se contradicen, vale el más reciente; si no encuentras la decisión, dímelo en vez de suponerla.»
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
- **Prompt mejorado (cómo lo pediría la próxima vez):** «Actúa como revisor de código Python. Contexto: `prestamos/reglas.py` con la función `prestar_videobeam`; las 11 pruebas de `tests/test_reglas.py` están en verde. Tarea: propón un refactor que mejore la legibilidad sin cambiar el comportamiento. Formato: lista de cambios con el motivo de cada uno, y después el código. Restricciones: no toques `tests/`; los mensajes de error no pueden cambiar; no agregues funciones nuevas; al terminar, ejecuta `pytest` y muéstrame el resultado.»
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
- **Prompt mejorado (cómo lo pediría la próxima vez):** «Actúa como revisor de código Python con experiencia en Django. Contexto: proyecto Control VideoBeam FET; rama `main` con `prestamos/reglas.py` y los parches de HU-01, HU-02 y HU-04 (`prestamos/registro.py`); el siguiente paso es conectar Django con `USE_TZ = True`. Tarea: revisa corrección, legibilidad y los problemas que aparecerán al conectar Django. Formato: tabla archivo | problema | importancia (alta, media, baja) | corrección sugerida. Restricciones: no cambies el código todavía; separa los problemas seguros de las sospechas; ejecuta `pytest` y `ruff` y dime el resultado.»
- **Decisión:** Aceptada.
- **Razón:** El error de las fechas solo habría aparecido al conectar Django, que era lo siguiente que iba a hacer. Las pruebas cambiaron solo en sus datos (fechas con `ZoneInfo("America/Bogota")`), no en lo que comprueban.
- **Cómo la verifiqué:** `ruff check --select DTZ,I,PYI .` sin avisos y 43 pruebas en verde. Commit «Revisión del 21 de noviembre».

### Entrada 15

- **Fecha:** 21 de noviembre de 2026
- **Sugerencia o prompt:** «Hazme la mitad de lo que falta.» Le pedí a la IA el proyecto Django con los modelos, las pantallas de las cuatro historias Must y el inicio de sesión, con pruebas primero, respetando el ADR-001 (Django y SQLite) y el ADR-002 (solo el bibliotecario). Su entorno no podía instalar Django, así que para probar copió el Django 5.2.1 que tengo instalado en mi computador.
- **Prompt mejorado (cómo lo pediría la próxima vez):** «Actúa como desarrollador Django que trabaja con pruebas primero. Contexto: proyecto Control VideoBeam FET; reglas de HU-01, HU-02, HU-04 y HU-08 en `prestamos/` con 43 pruebas; diseño con ADR-001 (Django y SQLite), ADR-002 (solo el bibliotecario), modelo de datos (sección 5) y API (sección 6). Tarea: crea el proyecto Django, los modelos, el inicio de sesión y las pantallas de las cuatro historias Must. Formato: un commit de pruebas en rojo, uno de implementación en verde y uno de refactor; al terminar, resume archivos, pruebas y resultado de `pytest` y `ruff`. Restricciones: no cambies las reglas de `prestamos/reglas.py` ni `registro.py`; contraseñas con scrypt; `login_required` en todas las vistas; la clave secreta en `.env`; fija la versión de Django; si algo del diseño no se puede cumplir, detente y pregúntame.»
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

## Entradas de la semana 7 (suite de pruebas y registro)

### Entrada 18

- **Fecha:** 21 de noviembre de 2026
- **Prompt:** «Actúa como analista de pruebas de software. Contexto: proyecto Control VideoBeam FET; te paso las reglas de 4 funciones tal como están en mis historias de usuario: `mensaje_disponibilidad` (HU-01), `prestar_videobeam` (HU-08), `registrar_prestamo` (HU-02, HU-03 y HU-08) y `registrar_devolucion` (HU-04). Tarea: propón los casos de prueba con particiones de equivalencia (incluidas las inválidas), valores límite (el último valor de una partición y el primero de la siguiente) y, para `registrar_prestamo`, una tabla de decisión con todas sus condiciones, simplificada donde una condición no importe. Formato: una tabla por técnica y por función, con el esperado de cada caso y la frase de la regla de donde sale. Restricciones: los esperados salen de la regla, nunca del código; si la regla no dice algo, márcalo como ambigüedad en vez de decidirlo tú; no agregues reglas que no estén en las historias.»
- **Resultado:** Propuso las particiones y los límites de las 4 funciones y una tabla de decisión de 5 condiciones (C1 a C5) simplificada a 6 reglas. Señaló tres ambigüedades: el mensaje cuando falta la clase, qué mensaje se muestra si faltan varios datos, y la longitud máxima de los nombres.
- **Decisión:** Ajustada.
- **Razón:** Revisé la propuesta con las cinco preguntas. Particiones: faltaba P4 de disponibilidad (dos registros abiertos del mismo videobeam), que la agregué aunque la base lo impide. Límites: agregué los códigos VB-00 y VB-06 a cada lado de VB-01 a VB-05. Origen del esperado: cada caso tiene su historia. Ambigüedades: decidí las tres y quedan anotadas para confirmar. Reglas inventadas: la propuesta incluía aceptar `"vb-02"` convirtiéndolo a mayúsculas; la rechacé, igual que en la entrada 5.
- **Cómo la verifiqué:** Comparé cada esperado con el texto de las historias del documento de requisitos de la semana 3. Resultado: sección 1 de `registro_pruebas.md` (commit 40960fc).

### Entrada 19

- **Fecha:** 21 de noviembre de 2026
- **Prompt:** «Actúa como desarrollador de pruebas en Python. Contexto: proyecto Control VideoBeam FET; te paso las reglas y la tabla de casos revisada de 4 funciones (sección 1 de `registro_pruebas.md`). Tarea: escribe las pruebas con pytest a partir de la regla y de la tabla, no del código. Formato: `@pytest.mark.parametrize` con un comentario por fila que diga la partición o el límite; `pytest.raises` con el tipo de error exacto; `pytest.approx` si hay decimales; esperados fijos, nunca calculados. Restricciones: no modifiques el código de `prestamos/`; guarda las pruebas en `tests/test_s7_*.py`; si un esperado no sale de la regla, dímelo en vez de inventarlo.»
- **Resultado:** 53 pruebas en 4 archivos. Al ejecutarlas, 52 pasaron y 1 falló (`test_texto_de_101_caracteres`).
- **Decisión:** Ajustada.
- **Razón:** La prueba que falló mostró un defecto real (D-01): el código aceptaba 101 caracteres y la aplicación web los guardaba. Corregí el código, no la prueba. Después revisé cada prueba con las tres preguntas: descarté 8, corregí 8 y agregué los casos que la IA no hizo (por ejemplo, el «—» de la tabla de decisión). La más débil era `pytest.raises(Exception)`, que pasa con cualquier error.
- **Cómo la verifiqué:** Rompí el código con 4 errores a propósito. La versión de la IA sin revisar dejó pasar 3 y la revisada los detectó todos (sección 2 de `registro_pruebas.md`). Commits 801a3c5 (sin revisar), 7df8939 (defecto) y 748fe94 (revisión).

### Entrada 20

- **Fecha:** 21 de noviembre de 2026
- **Prompt:** «Actúa como probador de software. Contexto: tengo 125 pruebas en verde de `prestamos/registro.py`, `prestamos/reglas.py` y `prestamos/views.py`. Tarea: propón errores pequeños y realistas para meter en el código uno a la vez (cambiar un `<` por `<=`, un borde, un valor que siempre se devuelve igual, quitar una protección) y dime cuál prueba debería fallar con cada uno. Formato: tabla error | archivo y línea | prueba que debería fallar. Restricciones: no cambies ninguna prueba; yo ejecuto `pytest` después de cada error y lo deshago con `git restore`.»
- **Resultado:** Propuso 8 errores (E1 a E8). Al ejecutarlos uno a uno, 7 hicieron fallar al menos una prueba, pero el E5 (guardar la clase sin quitar los espacios) pasó las 125 pruebas.
- **Decisión:** Aceptada, con un caso agregado.
- **Razón:** El E5 mostró un hueco: la partición P2 (espacios en los extremos) solo se probaba con quién lo lleva. Agregué `test_espacios_en_los_extremos_se_quitan_en_cada_campo` para los tres campos.
- **Cómo la verifiqué:** Repetí el E5 y el E6 con la prueba nueva: fallan `[clase]` y `[profesor]`. Después de cada error, `git status` quedó limpio. Sección 3 de `registro_pruebas.md`, commit 7e81012.

### Entrada 21

- **Fecha:** 21 de noviembre de 2026
- **Prompt:** «Actúa como generador de datos de prueba. Contexto: préstamos de videobeams de la biblioteca de la FET en Neiva; cada préstamo tiene código (VB-01 a VB-05), quién lo lleva, clase y profesor, con máximo 100 caracteres por texto. Tarea: genera 5 préstamos válidos y 5 inválidos con su mensaje de error esperado. Formato: JSON con los campos `caso`, `codigo`, `quien_lleva`, `clase`, `profesor` y, en los inválidos, `mensaje`. Restricciones: nombres inventados con apellidos comunes del Huila y materias de la FET; ninguna persona real ni pública; incluye tildes, ñ, diéresis, apóstrofo, guion, texto vacío, solo espacios, el texto «0» y textos de 100 y 101 caracteres con letras de dos bytes.»
- **Resultado:** El archivo `tests/datos_sinteticos.json` con 10 registros y todos los casos difíciles pedidos.
- **Decisión:** Ajustada.
- **Razón:** La IA no incluyó teléfonos porque el sistema no los guarda, y lo dejé así. Agregué una prueba que avisa si alguien quita un caso difícil del archivo, y otra que pasa los 5 préstamos válidos por la aplicación web para comprobar que SQLite guarda y muestra bien las tildes, la ñ y el apóstrofo.
- **Cómo la verifiqué:** Revisé que ningún nombre fuera de alguien conocido o de una persona pública. Conté los caracteres: 100 eñes son 200 bytes, y la regla las acepta porque cuenta caracteres. Las 4 pruebas de `tests/test_s7_datos_sinteticos.py` pasan con el fixture `datos_sinteticos` (sección 4 de `registro_pruebas.md`, commit e777a89).
## Entradas del 25 de noviembre (HU-06)

### Entrada 22

- **Fecha:** 25 de noviembre de 2026
- **Sugerencia o prompt:** Le pedí a la IA que revisara mi repositorio y me guiara para terminar lo que faltaba. le pedí el código de HU-06 listo para copiar: las pruebas (`tests/test_pendientes.py`), la función `prestamos_pendientes`, la vista y la tabla en `inicio.html`.
- **Prompt:**«Actúa como tutor de Python y Django. Contexto: proyecto Control VideoBeam FET; HU-06 dice que un videobeam puede quedar sin devolver en su jornada. Tarea: guíame paso a paso para que yo escriba las pruebas y la función `prestamos_pendientes`. Formato: una pista por paso y espera a que te muestre lo que escribí. Restricciones: no me des el código completo; solo dime si voy bien o qué revisar.»
- **Decisión:** Aceptada después de verificar.
- **Razón:** Las pruebas cubren los casos que yo había definido: sin préstamos, préstamo de hoy, de ayer sin devolver, de ayer devuelto, y los límites de 11:59 p. m. y 12:00 a. m. También cubren la zona horaria: la base guarda en UTC y una salida a las 7:00 p. m. en Neiva no debe contar como del día siguiente.
- **Cómo la verifiqué:** Hice el ciclo en mi computador con tres commits: pruebas en rojo (`ImportError`), implementación en verde y la página. Al correr `pytest` fallaron 16 pruebas web con `TemplateSyntaxError`. Descubrí que el formateador automático de VS Code partía en dos líneas la etiqueta `{% for mensaje in messages %}`. Desactivé "Format On Save", restauré la plantilla con `git checkout` y volví a agregar la sección. Resultado final: 143 pruebas en verde y `ruff` sin avisos.


### Entrada 23

- **Fecha:** 25 de noviembre de 2026
- **Sugerencia o prompt:** Le pedí a la IA el código de HU-05 (devolución por otra persona) listo para copiar, porque tenía poco tiempo para la entrega. Me dio las pruebas (`tests/test_devolucion_otra_persona.py` y 2 pruebas web), la función `registrar_devolucion_por`, el campo `quien_devuelve` en el modelo, la vista y el campo «Quién lo devuelve» en el formulario.
- **Prompt** «Actúa como tutor de Django. Contexto: proyecto Control VideoBeam FET; HU-05 pide registrar quién devuelve el videobeam, aunque no sea quien lo sacó, y mostrar «Escribe el nombre de quien devuelve el videobeam» si falta. Tarea: dime qué archivos tengo que tocar y en qué orden, con pruebas primero. Formato: un paso a la vez y espera a que te muestre lo que hice. Restricciones: no me des el código completo; no cambies las reglas de HU-04 sin avisarme.»
- **Decisión:** Ajustada.
- **Razón:** La acepté porque cumple los dos escenarios de HU-05 de mi documento de requisitos. Tuve que cambiar una prueba de HU-04 (`test_devolucion_guarda_la_hora_y_deja_el_videobeam_disponible`) porque ahora el nombre de quien devuelve es obligatorio; cambió el requisito, no el comportamiento que comprueba. Dejé la regla de que primero se revisa el videobeam y después el nombre: si el videobeam no está prestado, no tiene sentido pedir quién lo trae.
- **Cómo la verifiqué:** Hice el ciclo en la rama `hu-05`: pruebas en rojo (`ImportError`) y después en verde. Generé la migración con `makemigrations` y la apliqué con `migrate`. Ruff marcó 2 líneas de más de 100 caracteres que se habían juntado al pegar, y las separé. Con `git diff` descubrí que el campo «Quién lo devuelve» del formulario no había quedado en el commit: las pruebas pasaban porque envían los datos directamente, sin usar el formulario. Lo agregué en un commit aparte y lo probé en el navegador: sin nombre aparece el mensaje en rojo, y con nombre se registra la devolución. Resultado: 155 pruebas en verde y `ruff` sin avisos.


## Reflexión de la semana 5

El asistente me ayudó más a convertir la HU-08 en un contrato concreto, con firma, errores, supuestos y casos límite, y a pensar en casos que yo no habría probado, como que la función no modifique el conjunto que recibe o qué pasa cuando los 5 videobeams están prestados. Esta vez las pruebas no atraparon un error en la implementación, porque la primera versión pasó las 11 pruebas. Sí sirvieron para hacer el refactor con tranquilidad: sabía que si algo cambiaba, alguna prueba iba a fallar. El error más importante no lo atrapó una prueba sino la revisión contra mi diseño: el asistente me dijo que el proyecto era en HTML y localStorage, y el ADR-001 dice Django y SQLite. La próxima vez le pasaría el documento de diseño desde el primer mensaje y escribiría yo misma los casos límite antes de pedir sugerencias, para comparar mi lista con la del asistente.

## Reflexión de la semana 6

La revisión con IA fue útil para encontrar problemas reales rápido, pero la mitad de lo que marcó eran falsos positivos. Si hubiera copiado todo, habría «corregido» una inyección SQL en un código que no tiene SQL. Lo más importante, que el `.gitignore` ignoraba la plantilla `.env.example`, no lo encontró la IA: lo encontré con la lista de revisión, probando el archivo. Con el agente aprendí que la instrucción delimitada y el `git diff` antes de integrar son lo que permite confiar en su trabajo: sabía exactamente qué archivos podía tocar y lo comprobé.

## Reflexión de la semana 7

Lo más importante de esta semana fue ver que una suite que pasa no es lo mismo que una suite que prueba. La versión de la IA tenía 53 pruebas y 52 pasaban, pero dejaba pasar 3 de 4 errores que metí a propósito, porque comprobaba `is not None`, `isinstance(..., str)` o `pytest.raises(Exception)` en vez del valor exacto de la regla. La única prueba que falló fue la más útil: encontró un defecto real (101 caracteres guardados en la base). También aprendí que la tabla de decisión simplificada necesita sus propias pruebas: el «—» es una decisión, y hay que comprobarla. Y que mis prompts de las primeras semanas eran demasiado cortos: con rol, contexto, tarea, formato y restricciones, la IA hace menos suposiciones.

## Reflexión de la semana 8

Esta semana me di cuenta de que había dejado que la IA hiciera demasiado del proyecto para HU-06 usé la IA para el código, pero hice yo el ciclo completo en mi máquina: pruebas en rojo, implementación en verde y la página, cada parte con su commit. Lo que más me enseñó fue un error que no venía del código: al guardar, el formateador de VS Code partía en dos líneas una etiqueta de Django y fallaban 16 pruebas. Tuve que leer el error, revisar el archivo con `Get-Content`, encontrar la causa y restaurarlo con `git checkout`. Ahí entendí que las pruebas no solo sirven para mi código, también detectan problemas del entorno.

De ahora en adelante quiero usar la IA como tutora y no como quien hace el trabajo: pedirle pistas en vez de soluciones completas y escribir yo primero, para que me corrija después. Así puedo explicar lo que entrego.

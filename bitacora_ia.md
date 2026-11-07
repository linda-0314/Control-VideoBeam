# Bitácora de uso de IA – Semana 5

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

## Reflexión

El asistente me ayudó más a convertir la HU-08 en un contrato concreto, con firma, errores, supuestos y casos límite, y a pensar en casos que yo no habría probado, como que la función no modifique el conjunto que recibe o qué pasa cuando los 5 videobeams están prestados. Esta vez las pruebas no atraparon un error en la implementación, porque la primera versión pasó las 11 pruebas. Sí sirvieron para hacer el refactor con tranquilidad: sabía que si algo cambiaba, alguna prueba iba a fallar. El error más importante no lo atrapó una prueba sino la revisión contra mi diseño: el asistente me dijo que el proyecto era en HTML y localStorage, y el ADR-001 dice Django y SQLite. La próxima vez le pasaría el documento de diseño desde el primer mensaje y escribiría yo misma los casos límite antes de pedir sugerencias, para comparar mi lista con la del asistente.

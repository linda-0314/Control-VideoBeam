# Registro de pruebas – Semana 7

Proyecto: Control VideoBeam FET
Estudiante: Linda Paola Carreño Meneses
Fecha: 21 de noviembre de 2026
Rama: `semana7`, creada desde `desarrollo` (aplicación Django con las historias Must)

Funciones probadas: 4 funciones con reglas de negocio de `prestamos/`. La que combina varias condiciones es `registrar_prestamo` (función 3), que tiene su tabla de decisión.

| # | Función | Archivo | Historia | Tipo de regla |
|---|---|---|---|---|
| 1 | `mensaje_disponibilidad(prestamos)` | `prestamos/registro.py` | HU-01 | Cálculo y estado |
| 2 | `prestar_videobeam(codigo, prestados)` | `prestamos/reglas.py` | HU-08 | Validación |
| 3 | `registrar_prestamo(codigo, prestamos, quien_lleva, clase, profesor, fecha_hora_salida)` | `prestamos/registro.py` | HU-02, HU-03 y HU-08 | Validación con varias condiciones |
| 4 | `registrar_devolucion(codigo, prestamos, fecha_hora)` | `prestamos/registro.py` | HU-04 | Validación y cambio de estado |

**Origen de los esperados:** todos salen de las historias de usuario y sus criterios de aceptación (documento de requisitos de la semana 3) y de las decisiones del diseño (semana 4). Ninguno sale de ejecutar el código. Cuando la regla no decía algo, está en la tabla de ambigüedades de cada función, con la decisión que tomé.

No hay decimales en el proyecto (se cuentan videobeams y se comparan fechas), así que `pytest.approx` no aplica.

## 1. Reglas y tablas de casos

### Función 1. `mensaje_disponibilidad` (HU-01)

**Regla (oráculo).** HU-01: «Como bibliotecario, quiero ver cuántos videobeams hay disponibles en este momento, para responder de inmediato a quien llega a pedir uno».
- Escenario 1: «Dado que hay 5 videobeams y 3 están prestados, cuando abro la consulta de disponibilidad, entonces veo el mensaje «2 de 5 videobeams disponibles»».
- Escenario 2: «Dado que los 5 videobeams están prestados, cuando abro la consulta, entonces veo el mensaje «No hay videobeams disponibles en este momento»».
- La biblioteca tiene 5 videobeams. Un préstamo cuenta como prestado hasta que se registra su devolución (HU-04).

**Particiones de equivalencia** (entrada: cantidad de videobeams con préstamo abierto)

| Partición | Valores | Esperado | Válida |
|---|---|---|---|
| P1. Hay al menos uno libre | 0 a 4 prestados | «N de 5 videobeams disponibles», con N = 5 − prestados | Sí |
| P2. Ninguno libre | 5 prestados | «No hay videobeams disponibles en este momento» | Sí |
| P3. Préstamos ya devueltos | Cualquier cantidad de préstamos cerrados | No cuentan: siguen libres | Sí |
| P4. Dos registros abiertos del mismo videobeam | Datos inconsistentes | Cuenta una sola vez (un videobeam no puede estar prestado dos veces) | No (la base lo impide con `un_prestamo_abierto_por_videobeam`) |

**Valores límite**

| Borde | Último de una partición | Primero de la siguiente |
|---|---|---|
| Entre P1 y P2 | 4 prestados → «1 de 5 videobeams disponibles» | 5 prestados → «No hay videobeams disponibles en este momento» |
| Inicio de P1 | 0 prestados → «5 de 5 videobeams disponibles» | 1 prestado → «4 de 5 videobeams disponibles» |

**Ambigüedades**

| Ambigüedad | Decisión |
|---|---|
| Con 1 libre, ¿«1 de 5 videobeams disponibles» o «1 de 5 videobeam disponible»? La regla solo da el ejemplo «2 de 5». | Mantener el mismo formato «N de 5 videobeams disponibles». Pendiente de confirmar con el bibliotecario. |

### Función 2. `prestar_videobeam` (HU-08)

**Regla (oráculo).** HU-08: «Como bibliotecario, quiero que el sistema no me deje prestar un videobeam que ya está prestado, para que la disponibilidad que consulto sea real».
- Escenario 1: «Dado que el VB-04 está disponible, cuando registro su préstamo, entonces el VB-04 pasa a prestado y deja de aparecer como libre».
- Escenario 2: «Dado que el VB-01 está prestado a Mateo Díaz, cuando intento registrar otro préstamo del VB-01, entonces el sistema no lo permite y muestra «El VB-01 ya está prestado»».
- Los videobeams son VB-01, VB-02, VB-03, VB-04 y VB-05 (requisitos). El código llega exacto desde la lista del formulario (contrato de la semana 5). Un código que no existe responde 404 «El VB-09 no existe» (diseño, sección 6).

**Particiones de equivalencia**

| Partición | Ejemplo | Esperado | Válida |
|---|---|---|---|
| P1. Código de la biblioteca y libre | `"VB-04"` con `{"VB-01"}` prestado | `frozenset({"VB-01", "VB-04"})` | Sí |
| P2. Código de la biblioteca y ya prestado | `"VB-01"` con `{"VB-01"}` | `VideobeamYaPrestado`: «El VB-01 ya está prestado» | No |
| P3. Código con formato correcto que no es de la biblioteca | `"VB-09"` | `VideobeamNoExiste`: «El VB-09 no existe» | No |
| P4. Código con otro formato | `"vb-02"`, `" VB-02"`, `"VB2"` | `VideobeamNoExiste` | No |
| P5. Sin código | `""`, `None` | `VideobeamNoExiste` | No |

**Valores límite** (los códigos van de VB-01 a VB-05)

| Borde | Último de una partición | Primero de la siguiente |
|---|---|---|
| Inferior | `"VB-00"` → `VideobeamNoExiste` | `"VB-01"` → se presta |
| Superior | `"VB-05"` → se presta | `"VB-06"` → `VideobeamNoExiste` |
| Cantidad de prestados | 4 prestados: prestar el último libre → quedan los 5 | 5 prestados: cualquier código → `VideobeamYaPrestado` |

**Ambigüedades**

| Ambigüedad | Decisión |
|---|---|
| ¿Se acepta `"vb-02"` o `" VB-02"` convirtiéndolos a `"VB-02"`? | No. El formulario manda el código exacto; convertir el texto sería una regla inventada (bitácora, entrada 5). |

### Función 3. `registrar_prestamo` (HU-02, HU-03 y HU-08): varias condiciones

**Regla (oráculo).**
- HU-02: «Como bibliotecario, quiero registrar un préstamo con el nombre de quien lo lleva, la clase, el profesor y la hora». Escenario 1: con VB-02 disponible, registrar a «Laura Gómez», clase «Bases de datos», profesor «Andrés Ruiz» deja el VB-02 prestado con esos datos. Escenario 2: «intento guardar el préstamo sin escribir el nombre del profesor → el sistema no guarda el préstamo y muestra «Falta el nombre del profesor»».
- HU-03, escenario 2: «intento registrar el préstamo sin el nombre de quien lo lleva → el sistema no guarda el préstamo y muestra «Escribe el nombre de quien lleva el videobeam»».
- HU-08: no se presta un videobeam que ya está prestado (función 2).
- Diseño: un dato faltante responde 400; un código que no existe, 404; un videobeam ya prestado, 409.

**Condiciones**

| Id | Condición |
|---|---|
| C1 | Quién lo lleva tiene texto (no vacío, no solo espacios, no `None`) |
| C2 | La clase tiene texto |
| C3 | El profesor tiene texto |
| C4 | El código es de la biblioteca (VB-01 a VB-05) |
| C5 | El videobeam no tiene un préstamo abierto |

**Tabla de decisión** (simplificada: «—» significa que la condición no importa, porque una condición anterior ya decidió el resultado; las 32 combinaciones de 5 condiciones se reducen a 6 reglas)

| Regla | C1 | C2 | C3 | C4 | C5 | Resultado |
|---|---|---|---|---|---|---|
| R1 | No | — | — | — | — | `DatoInvalido` (400): «Escribe el nombre de quien lleva el videobeam» |
| R2 | Sí | No | — | — | — | `DatoInvalido` (400): «Falta la clase» |
| R3 | Sí | Sí | No | — | — | `DatoInvalido` (400): «Falta el nombre del profesor» |
| R4 | Sí | Sí | Sí | No | — | `VideobeamNoExiste` (404) |
| R5 | Sí | Sí | Sí | Sí | No | `VideobeamYaPrestado` (409) |
| R6 | Sí | Sí | Sí | Sí | Sí | Préstamo nuevo sin devolución, con los textos sin espacios en los extremos |

Para comprobar que el «—» es correcto, la suite tiene casos donde fallan varias condiciones a la vez (por ejemplo, todo vacío y además un videobeam ya prestado): siempre gana la primera regla de la tabla.

**Particiones de equivalencia de cada texto** (quién lo lleva, clase y profesor)

| Partición | Ejemplo | Esperado | Válida |
|---|---|---|---|
| P1. Texto normal | `"Laura Gómez"` | Se guarda igual | Sí |
| P2. Texto con espacios en los extremos | `"  Laura Gómez "` | Se guarda `"Laura Gómez"` | Sí |
| P3. Texto con tildes, ñ o apóstrofo | `"Íñigo Peña"`, `"Ana D'Ángelo"` | Se guarda igual | Sí |
| P4. Vacío | `""` | `DatoInvalido` con el mensaje del campo | No |
| P5. Solo espacios | `"   "` | `DatoInvalido` | No |
| P6. Sin valor | `None` | `DatoInvalido` | No |
| P7. Más largo de lo que se puede guardar | 101 caracteres | `DatoInvalido` | No |

**Valores límite de la longitud** (el campo guarda máximo 100 caracteres: `models.py` y el `maxlength` del formulario)

| Borde | Último de una partición | Primero de la siguiente |
|---|---|---|
| Inferior | 0 caracteres útiles (`""` o `"   "`) → `DatoInvalido` | 1 carácter (`"A"`) → se guarda |
| Superior | 100 caracteres → se guarda | 101 caracteres → `DatoInvalido` |

**Ambigüedades**

| Ambigüedad | Decisión |
|---|---|
| El mensaje cuando falta la clase no está en los requisitos. | «Falta la clase», con el mismo estilo de HU-02. Pendiente de confirmar con el bibliotecario (bitácora, entrada 11). |
| Si faltan varios datos, ¿qué mensaje se muestra? La regla habla de un dato a la vez. | El del primer campo en el orden del formulario: quién lo lleva, clase y profesor. Después se revisa el videobeam. |
| ¿Cuál es la longitud máxima de un nombre o una clase? El cliente no la dio. | 100 caracteres, como el campo de la base y el `maxlength` del formulario. Mensaje: «… no puede tener más de 100 caracteres». Decisión mía; queda anotada para confirmarla con el docente. |

### Función 4. `registrar_devolucion` (HU-04)

**Regla (oráculo).** HU-04: «Como bibliotecario, quiero registrar la devolución de un videobeam con la hora de entrega, para saber que volvió y que ya se puede prestar otra vez».
- Escenario 1: «Dado que el VB-02 está prestado desde las 6:40 p. m., cuando registro la devolución a las 9:30 p. m., entonces el VB-02 queda disponible, se guarda la hora 9:30 p. m. y la disponibilidad sube en 1».
- Escenario 2: «Dado que el VB-04 está disponible, cuando intento registrar su devolución, entonces el sistema no hace ningún cambio y muestra «El VB-04 no está prestado»».
- HU-06: un videobeam puede quedar sin devolver en su jornada; por eso la devolución se puede registrar otro día (diseño: `fecha_hora_devolucion`).
- Decisión del 14 de noviembre (bitácora, entrada 12): la devolución no puede ser anterior a la salida.

**Particiones de equivalencia**

| Partición | Ejemplo | Esperado | Válida |
|---|---|---|---|
| P1. Videobeam con préstamo abierto y hora ≥ salida | VB-02 salió 6:40 p. m., vuelve 9:30 p. m. | Copia del préstamo con `fecha_hora_devolucion` = 9:30 p. m. | Sí |
| P2. Videobeam sin préstamo abierto: nunca prestado | VB-04 | `VideobeamNoPrestado`: «El VB-04 no está prestado» | No |
| P3. Videobeam sin préstamo abierto: ya devuelto | VB-02 devuelto antes | `VideobeamNoPrestado` | No |
| P4. Código que no es de la biblioteca | `"VB-09"` | `VideobeamNoExiste` | No |
| P5. Hora anterior a la salida | 6:39 p. m. para una salida de 6:40 p. m. | `DatoInvalido`: «La hora de devolución no puede ser anterior a la de salida» | No |
| P6. Préstamos viejos del mismo videobeam | Uno cerrado ayer y uno abierto hoy | Se cierra el abierto | Sí |

**Valores límite** (hora de devolución respecto a la salida de las 6:40 p. m.)

| Borde | Último de una partición | Primero de la siguiente |
|---|---|---|
| Hora | 6:39 p. m. (1 minuto antes) → `DatoInvalido` | 6:40 p. m. (la misma hora) → se registra |
| Día | 11:59 p. m. del mismo día → se registra | 12:00 a. m. del día siguiente → se registra (HU-06) |

**Ambigüedades**

| Ambigüedad | Decisión |
|---|---|
| ¿Se puede devolver a la misma hora de la salida? | Sí: «anterior» no incluye la misma hora. |
| ¿Hay un tiempo máximo para devolver? | No en esta versión: HU-06 (pendientes de la jornada) lo marcará como no devuelto, pero se puede registrar. |

## 2. Pruebas de la IA corregidas o descartadas

**Cómo se generaron.** Le di a la IA las reglas y las tablas de la sección 1 con este prompt: «Actúa como desarrollador de pruebas en Python. Contexto: proyecto Control VideoBeam FET; te paso las reglas (historias de usuario) y la tabla de casos de 4 funciones: mensaje_disponibilidad, prestar_videobeam, registrar_prestamo (con su tabla de decisión) y registrar_devolucion. Tarea: escribe las pruebas con pytest a partir de la regla y la tabla, no del código. Formato: @pytest.mark.parametrize con un comentario por fila que diga la partición o el límite, pytest.raises con el tipo de error exacto, pytest.approx si hay decimales, y esperados fijos. Restricciones: no modifiques el código de prestamos/; si un esperado no sale de la regla, dímelo.»

La IA entregó 53 pruebas en 4 archivos `tests/test_s7_*.py` (commit 801a3c5, guardado sin revisar). Al ejecutarlas, 52 pasaron y 1 falló. Después revisé cada prueba con las tres preguntas: **(1)** ¿el esperado sale de la regla?, **(2)** ¿fallaría si rompo el código?, **(3)** ¿cubre algo que otra prueba no cubre?

**Prueba que falló: defecto real en el código**

| Id | Prueba | Qué pasó | Qué hice |
|---|---|---|---|
| D-01 | `test_texto_de_101_caracteres` | El esperado sale de la tabla (101 caracteres es el primer valor inválido). El código aceptaba 101 caracteres, y la aplicación web los guardaba completos porque SQLite no hace cumplir el `max_length` (lo comprobé: `POST /prestamos/` respondió 302 y guardó 101 caracteres). | Corregí el código, no la prueba: `_texto_obligatorio` revisa `LONGITUD_MAXIMA_TEXTO = 100` (commit 7df8939). Después fortalecí la prueba con el mensaje exacto en los tres campos. |

**Pruebas corregidas o descartadas**

| # | Archivo | Prueba de la IA | Pregunta que falló | Decisión | Razón | Qué hice en su lugar |
|---|---|---|---|---|---|---|
| 1 | disponibilidad | fila `(2, "3 de 5 …")` | 3 | Descartada | Es otro valor intermedio de P1; ya están el escenario 1 (3 prestados) y los límites 0, 1 y 4. | Nada: P1 sigue cubierta. |
| 2 | disponibilidad | `test_mensaje_devuelve_texto` | 2 y 3 | Descartada | Solo comprueba que el resultado sea `str`. Un mensaje equivocado también es `str`. | Nada: la fila parametrizada ya compara el texto exacto. |
| 3 | disponibilidad | `test_prestamos_devueltos_no_cuentan` | 2 | Corregida | Con un solo préstamo devuelto no comprueba la mezcla de abiertos y cerrados. | `test_los_prestamos_devueltos_no_cuentan` con 3 filas: uno devuelto, 2 abiertos más 3 cerrados, y los 5 abiertos más 2 viejos. |
| 4 | disponibilidad | `test_codigos_prestados_con_tres` | 2 y 3 | Descartada | `len(...) == 3` pasa aunque devuelva otros códigos; además `codigos_prestados` no es una de las 4 funciones y ya la prueba `test_disponibilidad.py`. | Nada. |
| 5 | disponibilidad | (faltaba) | — | Agregada | La IA no probó la partición P4 de la tabla (dos registros abiertos del mismo videobeam). | `test_dos_registros_abiertos_del_mismo_videobeam_cuentan_una_vez`. |
| 6 | prestar | `test_prestar_codigo_que_no_existe` (8 filas) | 2 | Corregida | Usaba `pytest.raises(Exception)`: pasa con cualquier error. Lo comprobé: si el código lanza `VideobeamYaPrestado` en lugar de `VideobeamNoExiste`, las 8 filas siguen pasando. | `pytest.raises(VideobeamNoExiste, match="^El VB-00 no existe$")` con el mensaje exacto en cada fila. |
| 7 | prestar | `test_prestar_uno_ya_prestado` y `test_prestar_con_los_cinco_prestados` | 1 | Corregidas y unidas | No comprobaban el mensaje «El VB-01 ya está prestado», que está literal en HU-08. | Una prueba parametrizada con `match` del mensaje exacto. |
| 8 | prestar | `test_mensaje_codigo_inexistente` | 2 y 3 | Descartada | `"no existe" in str(...)` es débil y queda repetida con la corrección 6. | Nada: la fila `VB-09` de la 6 la cubre. |
| 9 | registrar_prestamo | `test_r6_prestamo_valido` | 2 | Corregida | Solo revisaba `is not None` y el código. Lo comprobé: si el código guarda la clase en el profesor y al revés, la prueba seguía pasando. | Compara el `Prestamo` completo con los datos de HU-02, escenario 1. |
| 10 | registrar_prestamo | `test_textos_vacios_en_profesor` | 3 | Descartada | Igual a `test_textos_vacios_en_profesor_otra_vez`, pero sin el mensaje. | Nada. |
| 11 | registrar_prestamo | `test_textos_vacios_en_profesor_otra_vez` | 3 | Corregida | Solo probaba el profesor; quién lo lleva y la clase solo tenían el caso `""`. | `test_texto_vacio_en_cada_campo`: 3 campos × 3 vacíos (`""`, `"   "`, `None`) con su mensaje. |
| 12 | registrar_prestamo | (faltaba) | — | Agregada | La tabla de decisión simplificada usa «—», pero la IA no probó combinaciones con varias condiciones falsas. | `test_si_fallan_varias_condiciones_gana_la_primera` (4 filas) y `test_si_c4_y_c5_fallan_gana_que_no_existe`. |
| 13 | registrar_prestamo | (faltaba) | — | Agregada | El límite de 100 caracteres cuenta sin los espacios de los extremos; la IA no lo probó. | Fila `100-mas-espacios`: 102 caracteres con espacios se aceptan y se guardan 100. |
| 14 | devolucion | `test_devoluciones_validas` | 2 | Corregida | Solo comparaba la hora de devolución. Lo comprobé: si al devolver se borra quién lo llevó, las 5 filas seguían pasando. | Compara el préstamo completo: `replace(ABIERTO_VB02, fecha_hora_devolucion=…)`. |
| 15 | devolucion | fila `SALIDA + 1 minuto` | 3 | Descartada | El límite es la misma hora (primer valor válido); un minuto después es otro valor de la misma partición. | Nada. |
| 16 | devolucion | `test_devolucion_un_minuto_antes_de_la_salida` | 1 | Corregida | No comprobaba el mensaje de la regla. Lo comprobé: con otro mensaje seguía pasando. | `match` con el mensaje exacto. |
| 17 | devolucion | `test_devoluciones_invalidas` | 1 y 3 | Corregida | Sin mensajes, y faltaban P3 (ya devuelto) y P6 (préstamos viejos del mismo videobeam). La fila «VB-02 sin préstamos» repetía P2. | Mensajes exactos, fila de P3 en lugar de la repetida y `test_con_prestamos_viejos_cierra_el_abierto` para P6. |
| 18 | devolucion | `test_no_modifica_el_prestamo_original` | 2 | Descartada | `Prestamo` es un `dataclass(frozen=True)`: Python no deja modificarlo, así que la prueba no puede fallar nunca. | Nada: la protección la da `frozen=True`. |

**Comprobación de la revisión.** Con 4 errores a propósito, la versión de la IA sin revisar dejó pasar 3 y la revisada los detectó todos:

| Error introducido | Versión de la IA (sin revisar) | Versión revisada |
|---|---|---|
| Guardar la clase en el profesor y al revés | 19 pasan | 1 falla |
| Un código que no existe lanza `VideobeamYaPrestado` | 1 falla (solo `test_mensaje_codigo_inexistente`) | 8 fallan |
| Cambiar el mensaje de la hora anterior a la salida | 10 pasan | 1 falla |
| Al devolver, borrar quién lo llevó | 10 pasan | 5 fallan |

Ninguna prueba se ajustó para que pasara: las 62 pruebas revisadas pasaron sin cambiar el código, salvo la corrección del defecto D-01.

## 3. Romper el código a propósito

Cada error se introdujo solo, se ejecutó toda la suite (`pytest`, 125 pruebas en ese momento) y se deshizo con `git restore` antes del siguiente.

| # | Error introducido | Archivo | Pruebas que fallaron | Resultado |
|---|---|---|---|---|
| E1 | `<` por `<=` en la hora de devolución: no deja devolver a la misma hora | `registro.py` | `test_devolucion_valida_cierra_el_mismo_prestamo[devolucion0]` y `test_se_puede_devolver_en_el_mismo_minuto_de_la_salida` | Detectado (límite) |
| E2 | Borde de «ninguno libre»: `libres == 0` por `libres <= 1` | `registro.py` | `test_mensaje_segun_cantidad_de_prestados[4-1 de 5 …]` y `test_con_cuatro_prestados_queda_uno_disponible` | Detectado (límite) |
| E3 | `prestar_videobeam` devuelve siempre los mismos prestados, sin agregar el código | `reglas.py` | 10: las 4 filas de `test_prestar_un_videobeam_libre` y 6 de `test_reglas.py` | Detectado |
| E4 | `>` por `>=` en la longitud máxima: rechaza 100 caracteres | `registro.py` | `test_textos_validos_de_quien_lleva[100-caracteres]` y `[100-mas-espacios]` | Detectado (límite) |
| E5 | La clase se valida pero se guarda sin quitar los espacios | `registro.py` | **Ninguna** (125 pasaron) | **No detectado:** P2 solo se probaba con quién lo lleva. Agregué `test_espacios_en_los_extremos_se_quitan_en_cada_campo` (commit 7e81012). Al repetir E5, falla `[clase]`. |
| E6 | Lo mismo con el profesor | `registro.py` | Solo `test_quita_los_espacios_alrededor_de_los_nombres` (de la semana 5) | Detectado, pero no por la suite de la semana 7. Con la prueba nueva también falla `[profesor]`. |
| E7 | `codigos_prestados` cuenta también los préstamos devueltos | `registro.py` | 4: 2 filas de `test_los_prestamos_devueltos_no_cuentan` y 2 de semanas anteriores | Detectado |
| E8 | Quitar `@login_required` de la vista `crear_prestamo` | `views.py` | `test_abuso_sin_sesion_no_se_puede_registrar_un_prestamo` | Detectado (control de acceso) |

## 4. Datos de prueba sintéticos

| Aspecto | Detalle |
|---|---|
| Origen | Generados con IA (Claude) el 21 de noviembre de 2026, con el prompt: «Genera datos de prueba para préstamos de videobeams de la biblioteca de la FET en Neiva: nombres inventados con apellidos comunes del Huila, materias de la universidad y profesores ficticios. Sin personas reales. Incluye casos difíciles: tildes, ñ, diéresis, apóstrofo, guion, texto vacío, solo espacios, el texto 0 y textos en el límite de 100 caracteres.» Revisé que ningún nombre fuera de alguien que conozco o de una persona pública. |
| Archivo y fixture | `tests/datos_sinteticos.json` y el fixture `datos_sinteticos` de `tests/conftest.py` |
| Contexto local | Materias de la FET (Cálculo diferencial, Programación orientada a objetos, Inglés III, Ética profesional, Redes y telecomunicaciones) y apellidos comunes del Huila (Perdomo, Cuéllar, Polanía, Losada, Tovar) |
| Casos difíciles | Tildes («José Ángel Muñoz Perdomo»), ñ y diéresis («Begoña Núñez Güiza»), apóstrofo («Ana D'Ángelo Rojas»), guion («María-José Polanía»), espacios en los extremos, nombre de una letra («Ñ»), el texto «0» como clase, 100 eñes (200 bytes: comprueba que se cuentan caracteres y no bytes), 101 eñes, texto vacío, solo espacios y un tabulador |
| Datos que no se generaron | Teléfonos y documentos: el sistema no los guarda (solo quién lo lleva, clase y profesor) |
| Dónde se usan | `tests/test_s7_datos_sinteticos.py`: los 5 válidos y los 5 inválidos contra `registrar_prestamo`, y los 5 válidos por la aplicación web (se guardan en SQLite y se muestran con sus caracteres) |

## Resumen

| Concepto | Valor |
|---|---|
| Funciones probadas | 4 (una con tabla de decisión de 5 condiciones) |
| Pruebas de la semana 7 | 69 en `tests/test_s7_*.py` |
| Pruebas totales del proyecto | 132, todas pasan con `pytest -v` |
| Pruebas de la IA descartadas | 8 |
| Pruebas de la IA corregidas | 8 |
| Casos agregados que la IA no hizo | 6 grupos, más 1 caso agregado en el paso 5 (E5) |
| Defectos reales encontrados | 1 (D-01, textos de más de 100 caracteres), corregido en el código |
| Errores introducidos a propósito | 8; 1 no detectado (E5), con su caso agregado |

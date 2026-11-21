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

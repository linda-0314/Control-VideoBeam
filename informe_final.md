# Informe final del proyecto integrador

Proyecto: Proyecto Control VideoBeam FET
Estudiante: Linda Paola Carreño Meneses
Repositorio: https://github.com/linda-0314/Control-VideoBeam
Fecha: 2026-11-27


## 1. Resumen

En la FET, el bibliotecario presta los 5 videobeams en buen estado y registra cada préstamo en una planilla de papel, así que no sabe al instante si hay alguno libre. Desarrollé una aplicación web con Django y SQLite, que solo pueda usar el bibliotecario. Usé Claude en los requisitos, el diseño, el código, las pruebas y la revisión de seguridad: ordenó la entrevista en historias de usuario, propuso el diseño y generó la mayor parte del código y de las pruebas. Yo decidí qué construir, corregí sus errores y verifiqué cada resultado; todo quedó en la bitácora de IA. Las pruebas de la IA pasaban, pero dejaron pasar 3 de 4 errores que metí a propósito; después de revisarlas, detectaron los 4 y encontraron un defecto real. Resultado final: 198 pruebas en verde con pytest, ruff sin avisos y pip-audit sin vulnerabilidades.


## 2. Problema y usuario

**Quién tiene el problema.** El bibliotecario de la FET, que presta y recibe los 5 videobeams de la biblioteca. Es el único que usa el sistema: los profesores y estudiantes piden el videobeam en persona y no usan la aplicación.

**Cómo lo resolvía antes.** Anota cada préstamo en una planilla de papel que se firma al sacar el videobeam y otra vez al devolverlo. Cuando alguien llega a pedir uno, tiene que revisar la planilla o los equipos para saber si queda alguno libre, y muchas veces no hay.

**Qué necesita.** Saber al instante cuántos videobeams hay disponibles, registrar el préstamo (quién lo lleva, la clase, el profesor y la hora) y la devolución (la hora y quién lo trae, que puede ser otra persona), controlar que salga y vuelva con su cable HDMI y ver los que no se devolvieron en la jornada.

Algunas frases de la entrevista que muestran el problema:

- «Van a la biblioteca y no hay.»
- «Se firma una hoja: nombre del que la lleva, clase, profesor, a qué horas lo llevó.»
- «Si el estudiante X lo sacó, lo puede devolver otro.»
- «Siempre se entrega con HDMI.»

La entrevista fue simulada (24 de octubre de 2026): respondí yo como estudiante usuaria del servicio, a partir de mi experiencia. Por eso todo queda pendiente de validar con el bibliotecario.

Evidencia: [propuesta del módulo 1](docs/Carreno_Linda_S1_Propuesta_v2.pdf) y [requisitos y entrevista del módulo 2](docs/Carreno_Linda_S3_Requisitos.pdf).

## 3. La IA en el ciclo de vida

| Módulo y fase | Qué hiciste con IA | Herramienta | Evidencia (enlace) | Cómo verificaste |
|---|---|---|---|---|
| 1. Fundamentos | Definí el problema y planeé usar IA en requisitos y pruebas | Ninguna | [Propuesta](docs/Carreno_Linda_S1_Propuesta_v2.pdf) | La versión 2 ajusta el enfoque al bibliotecario, decidido en los módulos 2 y 3 |
| 2. Requisitos | Ordenar la entrevista en necesidades, escribir las historias con escenarios, revisarlas con INVEST, priorizar con MoSCoW y hacer los diagramas C4 | Claude (claude.ai) y mermaid.live | [Requisitos, sección 7 y anexo de prompts](docs/Carreno_Linda_S3_Requisitos.pdf) | Cada historia sale de una cita de la entrevista; conté 4 de 8 historias Must (50 %) |
| 3. Diseño | Comparar alternativas de arquitectura, redactar el ADR-001 y el ADR-002, el modelo de datos y la API | Claude (claude.ai) | [Diseño y ADR](docs/Carreno_Linda_S4_Diseno.pdf) | Revisé cada propuesta contra los requisitos y el ADR vigente ([Entrada 2](bitacora_ia.md)) |
| 4. Código | Reglas en Python puro con pruebas primero, aplicación Django, agente en una rama aparte y las historias HU-05 a HU-10 | Claude con un entorno para crear archivos y ejecutar pytest | [Bitácora, entradas 1 a 17 y 22 a 27](bitacora_ia.md); [integración del agente](https://github.com/linda-0314/Control-VideoBeam/commit/5996a84) | pytest en rojo y en verde, `git diff` de `tests/`, ruff y prueba en el navegador |
| 5. Pruebas | Particiones, valores límite y tabla de decisión; 53 pruebas generadas; errores introducidos a propósito; datos sintéticos | Claude con un entorno para ejecutar pytest | [Registro de pruebas](registro_pruebas.md) | Revisé cada prueba con tres preguntas y metí 4 errores a propósito para ver si las pruebas los detectaban |
| 6. Operación | Revisión de código y seguridad, auditoría de dependencias y pipeline de integración continua | Claude (claude.ai), ruff, pip-audit y GitHub Actions | [Revisión de seguridad](revision_seguridad.md); [pipeline](.github/workflows/pruebas.yml); [ejecución en verde](https://github.com/linda-0314/Control-VideoBeam/actions/runs/46012097081/job/140549910862) | pip-audit sin vulnerabilidades y pipeline en verde en cada `git push`. El despliegue no se hizo porque el docente indicó que no se evaluaría ([Entrada 29](bitacora_ia.md)) |

También usé Claude en la entrega final: para organizar este informe a partir de la plantilla, del repositorio y el pipeline. Revisé las cifras contra `pytest`, el pipeline y `git log`, y cambié por datos sintéticos una captura que tenía datos que podían ser reales ([Entradas 28 y 29 de la bitácora](bitacora_ia.md)).

## 4. Verificación: lo que la IA hizo mal y cómo lo encontraste

### Caso 1: la IA cambió el problema

- **Fase:** requisitos.
- **Qué propuso la IA:** un sistema de reservas anticipadas para evitar cruces de horario, que además incluía portátiles y salones.
- **Qué estaba mal:** en la FET los videobeams no se reservan, se piden en el momento, y el proyecto es solo de videobeams.
- **Cómo lo detecté:** comparé cada historia con lo que se dijo en la entrevista y ninguna cita hablaba de reservas.
- **Qué hice:** cambié el enfoque a préstamos y devoluciones de videobeams y quité portátiles y salones ([requisitos, sección 7](docs/Carreno_Linda_S3_Requisitos.pdf)).

### Caso 2: la IA contradijo el diseño

- **Fase:** diseño.
- **Qué propuso la IA:** dijo que el proyecto era una página en HTML, CSS y JavaScript que guardaba los datos en el navegador (localStorage); en los diagramas C4 ya había elegido Node.js sin que yo hubiera decidido la arquitectura.
- **Qué estaba mal:** el ADR-001 vigente dice Django y SQLite. Si lo hubiera aceptado, habría programado en otro lenguaje.
- **Cómo lo detecté:** revisé la respuesta contra el ADR-001 del documento de diseño.
- **Qué hice:** la rechacé, le pasé el documento de diseño y desde entonces todo se hizo en Python con pytest ([Entrada 2 de la bitácora](bitacora_ia.md)).

### Caso 3: pruebas que pasaban pero no probaban

- **Fase:** pruebas.
- **Qué propuso la IA:** 53 pruebas generadas desde mis tablas de casos; 52 pasaban ([commit 801a3c5](https://github.com/linda-0314/Control-VideoBeam/commit/801a3c5)).
- **Qué estaba mal:** muchas revisaban `is not None`, `isinstance(..., str)` o `pytest.raises(Exception)` en vez del valor exacto de la regla, y dejaron pasar 3 de 4 errores que metí a propósito.
- **Cómo lo detecté:** revisé cada prueba con tres preguntas y rompí el código a propósito. La única prueba que falló encontró un defecto real: se guardaban textos de 101 caracteres (D-01).
- **Qué hice:** corregí el código y no la prueba ([commit 7df8939](https://github.com/linda-0314/Control-VideoBeam/commit/7df8939)); descarté 8 pruebas, corregí 8 y agregué los casos que faltaban ([commit 748fe94](https://github.com/linda-0314/Control-VideoBeam/commit/748fe94) y [commit 7e81012](https://github.com/linda-0314/Control-VideoBeam/commit/7e81012)). La suite revisada detectó los 4 errores.

### Caso 4: falsos positivos en la revisión de seguridad

- **Fase:** revisión de código y seguridad.
- **Qué propuso la IA:** 3 problemas reales y 3 sospechas: inyección SQL, XSS y `assert` en las pruebas.
- **Qué estaba mal:** las tres sospechas eran falsos positivos, porque no había SQL ni HTML en ese código. Además, no vio que el `.gitignore` ignoraba la plantilla `.env.example`.
- **Cómo lo detecté:** revisé cada línea que señaló y probé el `.gitignore` con `git check-ignore -v`.
- **Qué hice:** convertí la sospecha de inyección en 5 pruebas de abuso ([commit ad44f0b](https://github.com/linda-0314/Control-VideoBeam/commit/ad44f0b)) y corregí el `.gitignore` ([commit a6c8f4a](https://github.com/linda-0314/Control-VideoBeam/commit/a6c8f4a)).

## 5. Estado final del sistema

- **Arquitectura:** aplicación web monolítica en Django 5.2.18 y SQLite; Solo la usa el bibliotecario, con inicio de sesión y contraseña guardada con scrypt (ADR-002). Las reglas del negocio están en Python puro (`prestamos/reglas.py` y `prestamos/registro.py`) y las vistas de Django solo las llaman. Ver el [diseño y los ADR del módulo 3](docs/Carreno_Linda_S4_Diseno.pdf).
- **Funcionalidades terminadas:**
  - Must: HU-01 consultar disponibilidad, HU-02 registrar préstamo, HU-04 registrar devolución y HU-08 no prestar uno ya prestado (también protegida con una restricción en la base de datos).
  - Should: HU-03 préstamo a un estudiante enviado por el profesor, HU-05 devolución por otra persona y HU-06 videobeams no devueltos en su jornada.
  - Could: HU-07 control del HDMI, con la tabla «HDMI por recuperar» y el botón «Marcar HDMI recuperado».
  - Historias nuevas que propuse: HU-09 identificación y celular de quien lleva el videobeam, y HU-10 préstamos de hoy con fechas y horas.
- **Pruebas:** 198 pruebas en verde con pytest, ruff sin avisos y pip-audit sin vulnerabilidades. Cobertura de la lógica del negocio (`prestamos/reglas.py` y `prestamos/registro.py`): 100 % (126 de 126 líneas). El pipeline de GitHub Actions ([pruebas.yml](.github/workflows/pruebas.yml)) corre todo esto en cada `git push`: [última ejecución en verde](https://github.com/linda-0314/Control-VideoBeam/actions/runs/46012097081/job/140549910862). Detalle en el [README](README.md) y el [registro de pruebas](registro_pruebas.md).
- **Pendientes:**
  - API en JSON de la sección 6 del diseño: ninguna historia la necesita, porque el único usuario usa las pantallas HTML.
  - Autorización para usar los datos personales (Ley 1581): hay que confirmar con la universidad cómo se pide.
  - Horarios de las jornadas: mientras se confirman, un préstamo cuenta como no devuelto si salió un día anterior.
  - La lista de los 5 videobeams está fija en `reglas.py`: si se agrega otro desde el admin, el conteo sigue diciendo «de 5».
  - Despliegue y validar todo con el bibliotecario real.

## 6. Reflexión ética y legal

| Principio | Decisión en mi proyecto | Evidencia |
|---|---|---|
| Datos personales (Ley 1581 de 2012) | Las pruebas usan datos sintéticos inventados. HU-09 guarda solo la identificación y el celular, lo mínimo para contactar a quien no devuelve, y solo los ve el bibliotecario con su sesión. La autorización queda pendiente con la universidad | [Bitácora, entradas 21 y 25](bitacora_ia.md); [revisión de seguridad, sección 5](revision_seguridad.md) |
| Sesgo | El sistema no decide nada sobre las personas, solo registra préstamos. Los datos de prueba usan nombres inventados con apellidos comunes del Huila, sin personas reales ni públicas | [Datos sintéticos](tests/datos_sinteticos.json) |
| Transparencia | Toda la ayuda de la IA está en la bitácora, también cuando generó la mayor parte del código | [Bitácora](bitacora_ia.md) |
| Responsabilidad | Nada se integró sin pytest, ruff o revisar el diff; respondo por lo que entrego porque lo verifiqué | [Bitácora, entradas 9, 19 y 22 a 27](bitacora_ia.md) |
| Propiedad intelectual y política de uso | Código generado con Claude y declarado. Dependencias con licencia libre (Django con licencia BSD). El logo de la FET se usa en una herramienta interna de la misma institución | [requirements.txt](requirements.txt); [Entrada 27](bitacora_ia.md) |

El principal dilema estuvo en el límite de confianza hacia la IA: aceptar sus respuestas por comodidad o asumir el control técnico de cada entrega. Opté por usarla como punto de partida, pero filtrando cada propuesta: evaluaba si correspondía al problema real, corregía sus fallos y validaba cada resultado antes de integrarlo. Comprendí que el verdadero valor no está en que la IA genere código rápido, sino en tener el criterio para auditarlo, corregirlo y defenderlo.

## 7. Aprendizajes

Lo que se aprendió fue un paso a paso completo sobre cómo desarrollar software con rigor y sin depender ciegamente de la IA: el proceso empezó desde lo más básico, aprendiendo a levantar entornos y validar requisitos reales antes de programar, para luego adoptar buenas prácticas como escribir pruebas primero, controlar versiones y auditar el código y los cambios manualmente antes de integrarlos; así se entendió que, aunque saber darle buenas instrucciones a la IA ayuda, nunca hay que confiar solo en que sus pruebas pasen ni dejar que haga todo el trabajo, sino usarla desde el principio como una tutora que corrija lo que uno mismo escribe para mantener el dominio total del proyecto.

## 8. Anexos

- Bitácora de uso de IA: [bitacora_ia.md](bitacora_ia.md)
- Registro de pruebas: [registro_pruebas.md](registro_pruebas.md)
- Revisión de código y seguridad: [revision_seguridad.md](revision_seguridad.md)
- README con las instrucciones de instalación: [README.md](README.md)
- Pipeline de integración continua: [.github/workflows/pruebas.yml](.github/workflows/pruebas.yml) y [ejecución en verde](https://github.com/linda-0314/Control-VideoBeam/actions/runs/46012097081/job/140549910862)
- Documentos de cada módulo:
  - [Módulo 1: propuesta (versión 2)](docs/Carreno_Linda_S1_Propuesta_v2.pdf)
  - [Módulo 2: requisitos y entrevista](docs/Carreno_Linda_S3_Requisitos.pdf)
  - [Módulo 3: diseño y ADR](docs/Carreno_Linda_S4_Diseno.pdf)
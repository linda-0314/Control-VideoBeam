# Control VideoBeam FET

Aplicación web para que el bibliotecario de la Fundación Escuela Tecnológica de Neiva (FET) registre el préstamo y la devolución de los 5 videobeams de la biblioteca (VB-01 a VB-05) y sepa al instante cuántos hay disponibles.

- Estudiante: Linda Paola Carreño Meneses
- Seminario en Inteligencia Artificial aplicada al ciclo de vida del software, FET, 2026
- Diseño (semana 4, ADR-001): aplicación web monolítica en Python con Django y SQLite, instalada en el computador de la biblioteca. Solo la usa el bibliotecario (ADR-002).

## Estructura

```
Control-VideoBeam/
├── prestamos/          # app de préstamos (ADR-001)
│   ├── __init__.py
│   └── reglas.py       # reglas del préstamo en Python puro, sin Django
├── tests/
│   └── test_reglas.py  # pruebas con pytest
├── bitacora_ia.md      # bitácora de uso de IA
├── pytest.ini
└── requirements.txt
```

Las reglas del préstamo van en `prestamos/reglas.py`, en Python puro, para poder probarlas sin base de datos ni servidor. La vista de Django de `POST /prestamos` (diseño, sección 6) las va a llamar antes de guardar y va a convertir los errores en los códigos 404 y 409.

## Funcionalidad de la semana 5

### Historia de usuario

**HU-08. No prestar uno ya prestado** (prioridad Must, necesidad N-01)

Como bibliotecario, quiero que el sistema no me deje prestar un videobeam que ya está prestado para que la disponibilidad que consulto sea real.

Criterios de aceptación:

- Escenario 1: prestar uno disponible. Dado que el VB-04 está disponible, cuando registro su préstamo, entonces el VB-04 pasa a prestado y deja de aparecer como libre.
- Escenario 2 (error): prestar uno ya prestado. Dado que el VB-01 está prestado a «Mateo Díaz», cuando intento registrar otro préstamo del VB-01, entonces el sistema no lo permite y muestra «El VB-01 ya está prestado».

### Contrato

```python
def prestar_videobeam(codigo: str, prestados: frozenset[str]) -> frozenset[str]
```

- **Qué recibe:**
  - `codigo`: el código del videobeam que se quiere prestar, por ejemplo `"VB-04"`.
  - `prestados`: los códigos de los videobeams que están prestados en este momento, es decir, los que tienen un préstamo sin devolución.
- **Qué devuelve:** un conjunto nuevo con los prestados más `codigo`. El conjunto que recibe no se modifica.
- **Errores:**
  - `VideobeamYaPrestado` con el mensaje `"El VB-01 ya está prestado"` si `codigo` ya está en `prestados`. Esto es el escenario 2 de HU-08 y en la API es el 409.
  - `VideobeamNoExiste` con el mensaje `"El VB-09 no existe"` si `codigo` no es uno de los 5 videobeams de la biblioteca. En la API es el 404.
- **Supuestos:**
  - La biblioteca tiene 5 videobeams: VB-01, VB-02, VB-03, VB-04 y VB-05.
  - El código llega exacto, como lo envía la lista del formulario: en mayúsculas y sin espacios. `"vb-02"` o `" VB-02"` se tratan como códigos que no existen.
  - `prestados` solo trae códigos válidos.
  - La función no guarda nada. Guardar el préstamo con quién lo lleva, la clase y el profesor es trabajo de la vista de Django (HU-02).
- **Casos límite:**
  - No hay ningún videobeam prestado (`prestados` vacío).
  - Primer videobeam (VB-01) y último videobeam (VB-05).
  - Se presta el último que quedaba libre: 4 prestados pasan a 5.
  - Ya están los 5 prestados: cualquier préstamo da `VideobeamYaPrestado`.

### Ejemplos de entrada y salida

| Entrada | Salida |
|---|---|
| `prestar_videobeam("VB-04", frozenset({"VB-01"}))` | `frozenset({"VB-01", "VB-04"})` |
| `prestar_videobeam("VB-02", frozenset())` | `frozenset({"VB-02"})` |
| `prestar_videobeam("VB-05", frozenset({"VB-01", "VB-02", "VB-03", "VB-04"}))` | `frozenset({"VB-01", "VB-02", "VB-03", "VB-04", "VB-05"})` |
| `prestar_videobeam("VB-01", frozenset({"VB-01"}))` | error `VideobeamYaPrestado`: «El VB-01 ya está prestado» |
| `prestar_videobeam("VB-09", frozenset())` | error `VideobeamNoExiste`: «El VB-09 no existe» |

### Cómo ejecutar las pruebas

Se necesita Python 3.10 o más reciente.

```bash
pip install -r requirements.txt
pytest
```

Con un solo comando (`pytest`) se ejecutan todas las pruebas de la carpeta `tests/`.

## Uso de IA

El registro de las sugerencias del asistente que acepté, ajusté o rechacé está en [bitacora_ia.md](bitacora_ia.md).

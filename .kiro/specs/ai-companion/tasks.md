# Plan de Implementación: AI Companion

## Visión General

Implementación incremental del AI Companion sobre la infraestructura existente (`src/ai_foundation`). Se construyen los módulos en el orden en que se necesitan: modelos de datos → memoria → personalidad → constructor de prompts → extractor → sesión → CLI. Cada grupo de tareas termina con un checkpoint para garantizar integración continua.

## Tareas

- [ ] 1. Estructura del paquete y modelos de datos
  - Crear el directorio `src/ai_companion/` con `__init__.py`
  - Crear `src/ai_companion/models.py` con los modelos Pydantic: `ImportantEvent`, `UserPreferences`, `UserProfile`, `Turn`, `UserProfileUpdate`
    - Configurar `UserProfile` con `extra="ignore"` para tolerancia a campos desconocidos (Requisito 7.3)
    - Definir la constante `MAX_HISTORY_TURNS: int = 20`
  - Crear el directorio `data/profiles/` con un `.gitkeep`
  - Agregar `[tool.hypothesis] max_examples = 100` a `pyproject.toml`
  - Agregar `src/ai_companion` al build target en `pyproject.toml`
  - _Requisitos: 1.1, 7.1, 7.2, 7.3, 7.4, 7.5_

- [ ] 2. Módulo de Memoria (persistencia de perfiles)
  - [ ] 2.1 Implementar `src/ai_companion/memory.py`
    - Implementar la clase `Memory` con `__init__(profiles_dir: Path)`
    - Implementar `load_profile(user_id: str) -> UserProfile`: carga desde `data/profiles/{user_id}.json`; si no existe o está corrupto retorna perfil vacío con logs apropiados (`WARNING` / `ERROR`)
    - Implementar `save_profile(profile: UserProfile) -> None`: serializa a JSON UTF-8 con `model_dump_json()`; crear el directorio si no existe; loguear `ERROR` en fallo de escritura sin propagar la excepción
    - _Requisitos: 1.5, 1.6, 1.7, 7.1, 7.2, 7.3, 7.5_

  - [ ]* 2.2 Escribir pruebas de ejemplo para `Memory` — `tests/test_memory.py`
    - Test: carga de perfil existente válido
    - Test: perfil no encontrado → retorna perfil vacío con `user_id` correcto
    - Test: JSON malformado → retorna perfil vacío sin lanzar excepción
    - Test: guardar y recargar produce el mismo perfil
    - _Requisitos: 1.6, 1.7, 7.1, 7.2_

  - [ ]* 2.3 Escribir prueba de propiedad 1: Ida y vuelta de serialización — `tests/test_memory.py`
    - **Propiedad 1: Ida y vuelta de serialización del perfil**
    - Para todo `UserProfile` generado por Hypothesis, `save_profile` seguido de `load_profile` SHALL producir un objeto equivalente al original
    - Usar `@given` con estrategias para `UserProfile` (strings, listas, datetimes)
    - Tag: `# Feature: ai-companion, Propiedad 1: Ida y vuelta de serialización del perfil`
    - **Valida: Requisito 7.4**

  - [ ]* 2.4 Escribir prueba de propiedad 2: Perfil vacío ante JSON inválido — `tests/test_memory.py`
    - **Propiedad 2: Perfil vacío ante JSON inválido o faltante**
    - Para cualquier `user_id` cuyo archivo no exista o tenga contenido arbitrario no-JSON, `load_profile()` SHALL retornar un `UserProfile` válido sin lanzar excepciones
    - Usar `@given(st.text())` para generar contenido de archivo arbitrario
    - Tag: `# Feature: ai-companion, Propiedad 2: Perfil vacío ante JSON inválido o faltante`
    - **Valida: Requisitos 1.7, 7.3**

- [ ] 3. Checkpoint — pruebas de memoria
  - Ejecutar `uv run pytest tests/test_memory.py -v` y asegurar que todos los tests pasen. Consultar al usuario si hay dudas antes de continuar.

- [ ] 4. Módulo de Personalidad y Constructor de Prompts
  - [ ] 4.1 Implementar `src/ai_companion/personality.py`
    - Definir la constante `COMPANION_NAME` y el system prompt base con personalidad: tono cálido, empático, humor ligero, opiniones propias, humildad ante incertidumbre
    - Implementar `get_system_prompt(profile: UserProfile) -> str`: combina el prompt base con el contexto del perfil (nombre, gustos, aversiones, intereses, eventos próximos en 3 días, tópicos discutidos)
    - Incluir lógica para mencionar eventos importantes con fecha próxima (Requisito 4.4)
    - _Requisitos: 3.1, 3.2, 3.3, 3.4, 3.5, 3.6, 4.1, 4.2, 4.4, 4.5_

  - [ ] 4.2 Implementar `src/ai_companion/prompt_builder.py`
    - Implementar `build_messages(profile: UserProfile, history: list[Turn], user_message: str) -> list[BaseMessage]`
    - Construir: `SystemMessage` desde `get_system_prompt()` + un par `HumanMessage`/`AIMessage` por cada turno del historial + `HumanMessage` con el mensaje actual
    - _Requisitos: 2.3, 4.1_

  - [ ]* 4.3 Escribir pruebas de ejemplo para `prompt_builder` — `tests/test_prompt_builder.py`
    - Test: prompt con perfil vacío → `SystemMessage` presente, sin contexto personal
    - Test: prompt con historial de N turnos → longitud de `messages` = `1 + 2*N + 1`
    - Test: prompt con evento próximo → string del evento aparece en el `SystemMessage`
    - _Requisitos: 2.3, 4.1, 4.4_

  - [ ]* 4.4 Escribir prueba de propiedad 4: El prompt incluye el historial completo — `tests/test_prompt_builder.py`
    - **Propiedad 4: El prompt incluye el historial completo de la sesión activa**
    - Para cualquier lista de turnos (0 a 20), `build_messages()` SHALL producir exactamente `1 + 2*len(history) + 1` mensajes con `HumanMessage`/`AIMessage` en orden correcto
    - Usar `@given(st.lists(st.builds(Turn, ...), max_size=20))`
    - Tag: `# Feature: ai-companion, Propiedad 4: El prompt incluye el historial completo de la sesión activa`
    - **Valida: Requisito 2.3**

- [ ] 5. Módulo Extractor de Información
  - [ ] 5.1 Implementar `src/ai_companion/extractor.py`
    - Implementar `extract_user_info(history: list[Turn], current_profile: UserProfile, llm: BaseChatModel) -> UserProfileUpdate`
    - Construir un prompt estructurado que instruya al LLM a extraer solo información sobre el usuario (nombre, gustos, aversiones, intereses, eventos) — Requisito 8.3
    - Parsear la respuesta del LLM a `UserProfileUpdate`; en caso de error retornar `UserProfileUpdate()` vacío con log `ERROR`
    - Implementar `apply_update(profile: UserProfile, update: UserProfileUpdate) -> UserProfile`
    - `apply_update` extiende listas (sin duplicados), actualiza `name` si se detectó uno nuevo, actualiza `updated_at` al timestamp actual
    - _Requisitos: 8.1, 8.2, 8.3, 8.4_

  - [ ]* 5.2 Escribir pruebas de ejemplo para `extractor` — `tests/test_extractor.py`
    - Test: historial vacío → `UserProfileUpdate` vacío
    - Test: `apply_update` no borra datos previos del perfil (likes existentes se conservan)
    - Test: `apply_update` actualiza el `name` cuando el update trae un nombre nuevo
    - Test: `apply_update` con update vacío → `updated_at` no retrocede
    - _Requisitos: 8.1, 8.2, 8.4_

  - [ ]* 5.3 Escribir prueba de propiedad 5: La extracción no corrompe el perfil — `tests/test_extractor.py`
    - **Propiedad 5: La extracción no corrompe el perfil original**
    - Para cualquier `UserProfile` y cualquier `UserProfileUpdate`, `apply_update()` SHALL preservar todos los campos preexistentes (listas solo crecen, sin eliminar entradas)
    - Usar `@given` con perfiles y updates generados por Hypothesis
    - Tag: `# Feature: ai-companion, Propiedad 5: La extracción no corrompe el perfil original`
    - **Valida: Requisito 8.2**

  - [ ]* 5.4 Escribir prueba de propiedad 6: `updated_at` avanza con cada actualización — `tests/test_extractor.py`
    - **Propiedad 6: El campo `updated_at` avanza con cada actualización**
    - Para cualquier `UserProfile` y `UserProfileUpdate` no vacío, `apply_update()` SHALL producir un `updated_at` >= al `updated_at` original
    - Tag: `# Feature: ai-companion, Propiedad 6: El campo updated_at avanza con cada actualización`
    - **Valida: Requisito 8.4**

- [ ] 6. Checkpoint — pruebas de personalidad, prompts y extractor
  - Ejecutar `uv run pytest tests/test_prompt_builder.py tests/test_extractor.py -v` y asegurar que todos los tests pasen. Consultar al usuario si hay dudas antes de continuar.

- [ ] 7. Módulo de Sesión
  - [ ] 7.1 Implementar `src/ai_companion/session.py`
    - Implementar `CompanionSession.__init__(user_id: str, memory: Memory, llm: BaseChatModel)`
    - Inicializar `history: list[Turn] = []` y cargar el perfil con `memory.load_profile(user_id)`
    - Implementar `chat(message: str) -> str`:
      - Llamar a `build_messages(profile, history, message)`
      - Invocar `llm.invoke(messages)`; capturar excepciones y retornar mensaje amigable con log `ERROR`
      - Agregar el turno al historial; si `len(history) > MAX_HISTORY_TURNS` descartar el más antiguo
      - Retornar la respuesta del Companion
    - Implementar `end_session() -> None`:
      - Llamar a `extract_user_info(history, profile, llm)`
      - Aplicar el update con `apply_update(profile, update)` y guardar con `memory.save_profile()`
      - En caso de error en extracción: loguear `ERROR` y guardar el perfil sin modificaciones
    - _Requisitos: 1.2, 1.3, 1.4, 2.1, 2.2, 2.4, 5.1, 8.1_

  - [ ]* 7.2 Escribir pruebas de ejemplo para `session` — `tests/test_session.py`
    - Test: ventana de 20 turnos exactos — el historial no supera `MAX_HISTORY_TURNS`
    - Test: turno 21 → el turno más antiguo es descartado
    - Test: flujo completo de `chat()` con LLM mockeado retorna string no vacío
    - Test: `end_session()` llama a `memory.save_profile()` una vez
    - _Requisitos: 2.1, 2.2, 2.4_

  - [ ]* 7.3 Escribir prueba de propiedad 3: Ventana deslizante del historial — `tests/test_session.py`
    - **Propiedad 3: Ventana deslizante del historial**
    - Para cualquier secuencia de N mensajes enviados (N arbitrario ≥ 0), `len(session.history)` SHALL nunca superar `MAX_HISTORY_TURNS` y SHALL contener los N más recientes si N ≤ 20
    - Usar LLM mockeado; `@given(st.lists(st.text(min_size=1), min_size=0, max_size=50))`
    - Tag: `# Feature: ai-companion, Propiedad 3: Ventana deslizante del historial`
    - **Valida: Requisito 2.2**

- [ ] 8. Interfaz de Línea de Comandos
  - [ ] 8.1 Implementar `src/ai_companion/cli.py`
    - Implementar `run_cli() -> None`:
      - Solicitar identificador de usuario al iniciar (Requisito 6.2)
      - Instanciar `Memory`, `get_llm()` y `CompanionSession`
      - Bucle de lectura de stdin: mostrar respuesta con prefijo del nombre del Companion (Requisito 6.3)
      - Detectar `/salir`, `/exit`, `/quit` → llamar a `end_session()` y salir (Requisito 6.4)
      - Capturar errores en el bucle y mostrar mensaje amigable; loguear detalles técnicos (Requisito 6.5)
    - Agregar el entry point `companion = "ai_companion.cli:run_cli"` en `pyproject.toml` bajo `[project.scripts]`
    - _Requisitos: 6.1, 6.2, 6.3, 6.4, 6.5_

  - [ ]* 8.2 Escribir pruebas de ejemplo para `cli` — `tests/test_cli.py`
    - Test: `/salir` termina el bucle y llama a `end_session()` (usando mock de `CompanionSession`)
    - Test: `/exit` y `/quit` tienen el mismo comportamiento que `/salir`
    - Test: error en `chat()` → se muestra mensaje amigable sin propagar la excepción
    - _Requisitos: 6.4, 6.5_

- [ ] 9. Integración final y wiring
  - [ ] 9.1 Conectar todos los módulos en `src/ai_companion/__init__.py`
    - Exportar `CompanionSession`, `Memory`, `run_cli` y los modelos principales
  - [ ] 9.2 Verificar que `uv run companion` lanza la CLI correctamente con el entry point configurado
    - Confirmar que `data/profiles/` se crea automáticamente si no existe
    - Confirmar que el perfil persiste correctamente entre dos ejecuciones consecutivas
    - _Requisitos: 1.5, 1.6, 6.1, 6.2, 7.5_

- [ ] 10. Checkpoint final — suite completa de tests
  - Ejecutar `uv run pytest tests/ -v --tb=short` y asegurar que todos los tests pasen.
  - Ejecutar `uv run ruff check src/ai_companion/ tests/` y corregir cualquier problema de lint.
  - Consultar al usuario si hay dudas antes de dar el feature por completo.

## Notas

- Las tareas marcadas con `*` son opcionales y pueden omitirse para un MVP más rápido.
- El LLM debe mockearse en todos los tests de propiedad para evitar llamadas a APIs externas y garantizar reproducibilidad.
- Cada test de propiedad de Hypothesis incluye el tag `# Feature: ai-companion, Propiedad N: <título>` para trazabilidad.
- Los errores de I/O (lectura/escritura de perfiles) nunca deben romper la conversación del usuario — solo loguear y continuar.
- Todos los módulos nuevos van en `src/ai_companion/`, separado de `src/ai_foundation/` que no debe modificarse.

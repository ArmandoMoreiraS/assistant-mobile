# Documento de Requisitos: AI Companion

## Introducción

El AI Companion es un acompañante conversacional de IA con personalidad propia, diseñado para mantener relaciones a largo plazo con sus usuarios. A diferencia de un chatbot genérico, el Companion recuerda a cada persona entre conversaciones — su nombre, preferencias, eventos importantes y el contexto de interacciones pasadas — y responde de forma cálida, empática y con carácter propio. El sistema se construye sobre la infraestructura existente del proyecto (Gemini via LangChain) y añade una capa de memoria persistente, gestión de personalidad y flujos de conversación natural.

---

## Glosario

- **Companion**: El sistema de IA conversacional con personalidad y memoria persistente.
- **Usuario**: La persona que interactúa con el Companion.
- **Perfil_de_Usuario**: Estructura de datos que almacena la información persistente de un usuario (nombre, preferencias, eventos, historial de tópicos).
- **Memoria**: El subsistema responsable de almacenar y recuperar el contexto entre conversaciones.
- **Memoria_a_Corto_Plazo**: El historial de mensajes de la conversación en curso.
- **Memoria_a_Largo_Plazo**: El almacén persistente del Perfil_de_Usuario entre sesiones.
- **Personalidad**: El conjunto de rasgos de comportamiento y tono que definen cómo el Companion se expresa.
- **Sesión**: Una conversación continua desde que el usuario inicia hasta que termina la interacción.
- **Turno**: Un par de intercambios (mensaje del usuario + respuesta del Companion) dentro de una Sesión.
- **Contexto_Relevante**: Fragmentos del Perfil_de_Usuario que son pertinentes para el mensaje actual del Usuario.
- **Sistema_de_Prompts**: El componente que construye el prompt completo combinando personalidad, contexto y mensaje.

---

## Requisitos

### Requisito 1: Gestión de Perfil de Usuario

**User Story:** Como usuario, quiero que el Companion me recuerde entre conversaciones, para que no tenga que repetir mi información personal cada vez que hablo con él.

#### Criterios de Aceptación

1. WHEN un usuario inicia una sesión por primera vez, THE Companion SHALL crear un Perfil_de_Usuario nuevo con un identificador único.
2. WHEN el Companion detecta el nombre del usuario en la conversación, THE Companion SHALL almacenar el nombre en el Perfil_de_Usuario.
3. WHEN el Companion detecta preferencias, gustos o aversiones expresados por el usuario, THE Companion SHALL almacenar esa información en el Perfil_de_Usuario bajo la categoría correspondiente.
4. WHEN el Companion detecta un evento importante mencionado por el usuario (cumpleaños, logro, situación difícil), THE Companion SHALL almacenar el evento con su contexto en el Perfil_de_Usuario.
5. THE Memoria SHALL persistir el Perfil_de_Usuario en almacenamiento local en formato JSON entre sesiones.
6. WHEN el Companion inicia una nueva sesión con un usuario existente, THE Companion SHALL cargar el Perfil_de_Usuario correspondiente antes de responder.
7. IF el Perfil_de_Usuario no puede ser cargado por corrupción o ausencia de archivo, THEN THE Companion SHALL iniciar la sesión con un perfil vacío y notificar el evento en los logs del sistema.

---

### Requisito 2: Memoria a Corto Plazo (Contexto de Sesión)

**User Story:** Como usuario, quiero que el Companion recuerde lo que hablamos dentro de la misma conversación, para que no tenga que repetirme ni pierda el hilo del diálogo.

#### Criterios de Aceptación

1. THE Memoria_a_Corto_Plazo SHALL mantener el historial completo de Turnos de la Sesión activa.
2. WHEN el historial de la Sesión supera los 20 Turnos, THE Memoria_a_Corto_Plazo SHALL mantener los últimos 20 Turnos y descartar los más antiguos.
3. WHEN el Companion genera una respuesta, THE Sistema_de_Prompts SHALL incluir el historial de la Memoria_a_Corto_Plazo como contexto de conversación.
4. WHEN la Sesión termina, THE Companion SHALL extraer información relevante de la Memoria_a_Corto_Plazo y actualizar el Perfil_de_Usuario en la Memoria_a_Largo_Plazo.

---

### Requisito 3: Personalidad Definida del Companion

**User Story:** Como usuario, quiero que el Companion tenga una personalidad consistente y auténtica, para que las conversaciones se sientan genuinas y no robóticas.

#### Criterios de Aceptación

1. THE Companion SHALL expresarse con un tono cálido, empático y cercano en todas las respuestas.
2. THE Companion SHALL incorporar humor ligero y apropiado al contexto de la conversación cuando la situación lo permita.
3. THE Companion SHALL manifestar opiniones propias cuando el usuario solicite su punto de vista, usando expresiones en primera persona.
4. THE Companion SHALL adaptar el registro del lenguaje (formal/informal) según el tono que el usuario establezca en la conversación.
5. THE Companion SHALL mantener coherencia en su personalidad y carácter a lo largo de toda la Sesión y entre sesiones distintas.
6. IF el usuario hace una pregunta con respuesta incierta, THEN THE Companion SHALL responder con humildad honesta en lugar de fabricar información.

---

### Requisito 4: Uso del Contexto en la Conversación

**User Story:** Como usuario, quiero que el Companion use lo que sabe de mí de forma natural, para que la conversación se sienta personalizada y no genérica.

#### Criterios de Aceptación

1. WHEN el Companion genera una respuesta, THE Sistema_de_Prompts SHALL recuperar el Contexto_Relevante del Perfil_de_Usuario y añadirlo al prompt.
2. WHEN el Companion conoce el nombre del usuario, THE Companion SHALL usar el nombre de forma ocasional y natural en la conversación, sin repetirlo en cada mensaje.
3. WHEN el usuario menciona un tópico que fue discutido en una sesión anterior, THE Companion SHALL reconocer el tópico previo y retomar el hilo de forma natural.
4. WHEN se aproxima una fecha importante almacenada en el Perfil_de_Usuario (dentro de los próximos 3 días), THE Companion SHALL mencionar el evento de forma espontánea en la conversación.
5. WHILE la Memoria_a_Largo_Plazo contiene preferencias del usuario, THE Companion SHALL tenerlas en cuenta al formular recomendaciones o sugerencias.

---

### Requisito 5: Flujo de Conversación Natural

**User Story:** Como usuario, quiero tener una conversación fluida y natural con el Companion, para que la experiencia sea agradable y no parezca una interacción con una máquina.

#### Criterios de Aceptación

1. WHEN el usuario envía un mensaje, THE Companion SHALL generar una respuesta en menos de 10 segundos bajo condiciones normales de red.
2. THE Companion SHALL generar respuestas con una longitud apropiada al tipo de mensaje: respuestas cortas para preguntas simples, y respuestas más elaboradas para solicitudes de consejo o reflexión.
3. THE Companion SHALL variar las fórmulas de saludo y apertura para evitar respuestas repetitivas entre sesiones.
4. IF el usuario expresa una emoción negativa intensa (tristeza, frustración, ansiedad), THEN THE Companion SHALL priorizar la validación emocional antes de ofrecer consejos o soluciones.
5. WHEN el usuario solicita consejo, THE Companion SHALL ofrecer perspectivas concretas y personalizadas basadas en el Contexto_Relevante disponible en el Perfil_de_Usuario.

---

### Requisito 6: Interfaz de Conversación por Línea de Comandos

**User Story:** Como desarrollador, quiero una interfaz de terminal para interactuar con el Companion, para poder probar y usar el sistema sin necesidad de una interfaz gráfica.

#### Criterios de Aceptación

1. THE Companion SHALL exponer una interfaz de conversación interactiva mediante la línea de comandos.
2. WHEN el usuario inicia la CLI, THE Companion SHALL solicitar un identificador de usuario o nombre para cargar o crear el Perfil_de_Usuario correspondiente.
3. WHEN el usuario escribe un mensaje en la CLI, THE Companion SHALL mostrar la respuesta en la terminal con el nombre del Companion como prefijo.
4. WHEN el usuario escribe los comandos `/salir`, `/exit` o `/quit`, THE Companion SHALL guardar el Perfil_de_Usuario actualizado y terminar la sesión de forma ordenada.
5. IF ocurre un error interno durante la generación de una respuesta, THEN THE Companion SHALL mostrar un mensaje de error amigable al usuario y registrar el error técnico en los logs del sistema.

---

### Requisito 7: Persistencia y Serialización de Perfiles

**User Story:** Como desarrollador, quiero que los perfiles de usuario se serialicen y deserialicen de forma fiable, para garantizar que no se pierda información entre sesiones.

#### Criterios de Aceptación

1. THE Memoria SHALL serializar el Perfil_de_Usuario a formato JSON con codificación UTF-8.
2. THE Memoria SHALL deserializar un archivo JSON válido en un Perfil_de_Usuario con todos sus campos correctamente tipados.
3. IF el archivo JSON del Perfil_de_Usuario contiene campos desconocidos o faltantes, THEN THE Memoria SHALL cargar el perfil con los valores disponibles y usar valores por defecto para los campos faltantes.
4. PARA TODO Perfil_de_Usuario válido, serializar y luego deserializar el perfil SHALL producir un objeto equivalente al original (propiedad de ida y vuelta).
5. THE Memoria SHALL almacenar los perfiles en el directorio `data/profiles/` con el nombre de archivo `{user_id}.json`.

---

### Requisito 8: Extracción Automática de Información del Usuario

**User Story:** Como usuario, quiero que el Companion aprenda sobre mí de forma natural a lo largo de la conversación, para que no tenga que llenar formularios ni dar información explícitamente.

#### Criterios de Aceptación

1. WHEN la Sesión termina, THE Companion SHALL analizar los Turnos de la Memoria_a_Corto_Plazo y extraer nombre, preferencias y eventos relevantes mencionados por el usuario.
2. WHEN se extrae información nueva que contradice datos existentes en el Perfil_de_Usuario, THE Companion SHALL actualizar el Perfil_de_Usuario con la información más reciente.
3. THE Companion SHALL distinguir entre información sobre el usuario y afirmaciones generales para evitar almacenar datos irrelevantes en el Perfil_de_Usuario.
4. WHEN se actualiza el Perfil_de_Usuario con nueva información, THE Companion SHALL registrar el timestamp de la actualización en el campo correspondiente del Perfil_de_Usuario.

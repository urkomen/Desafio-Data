# Sistema Integral de Recomendación y Descubrimiento de Eventos

## 1. ¿De qué trata el proyecto?

Esta plataforma es un sistema inteligente diseñado para transformar la manera en que las personas y las familias descubren eventos culturales en el País Vasco. En lugar de obligar al usuario a navegar por interminables listas o utilizar filtros manuales complicados, el sistema actúa como un guía local experto.

El objetivo principal es ofrecer planes culturales (como exposiciones, conciertos, teatro o rutas de senderismo) que se ajusten perfectamente a la situación y preferencias de cada usuario. Para lograrlo, la plataforma combina la información pública de eventos con inteligencia artificial, creando una experiencia de descubrimiento intuitiva, rápida y altamente personalizada.

## 2. Experiencia Doble

Para ofrecer el mejor servicio, el proyecto se ha dividido en dos grandes herramientas complementarias que el usuario puede utilizar según lo que necesite en cada momento:

### GUNI (Asistente conversacional)

* **¿Qué hace?** Guni es un asistente virtual con el que el usuario puede interactuar de forma natural. Está pensado para búsquedas rápidas e inmediatas.
* **¿Cómo funciona para el usuario?** Alguien puede simplemente escribir o decir:  *"Quiero un plan sin lluvia en Leioa"*  o "Dime eventos gratis en Bilbao a partir de las 19:00". Guni entiende la intención de la frase, busca eventos en esa ciudad, revisa automáticamente el pronóstico del tiempo en tiempo real para descartar los planes pasados por agua, y devuelve sugerencias claras con toda la información necesaria (precios, horarios, clima y descripciones).

### El Recomendador Personalizado (Búsqueda con filtros)

* **¿Qué hace?** Funciona como un consejero a largo plazo que aprende de los gustos del usuario y de su contexto familiar.
* **¿Cómo funciona para el usuario?** Si una familia tiene dos niños pequeños y un perro, el recomendador lo sabe. Cuando buscan un plan genérico, el sistema filtra opciones priorizando lugares al aire libre, con cambiadores o donde se admitan mascotas. Además, si en el pasado la familia disfrutó de ciertos museos o actividades en la naturaleza, el sistema recordará esos gustos y buscará experiencias con un ambiente similar, evitando además sugerir lugares que acaban de visitar recientemente.

## 3. El Corazón del Sistema: La Información

Ninguna recomendación inteligente sería posible sin una base sólida de información. El sistema se alimenta y organiza a través de varias fuentes:

* **Catálogo Cultural:** Se conecta a las fuentes oficiales del País Vasco para tener los eventos siempre disponibles y clasificados.
* **Contexto del Mundo Real:** Se integra con servicios meteorológicos para saber con antelación las condiciones climáticas del día y lugar del evento.
* **Perfiles y Experiencias:** Guarda información sobre los usuarios, la composición de sus familias (edades, roles, mascotas) y, lo más importante, un historial con las valoraciones de los eventos a los que ya han asistido.

## 4. Nuestro Camino: Evolución del Producto

El sistema actual es el resultado de un proceso de evolución iterativo. No se construyó todo de golpe, sino que ha ido superando distintas fases de madurez:

* **Fase Inicial (El Producto Mínimo Viable):** Todo comenzó con un concepto básico donde el sistema recibía preguntas simples y devolvía listas de eventos usando datos simulados. El objetivo era, simplemente, conectar las piezas y demostrar que la idea funcionaba.
* **La Evolución del Asistente:** El chatbot pasó por cinco versiones de desarrollo. Al principio solo daba respuestas planas (v1); luego mejoró la forma de presentar la información visualmente (v2); más adelante aprendió a consultar el clima (v3); se optimizó para responder mucho más rápido (v4); hasta llegar a la versión actual (v5), donde una inteligencia artificial traduce el lenguaje humano en búsquedas exactas dentro de la base de datos.
* **La Evolución del Recomendador:** Inicialmente, el recomendador hacía cruces de datos simples. El gran salto ocurrió cuando se le enseñó a comprender el significado "semántico" de los eventos. El sistema aprendió a equilibrar dos cosas: lo que el usuario está buscando *hoy* frente a lo que le ha gustado  *históricamente* .
* **Refinamiento del Negocio y Experiencia:** En sus etapas más recientes, la plataforma incluyó reglas de oro. Por ejemplo: aplicar penalizaciones temporales para no recomendar el mismo lugar visitado hace poco tiempo, o dar un pequeño impulso de visibilidad a los eventos promocionados (sin perder la calidad de la recomendación para el usuario).

## 5. El Presente y el Futuro

Hoy en día, el proyecto es una herramienta que procesa peticiones en apenas unos segundos, entiende múltiples idiomas y es capaz de cruzar datos climáticos, geográficos y personales de manera invisible y fluida.

De cara al futuro, el camino está marcado para seguir innovando: se planea mejorar la selección de eventossistemas colaborativos que encuentren similitudes entre diferentes usuarios ("a familias como la tuya también les gustó esto") y perfeccionar la capacidad de mantener conversaciones aún más complejas y largas con el asistente. Además, se quiere conectar el chatbot con el recomendador para que las respuestas del Chatbot pasen sean mucho más sofísticadas.

## 6. Aspectos Técnicos

Para profundizar en alguno de los aspectos técnicos del proyecto se recomienda leer los archivos de la carpeta /documentación y el README.

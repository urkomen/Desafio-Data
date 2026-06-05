# Memoria de proyecto — Recomendador inteligente de planes para familias en Euskadi

**Proyecto:** Recomendador NLP de lugares y actividades familiares en el País Vasco
**Edición:** Sprint intensivo — semana 1
**Equipos:** Data Science · Full Stack · Ciberseguridad · Marketing
**Estado:** Primera entrega funcional

---

## Índice

1. [Resumen ejecutivo](#1-resumen-ejecutivo)
2. [Contexto y motivación](#2-contexto-y-motivación)
3. [A quién va dirigido](#3-a-quién-va-dirigido)
4. [Qué hemos construido](#4-qué-hemos-construido)
5. [Cómo está estructurado el proyecto](#5-cómo-está-estructurado-el-proyecto)
6. [Cómo lo hemos hecho — fases del desarrollo](#6-cómo-lo-hemos-hecho--fases-del-desarrollo)
7. [El papel de la inteligencia artificial](#7-el-papel-de-la-inteligencia-artificial)
8. [Conclusiones](#8-conclusiones)
9. [Limitaciones actuales](#9-limitaciones-actuales)
10. [Mejoras futuras](#10-mejoras-futuras)
11. [Equipo y reparto de trabajo](#11-equipo-y-reparto-de-trabajo)

---

## 1. Resumen ejecutivo

Este proyecto nació con una pregunta sencilla: ¿por qué sigue siendo tan difícil encontrar un plan familiar para el fin de semana si vivimos rodeados de datos y tecnología?

La respuesta que hemos construido es un sistema de recomendación inteligente orientado a familias con niños pequeños en el País Vasco. A diferencia de un buscador convencional, el sistema entiende lenguaje natural —no hace falta saber qué palabras usar ni conocer los filtros correctos— y tiene en cuenta el contexto real de las familias: la edad de los niños, la accesibilidad, el tiempo, la distancia y las circunstancias del día.

En una semana de trabajo intensivo, cuatro equipos han diseñado y construido la primera versión funcional del sistema, integrando datos geográficos abiertos del Gobierno Vasco (GEO-EUSKADI) con técnicas modernas de procesamiento de lenguaje natural e inteligencia artificial.

---

## 2. Contexto y motivación

### El punto de partida

El País Vasco dispone de una infraestructura de datos geográficos abiertos de gran calidad a través de GEO-EUSKADI: lugares turísticos, espacios culturales, parques, servicios municipales y mucho más, todo georreferenciado y de acceso público. Sin embargo, estos datos permanecen en gran medida infrautilizados para el ciudadano de a pie, porque acceder a ellos requiere conocimiento técnico o navegar por interfaces poco intuitivas.

Al mismo tiempo, las familias con hijos pequeños son uno de los colectivos con mayor necesidad de planificación y menor tiempo disponible para hacerla. El coste de equivocarse —llegar a un sitio cerrado, sin cambiador, demasiado lejos o poco adecuado para un bebé— es real y frustrante.

### La oportunidad

La confluencia de tres factores hace posible este proyecto ahora y no antes: la disponibilidad de datos geográficos abiertos y estructurados, la madurez de los modelos de lenguaje para entender intenciones expresadas de forma coloquial, y las herramientas de búsqueda semántica que permiten conectar ambos mundos sin necesidad de grandes infraestructuras de computación.

No estamos construyendo tecnología especulativa. Estamos combinando piezas que ya existen de una forma que tiene sentido para un problema real.

---

## 3. A quién va dirigido

El sistema está diseñado pensando en perfiles concretos, no en usuarios abstractos. Durante el desarrollo hemos trabajado con dos personas de referencia:

**Ainhoa, 32 años, Barakaldo.** Tiene un bebé de pocos meses. Los fines de semana quiere salir a Bilbao, pero organizar cualquier plan requiere verificar una lista mental larga: ¿hay cambiador? ¿es accesible con silla? ¿hay dónde comer tranquilamente? ¿está lejos? Cuando algo falla, el día entero se complica.

**Jaime, 40 años, Getxo.** Tiene un hijo de 3 años. Le gusta que los planes tengan cierta actividad, que el niño pueda moverse y disfrutar. El problema no es la falta de opciones, sino la dificultad de evaluarlas rápidamente sin pasar media tarde investigando.

Lo que ambos comparten es la necesidad de planes sin sobresaltos, donde la información que les llega sea fiable, adaptada a su situación real y fácil de consumir. El sistema habla su idioma —literalmente— y razona como lo harían ellos.

---

## 4. Qué hemos construido

El resultado es una aplicación web con una interfaz de búsqueda en lenguaje natural conectada a un motor de recomendación inteligente y un mapa interactivo con los datos de Open data-EUSKADI.

El usuario escribe o dice algo como _"algo tranquilo mañana en Bilbao con el bebé y el niño de 3 años, que tenga dónde comer"_ y el sistema devuelve un conjunto de opciones ordenadas por relevancia, con información práctica sobre accesibilidad, distancia, horarios y por qué cada sitio encaja con lo que se ha pedido.

Lo que hace que esto sea más que un buscador convencional son tres capacidades que funcionan al mismo tiempo:

**Comprensión del lenguaje.** El sistema entiende intenciones, no palabras clave. "Algo tranquilo", "para los peques", "que no esté muy lejos" son expresiones que el sistema procesa y traduce en criterios de búsqueda concretos.

**Contexto geográfico y familiar.** La distancia desde la ubicación del usuario, la accesibilidad para sillas de paseo, la disponibilidad de zonas de cambio de pañales o menús infantiles son variables de primera clase en el sistema, no filtros opcionales.

**Diversidad de resultados.** El sistema evita devolver cinco museos cuando lo que se busca es un plan variado para el día. Los resultados están deliberadamente diversificados para ofrecer opciones complementarias, no repetidas.

---

## 5. Cómo está estructurado el proyecto

El proyecto se organiza en cuatro grandes bloques que corresponden a los cuatro equipos participantes. Cada bloque tiene una responsabilidad clara y se comunica con los demás a través de interfaces bien definidas.

### Los datos — capa de conocimiento

El equipo de Data Science construye y mantiene la base de conocimiento del sistema: los datos de lugares extraídos de Open data-EUSKADI, enriquecidos con atributos familiares que no existen en la fuente original (si hay cambiador, si es ruidoso, si es accesible con silla) y transformados en representaciones que la IA puede utilizar para buscar y comparar.

Esta capa es el fundamento de todo. Sin datos limpios, enriquecidos y actualizados, el sistema más sofisticado produce resultados inútiles.

### La inteligencia — motor de recomendación

También responsabilidad de Data Science, el motor de recomendación es el núcleo inteligente del sistema. Toma la pregunta del usuario, entiende qué está buscando realmente, busca entre los candidatos disponibles y los ordena según su relevancia para esa situación concreta.

Este motor combina tres tipos de razonamiento: semántico (¿este lugar se parece a lo que se está buscando?), geográfico (¿está a una distancia razonable?) y contextual (¿encaja con el perfil familiar del momento?).

### La plataforma — backend y frontend

El equipo de Full Stack construye la infraestructura que hace accesible toda esa inteligencia: una API que conecta el motor de recomendación con el mundo exterior, y una interfaz web que lo hace usable para Ainhoa y Jaime sin necesidad de conocimientos técnicos.

La interfaz incluye un campo de búsqueda en lenguaje libre, tarjetas de resultado con la información relevante y un mapa interactivo construido sobre las capas geográficas de GEO-EUSKADI.

### La confianza — seguridad y privacidad

El equipo de Ciberseguridad garantiza que el sistema funciona de forma segura: que las comunicaciones están cifradas, que los datos de los usuarios se tratan con respeto a la privacidad, que el acceso está controlado y que el sistema cumple con la normativa europea de protección de datos (GDPR).

En un sistema que recibe la ubicación del usuario y el perfil de su familia, la confianza no es un añadido opcional: es una condición para que el producto exista.

### La propuesta de valor — marketing y experiencia

El equipo de Marketing da forma al "para qué" de todo lo anterior: cómo se presenta el sistema, qué lenguaje usa, cómo se comunica el valor para Ainhoa y Jaime, y cómo se mide si efectivamente les está ayudando. También definen la taxonomía de los resultados —las categorías, los filtros, los textos de justificación— que el resto de equipos implementa.

---

## 6. Cómo lo hemos hecho — fases del desarrollo

El proyecto se ha desarrollado en una semana de trabajo intensivo organizada en cinco fases solapadas, no secuenciales.

### Fase 1 — Definición y diseño ~~(días 1-2)~~

Antes de escribir código, el equipo dedicó tiempo a entender el problema. Se definieron los perfiles de usuario (Ainhoa y Jaime), se exploró el catálogo de datos de Open data-EUSKADI para entender qué había disponible y qué faltaba, y se acordó la arquitectura general del sistema y los contratos entre equipos.

Esta fase es más valiosa de lo que parece. El mayor riesgo en un proyecto de una semana no es no terminar el código: es terminar el código equivocado.

### Fase 2 — Datos y conocimiento ~~(días 2-3)~~

Con la dirección clara, el equipo de Data Science se volcó en construir la base de datos del sistema. Se extrajeron los datos de Open-data-EUSKADI, se normalizaron y limpiaron, y se realizó el trabajo más artesanal y crítico del proyecto: enriquecer cada lugar con los atributos familiares que GEO-EUSKADI no proporciona.

¿Cómo sabe el sistema que un lugar tiene cambiador? ¿O que es accesible con silla? Parte de esa información se infiere de las descripciones existentes mediante reglas y modelos de lenguaje; parte requirió criterio humano. Esta capa de enriquecimiento es uno de los mayores diferenciadores del sistema respecto a cualquier alternativa existente.

***Datos utilizados: v1 ficticios, v2 reales, v3 mezcla de ficticios+reales***


### Fase 3 — Construcción del motor ~~(días 3-4)~~

Con los datos listos, el equipo construyó el motor de recomendación. Esto incluyó transformar cada lugar en una representación matemática que capture su significado (los embeddings), diseñar el sistema de puntuación que combina similitud semántica con distancia geográfica y relevancia familiar, y crear el módulo de comprensión de lenguaje natural que traduce una frase coloquial en criterios de búsqueda concretos.

***BBDD: v1 datos ficitcios, v2 datos reales***

En paralelo, el equipo de Full Stack construyó el backend y comenzó la integración con la capa de datos.

### Fase 4 — Integración y experiencia ~~(días 4-5)~~

Los cuatro equipos convergieron para conectar sus piezas. El motor de recomendación se expuso como una API que el backend consume; el frontend se conectó al backend; el mapa se integró con las capas geográficas de GEO-EUSKADI; el equipo de Ciberseguridad configuró la autenticación y los controles de acceso.

Esta fase es siempre más costosa de lo que parece en papel. Las interfaces entre equipos son donde viven los malentendidos, los formatos incompatibles y los supuestos no declarados. Haber dedicado tiempo a los acuerdos en la fase 1 amortiguó estos problemas.

### Fase 5 — Prueba y ajuste ~~(días 5-6)~~

La última fase consistió en probar el sistema con escenarios reales: queries del tipo que haría Ainhoa o Jaime, situaciones límite (bebés en lugares ruidosos, lluvia, zonas con pocos resultados) y verificación de que la seguridad y la privacidad funcionan como se diseñaron.

Los ajustes en esta fase no son correcciones de errores en el sentido técnico: son calibraciones de la inteligencia del sistema. ¿Los resultados son suficientemente variados? ¿Penaliza bien la distancia? ¿Entiende correctamente las queries en euskera? Estas preguntas no tienen respuesta binaria, solo mejora continua.

---

## 7. El papel de la inteligencia artificial

La IA no es el objetivo de este proyecto: es el instrumento que hace posible algo que sin ella sería imposible o muy inferior.

Hay tres lugares donde la inteligencia artificial hace un trabajo que ningún sistema de reglas podría replicar con la misma calidad:

**Comprensión de lenguaje.** Entender que "algo tranquilo para los peques" y "actividad familiar sin mucho ruido" son la misma necesidad expresada de formas distintas requiere un modelo que haya aprendido el significado del lenguaje, no uno que compare palabras. Los modelos de lenguaje grandes (LLM) son hoy la herramienta más efectiva para esto.

**Representación semántica.** Cada lugar del catálogo se transforma en un vector numérico —una especie de huella digital de su significado— que permite comparar lugares entre sí y con las queries de los usuarios de forma mucho más rica que una búsqueda por palabras clave. Esta técnica, llamada embeddings, es lo que permite que el sistema encuentre un lugar "tranquilo y familiar" aunque esas palabras exactas no aparezcan en su descripción.

**Recomendación contextual.** El sistema no devuelve simplemente los lugares más relevantes en abstracto: los reordena según el contexto del momento. Un mismo conjunto de candidatos se presenta de forma diferente si es sábado por la mañana con lluvia que si es domingo soleado, si hay un bebé de meses o un niño de tres años, si el usuario está en Getxo o en Barakaldo.

Lo que hace que este uso de la IA sea técnicamente interesante —y no un juguete— es la combinación de estas tres capas en un sistema híbrido que ninguna de ellas podría sostener sola.

---

## 8. Conclusiones

### Lo que hemos demostrado

En una semana de trabajo con equipos y recursos portátiles normales, es posible construir un sistema de recomendación inteligente funcional sobre datos geográficos reales. No un prototipo de laboratorio, sino un sistema que responde a queries en lenguaje natural, integra datos de una fuente pública oficial y devuelve resultados útiles para el perfil de usuario definido.

Esto es posible en 2026 porque las herramientas han madurado hasta el punto en que el esfuerzo se concentra en el problema —entender al usuario, enriquecer los datos, calibrar la relevancia— y no en la infraestructura.

### Lo que hemos aprendido

**Los datos son la capa más difícil.** El motor de IA es la parte más visible e impresionante del sistema, pero el trabajo más crítico y más laborioso ha sido el enriquecimiento de datos: añadir a cada lugar los atributos familiares que ninguna fuente proporciona de forma estructurada. Sin esa capa, la IA más sofisticada produce resultados genéricos.

**El diseño del problema importa más que la elección de tecnología.** Definir bien quién es el usuario, qué necesita y cómo lo expresa ha guiado todas las decisiones técnicas posteriores. Proyectos similares fracasan no por limitaciones técnicas, sino por construir la solución correcta para el usuario equivocado.

**La integración entre equipos es un problema de diseño, no solo de coordinación.** Los momentos más costosos de la semana han sido las fricciones entre capas: formatos de datos que no coincidían, supuestos no declarados sobre cómo funcionaría cada pieza. Invertir en contratos explícitos entre equipos al principio —aunque parezca burocrático— es siempre rentable.

**La privacidad no es un trámite.** Un sistema que recibe la ubicación y el perfil familiar de un usuario tiene una responsabilidad real. Diseñarla desde el primer día, en lugar de añadirla al final, ha condicionado decisiones de arquitectura que de otro modo habrían sido difíciles de cambiar.

---

## 9. Limitaciones actuales

La primera versión del sistema es funcional pero tiene límites conocidos que conviene nombrar con honestidad.

El catálogo de lugares en esta versión cubre una muestra representativa de Bilbao y su entorno inmediato, no el conjunto completo del País Vasco. GEO-EUSKADI es una fuente excelente para espacios públicos, turismo y cultura, pero no indexa toda la hostelería ni el comercio local, lo que ha requerido complementar con otras fuentes.

El sistema no tiene memoria entre sesiones. Cada búsqueda es independiente: el sistema no aprende de las preferencias pasadas del usuario ni mejora con el uso. Esto es una decisión de diseño para la primera versión, compatible con la privacidad, pero limita la personalización.

La información de horarios y disponibilidad en tiempo real no está integrada. El sistema puede recomendar un lugar que el día de la consulta está cerrado por obras o por festivo. Esto requiere integración con fuentes de datos en tiempo real que quedan fuera del alcance del sprint.

*************************************REPASAR***********************
El soporte del euskera, aunque presente gracias al modelo de embeddings multilingüe utilizado, no está optimizado para el dominio turístico local. Queries muy coloquiales en euskera pueden obtener resultados algo menos precisos que sus equivalentes en castellano.

---

## 10. Mejoras futuras

Las mejoras identificadas se organizan en tres horizontes según su complejidad y valor esperado.

### A corto plazo — siguientes dos sprints

Ampliar el catálogo de lugares a todo el territorio de la Comunidad Autónoma Vasca, incorporando más capas de GEO-EUSKADI y completando la cobertura de hostelería con fuentes complementarias. Es la mejora con mayor impacto inmediato sobre la utilidad del sistema para Ainhoa y Jaime.

Integrar información de horarios verificada en tiempo real, conectando con Google Places u otras fuentes, para eliminar el riesgo de recomendar lugares cerrados. Esta mejora tiene un impacto directo en la confianza del usuario.

Añadir fotos de los lugares en las tarjetas de resultado. Es un detalle aparentemente menor con un impacto grande en la experiencia de uso: ver el aspecto de un parque o un museo ayuda a tomar la decisión mucho más que cualquier descripción textual.

### A medio plazo — dos a cuatro meses

Incorporar historial de preferencias del usuario, de forma anónima y con consentimiento explícito, para personalizar los resultados según sus patrones de uso previos. Un usuario que siempre elige espacios al aire libre debería verlos mejor posicionados sin tener que pedirlo.

Diseñar un mecanismo de feedback explícito —una valoración simple después de la visita— que permita al sistema aprender de la experiencia real de los usuarios y mejorar la calibración de los resultados con el tiempo. Este es el paso que convierte un sistema estático en uno que evoluciona.

Desarrollar una versión específica para el modelo de embeddings ajustada al dominio turístico en euskera, para equiparar la calidad de resultados independientemente del idioma de la query.

### A largo plazo — visión de producto

Extender el sistema más allá de la recomendación puntual hacia la planificación de un día completo: dado un perfil familiar y una mañana libre, sugerir un itinerario coherente con tiempos, distancias y descansos. Esto requiere modelar la secuencia de actividades, no solo la relevancia individual de cada una.

Abrir el sistema como plataforma para que otros municipios y comunidades autónomas puedan conectar sus propios catálogos de datos geográficos, con el mismo motor de inteligencia aplicado a contextos locales distintos.

---

## 11. Equipo y reparto de trabajo

Este proyecto ha sido posible gracias a la colaboración de cuatro equipos con responsabilidades complementarias.

| Equipo                   | Contribución principal                                                                                                                                   |
| ------------------------ | --------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Data Science**   | Extracción y enriquecimiento de datos Open-data-EUSKADI, motor de embeddings y búsqueda semántica, diseño del sistema de recomendación, API de datos |
| **Full Stack**     | Backend de la aplicación, integración del motor DS, interfaz web, mapa interactivo con capas GEO-EUSKADI                                                |
| **Ciberseguridad** | Autenticación y autorización, cifrado de comunicaciones, cumplimiento GDPR, gestión de secretos                                                        |
| **Marketing**      | Definición de personas y propuesta de valor, taxonomía de categorías y resultados, textos de interfaz, métricas de éxito                             |

---

*Memoria elaborada al cierre del sprint inicial. Sujeta a revisión en función de los resultados de las primeras pruebas con usuarios reales.*

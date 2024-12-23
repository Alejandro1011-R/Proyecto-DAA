# Proyecto - Diseño y Análisis de Algoritmos

## Título del Proyecto
**Optimización de Cronograma de Rodaje para un Programa de Televisión o Película**

### Descripción
Este proyecto se enfoca en la planificación y gestión integral de todos los recursos necesarios para rodar un programa de televisión o una película de manera eficiente y ajustada al presupuesto. Para lograrlo, se consideran múltiples factores que suelen complicar la producción:

• Disponibilidad de actores: Cada actor o actriz tiene un horario limitado que puede solaparse con otras actividades o producciones, por lo que la asignación de escenas debe coincidir con su presencia.
• Restricciones de localizaciones: Muchas locaciones están disponibles solo ciertos días o requieren permisos especiales, lo que obliga a programar secuencias específicas durante ese margen.
• Continuidad narrativa: Algunas escenas deben rodarse antes que otras para mantener la coherencia de la trama; esto implica respetar un orden parcial en la grabación.
• Equipo técnico especializado: Operadores de cámara, ingenieros de sonido, departamento de arte y demás personal técnico también tienen agendas y límites en sus horas de trabajo.
• Presupuesto fijo: A menudo, los gastos totales no pueden superar un monto predeterminado, por lo que cualquier cambio en la planificación debe considerar su efecto sobre el costo final.

La meta principal es minimizar el tiempo total requerido para completar el rodaje y evitar sobrecostos, todo ello manteniendo la calidad de la producción y cumpliendo con los plazos de entrega pactados. Para abordar estos retos, se pueden proponer distintos enfoques, como la aplicación de técnicas de programación dinámica, metodologías de divide y vencerás que segmenten el problema en episodios o actos, o algoritmos codiciosos que prioricen la filmación de escenas con mayor complejidad y valor de producción. Cada enfoque tendrá sus fortalezas y limitaciones, pero todos deben lidiar con la complejidad combinatoria que nace de la gran cantidad de restricciones interconectadas.

Este problema es de gran importancia práctica en el ámbito audiovisual, ya que la correcta organización de recursos humanos y técnicos puede ahorrar miles de dólares al evitar retrasos o cambios de última hora. Además, garantizar que todos los elementos necesarios (actores, locaciones, equipo) estén disponibles en el momento oportuno reduce la probabilidad de rehacer escenas o duplicar esfuerzos. Por otra parte, la industria audiovisual trabaja a menudo bajo calendarios muy ajustados, por lo que toda mejora en la eficiencia del programa de rodaje se traduce en grabaciones más ágiles y un mayor cumplimiento de las fechas de entrega.

Desde un punto de vista computacional, el problema es muy desafiante debido a la gran variedad de restricciones entrelazadas: dependencias entre escenas, limitaciones de recursos, coordinación de agendas y sumas de costos. Esto lo sitúa dentro del ámbito de los problemas complejos (muchos de ellos NP-difíciles), en los que buscar la solución óptima puede resultar prohibitivo en términos de tiempo cuando el número de actores, escenas y localizaciones crece. Por este motivo, resultan atractivas aproximaciones basadas en heurísticas o algoritmos parciales, así como el uso de diversas técnicas (programación dinámica, codiciosa, etc.) para balancear la complejidad de la planificación y obtener soluciones razonables en la práctica.
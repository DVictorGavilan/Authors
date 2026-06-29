# Resumen del uso de IA

Durante el desarrollo de esta prueba se ha utilizado IA como herramienta de apoyo para razonar sobre arquitectura, diseño del pipeline, estrategia de matching, reglas de calidad, testing y documentación.

La IA se ha usado como asistente técnico, no como sustituto de la toma de decisiones. Las decisiones finales sobre alcance, estructura, simplificación, implementación y entrega han sido revisadas y seleccionadas manualmente.

No se han compartido claves, tokens, credenciales ni información sensible.

## Temas discutidos

### Arquitectura

Se valoró una arquitectura Medallion, pero se descartó porque el volumen y alcance de la prueba no justificaban capas Bronze/Silver/Gold persistentes. Se decidió implementar un pipeline ETL ligero, modular y fácil de ejecutar localmente.

También se descartó usar Spark, Airflow, Docker y frameworks externos de calidad de datos para evitar sobreingeniería. La solución final se mantuvo deliberadamente simple.

### Matching de autores

Se identificó que el problema no era únicamente consultar una API externa, sino resolver posibles variantes, nombres incompletos, errores tipográficos y candidatos ambiguos.

Se decidió usar una estrategia de matching explicable basada en:

* normalización de nombres;
* similitud textual con `SequenceMatcher`;
* `work_count` como señal secundaria;
* `score_gap` entre el mejor y segundo mejor candidato;
* niveles de confianza.

La decisión final fue enriquecer únicamente autores clasificados como `high_confidence`.

### Calidad de datos

Se decidió centralizar las reglas de calidad en un módulo propio `quality.py`, manteniendo el código simple y sin introducir herramientas como Great Expectations o Pandera.

Las reglas de calidad se dividieron conceptualmente entre reglas críticas y reglas no críticas. También se decidió generar reportes tabulares en CSV dentro de `data/reports/`.

### Testing

Se usó de apoyo para añadir tests unitarios simples con `pytest` y `assertpy`, separados por módulo, para ganar confianza en las piezas principales del pipeline sin sobredimensionar la prueba.

### CI/CD

Se usó de apoyo para añadir un workflow básico de GitHub Actions para ejecutar automáticamente los tests unitarios y validar la cobertura mínima del proyecto.

### Documentación

Se usó de apoyo para documentar el proyecto de forma clara, concisa y profesional.

Se preparó una estructura de README con objetivo, arquitectura, decisiones técnicas, matching, data quality, ejecución, tests, limitaciones y uso de IA.

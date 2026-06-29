# Changelog

All notable changes to this project are documented in this file.

## [0.1.0] - 2026-06-28

### Added

* Pipeline inicial de enriquecimiento de autores.
* Lector de input CSV para nombres de autores en bruto.
* Normalización y eliminación de duplicados de nombres de autores.
* Cliente de Open Library para búsqueda de autores y consulta de detalles.
* Estrategia de matching ligera basada en:
  * similitud del nombre normalizado
  * `work_count` como señal secundaria
  * `score_gap` entre el mejor y el segundo mejor candidato.
* Clasificación de confianza con:
  * `high_confidence`
  * `medium_confidence`
  * `low_confidence`
  * `ambiguous`
  * `not_found`
* Quality gate para consultar detalles solo en autores con alta confianza.
* Generación de output en CSV.
* Generación de output en SQLite.
* Reglas de calidad para validaciones de input y output.
* Configuración de logging.
* Tests unitarios con `pytest` y `assertpy`.
* Documentación del proyecto en `README.md`.
* Arquitectura mantenida intencionadamente ligera, descartando arquitectura Medallion, Airflow, Spark y frameworks externos de calidad de datos.
# Base de Datos de Autores

Pipeline ETL ligero para construir una base de datos enriquecida de autores a partir de un fichero CSV semilla.

El proyecto parte de una lista de nombres de autores, busca candidatos en Open Library, selecciona el match más probable, enriquece solo los casos con suficiente confianza y genera una salida reproducible en CSV y SQLite.

For any bugs or questions, please contact [Dani Gavilán](mailto:danigavipedro96@gmail.com).

---

## 🚀 Objetivo

Dado un fichero `authors_seed.csv` con una columna `author_name`, el pipeline genera una base de datos enriquecida con información pública de autores. Las base de datos contiene la siguiente información:


El fichero de entrada debe llamarse, por defecto:

```text
data/input/authors_seed.csv
```

Y debe tener esta estructura:

```csv
author_name
Jane Austen
Gabriel García Márquez
...
```

El pipeline genera dos salidas:

```text
data/output/authors_enriched.csv
data/output/authors_enriched.db
```

Columnas principales del output:

| Columna               | Descripción                                         |
|-----------------------|-----------------------------------------------------|
| `input_author_name`   | Nombre original leído del input                     |
| `openlibrary_key`     | Identificador del autor en Open Library             |
| `matched_author_name` | Nombre del candidato seleccionado                   |
| `match_score`         | Puntuación final del match                          |
| `score_gap`           | Diferencia entre el mejor y segundo mejor candidato |
| `candidate_count`     | Número de candidatos encontrados                    |
| `confidence_level`    | Nivel de confianza asignado                         |
| `enrichment_status`   | Estado del enriquecimiento                          |
| `birth_date`          | Fecha de nacimiento                                 |
| `death_date`          | Fecha de fallecimiento                              |
| `bio`                 | Biografía limpia en una sola línea                  |
| `source`              | Fuente de datos utilizada                           |

---

## ⚙️ Cómo ejecutar el proyecto

### Crear entorno virtual

En Linux:
```bash
python -m venv .venv
source .venv/bin/activate
```

En Windows:

```bash
python -m venv .venv
.venv\Scripts\activate
```

### Instalar dependencias

```bash
pip install -r requirements.txt
```

### Ejecutar el pipeline

```bash
python main.py
```

### Ejecutar tests

El proyecto incluye tests unitarios las distintas funciones codificadas

```bash
python -m pytest --cov=src --cov-fail-under=95 -q
```

---

## 📂 Estructura del proyecto

```text
├── ai-usage/
│   └── summary.md
├── config/
│   ├── settings.json
│   └── log_configuration.json
├── data/
│   ├── input/
│   │   └── authors_seed.csv
│   └── output/
│   │   ├── authors_enriched.csv
│   │   └── authors_enriched.db
│   └── reports/
│       ├── quality_columns.csv
│       ├── quality_table_input.csv
│       └── quality_table_output.csv
├── logs/
│   └── pipeline.log
├── src/
│   ├── extract.py
│   ├── load.py
│   ├── openlibrary.py
│   ├── quality.py
│   ├── transform.py
│   └── utils_matching.py
├── tests/
│   ├── test_extract.py
│   ├── test_load.py
│   ├── test_openlibrary.py
│   ├── test_quality.py
│   ├── test_transform.py
│   └── test_utils_matching.py
├── main.py
├── .gitignore
├── pytest.ini
├── requirements.txt
├── CHANGELOG.md
└── README.md
```

---

## ▶️ Flujo del pipeline

El pipeline sigue un flujo ETL simple:

```text
Lectura del fichero input
   ↓
Data Quality sobre el fichero input
   ↓
Enriquecimiento de la información
   ↓
Data Quality sobre el fichero output
   ↓
Almacenamiento en CSV + SQLite
```

---

## 🌟 Data Quality

Las reglas de calidad están centralizadas en `src/quality.py`.

Se han separado conceptualmente en reglas críticas y reglas informativas/de dominio. Las reglas críticas pueden detener la ejecución si el pipeline no puede continuar de forma segura. Las reglas no críticas no bloquean el proceso, pero se reportan como métricas para facilitar la revisión del resultado.

| Regla                        | Capa   | Tipo       | Acción                                                         |
|------------------------------|--------|------------|----------------------------------------------------------------|
| Input file exists            | Input  | Crítica    | Detiene el pipeline si el fichero no existe                    |
| Input file not empty         | Input  | Crítica    | Detiene el pipeline si el fichero está vacío                   |
| Column `author_name` exists  | Input  | Crítica    | Detiene el pipeline si falta la columna requerida              |
| Author name empty            | Input  | No crítica | Cuenta autores vacíos; no se procesan                          |
| Duplicated normalized author | Input  | No crítica | Cuenta duplicados tras normalización; se procesa una única vez |
| Output CSV exists            | Output | Crítica    | Valida que el fichero CSV final se ha generado                 |
| Output DB exists             | Output | Crítica    | Valida que la base de datos SQLite final se ha generado        |
| Birth date missing           | Output | No crítica | Cuenta autores enriquecidos sin fecha de nacimiento            |
| Death date missing           | Output | No crítica | Cuenta autores enriquecidos sin fecha de fallecimiento         |
| Bio missing                  | Output | No crítica | Cuenta autores enriquecidos sin biografía                      |

Además del dataset enriquecido, el pipeline genera reportes de calidad en formato CSV dentro de la carpeta de reporting. Estos reportes permiten revisar la calidad del fichero input, la tabla output y la calidad de las columnas principales del output.

| Reporte                           | Descripción                                                                                                                                  |
|-----------------------------------|----------------------------------------------------------------------------------------------------------------------------------------------|
| `quality_table_input.csv`         | Resume la calidad del fichero de entrada: número total de filas, autores vacíos, duplicados normalizados y autores únicos válidos procesados |
| `quality_table_output.csv`        | Resume la distribución de registros por tipo de match: `high_confidence`, `medium_confidence`, `low_confidence`, `ambiguous` y `not_found`   |
| `quality_columns.csv`             | Resume la calidad por columna, indicando regla aplicada, registros que pasan, registros que fallan, porcentaje de superación y severidad     |

Los campos `birth_date`, `death_date` y `bio` solo se evalúan sobre autores enriquecidos. Los registros clasificados como `ambiguous`, `not_found` o `skipped` no se penalizan por no tener información enriquecida.

Por último, aplicamos un diseño de calidad asociada al dato por lo que se puede leer directamente la tabla output y filtrar por los registros KO (`ambiguous`, `not_found` o `skipped`).

---

## 🧠 Decisiones técnicas

### Por qué no se usa una arquitectura Medallion

Se ha descartado una arquitectura formal tipo Bronze/Silver/Gold porque el alcance de la prueba es pequeño y el volumen de datos esperado es bajo.

Una arquitectura Medallion tendría sentido si el proyecto necesitara, por ejemplo:

* almacenamiento histórico
* reprocesamiento incremental
* capas intermedias persistentes

En este caso, añadir esas capas habría introducido más complejidad de la necesaria. La solución elegida mantiene una estructura ETL clara, pero sin sobredimensionar el diseño.

---

### Reto detectado: matching de entidades / NLP ligero
#### Problemática identificada

El input contiene únicamente nombres de autores. Esto introduce un problema típico de procesamiento de lenguaje natural y resolución de entidades:

* nombres escritos con o sin acentos
* iniciales con puntos o sin puntos
* variantes del mismo autor
* nombres incompletos
* múltiples candidatos devueltos por la API

Ejemplos:

```text
J. K. Rowling
j k rowling
Gabriel García Márquez
Gabriel Marquez
Cervantes
```

El reto no consiste solo en buscar texto, sino en decidir si un candidato externo representa realmente al autor del input.

#### Solución de matching elegida

La estrategia de matching se basa en:

1. Normalización del nombre.
2. Similaridad textual usando `SequenceMatcher`.
3. Uso de `work_count` (obras asociadas al autor) como señal secundaria para desempatar candidatos.
4. Cálculo de `score_gap` entre el mejor y segundo mejor candidato para añadir confianza al match detectado.
5. Clasificación del resultado en niveles de confianza.

La puntuación final de cada candidato se calcula así:

```text
final_score = name_score * 0.90 + work_count_score * 0.10
```

Donde:

```text
name_score = similitud entre el nombre de entrada y el nombre candidato
work_count_score = work_count / (work_count + 100)
```

La razón de esta ponderación es que el nombre debe ser la señal principal, mientras que `work_count` solo debe ayudar a desempatar entre candidatos parecidos.

Además del `final_score`, el pipeline calcula:

```text
score_gap = best_score - second_best_score
```

Este valor es relevante porque permite detectar ambigüedad. Un candidato puede tener una puntuación alta, pero si el segundo candidato tiene una puntuación muy similar, el match no es suficientemente claro.

Por ejemplo:

```text
best_score = 0.91
second_best_score = 0.90
score_gap = 0.01
```

Aunque el mejor candidato tenga buen score, la diferencia es demasiado pequeña. En ese caso, el pipeline clasifica el resultado como `ambiguous` y evita enriquecerlo automáticamente.

Esto reduce el riesgo de seleccionar un autor incorrecto en casos con muchos candidatos parecidos, nombres incompletos o nombres comunes.

---

### Niveles de confianza

El pipeline clasifica cada match en uno de estos niveles:

| Nivel               | Condición                                  | Significado                                                                               |
|---------------------|--------------------------------------------|-------------------------------------------------------------------------------------------|
| `not_found`         | `candidate_count == 0`                     | No se encontraron candidatos en Open Library                                              |
| `ambiguous`         | `candidate_count > 1` y `score_gap < 0.05` | Hay varios candidatos demasiado cercanos, por lo que el match no es suficientemente claro |
| `high_confidence`   | `final_score >= 0.90` y `score_gap > 0.05` | Match suficientemente fiable para enriquecer                                              |
| `medium_confidence` | `0.80 <= final_score < 0.90`               | Match razonable, pero no enriquecido en esta versión                                      |
| `low_confidence`    | `final_score < 0.80`                       | Match débil                                                                               |

Actualmente, solo se enriquecen automáticamente los autores clasificados como:

```text
confidence_level == "high_confidence"
```


---

### Por qué no se usa Spark, Airflow ni frameworks de Data Quality

No se ha usado Spark porque el volumen de datos no lo justifica. El procesamiento es local, pequeño y principalmente dependiente de llamadas HTTP.

No se ha usado Airflow porque la prueba requiere un proceso reproducible, pero no necesariamente una orquestación productiva. El código está organizado de forma que podría orquestarse fácilmente en el futuro con tareas como:

```text
validate_input → run_pipeline → validate_outputs
```

No se ha usado Great Expectations, Pandera u otra librería de calidad de datos porque las reglas son pocas y específicas del dominio. Un módulo propio `quality.py` mantiene el proyecto simple, testeable y fácil de entender.

---

## 🔜 Posibles mejoras futuras

Si el proyecto creciera en volumen o criticidad, las siguientes mejoras serían razonables:

1. Añadir cache local para búsquedas y detalles de autores.
2. Implementar retries con backoff para llamadas HTTP.
3. Añadir rate limiting para ser respetuosos con la API pública.
4. Guardar candidatos intermedios para auditoría.
5. Escribir resultados por batches.
6. Añadir checkpoints para poder reanudar ejecuciones largas.
7. Orquestar el pipeline con Airflow.
8. Migrar reglas de calidad a Pandera o Great Expectations si aumentan en complejidad.
9. Evaluar embeddings o modelos NLP si hubiera muchos alias, errores tipográficos o nombres incompletos.

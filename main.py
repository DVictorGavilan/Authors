import essentialkit
import logging.config

from src import extract, transform, load, quality
from pathlib import Path
from src.openlibrary import OpenLibraryClient


logger = logging.getLogger(__name__)


DEFAULT_SETTINGS_PATH = "config/settings.json"
SETTINGS = essentialkit.files.read_json(Path(DEFAULT_SETTINGS_PATH))


def setup_logging() -> None:
    Path("logs").mkdir(exist_ok=True)
    config_logging = essentialkit.files.read_json(Path(SETTINGS["paths"]["log_config"]))
    logging.config.dictConfig(config_logging)


def run_pipeline(input_path: str, output_csv_path: str, output_db_path: str, reports_path: str) -> None:
    setup_logging()

    logger.info("Starting author enrichment pipeline")

    quality.validate_input_file(input_path)
    logging.info("Validated input file: %s", input_path)

    raw_authors = extract.load_author_names(Path(input_path))
    authors = extract.get_unique_valid_authors(raw_authors)
    logging.info("Loaded %s unique authors", len(authors))

    input_table_quality = quality.input_table_rules(raw_authors, authors)
    load.write_csv(input_table_quality, Path(f"{reports_path}/quality_table_input.csv"))
    logger.info("Input quality summary: %s", {q["Metric"]: q["Value"] for q in input_table_quality})
    logger.info("CSV generated: input table quality summary")

    openlibrary = OpenLibraryClient()

    rows = [transform.enrich_author(author_name, openlibrary) for author_name in authors]

    load.write_csv(rows, Path(output_csv_path))
    logging.info("CSV generated: %s", output_csv_path)
    load.write_sqlite_db(rows, Path(output_db_path))
    logging.info("SQLite DB generated: %s", output_db_path)
    quality.validate_output_files(output_csv_path=output_csv_path, output_db_path=output_db_path)

    output_table_quality = quality.output_table_rules(rows)
    load.write_csv(output_table_quality, Path(f"{reports_path}/quality_table_output.csv"))
    logger.info("Output quality summary: %s", [{q["match_category"]: q["percentage"]} for q in output_table_quality])
    logger.info("CSV generated table quality summary")

    output_columns_quality = quality.output_columns_rules(rows=rows)
    load.write_csv(output_columns_quality, Path(f"{reports_path}/quality_columns.csv"))
    logger.info("Output quality summary: %s", {q["column"]: q["pass_rate"] for q in output_columns_quality})
    logger.info("CSV generated columns quality summary")

    logger.info("Pipeline finished successfully")


def main() -> None:

    run_pipeline(
        input_path=SETTINGS["paths"]["input_csv"],
        output_csv_path=SETTINGS["paths"]["output_csv"],
        output_db_path=SETTINGS["paths"]["output_db"],
        reports_path=SETTINGS["paths"]["reports"]
    )


if __name__ == '__main__':
    main()

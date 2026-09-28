
import argparse
import json
import os

from pyspark.sql import SparkSession

from dataflow_pipeline.source import load_source
from dataflow_pipeline.target import write_target
from dataflow_pipeline.transformations import (
    apply_transformations,
)


def create_spark_session() -> SparkSession:

    return (
        SparkSession.builder
        .appName(
            "DataflowPipeline"
        )
        .getOrCreate()
    )


def load_manifest(
    path: str,
) -> dict:

    with open(
        path,
        "r",
        encoding="utf-8",
    ) as file:

        return json.load(file)


def run(
    manifest: dict,
) -> None:

    spark = create_spark_session()

    try:

        source = manifest["source"]

        target = manifest["target"]

        transformations = manifest.get(
            "transformations",
            [],
        )

        # -----------------------------------------
        # SOURCE
        # -----------------------------------------

        dataframe = load_source(
            spark=spark,
            source=source,
        )

        # -----------------------------------------
        # TRANSFORMATIONS
        # -----------------------------------------

        dataframe = apply_transformations(
            dataframe=dataframe,
            transformations=transformations,
        )

        # -----------------------------------------
        # TARGET
        # -----------------------------------------

        write_target(
            dataframe=dataframe,
            target=target,
        )

    finally:

        spark.stop()


def main():

    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--manifest",
        required=True,
    )

    args = parser.parse_args()

    manifest = load_manifest(
        args.manifest
    )

    run(manifest)


if __name__ == "__main__":
    main()


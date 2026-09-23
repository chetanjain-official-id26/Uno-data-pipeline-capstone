import argparse
import json
import os

from pyspark.sql import SparkSession

from dataflow_pipeline.source import SourceLoader
from dataflow_pipeline.target import TargetWriter
from dataflow_pipeline.transform import TransformationExecutor


def load_config():

    config_json = os.environ.get(
        "DATAFLOW_PIPELINE_CONFIG"
    )

    if not config_json:
        raise RuntimeError(
            "DATAFLOW_PIPELINE_CONFIG is not set"
        )

    return json.loads(config_json)


def create_spark():

    return (
        SparkSession.builder
        .appName("DataFlowPipeline")
        .getOrCreate()
    )


def run_pipeline():

    config = load_config()

    spark = create_spark()

    try:

        source = config["source"]
        transformations = config["transformations"]
        target = config["target"]

        source_loader = SourceLoader()

        source_df = source_loader.load(
            spark=spark,
            jdbc_url=source["jdbc_url"],
            username=source["username"],
            password=source["password"],
            source_table=source["table"],
        )

        transformer = TransformationExecutor()

        result_df = transformer.execute(
            spark=spark,
            source_df=source_df,
            transformations=transformations,
        )

        writer = TargetWriter()

        rows_written = writer.write(
            df=result_df,
            jdbc_url=target["jdbc_url"],
            username=target["username"],
            password=target["password"],
            target_table=target["table"],
            write_mode=target["write_mode"],
        )

        print(
            f"Pipeline completed successfully. "
            f"Rows written: {rows_written}"
        )

        return rows_written

    finally:

        spark.stop()


def main():

    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--run-id",
        required=True,
    )

    args = parser.parse_args()

    print(
        f"Starting DataFlow pipeline run: "
        f"{args.run_id}"
    )

    run_pipeline()


if __name__ == "__main__":
    main()
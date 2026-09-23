import shutil
import subprocess
import tempfile
from pathlib import Path


class WheelBuilder:

    def __init__(
        self,
        runtime_directory: str,
    ):
        self.runtime_directory = Path(
            runtime_directory
        )

    def build(self) -> Path:

        if not self.runtime_directory.exists():
            raise RuntimeError(
                "Pipeline runtime directory does not exist"
            )

        output_directory = Path(
            tempfile.mkdtemp(
                prefix="dataflow-wheel-"
            )
        )

        try:

            subprocess.run(
                [
                    "python",
                    "-m",
                    "build",
                    "--wheel",
                    "--outdir",
                    str(output_directory),
                ],
                cwd=self.runtime_directory,
                check=True,
                capture_output=True,
                text=True,
            )

            wheels = list(
                output_directory.glob("*.whl")
            )

            if len(wheels) != 1:
                raise RuntimeError(
                    "Expected exactly one wheel artifact"
                )

            final_path = (
                output_directory / wheels[0].name
            )

            return final_path

        except subprocess.CalledProcessError as exc:

            raise RuntimeError(
                f"Wheel build failed: {exc.stderr}"
            ) from exc
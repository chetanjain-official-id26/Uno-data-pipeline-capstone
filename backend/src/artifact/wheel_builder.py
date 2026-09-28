import shutil
import subprocess
import sys
from pathlib import Path


class WheelBuilder:
    """Build the pipeline runtime Python wheel."""

    def __init__(
        self,
        runtime_directory: str = "pipeline_runtime",
    ) -> None:
        self.runtime_directory = Path(
            runtime_directory
        )

    def build(self) -> Path:
        if not self.runtime_directory.exists():
            raise RuntimeError(
                "Pipeline runtime directory does not exist"
            )

        if not self.runtime_directory.is_dir():
            raise RuntimeError(
                "Pipeline runtime path is not a directory"
            )

        dist_directory = (
            self.runtime_directory / "dist"
        )

        if dist_directory.exists():
            shutil.rmtree(
                dist_directory
            )

        dist_directory.mkdir(
            parents=True,
            exist_ok=True,
        )

        try:
            subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "pip",
                    "wheel",
                    ".",
                    "--no-deps",
                    "--wheel-dir",
                    str(dist_directory),
                ],
                cwd=self.runtime_directory,
                check=True,
                capture_output=True,
                text=True,
            )

        except subprocess.CalledProcessError as exc:
            raise RuntimeError(
                "Failed to build pipeline runtime wheel: "
                f"{exc.stderr.strip()}"
            ) from exc

        wheels = list(
            dist_directory.glob("*.whl")
        )

        if not wheels:
            raise RuntimeError(
                "Wheel build completed but no wheel was produced"
            )

        if len(wheels) > 1:
            raise RuntimeError(
                "Wheel build produced multiple wheels; "
                "expected exactly one"
            )

        return wheels[0]
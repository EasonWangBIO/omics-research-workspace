import subprocess
from pathlib import Path


def run_deseq2(
    count_path: Path,
    metadata_path: Path,
    reference_group: str,
    comparison_group: str,
    output_dir: Path,
) -> tuple[Path, str]:
    """Run the DESeq2 R script and return its result file and log."""

    project_root = Path(__file__).resolve().parents[2]
    script_path = project_root / "scripts" / "run_deseq2.R"

    count_path = count_path.resolve()
    metadata_path = metadata_path.resolve()
    output_dir = output_dir.resolve()

    output_dir.mkdir(
        parents=True,
        exist_ok=True,
    )

    command = [
        "Rscript",
        str(script_path),
        str(count_path),
        str(metadata_path),
        reference_group,
        comparison_group,
        str(output_dir),
    ]

    try:
        completed = subprocess.run(
            command,
            cwd=project_root,
            check=True,
            capture_output=True,
            text=True,
        )
    except subprocess.CalledProcessError as error:
        parts = [error.stdout, error.stderr]
        log = "\n".join(part for part in parts if part)

        raise RuntimeError(f"DESeq2 analysis failed.\n{log}") from error

    result_path = output_dir / (f"deseq2_{comparison_group}_vs_{reference_group}.csv")

    if not result_path.exists():
        raise FileNotFoundError(f"DESeq2 result file was not created: {result_path}")

    parts = [completed.stdout, completed.stderr]
    log = "\n".join(part for part in parts if part)

    return result_path, log

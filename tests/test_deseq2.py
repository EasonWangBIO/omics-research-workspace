import subprocess
from pathlib import Path

import pytest

from omics_workspace.deseq2 import run_deseq2


def test_run_deseq2_returns_result_and_log(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    count_path = tmp_path / "counts.tsv"
    metadata_path = tmp_path / "metadata.csv"
    output_dir = tmp_path / "results"

    count_path.write_text("gene_id\tsample_1\ngene_1\t10\n")
    metadata_path.write_text("sample_id,group\nsample_1,control\n")

    def fake_run(
        command: list[str],
        **_: object,
    ) -> subprocess.CompletedProcess[str]:
        result_path = output_dir / "deseq2_treatment_vs_control.csv"
        result_path.write_text("gene_id,padj\ngene_1,0.01\n")

        return subprocess.CompletedProcess(
            command,
            returncode=0,
            stdout="analysis complete",
            stderr="model log",
        )

    monkeypatch.setattr(
        "omics_workspace.deseq2.subprocess.run",
        fake_run,
    )

    result_path, log = run_deseq2(
        count_path=count_path,
        metadata_path=metadata_path,
        reference_group="control",
        comparison_group="treatment",
        output_dir=output_dir,
    )

    assert result_path.exists()
    assert result_path.name == "deseq2_treatment_vs_control.csv"
    assert "analysis complete" in log
    assert "model log" in log


def test_run_deseq2_reports_r_failure(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    count_path = tmp_path / "counts.tsv"
    metadata_path = tmp_path / "metadata.csv"

    count_path.touch()
    metadata_path.touch()

    def fake_run(
        command: list[str],
        **_: object,
    ) -> subprocess.CompletedProcess[str]:
        raise subprocess.CalledProcessError(
            returncode=1,
            cmd=command,
            output="",
            stderr="R validation failed",
        )

    monkeypatch.setattr(
        "omics_workspace.deseq2.subprocess.run",
        fake_run,
    )

    with pytest.raises(RuntimeError, match="R validation failed"):
        run_deseq2(
            count_path=count_path,
            metadata_path=metadata_path,
            reference_group="control",
            comparison_group="treatment",
            output_dir=tmp_path / "results",
        )

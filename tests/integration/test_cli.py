"""
Integration tests for the Avatar CLI subcommands and exit codes.
"""

from pathlib import Path
from click.testing import CliRunner
from avatar_system.cli import cli


def test_cli_validate_success(tmp_path: Path):
    """Verifies that `avatar validate` returns exit code 0 for a valid YAML."""
    valid_yaml = tmp_path / "valid.yaml"
    valid_yaml.write_text(
        """
        avatar_id: "cli_test_01"
        age_band: "adult"
        presentation: "casual"
        skin_tone: "fair"
        hair: "black"
        hair_style: "short"
        attire: "shirt"
        background: "studio"
        aspect_ratio: "1:1"
        seed: 1234
        """,
        encoding="utf-8",
    )

    runner = CliRunner()
    result = runner.invoke(cli, ["validate", "--spec", str(valid_yaml)])
    assert result.exit_code == 0
    assert "[PASS]" in result.output


def test_cli_validate_failure(tmp_path: Path):
    """Verifies that `avatar validate` returns non-zero exit code for invalid schema."""
    invalid_yaml = tmp_path / "invalid.yaml"
    invalid_yaml.write_text(
        """
        avatar_id: "invalid_01"
        age_band: "adult"
        # missing skin_tone, hair, attire
        """,
        encoding="utf-8",
    )

    runner = CliRunner()
    result = runner.invoke(cli, ["validate", "--spec", str(invalid_yaml)])
    assert result.exit_code != 0


def test_cli_safety_check_refusal(tmp_path: Path):
    """Verifies that `avatar safety-check` flags unsafe celebrity requests with exit code 3."""
    unsafe_yaml = tmp_path / "unsafe.yaml"
    unsafe_yaml.write_text(
        """
        avatar_id: "unsafe_elon"
        age_band: "adult"
        presentation: "professional"
        skin_tone: "fair"
        hair: "brown"
        hair_style: "short"
        attire: "suit"
        background: "studio"
        cultural_context: "Elon Musk portrait"
        """,
        encoding="utf-8",
    )

    runner = CliRunner()
    result = runner.invoke(cli, ["safety-check", "--spec", str(unsafe_yaml)])
    assert result.exit_code == 3
    assert "[REFUSAL]" in result.output


def test_cli_prepare_and_run_mock(tmp_path: Path):
    """Verifies end-to-end CLI workflow: prepare -> run (mock) -> inspect-manifest."""
    spec_yaml = tmp_path / "avatar.yaml"
    spec_yaml.write_text(
        """
        avatar_id: "flow_test_01"
        age_band: "adult"
        presentation: "professional"
        skin_tone: "medium_warm"
        hair: "black"
        hair_style: "fade"
        attire: "suit"
        background: "studio"
        seed: 9999
        """,
        encoding="utf-8",
    )

    job_out = tmp_path / "jobs"
    runner = CliRunner()

    # Step 1: Prepare
    res_prep = runner.invoke(cli, ["prepare", "--spec", str(spec_yaml), "--out", str(job_out), "--route", "mock_runner"])
    assert res_prep.exit_code == 0
    job_folder = job_out / "job_flow_test_01_9999"
    assert job_folder.exists()

    # Step 2: Run
    out_dir = tmp_path / "outputs"
    res_run = runner.invoke(cli, ["run", "--job", str(job_folder), "--route", "mock_runner", "--output-dir", str(out_dir)])
    assert res_run.exit_code == 0
    assert (out_dir / "flow_test_01_9999.png").exists()

    # Step 3: Inspect Manifest
    manifest_path = out_dir / "flow_test_01_9999_manifest.json"
    res_inspect = runner.invoke(cli, ["inspect-manifest", "--path", str(manifest_path)])
    assert res_inspect.exit_code == 0
    assert "PASSED" in res_inspect.output

    # Step 4: Evaluate Folder
    res_eval = runner.invoke(cli, ["evaluate", "--results", str(out_dir)])
    assert res_eval.exit_code == 0
    assert "Batch Evaluation Results" in res_eval.output

    # Step 5: Ingest from output folder
    ingest_dir = tmp_path / "ingested"
    res_ingest = runner.invoke(cli, ["ingest", "--results", str(out_dir), "--target-dir", str(ingest_dir)])
    assert res_ingest.exit_code == 0
    assert "VALID" in res_ingest.output


def test_cli_benchmark_and_clean(tmp_path: Path):
    """Verifies that `avatar benchmark` and `avatar clean` run smoothly."""
    runner = CliRunner()
    res_bench = runner.invoke(cli, ["benchmark"])
    assert res_bench.exit_code == 0
    assert "Benchmark Performance Summary" in res_bench.output

    res_clean = runner.invoke(cli, ["clean"])
    assert res_clean.exit_code == 0

"""
Unified Command-Line Interface (CLI) for the Human Avatar System.
Provides rich terminal formatting, informative exit codes, and comprehensive subcommands.
"""

import json
from pathlib import Path
import sys
from typing import Optional
import zipfile

# Ensure UTF-8 output on Windows consoles if supported
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

import click
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
import yaml

from avatar_system import __version__
from avatar_system.benchmark import BenchmarkRunner
from avatar_system.config import SystemConfig, default_config
from avatar_system.evaluation import EvaluationEngine
from avatar_system.exceptions import (
    AvatarSystemError,
    ConfigurationError,
    JobExecutionError,
    OutputCorruptedError,
    ProvenanceError,
    SafetyRefusalError,
    ValidationError,
)
from avatar_system.job_manager import JobManager
from avatar_system.provenance import ProvenanceManager
from avatar_system.routing import ExecutionRouter
from avatar_system.safety import SafetyEngine
from avatar_system.schemas import AvatarSpec, ProvenanceManifest
from avatar_system.validator import OutputValidator

console = Console(safe_box=True, highlight=False)


def load_specs_from_file(spec_path: Path) -> list[AvatarSpec]:
    """Helper to parse one or more AvatarSpec instances from a YAML/JSON file."""
    if not spec_path.exists():
        raise ValidationError(f"Specification file not found: {spec_path}")

    with open(spec_path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)

    specs = []
    if isinstance(data, list):
        for idx, item in enumerate(data):
            try:
                specs.append(AvatarSpec.model_validate(item))
            except Exception as e:
                raise ValidationError(f"Error parsing item #{idx+1} in {spec_path}: {e}")
    elif isinstance(data, dict):
        if "avatars" in data and isinstance(data["avatars"], list):
            for idx, item in enumerate(data["avatars"]):
                try:
                    specs.append(AvatarSpec.model_validate(item))
                except Exception as e:
                    raise ValidationError(f"Error parsing avatar #{idx+1} in {spec_path}: {e}")
        else:
            try:
                specs.append(AvatarSpec.model_validate(data))
            except Exception as e:
                raise ValidationError(f"Error parsing spec in {spec_path}: {e}")
    else:
        raise ValidationError(f"Invalid format in {spec_path}. Expected dict or list of dicts.")

    return specs


@click.group()
@click.version_option(version=__version__, prog_name="avatar")
def cli():
    """Open-Source AI Human-Avatar Generation Orchestration System."""
    pass


@cli.command("validate")
@click.option("--spec", "-s", required=True, type=click.Path(exists=True, path_type=Path), help="Path to avatar specification file (.yaml or .json).")
def validate_cmd(spec: Path):
    """Validates an avatar specification against the schema."""
    try:
        specs = load_specs_from_file(spec)
        console.print(f"[bold green][PASS][/bold green] Successfully validated [bold]{len(specs)}[/bold] avatar specification(s) in `{spec.name}`.")
        
        table = Table(title=f"Avatar Specifications Summary: {spec.name}", show_header=True, header_style="bold cyan")
        table.add_column("Avatar ID", style="cyan")
        table.add_column("Age Band")
        table.add_column("Skin Tone")
        table.add_column("Hair Style")
        table.add_column("Attire")
        table.add_column("Aspect Ratio")
        table.add_column("Seed")

        for s in specs:
            table.add_row(
                s.avatar_id,
                s.age_band,
                s.skin_tone,
                f"{s.hair} {s.hair_style}",
                s.attire,
                s.aspect_ratio,
                str(s.seed) if s.seed is not None else "auto",
            )
        console.print(table)
    except ValidationError as e:
        console.print(f"[bold red]Validation Error:[/bold red] {e}")
        sys.exit(e.exit_code)
    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {e}")
        sys.exit(1)


@cli.command("safety-check")
@click.option("--spec", "-s", required=True, type=click.Path(exists=True, path_type=Path), help="Path to avatar specification file.")
def safety_check_cmd(spec: Path):
    """Evaluates safety policies, likeness checks, and reference consent status."""
    try:
        specs = load_specs_from_file(spec)
        engine = SafetyEngine()
        all_safe = True

        for s in specs:
            res = engine.evaluate_spec(s)
            if res.is_safe:
                console.print(f"[bold green][PASS][/bold green] Avatar '[cyan]{s.avatar_id}[/cyan]' passed safety checks.")
            else:
                all_safe = False
                console.print(f"[bold red][REFUSAL][/bold red] Avatar '[cyan]{s.avatar_id}[/cyan]' violated safety policies:")
                for reason in res.refusal_reasons:
                    console.print(f"  - [red]{reason}[/red]")

        if not all_safe:
            sys.exit(3)
    except ValidationError as e:
        console.print(f"[bold red]Validation Error:[/bold red] {e}")
        sys.exit(e.exit_code)


@cli.command("prepare")
@click.option("--spec", "-s", required=True, type=click.Path(exists=True, path_type=Path), help="Path to avatar specification file.")
@click.option("--out", "-o", type=click.Path(path_type=Path), default=None, help="Target directory for job bundles.")
@click.option("--model", default=None, help="HuggingFace model repository name.")
@click.option("--revision", default=None, help="Pinned model commit/revision.")
@click.option("--route", default="kaggle_accelerator", type=click.Choice(["kaggle_accelerator", "local_cpu", "local_gpu", "mock_runner"]))
def prepare_cmd(spec: Path, out: Optional[Path], model: Optional[str], revision: Optional[str], route: str):
    """Prepares portable job bundles with deterministic seeds and prompts."""
    try:
        specs = load_specs_from_file(spec)
        mgr = JobManager()
        created_bundles = []

        for s in specs:
            bundle = mgr.prepare_job(
                spec=s,
                model_repo=model,
                model_revision=revision,
                route=route,
            )
            job_path = mgr.write_job_bundle(bundle, target_dir=out / bundle.job_id if out else None)
            created_bundles.append(job_path)
            console.print(f"[bold green][PASS][/bold green] Prepared portable job bundle: [cyan]{job_path.name}[/cyan] (Seed: [yellow]{bundle.seed}[/yellow])")

        console.print(f"\n[bold green]Ready:[/bold green] Created [bold]{len(created_bundles)}[/bold] job bundle(s).")
    except SafetyRefusalError as e:
        console.print(f"[bold red]Safety Refusal:[/bold red] {e}")
        sys.exit(e.exit_code)
    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {e}")
        sys.exit(1)


@cli.command("run")
@click.option("--job", "-j", required=True, type=click.Path(exists=True, path_type=Path), help="Path to job bundle folder.")
@click.option("--route", type=click.Choice(["local_cpu", "local_gpu", "mock_runner"]), default="mock_runner", help="Local execution backend.")
@click.option("--output-dir", type=click.Path(path_type=Path), default=None, help="Output destination folder.")
def run_cmd(job: Path, route: str, output_dir: Optional[Path]):
    """Executes a prepared job bundle locally (mock or local PyTorch engine)."""
    try:
        mgr = JobManager()
        router = ExecutionRouter()
        bundle = mgr.load_job_bundle(job)

        console.print(f"Executing job '[cyan]{bundle.job_id}[/cyan]' via route '[magenta]{route}[/magenta]'...")
        manifest = router.execute_job(bundle, route=route, output_dir=output_dir)

        console.print(f"[bold green][COMPLETE][/bold green] Generated output for avatar '[cyan]{manifest.avatar_id}[/cyan]'.")
        console.print(f"  - Output Image: [cyan]{manifest.output_filename}[/cyan]")
        console.print(f"  - SHA256: [yellow]{manifest.image_sha256}[/yellow]")
    except AvatarSystemError as e:
        console.print(f"[bold red]Execution Error:[/bold red] {e}")
        sys.exit(e.exit_code)
    except Exception as e:
        console.print(f"[bold red]Unexpected Error:[/bold red] {e}")
        sys.exit(1)


@cli.command("ingest")
@click.option("--results", "-r", required=True, type=click.Path(exists=True, path_type=Path), help="Path to results directory or results.zip from Kaggle.")
@click.option("--target-dir", type=click.Path(path_type=Path), default=None, help="Local directory to ingest into.")
def ingest_cmd(results: Path, target_dir: Optional[Path]):
    """Ingests generated outputs and manifests from Kaggle or local execution."""
    dest = target_dir or default_config.output_dir
    dest.mkdir(parents=True, exist_ok=True)

    if results.is_file() and results.suffix.lower() == ".zip":
        console.print(f"Extracting zip archive: [cyan]{results}[/cyan] -> [cyan]{dest}[/cyan]...")
        with zipfile.ZipFile(results, "r") as zf:
            zf.extractall(dest)
        scan_dir = dest
    elif results.is_dir():
        scan_dir = results
    else:
        console.print(f"[bold red]Error:[/bold red] '{results}' is neither a valid directory nor a ZIP archive.")
        sys.exit(1)

    # Scan and validate all manifests
    manifest_files = list(scan_dir.glob("*_manifest.json")) + list(scan_dir.glob("manifest*.json"))
    console.print(f"Found [bold]{len(manifest_files)}[/bold] manifest(s) to ingest and validate.")

    table = Table(title="Ingested Outputs Validation", show_header=True, header_style="bold magenta")
    table.add_column("Avatar ID", style="cyan")
    table.add_column("Seed")
    table.add_column("Image File")
    table.add_column("Status")
    table.add_column("Integrity / Hash Match")

    all_valid = True
    for mf in manifest_files:
        val = OutputValidator.validate_manifest_and_image(mf)
        try:
            m = ProvenanceManager.load_manifest(mf)
            status_str = "[green]VALID[/green]" if val.is_valid else "[red]INVALID[/red]"
            hash_str = "[green]MATCH[/green]" if val.manifest_verified else f"[red]{'; '.join(val.errors)}[/red]"
            table.add_row(m.avatar_id, str(m.seed), m.output_filename or "N/A", status_str, hash_str)
            if not val.is_valid:
                all_valid = False
        except Exception as e:
            table.add_row(mf.name, "N/A", "N/A", "[red]CORRUPT[/red]", str(e))
            all_valid = False

    console.print(table)
    if not all_valid:
        console.print("[bold yellow]Warning:[/bold yellow] One or more ingested outputs had validation errors.")


@cli.command("evaluate")
@click.option("--results", "-r", required=True, type=click.Path(exists=True, path_type=Path), help="Directory containing manifests and images.")
def evaluate_cmd(results: Path):
    """Computes adherence, diversity, and validation metrics across an output folder."""
    manifest_files = list(results.glob("*_manifest.json")) + list(results.glob("manifest*.json"))
    if not manifest_files:
        console.print(f"[bold yellow]No manifest files found in {results}.[/bold yellow]")
        sys.exit(1)

    manifests = []
    adherence_records = []

    for mf in manifest_files:
        try:
            m = ProvenanceManager.load_manifest(mf)
            manifests.append(m)
            adh = EvaluationEngine.evaluate_prompt_adherence(m)
            adherence_records.append(adh)
        except Exception:
            pass

    diversity = EvaluationEngine.evaluate_batch_diversity(manifests)
    avg_adh = sum(a["adherence_score"] for a in adherence_records) / len(adherence_records) if adherence_records else 0.0

    panel_content = (
        f"[bold]Total Avatars Evaluated:[/bold] {len(manifests)}\n"
        f"[bold]Mean Prompt Adherence:[/bold] {avg_adh * 100:.1f}%\n"
        f"[bold]Overall Batch Diversity Score:[/bold] {diversity['overall_diversity_score'] * 100:.1f}%\n"
        f"  - Unique Skin Tones: {diversity['unique_skin_tones_count']}\n"
        f"  - Unique Age Bands: {diversity['unique_age_bands_count']}\n"
        f"  - Unique Hairstyles: {diversity['unique_hairstyles_count']}\n"
        f"  - Unique Presentations: {diversity['unique_presentations_count']}\n"
        f"  - Unique Backgrounds: {diversity['unique_backgrounds_count']}"
    )
    console.print(Panel(panel_content, title="[bold cyan]Batch Evaluation Results[/bold cyan]", expand=False))


@cli.command("benchmark")
@click.option("--matrix", "-m", type=click.Path(exists=True, path_type=Path), default=None, help="Path to test matrix YAML file.")
def benchmark_cmd(matrix: Optional[Path]):
    """Executes automated benchmark measuring latency, memory, and throughput."""
    console.print("[bold]Running automated benchmark suite...[/bold]")
    runner = BenchmarkRunner()
    results = runner.run_benchmark(specs_file=matrix, use_mock_runner=True, save_results=True)

    lat = results["latency_metrics"]
    mem = results["memory_metrics"]
    eval_m = results["evaluation_metrics"]

    table = Table(title="Benchmark Performance Summary", show_header=True, header_style="bold green")
    table.add_column("Metric Category", style="cyan")
    table.add_column("Measurement", style="white")

    table.add_row("Total Specs Processed", str(results["total_specs_evaluated"]))
    table.add_row("Successful Jobs", f"{results['successful_jobs']} / {results['total_specs_evaluated']} ({results['job_success_rate']*100:.1f}%)")
    table.add_row("Wall Clock Duration", f"{results['total_wall_clock_time_sec']:.2f} s")
    table.add_row("Avg Job Preparation", f"{lat['avg_job_preparation_ms']:.2f} ms")
    table.add_row("Avg Execution (Mock/Synthetic)", f"{lat['avg_execution_ms']:.2f} ms")
    table.add_row("Avg Validation & Provenance", f"{lat['avg_validation_ms']:.2f} ms")
    table.add_row("Throughput", f"{lat['throughput_jobs_per_sec']:.1f} jobs/sec")
    table.add_row("Peak Process RAM", f"{mem['peak_process_ram_mb']:.1f} MB (Total System: {mem['system_total_ram_gb']} GB)")
    table.add_row("Mean Prompt Adherence", f"{eval_m['mean_prompt_adherence']*100:.1f}%")
    table.add_row("Batch Diversity Score", f"{eval_m['batch_diversity_score']*100:.1f}%")

    console.print(table)
    console.print(f"\n[bold green]Saved Benchmark Evidence:[/bold green] `evidence/benchmarks/benchmark_results.json`")


@cli.command("inspect-manifest")
@click.option("--path", "-p", required=True, type=click.Path(exists=True, path_type=Path), help="Path to manifest JSON file.")
def inspect_manifest_cmd(path: Path):
    """Displays formatted details of a provenance manifest and verifies integrity."""
    try:
        manifest = ProvenanceManager.load_manifest(path)
        val = OutputValidator.validate_manifest_and_image(path)

        console.print(Panel(
            f"[bold]Manifest ID:[/bold] {manifest.manifest_id}\n"
            f"[bold]Job ID:[/bold] {manifest.job_id}\n"
            f"[bold]Avatar ID:[/bold] {manifest.avatar_id}\n"
            f"[bold]Deterministic Seed:[/bold] {manifest.seed}\n"
            f"[bold]Model Repo:[/bold] {manifest.model_name} (Rev: {manifest.model_revision})\n"
            f"[bold]Image Resolution:[/bold] {manifest.image_width}x{manifest.image_height} ({manifest.aspect_ratio})\n"
            f"[bold]Image SHA256:[/bold] {manifest.image_sha256 or 'N/A'}\n"
            f"[bold]Synthetic Media Declared:[/bold] {manifest.synthetic_media} ('{manifest.synthetic_label}')\n"
            f"[bold]Compute Route:[/bold] {manifest.compute_route}\n"
            f"[bold]Timestamp (UTC):[/bold] {manifest.timestamp_utc}\n"
            f"[bold]Integrity Verification:[/bold] {'[green]PASSED[/green]' if val.is_valid else '[red]FAILED (' + '; '.join(val.errors) + ')[/red]'}",
            title=f"[bold cyan]Provenance Manifest: {path.name}[/bold cyan]",
            expand=False,
        ))
    except Exception as e:
        console.print(f"[bold red]Error loading manifest:[/bold red] {e}")
        sys.exit(1)


@cli.command("test")
def test_cmd():
    """Runs the pytest automated test suite."""
    import subprocess
    console.print("[bold]Running automated test suite via pytest...[/bold]")
    ret = subprocess.run([sys.executable, "-m", "pytest", "tests/", "-v"], cwd=str(default_config.project_root))
    sys.exit(ret.returncode)


@cli.command("clean")
def clean_cmd():
    """Cleans temporary test jobs and intermediate caches."""
    import shutil
    cfg = default_config
    cleaned = 0
    for d in [cfg.job_dir]:
        if d.exists():
            for item in d.iterdir():
                if item.is_dir() and item.name.startswith("job_"):
                    shutil.rmtree(item)
                    cleaned += 1
    console.print(f"[bold green][PASS][/bold green] Cleaned {cleaned} temporary job directories.")


if __name__ == "__main__":
    cli()

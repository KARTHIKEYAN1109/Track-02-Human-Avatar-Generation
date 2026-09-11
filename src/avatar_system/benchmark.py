"""
Benchmarking engine for the Human Avatar System.
Measures orchestration throughput, validation speed, memory utilization, and adherence metrics.
"""

from datetime import datetime, timezone
import json
from pathlib import Path
import time
from typing import Any, Dict, List, Optional
import psutil
import yaml

from avatar_system.config import SystemConfig, default_config
from avatar_system.evaluation import EvaluationEngine
from avatar_system.job_manager import JobManager
from avatar_system.routing import ExecutionRouter
from avatar_system.schemas import AvatarSpec, ProvenanceManifest
from avatar_system.validator import OutputValidator


class BenchmarkRunner:
    """Executes systematic benchmarks on avatar specification datasets."""

    def __init__(self, config: Optional[SystemConfig] = None):
        self.config = config or default_config
        self.job_manager = JobManager(config=self.config)
        self.router = ExecutionRouter(config=self.config)

    def run_benchmark(
        self,
        specs_file: Optional[Path] = None,
        use_mock_runner: bool = True,
        save_results: bool = True,
    ) -> Dict[str, Any]:
        """
        Runs complete benchmark suite across a matrix of avatar specifications.
        """
        self.config.ensure_directories()
        start_wall_time = time.time()
        process = psutil.Process()
        initial_mem_mb = process.memory_info().rss / (1024 * 1024)

        target_file = specs_file or (self.config.config_dir / "baseline_avatars.yaml")
        if not target_file.exists():
            target_file = self.config.config_dir / "example_avatar.yaml"
        if not target_file.exists():
            global_baseline = default_config.config_dir / "baseline_avatars.yaml"
            if global_baseline.exists():
                target_file = global_baseline
            else:
                target_file = default_config.config_dir / "example_avatar.yaml"

        specs: List[AvatarSpec] = []
        if target_file.exists():
            with open(target_file, "r", encoding="utf-8") as f:
                raw_data = yaml.safe_load(f)

            if isinstance(raw_data, list):
                for item in raw_data:
                    specs.append(AvatarSpec.model_validate(item))
            elif isinstance(raw_data, dict):
                if "avatars" in raw_data:
                    for item in raw_data["avatars"]:
                        specs.append(AvatarSpec.model_validate(item))
                else:
                    specs.append(AvatarSpec.model_validate(raw_data))

        if not specs:
            # Fallback baseline spec if no file present
            specs = [
                AvatarSpec(
                    avatar_id="benchmark_sample_01",
                    age_band="adult",
                    presentation="professional",
                    skin_tone="medium_warm",
                    hair="dark_brown",
                    hair_style="short_fade",
                    attire="business_casual",
                    background="neutral_studio",
                    aspect_ratio="1:1",
                    seed=111111,
                )
            ]

        prep_durations = []
        exec_durations = []
        val_durations = []
        manifests: List[ProvenanceManifest] = []
        adherence_results = []
        successful_count = 0
        failed_count = 0

        route = "mock_runner" if use_mock_runner else "local_cpu"

        for spec in specs:
            try:
                # 1. Job Preparation Benchmark
                t0 = time.time()
                bundle = self.job_manager.prepare_job(spec, route=route)
                self.job_manager.write_job_bundle(bundle)
                prep_time = time.time() - t0
                prep_durations.append(prep_time)

                # 2. Execution Benchmark
                t1 = time.time()
                manifest = self.router.execute_job(bundle, route=route)
                exec_time = time.time() - t1
                exec_durations.append(exec_time)
                manifests.append(manifest)

                # 3. Output Validation Benchmark
                t2 = time.time()
                manifest_path = self.config.output_dir / f"{manifest.avatar_id}_{manifest.seed}_manifest.json"
                val_res = OutputValidator.validate_manifest_and_image(manifest_path)
                val_time = time.time() - t2
                val_durations.append(val_time)

                if val_res.is_valid:
                    successful_count += 1
                else:
                    failed_count += 1

                # 4. Adherence Evaluation
                adh = EvaluationEngine.evaluate_prompt_adherence(manifest)
                adherence_results.append(adh)

            except Exception as e:
                failed_count += 1

        total_wall_time = time.time() - start_wall_time
        final_mem_mb = process.memory_info().rss / (1024 * 1024)

        # Compute aggregate metrics
        avg_prep_ms = (sum(prep_durations) / len(prep_durations) * 1000) if prep_durations else 0.0
        avg_exec_ms = (sum(exec_durations) / len(exec_durations) * 1000) if exec_durations else 0.0
        avg_val_ms = (sum(val_durations) / len(val_durations) * 1000) if val_durations else 0.0
        diversity_summary = EvaluationEngine.evaluate_batch_diversity(manifests)
        avg_adherence = (
            sum(a["adherence_score"] for a in adherence_results) / len(adherence_results)
            if adherence_results else 0.0
        )

        benchmark_data = {
            "benchmark_timestamp_utc": datetime.now(timezone.utc).isoformat(),
            "total_specs_evaluated": len(specs),
            "successful_jobs": successful_count,
            "failed_jobs": failed_count,
            "job_success_rate": round(successful_count / len(specs), 4) if specs else 0.0,
            "total_wall_clock_time_sec": round(total_wall_time, 4),
            "latency_metrics": {
                "avg_job_preparation_ms": round(avg_prep_ms, 2),
                "avg_execution_ms": round(avg_exec_ms, 2),
                "avg_validation_ms": round(avg_val_ms, 2),
                "throughput_jobs_per_sec": round(len(specs) / total_wall_time, 2) if total_wall_time > 0 else 0.0,
            },
            "memory_metrics": {
                "initial_process_ram_mb": round(initial_mem_mb, 2),
                "final_process_ram_mb": round(final_mem_mb, 2),
                "peak_process_ram_mb": round(final_mem_mb, 2),
                "system_total_ram_gb": round(psutil.virtual_memory().total / (1024**3), 2),
            },
            "evaluation_metrics": {
                "mean_prompt_adherence": round(avg_adherence, 4),
                "batch_diversity_score": diversity_summary.get("overall_diversity_score", 0.0),
                "diversity_details": diversity_summary,
            },
            "environment": {
                "route_used": route,
                "model_repo": self.config.default_model_repo,
                "model_revision": self.config.default_model_revision,
            },
        }

        if save_results:
            results_path = self.config.evidence_dir / "benchmarks" / "benchmark_results.json"
            results_path.parent.mkdir(parents=True, exist_ok=True)
            with open(results_path, "w", encoding="utf-8") as f:
                json.dump(benchmark_data, f, indent=2)

        return benchmark_data

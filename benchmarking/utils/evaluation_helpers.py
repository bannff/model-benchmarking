from __future__ import annotations

import json
import os
from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, List


def ensure_dir(path: str) -> None:
	os.makedirs(path, exist_ok=True)


def save_results(results: List[Dict[str, Any]], output_dir: str, suite: str, model_name: str, metadata: Dict[str, Any]) -> str:
	"""Save results with metadata into a timestamped JSON file."""
	ensure_dir(output_dir)
	ts = datetime.now().strftime("%Y%m%d_%H%M%S")
	out_path = os.path.join(output_dir, f"{suite}_{model_name}_{ts}.json")
	payload: Dict[str, Any] = {
		"suite": suite,
		"model": model_name,
		"created_at": ts,
		"metadata": metadata,
		"results": results,
	}
	with open(out_path, "w") as f:
		json.dump(payload, f, indent=2)
	print(f"💾 Results saved to {out_path}")
	return out_path


def calculate_metrics(predictions: List[str], ground_truth: List[str], categories: List[str]) -> Dict[str, Any]:
	"""Compute simple accuracy metrics overall and per-category.

	Assumes predictions and ground_truth are letter choices like 'A', 'B', etc.
	"""
	assert len(predictions) == len(ground_truth) == len(categories)
	total = len(predictions)
	correct = 0
	per_cat_totals: Dict[str, int] = defaultdict(int)
	per_cat_correct: Dict[str, int] = defaultdict(int)

	for pred, gt, cat in zip(predictions, ground_truth, categories):
		per_cat_totals[cat] += 1
		if (pred or "").strip().upper() == (gt or "").strip().upper():
			correct += 1
			per_cat_correct[cat] += 1

	per_category_accuracy = {
		cat: (per_cat_correct[cat] / per_cat_totals[cat]) if per_cat_totals[cat] else 0.0
		for cat in per_cat_totals
	}

	return {
		"overall_accuracy": (correct / total) if total else 0.0,
		"correct_answers": correct,
		"total_questions": total,
		"per_category_accuracy": per_category_accuracy,
	}


def generate_report(results: List[Dict[str, Any]], metrics: Dict[str, Any], suite_name: str, model_name: str) -> str:
	"""Generate a simple Markdown report for human consumption."""
	lines: List[str] = []
	lines.append(f"# {suite_name} Report - {model_name}")
	lines.append("")
	lines.append(f"Generated: {datetime.now().isoformat()}")
	lines.append("")
	lines.append("## Summary")
	lines.append(f"- Overall Accuracy: {metrics.get('overall_accuracy', 0.0):.2%}")
	lines.append(f"- Correct: {metrics.get('correct_answers', 0)} / {metrics.get('total_questions', 0)}")
	lines.append("")
	lines.append("## Per-Category Accuracy")
	for cat, acc in metrics.get("per_category_accuracy", {}).items():
		lines.append(f"- {cat}: {acc:.2%}")
	lines.append("")
	lines.append("## Notes")
	lines.append("This is an automated report. Inspect the raw JSON for detailed per-question outputs.")
	return "\n".join(lines)


def format_question_for_display(question: Dict[str, Any]) -> str:
	q = question.get("question", "")
	opts: List[str] = list(question.get("options", []) or [])
	formatted_opts = "\n".join([f"  {chr(65+i)}. {str(opt)}" for i, opt in enumerate(opts)])
	return f"{q}\n{formatted_opts}"


@dataclass
class ProgressTracker:
	total: int
	title: str = "Progress"
	_current: int = 0

	def update(self, n: int = 1) -> None:
		self._current += n
		self._print()

	def _print(self) -> None:
		pct = (self._current / self.total * 100) if self.total else 100
		print(f"\r{self.title}: {self._current}/{self.total} ({pct:.1f}%)", end="", flush=True)

	def finish(self) -> None:
		self._current = self.total
		self._print()
		print("")

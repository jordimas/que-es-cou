"""
Evaluation of tech_topic_filter.md classifier using DeepEval.

Golden dataset: golden_dataset.json (manually labeled)
Prediction: run claude or groq_tech_filter.py to produce tech_topic_filter.json, then compare.

Usage:
  python eval_classifier.py              # uses claude (default)
  python eval_classifier.py --impl groq  # uses groq_tech_filter.py
"""

import argparse
import json
import os
import subprocess
import sys
import time
from pathlib import Path
from deepeval import evaluate
from deepeval.evaluate.configs import AsyncConfig
from deepeval.test_case import LLMTestCase
from deepeval.metrics import BaseMetric


class ClassifierF1Metric(BaseMetric):
    """Measures F1 score of the tech/not-tech classifier against golden labels."""

    def __init__(self, threshold=0.8):
        self.threshold = threshold
        self.score = 0
        self.success = False

    @property
    def __name__(self):
        return "ClassifierF1"

    def measure(self, test_case: LLMTestCase) -> float:
        gold = json.loads(test_case.expected_output)
        pred = json.loads(test_case.actual_output)

        tp = fp = fn = 0
        details = []
        for item in gold:
            cat = item["category"]
            lid = item["link_id"]
            expected = item["is_tech"]
            predicted = lid in pred.get(cat, [])
            if expected and predicted:
                tp += 1
            elif not expected and predicted:
                fp += 1
                details.append(f"FP: [{cat}] {item['title'][:60]}")
            elif expected and not predicted:
                fn += 1
                details.append(f"FN: [{cat}] {item['title'][:60]}")

        precision = tp / (tp + fp) if (tp + fp) > 0 else 0
        recall = tp / (tp + fn) if (tp + fn) > 0 else 0
        f1 = (
            2 * precision * recall / (precision + recall)
            if (precision + recall) > 0
            else 0
        )

        self.score = f1
        self.success = f1 >= self.threshold
        self.reason = (
            f"F1={f1:.2f} (P={precision:.2f}, R={recall:.2f}) "
            f"TP={tp} FP={fp} FN={fn}"
            + (("\n" + "\n".join(details)) if details else "")
        )
        return f1

    def is_successful(self) -> bool:
        return self.success


ROOT = Path(__file__).parent.parent

EVAL_DIR = Path(__file__).parent


def build_feeds_from_golden(golden: list) -> tuple[dict, dict]:
    """Build minimal synthetic feed dicts containing only golden dataset items."""
    by_cat: dict[str, list] = {}
    for item in golden:
        by_cat.setdefault(item["category"], []).append(
            {
                "link_id": item["link_id"],
                "title": item["title"],
                "description": item.get("description", ""),
            }
        )

    def feed(cat):
        return {
            "section": {
                "id": cat,
                "sources": [{"name": "golden", "items": by_cat.get(cat, [])}],
            }
        }

    return feed("world"), feed("catalunya")


def run_classifier_claude(golden: list) -> dict:
    world_feed, cat_feed = build_feeds_from_golden(golden)
    world_path = EVAL_DIR / "eval_feeds_world.json"
    cat_path = EVAL_DIR / "eval_feeds_catalunya.json"
    world_path.write_text(json.dumps(world_feed))
    cat_path.write_text(json.dumps(cat_feed))

    prompt = (ROOT / "prompts" / "tech_topic_filter.md").read_text()
    prompt = prompt.replace("output/raw_feeds_world.json", str(world_path))
    prompt = prompt.replace("output/raw_feeds_catalunya.json", str(cat_path))
    prompt = prompt.replace(
        "output/tech_topic_filter_new.json", str(EVAL_DIR / "tech_topic_filter.json")
    )
    subprocess.run(
        ["claude", "--dangerously-skip-permissions", "-p", prompt],
        check=True,
        cwd=EVAL_DIR,
    )
    world_path.unlink(missing_ok=True)
    cat_path.unlink(missing_ok=True)
    with open(EVAL_DIR / "tech_topic_filter.json") as f:
        return json.load(f)


def run_classifier_groq(golden: list, model: str = None) -> dict:
    world_feed, cat_feed = build_feeds_from_golden(golden)
    world_path = EVAL_DIR / "eval_feeds_world.json"
    cat_path = EVAL_DIR / "eval_feeds_catalunya.json"
    world_path.write_text(json.dumps(world_feed))
    cat_path.write_text(json.dumps(cat_feed))

    groq_script = ROOT / "groq_tech_filter.py"
    env_overrides = {
        "WORLD_PATH": str(world_path),
        "CATALUNYA_PATH": str(cat_path),
        "OUT_PATH": str(EVAL_DIR / "tech_topic_filter.json"),
    }
    if model:
        env_overrides["GROQ_MODEL"] = model
    env = {**os.environ, **env_overrides}
    subprocess.run(
        [sys.executable, str(groq_script)], check=True, cwd=EVAL_DIR, env=env
    )
    world_path.unlink(missing_ok=True)
    cat_path.unlink(missing_ok=True)
    with open(EVAL_DIR / "tech_topic_filter.json") as f:
        return json.load(f)


def run_classifier(golden: list, impl: str, model: str = None) -> dict:
    if impl == "groq":
        return run_classifier_groq(golden, model=model)
    return run_classifier_claude(golden)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--impl",
        choices=["claude", "groq"],
        default="claude",
        help="Which classifier implementation to evaluate (default: claude)",
    )
    parser.add_argument(
        "--model",
        default=None,
        help="Override model (for groq impl)",
    )
    args = parser.parse_args()

    start = time.time()

    with open(Path(__file__).parent / "golden_dataset.json") as f:
        golden = json.load(f)

    print(
        f"Running classifier ({args.impl}{f'/{args.model}' if args.model else ''})..."
    )
    predictions = run_classifier(golden, args.impl, model=args.model)

    test_case = LLMTestCase(
        input="Classify articles from raw feeds as tech or not-tech",
        actual_output=json.dumps(predictions),
        expected_output=json.dumps(golden),
    )

    metric = ClassifierF1Metric(threshold=0.8)
    evaluate([test_case], [metric], async_config=AsyncConfig(run_async=False))
    print(metric.reason)
    print(f"Total time: {time.time() - start:.1f}s")


if __name__ == "__main__":
    main()

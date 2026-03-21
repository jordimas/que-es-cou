"""
Evaluation of tech_topic_filter.md classifier using DeepEval.

Golden dataset: golden_dataset.json (manually labeled)
Prediction: run claude to produce tech_topic_filter.json, then compare.
"""
import json
import subprocess
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
        f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0

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
        by_cat.setdefault(item["category"], []).append({
            "link_id": item["link_id"],
            "title": item["title"],
            "description": item.get("description", ""),
        })

    def feed(cat):
        return {"section": {"id": cat, "sources": [{"name": "golden", "items": by_cat.get(cat, [])}]}}

    return feed("world"), feed("catalunya")


def run_classifier(golden: list):
    world_feed, cat_feed = build_feeds_from_golden(golden)
    world_path = EVAL_DIR / "eval_feeds_world.json"
    cat_path = EVAL_DIR / "eval_feeds_catalunya.json"
    world_path.write_text(json.dumps(world_feed))
    cat_path.write_text(json.dumps(cat_feed))

    prompt = (ROOT / "prompts" / "tech_topic_filter.md").read_text()
    prompt = prompt.replace("output/raw_feeds_world.json", str(world_path))
    prompt = prompt.replace("output/raw_feeds_catalunya.json", str(cat_path))
    prompt = prompt.replace("output/tech_topic_filter_new.json", str(EVAL_DIR / "tech_topic_filter.json"))
    subprocess.run(
        ["claude", "--dangerously-skip-permissions", "-p", prompt],
        check=True,
        cwd=EVAL_DIR,
    )
    world_path.unlink()
    cat_path.unlink()
    with open(EVAL_DIR / "tech_topic_filter.json") as f:
        return json.load(f)


def main():
    with open(Path(__file__).parent / "golden_dataset.json") as f:
        golden = json.load(f)

    print("Running classifier...")
    predictions = run_classifier(golden)

    test_case = LLMTestCase(
        input="Classify articles from raw feeds as tech or not-tech",
        actual_output=json.dumps(predictions),
        expected_output=json.dumps(golden),
    )

    metric = ClassifierF1Metric(threshold=0.8)
    evaluate([test_case], [metric], async_config=AsyncConfig(run_async=False))


if __name__ == "__main__":
    main()

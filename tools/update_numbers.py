"""Fill the README and the Hub cards from docs/results.json.

docs/results.json is the single source for the scores and the dataset counts. The project page
reads it directly. After changing it, run:

  python tools/update_numbers.py            # rewrite README.md
  python tools/update_numbers.py --push     # also upload the dataset and model cards to the Hub
"""
import argparse
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATASET = "ahd03/vln-synthetic-scenes"
MODEL = "ahd03/masar"
DATASET_META = """---
license: cc-by-4.0
pretty_name: VLN Synthetic Scenes
size_categories:
- 10K<n<100K
task_categories:
- image-text-to-text
tags:
- navigation
- vision-language-navigation
- synthetic
- blender
- navitrace
configs:
- config_name: default
  data_files:
  - split: train
    path: data/train-*
  - split: test
    path: data/test-*
---

"""


def fill(text, results):
    """Replace {{section.key}} with the value from results.json (integers get thousands separators)."""
    def value(match):
        section, key = match.group(1).split(".", 1)
        v = results[section][key]
        return f"{v:,}" if isinstance(v, int) else f"{v:.1f}"
    return re.sub(r"\{\{([^}]+)\}\}", value, text)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--push", action="store_true", help="Upload the dataset and model cards to the Hub.")
    args = parser.parse_args()
    results = json.loads((ROOT / "docs" / "results.json").read_text(encoding="utf-8"))
    cards = ROOT / "cards"
    readme = fill((cards / "README.template.md").read_text(encoding="utf-8"), results)
    (ROOT / "README.md").write_bytes(readme.encode("utf-8"))
    print("README.md written")
    if args.push:
        from huggingface_hub import HfApi
        api = HfApi()
        dataset_card = DATASET_META + fill((cards / "dataset_card.md").read_text(encoding="utf-8"), results)
        model_card = fill((cards / "model_card.md").read_text(encoding="utf-8"), results)
        api.upload_file(path_or_fileobj=dataset_card.encode("utf-8"), path_in_repo="README.md", repo_id=DATASET,
                        repo_type="dataset", commit_message="Update dataset card")
        api.upload_file(path_or_fileobj=model_card.encode("utf-8"), path_in_repo="README.md", repo_id=MODEL,
                        commit_message="Update model card")
        api.upload_file(path_or_fileobj=str(ROOT / "finetune" / "prompts.py"), path_in_repo="prompts.py",
                        repo_id=MODEL, commit_message="Add the prompts used in training")
        print("cards uploaded")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Find new Hadrian roles that fit config.json and write a Markdown digest."""
import json
import os
import re
import sys
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent
YEARS = re.compile(r"\b(\d{1,2})\s*(?:\+|-\s*\d{1,2}\s*\+?)?\s*years?\b", re.I)


def fetch_jobs(url):
    request = urllib.request.Request(url, headers={"User-Agent": "hadrian-job-alerts/1.0"})
    with urllib.request.urlopen(request, timeout=30) as response:
        return json.load(response)["jobs"]


def required_years(description):
    """Return the highest minimum experience stated in a job description."""
    return max((int(n) for n in YEARS.findall(description)), default=0)


def is_match(job, config):
    if not job.get("isListed", True):
        return False
    title = job["title"]
    if not any(re.search(p, title, re.I) for p in config["title_include"]):
        return False
    if any(re.search(p, title, re.I) for p in config["title_exclude"]):
        return False
    # Interns and explicitly entry-level titles qualify regardless of the text.
    if job.get("employmentType") == "Intern":
        return True
    if any(re.search(p, title, re.I) for p in config["early_career_titles"]):
        return True
    return required_years(job.get("descriptionPlain", "")) <= config["max_required_years"]


def build_digest(jobs, mention):
    lines = [f"@{mention} new Hadrian roles that match your filters:", ""]
    for job in jobs:
        lines.append(f"- **[{job['title']}]({job['jobUrl']})**")
        lines.append(f"  {job.get('location', 'Location not listed')} · {job.get('department', 'No department')}")
    return "\n".join(lines) + "\n"


def main():
    config = json.loads((ROOT / "config.json").read_text())
    seen_path = ROOT / "seen.json"
    seen = set(json.loads(seen_path.read_text()))

    new = [
        job
        for job in fetch_jobs(config["board_url"])
        if job["id"] not in seen and is_match(job, config)
    ]
    print(f"{len(new)} new matching role(s)")
    for job in new:
        print(f"  {job['title']} ({job.get('location')})")

    output = os.environ.get("GITHUB_OUTPUT")
    if output:
        with open(output, "a") as f:
            f.write(f"count={len(new)}\n")
    if not new:
        return 0

    mention = os.environ.get("NOTIFY_USER", "")
    (ROOT / "digest.md").write_text(build_digest(new, mention))
    seen_path.write_text(json.dumps(sorted(seen | {j["id"] for j in new}), indent=2) + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())

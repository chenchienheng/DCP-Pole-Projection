"""Read-only, public-source PR baseline inventory. No GitHub writes or approvals.

Enumerates all PR pages, compares every open-PR changed path to pinned main
and (for DCP) the existing kernel candidate, preserves patches, then checks
that main and the open head/base sets did not drift during acquisition.
Byte coverage is not semantic adoption, test execution, or deletion authority.
"""
from __future__ import annotations
import argparse
import base64
from collections import Counter
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import re
import time
from urllib.parse import quote, urlparse
from urllib.request import Request, urlopen

REPOS = ("chenchienheng/DCP-Pole-Projection", "chenchienheng/GLModel-Pole-Projection", "chenchienheng/Ideas-Pole-Projection")
POLICIES = ("README.md", "AGENTS.md", "CURRENT-SURFACE-MANIFEST.json", "SEMANTIC-CONTROL-PLANE.json", "FAILURE-EVOLUTION-POLICY.md", "PUBLIC-SURFACE-POLICY.md", "STATUS.md")


def now() -> str:
    return datetime.now(timezone.utc).isoformat()


def relation(status: str, path: str, source: dict, target: dict) -> str:
    if status == "removed":
        return "PROPOSED_DELETION_NOT_APPLIED" if path in target else "ABSENT_IN_TARGET_NOT_DELETION_AUTHORITY"
    if path not in source:
        return "SOURCE_TREE_MISMATCH"
    if path not in target:
        return "MISSING_FROM_TARGET"
    fields = ("sha", "mode", "type")
    return "EXACT_BLOB_AND_MODE" if all(source[path][k] == target[path][k] for k in fields) else "DIFFERENT_CONTENT_OR_MODE_REVIEW"


def executable(path: str) -> bool:
    return path == "pyproject.toml" or path.startswith(("dcp_kernel/", "contracts/", "fixtures/", "tests/", "tools/"))


class Reader:
    def __init__(self):
        self.started = time.monotonic()
        self.calls = []
        self.cache = {}

    def get(self, path: str):
        url = path if path.startswith("https://") else "https://api.github.com" + path
        parsed = urlparse(url)
        if parsed.scheme != "https" or parsed.netloc != "api.github.com" or not any(parsed.path.startswith("/repos/" + repo + "/") for repo in REPOS):
            raise ValueError("OUTSIDE_PUBLIC_REPOSITORY_ALLOWLIST")
        if len(self.calls) >= 110 or time.monotonic() - self.started > 210:
            raise RuntimeError("BOUNDED_ACQUISITION_BUDGET_EXCEEDED")
        headers = {"Accept": "application/vnd.github+json", "X-GitHub-Api-Version": "2022-11-28", "User-Agent": "bounded-pr-baseline-reader"}
        token = os.environ.get("GH_TOKEN")
        if token:
            headers["Authorization"] = "Bearer " + token
        observed = now()
        with urlopen(Request(url, headers=headers), timeout=25) as response:
            if urlparse(response.url).netloc != "api.github.com":
                raise RuntimeError("UNEXPECTED_RESPONSE_HOST")
            raw = response.read(12000000)
            if len(raw) == 12000000:
                raise RuntimeError("RESPONSE_SIZE_LIMIT")
            links = response.headers.get("Link", "")
        self.calls.append({"url": url, "observed_at": observed, "bytes": len(raw), "sha256": hashlib.sha256(raw).hexdigest()})
        return json.loads(raw), links

    def pages(self, path: str) -> list:
        items = []
        next_url = path
        while next_url:
            page, links = self.get(next_url)
            if not isinstance(page, list):
                raise ValueError("EXPECTED_PAGINATED_LIST")
            items.extend(page)
            match = re.search(r'<([^>]+)>; rel="next"', links)
            next_url = match.group(1) if match else None
        return items

    def tree(self, repo: str, ref: str) -> dict:
        key = repo + "@" + ref
        if key not in self.cache:
            payload, _ = self.get(f"/repos/{repo}/git/trees/{quote(ref, safe='')}?recursive=1")
            if payload.get("truncated"):
                raise RuntimeError("TRUNCATED_TREE:" + key)
            self.cache[key] = {item["path"]: {k: item[k] for k in ("sha", "mode", "type")} for item in payload["tree"] if item["type"] != "tree"}
        return self.cache[key]

    def main(self, repo: str) -> str:
        result, _ = self.get(f"/repos/{repo}/git/ref/heads/main")
        return result["object"]["sha"]


def binding(pr: dict) -> tuple:
    return pr["number"], pr["head"]["sha"], pr["base"]["ref"], pr["base"]["sha"]


def snapshot(output: Path) -> dict:
    reader = Reader()
    result = {"record": "PR_COMMON_BASELINE_20260927", "started_at": now(), "acquisition": "LIVE_GITHUB_REST_GET_ONLY", "repositories": {}, "claim_ceiling": ["BYTE_COMPARISON_NOT_SEMANTIC_ACCEPTANCE", "NO_MAIN_WRITE", "NO_PR_MERGE_OR_CLOSE", "NO_RUNTIME_OR_APPROVAL", "CLOSED_METADATA_NOT_FULL_HISTORICAL_DIFF_REVIEW"]}
    for repo in REPOS:
        baseline = reader.main(repo)
        main_tree = reader.tree(repo, baseline)
        all_prs = reader.pages(f"/repos/{repo}/pulls?state=all&sort=created&direction=asc&per_page=100")
        open_prs = [pr for pr in all_prs if pr["state"] == "open"]
        comparison_sha = next((p["head"]["sha"] for p in open_prs if repo == REPOS[0] and p["number"] == 406), baseline)
        comparison_tree = reader.tree(repo, comparison_sha)
        item = {"main_sha": baseline, "comparison_sha": comparison_sha, "main_tree": main_tree, "inventory": [], "open_prs": [], "policies": {}, "pagination_exhausted": True}
        for pr in all_prs:
            item["inventory"].append({"number": pr["number"], "url": pr["html_url"], "title": pr["title"], "state": pr["state"], "draft": pr["draft"], "merged_at": pr.get("merged_at"), "closed_at": pr.get("closed_at"), "updated_at": pr["updated_at"], "head_sha": pr["head"]["sha"], "head_ref": pr["head"]["ref"], "base_sha": pr["base"]["sha"], "base_ref": pr["base"]["ref"], "body": pr.get("body") or ""})
        for pr in open_prs:
            files = reader.pages(f"/repos/{repo}/pulls/{pr['number']}/files?per_page=100")
            source = reader.tree(repo, pr["head"]["sha"])
            rows = []
            for f in files:
                path = f["filename"]
                rows.append({"path": path, "status": f["status"], "previous_filename": f.get("previous_filename"), "source_sha": source.get(path, {}).get("sha"), "main_sha": main_tree.get(path, {}).get("sha"), "comparison_sha": comparison_tree.get(path, {}).get("sha"), "main_relation": relation(f["status"], path, source, main_tree), "comparison_relation": relation(f["status"], path, source, comparison_tree), "executable_surface": executable(path), "patch": f.get("patch"), "additions": f["additions"], "deletions": f["deletions"]})
            item["open_prs"].append({"number": pr["number"], "url": pr["html_url"], "title": pr["title"], "head_sha": pr["head"]["sha"], "base_ref": pr["base"]["ref"], "recorded_base_sha": pr["base"]["sha"], "changed_path_count": len(rows), "main_comparison_counts": dict(Counter(r["main_relation"] for r in rows)), "comparison_counts": dict(Counter(r["comparison_relation"] for r in rows)), "files": rows})
        for path in POLICIES:
            if path in main_tree:
                blob, _ = reader.get(f"/repos/{repo}/git/blobs/{main_tree[path]['sha']}")
                if blob.get("encoding") != "base64":
                    raise ValueError("UNSUPPORTED_POLICY_ENCODING")
                content = base64.b64decode(blob["content"]).decode("utf-8")
                item["policies"][path] = {"blob_sha": main_tree[path]["sha"], "content": content}
        end_main = reader.main(repo)
        end_open = reader.pages(f"/repos/{repo}/pulls?state=open&per_page=100")
        item["revalidation"] = {"main_sha": end_main, "same_main": end_main == baseline, "same_open_bindings": sorted(map(binding, open_prs)) == sorted(map(binding, end_open)), "observed_at": now()}
        if not item["revalidation"]["same_main"] or not item["revalidation"]["same_open_bindings"]:
            result.setdefault("drift", []).append(repo)
        result["repositories"][repo] = item
    result["finished_at"] = now()
    result["requests"] = reader.calls
    result["complete"] = not result.get("drift")
    output.mkdir(parents=True, exist_ok=True)
    (output / "baseline.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    lines = ["# PR common-baseline snapshot", "", "Read-only public repository inventory; byte coverage is not semantic acceptance.", "", "| Repository | All PRs | Open PRs | Main | Stable during acquisition |", "|---|---:|---:|---|---|"]
    for repo, item in result["repositories"].items():
        stable = item["revalidation"]["same_main"] and item["revalidation"]["same_open_bindings"]
        lines.append(f"| {repo} | {len(item['inventory'])} | {len(item['open_prs'])} | {item['main_sha']} | {stable} |")
    lines += ["", "## Every open PR", "", "| PR | Base ref | Changed paths | Against main | Against selected comparison |", "|---|---|---:|---|---|"]
    for repo, item in result["repositories"].items():
        for pr in item["open_prs"]:
            lines.append(f"| {repo}#{pr['number']} | {pr['base_ref']} | {pr['changed_path_count']} | {pr['main_comparison_counts']} | {pr['comparison_counts']} |")
    lines += ["", "Snapshot complete and no head/base/main drift: " + str(result["complete"]), "All historical PR metadata was enumerated; only open-PR patches were reviewed by this acquisition."]
    (output / "summary.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("PR_BASELINE_COMPLETE=" + str(result["complete"]))
    for repo, item in result["repositories"].items():
        print(repo, "all", len(item["inventory"]), "open", len(item["open_prs"]), "main", item["main_sha"])
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    try:
        outcome = snapshot(args.output)
    except Exception as exc:
        args.output.mkdir(parents=True, exist_ok=True)
        (args.output / "failure.json").write_text(json.dumps({"record": "PR_COMMON_BASELINE_20260927", "complete": False, "error": type(exc).__name__ + ":" + str(exc), "recorded_at": now()}, indent=2), encoding="utf-8")
        raise
    raise SystemExit(0 if outcome["complete"] else 2)

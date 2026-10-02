"""On-demand, credential-free byte-delivery verification CLI.

prepare reads the expected source files and saves a pending verification;
receive reopens a separately received copy and reconciles it without an executor.
Neither command uploads files or approves their semantic contents.
"""
from __future__ import annotations

import argparse
from dataclasses import asdict
import json
import os
from pathlib import Path
import stat
import sys
import tempfile

from dcp_kernel import (
    Decision, contract_from_dict, pending_from_dict, pending_to_dict,
    prepare_artifact_delivery, receive_artifact_delivery,
)


def _unique(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("DUPLICATE_JSON_KEY")
        result[key] = value
    return result


def _bad_constant(value):
    raise ValueError("NON_FINITE_JSON_CONSTANT")


def _load(path):
    data = json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=_unique,
                      parse_constant=_bad_constant)
    if not isinstance(data, dict):
        raise ValueError("JSON_OBJECT_REQUIRED")
    return data


def _saved_pending(data):
    """Read a prepared result or this CLI's saved check; never trust its flags."""
    if "result" in data:
        if (set(data) != {"result", "observations", "scope"}
                or data["scope"] != "BYTE_DELIVERY_ONLY_NOT_SEMANTIC_OR_NATIVE_ACCEPTANCE"
                or not isinstance(data["observations"], list)
                or not isinstance(data["result"], dict)):
            raise ValueError("INVALID_SAVED_CHECK_ENVELOPE")
        data = data["result"]
    return pending_from_dict(data)


def _same_existing_output(path, raw):
    """Inspect, never replace, a prior output during an explicit resume.

    A regular, unchanged, byte-identical output can close an interrupted
    publication receipt. Parent directories remain caller-controlled.
    """
    if not hasattr(os, "O_NOFOLLOW"):
        raise ValueError("RESUME_NOFOLLOW_UNSUPPORTED")
    fd = os.open(path, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK)
    try:
        before = os.fstat(fd)
        if not stat.S_ISREG(before.st_mode) or before.st_size != len(raw):
            return False
        chunks = []
        remaining = len(raw) + 1
        while remaining:
            block = os.read(fd, min(remaining, 1024 * 1024))
            if not block:
                break
            chunks.append(block)
            remaining -= len(block)
        after = os.fstat(fd)
        identity = lambda s: (s.st_dev, s.st_ino, s.st_size, s.st_mtime_ns, s.st_ctime_ns)
        return identity(before) == identity(after) and b"".join(chunks) == raw
    finally:
        os.close(fd)


def _save_new(path, value, protected, *, resume=False):
    resolved = path.resolve()
    if any(resolved == other.resolve() for other in protected):
        raise ValueError("OUTPUT_OVERLAPS_INPUT")
    raw = (json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2, allow_nan=False) + "\n").encode("utf-8")
    # Create-only publication; an existing output is never silently overwritten.
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(dir=path.parent, prefix=".delivery-", delete=False) as stream:
            temporary = Path(stream.name)
            stream.write(raw)
            stream.flush()
            os.fsync(stream.fileno())
        try:
            os.link(temporary, path)
        except FileExistsError:
            if not resume:
                raise
            if not _same_existing_output(path, raw):
                raise ValueError("EXISTING_OUTPUT_CONFLICT")
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("phase", choices=("prepare", "receive"))
    parser.add_argument("--contract", type=Path, required=True)
    parser.add_argument("--root", type=Path, required=True,
                        help="Expected source root for prepare; downloaded/readback root for receive.")
    parser.add_argument("--pending", type=Path)
    parser.add_argument("--output", type=Path, required=True,
                        help="New JSON output path; no overwrite.")
    parser.add_argument("--resume", action="store_true",
                        help="Re-read inputs and reuse only byte-identical existing output; never overwrite.")
    args = parser.parse_args(argv)
    try:
        contract = contract_from_dict(_load(args.contract))
        protected = [args.contract, *(args.root / item.path for item in contract.artifacts)]
        if args.phase == "prepare":
            if args.pending is not None:
                raise ValueError("PREPARE_DOES_NOT_READ_PENDING")
            pending = prepare_artifact_delivery(contract, args.root)
            value = pending_to_dict(pending)
            exit_code = 0 if pending.effect is not None else 3
        else:
            if args.pending is None:
                raise ValueError("RECEIVE_REQUIRES_SAVED_PENDING")
            protected.append(args.pending)
            pending = _saved_pending(_load(args.pending))
            checked = receive_artifact_delivery(contract, pending, args.root)
            value = asdict(checked)
            exit_code = 0 if checked.result.decision is Decision.PASS else 3
        _save_new(args.output, value, protected, resume=args.resume)
        print(args.output)
        return exit_code
    except (OSError, ValueError, TypeError, KeyError) as exc:
        message = f"IO_ERRNO_{exc.errno}" if isinstance(exc, OSError) else str(exc)
        print(f"DELIVERY_CHECK_FAILED: {message}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())

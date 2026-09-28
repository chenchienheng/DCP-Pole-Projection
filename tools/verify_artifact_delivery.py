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


def _save_new(path, value, protected):
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
        os.link(temporary, path)
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
            pending = pending_from_dict(_load(args.pending))
            checked = receive_artifact_delivery(contract, pending, args.root)
            value = asdict(checked)
            exit_code = 0 if checked.result.decision is Decision.PASS else 3
        _save_new(args.output, value, protected)
        print(args.output)
        return exit_code
    except (OSError, ValueError, TypeError, KeyError) as exc:
        message = f"IO_ERRNO_{exc.errno}" if isinstance(exc, OSError) else str(exc)
        print(f"DELIVERY_CHECK_FAILED: {message}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())

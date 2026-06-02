#!/usr/bin/env python
from __future__ import annotations

import argparse
from pathlib import Path

import torch


def unwrap_state(obj):
    if isinstance(obj, dict):
        for key in ("model_state_dict", "state_dict", "model"):
            if key in obj and isinstance(obj[key], dict):
                return obj[key], key
    if isinstance(obj, dict):
        return obj, None
    raise TypeError(f"Unsupported checkpoint format: {type(obj)}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--base", required=True, help="Base checkpoint, usually v10 frozen")
    parser.add_argument("--candidate", required=True, help="Candidate checkpoint to blend in")
    parser.add_argument("--out", required=True)
    parser.add_argument("--alpha", type=float, required=True, help="0 keeps base, 1 keeps candidate")
    args = parser.parse_args()

    if not (0.0 <= args.alpha <= 1.0):
        raise ValueError("--alpha must be between 0 and 1")

    base_obj = torch.load(args.base, map_location="cpu")
    cand_obj = torch.load(args.candidate, map_location="cpu")

    base_sd, base_key = unwrap_state(base_obj)
    cand_sd, _ = unwrap_state(cand_obj)

    out_sd = {}
    for k, v in base_sd.items():
        if k not in cand_sd:
            raise KeyError(f"Missing key in candidate: {k}")
        cv = cand_sd[k]
        if torch.is_floating_point(v):
            out_sd[k] = (1.0 - args.alpha) * v + args.alpha * cv
        else:
            out_sd[k] = v.clone()

    if isinstance(base_obj, dict) and base_key is not None:
        out_obj = dict(base_obj)
        out_obj[base_key] = out_sd
    else:
        out_obj = out_sd

    Path(args.out).parent.mkdir(parents=True, exist_ok=True)
    torch.save(out_obj, args.out)
    print(f"saved {args.out} with alpha={args.alpha}")


if __name__ == "__main__":
    main()

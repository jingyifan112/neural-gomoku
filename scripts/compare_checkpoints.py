#!/usr/bin/env python
from __future__ import annotations

import argparse
import torch


def unwrap_state(obj):
    if isinstance(obj, dict):
        for key in ("model_state_dict", "state_dict", "model"):
            if key in obj and isinstance(obj[key], dict):
                return obj[key]
    if isinstance(obj, dict):
        return obj
    raise TypeError(type(obj))


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--a", required=True)
    p.add_argument("--b", required=True)
    args = p.parse_args()

    a = unwrap_state(torch.load(args.a, map_location="cpu"))
    b = unwrap_state(torch.load(args.b, map_location="cpu"))

    max_diff = 0.0
    max_key = None
    compared = 0

    for k in a:
        if k not in b:
            print(f"missing in b: {k}")
            continue
        if torch.is_floating_point(a[k]):
            diff = (a[k] - b[k]).abs().max().item()
            compared += 1
            if diff > max_diff:
                max_diff = diff
                max_key = k

    print(f"compared_float_tensors={compared}")
    print(f"max_abs_diff={max_diff}")
    print(f"max_key={max_key}")


if __name__ == "__main__":
    main()

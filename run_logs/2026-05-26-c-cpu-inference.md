# C CPU Inference Migration

Goal: migrate the GPU-trained PyTorch CNN checkpoint to C CPU inference.

Result:
- Exported the PyTorch 9x9 checkpoint to C-readable binary weights.
- Implemented C CPU forward pass for the CNN policy-value model.
- Added a Python/C consistency test.

Consistency test result:

```text
policy_logits_max_abs_diff 4.991889e-07
policy_probs_max_abs_diff 1.86264515e-08
value_abs_diff 3.27825546e-07
top_legal_move C=60 Python=60                                                                     Conclusion:
The C inference output matches the Python/PyTorch output very closely. This confirms that the GPU-trained checkpoint can be exported and used for CPU inference in C.

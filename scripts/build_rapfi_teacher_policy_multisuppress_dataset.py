from __future__ import annotations
import argparse, json
from pathlib import Path
import numpy as np
import torch
from train_rapfi_teacher_policy_margin import BOARD_SIZE, encode_state, legal_mask_from_board, load_model, masked_softmax, rank_of_action, rc_to_action

def action_to_rc(a):
    return [int(a)//BOARD_SIZE, int(a)%BOARD_SIZE]

def parse_args():
    ap=argparse.ArgumentParser(description="Build policy-only multi-suppress teacher dataset.")
    ap.add_argument("--source-dataset", type=Path, default=Path("analysis/public_benchmark_eval/rapfi_teacher_policy_margin_dataset_corpus8_selected.json"))
    ap.add_argument("--checkpoint", type=Path, default=Path("checkpoints/15x15_current_best.pt"))
    ap.add_argument("--out", type=Path, default=Path("analysis/public_benchmark_eval/rapfi_teacher_policy_multisuppress_dataset_corpus8_selected.json"))
    ap.add_argument("--top-k", type=int, default=10)
    ap.add_argument("--max-suppress", type=int, default=5)
    ap.add_argument("--margin", type=float, default=1.0)
    return ap.parse_args()

def sorted_legal_actions(probs, legal_mask):
    legal=torch.nonzero(legal_mask>0, as_tuple=False).flatten()
    order=torch.argsort(probs[legal], descending=True)
    return [int(legal[i].item()) for i in order]

def build_row(sample, model, device, args):
    board=sample["board"]
    current_player=int(sample["current_player"])
    legal_np=legal_mask_from_board(board)
    target_action=rc_to_action(sample["target_rc"])
    primary_action=rc_to_action(sample["suppress_rc"])
    if legal_np[target_action] <= 0: raise ValueError(sample["case_id"] + ": illegal target")
    if legal_np[primary_action] <= 0: raise ValueError(sample["case_id"] + ": illegal primary suppress")
    state=torch.tensor(encode_state(board,current_player), dtype=torch.float32, device=device).unsqueeze(0)
    mask=torch.tensor(legal_np, dtype=torch.float32, device=device).unsqueeze(0)
    with torch.no_grad():
        logits,_=model(state)
        probs=masked_softmax(logits,mask)[0]
    logits0=logits[0]
    mask0=mask[0]
    ranked=sorted_legal_actions(probs,mask0)
    suppress=[]
    if primary_action != target_action: suppress.append(primary_action)
    top_added=0
    for a in ranked:
        if len(suppress) >= args.max_suppress: break
        if a == target_action or a in suppress: continue
        suppress.append(a)
        top_added += 1
        if top_added >= args.top_k: break
    if not suppress: raise ValueError(sample["case_id"] + ": no suppress actions")
    target_logit=float(logits0[target_action].item())
    primary_gap=target_logit-float(logits0[primary_action].item())
    gaps=[target_logit-float(logits0[a].item()) for a in suppress]
    worst_gap=min(gaps)
    hardness=min(3.0, 1.0 + 0.25*max(0.0, args.margin-worst_gap))
    out=dict(sample)
    out["primary_suppress_rc"]=list(sample["suppress_rc"])
    out["suppress_rcs"]=[action_to_rc(a) for a in suppress]
    out["suppress_candidates"]=[{"rc":action_to_rc(a),"action":a,"prob":float(probs[a].item()),"rank":int(rank_of_action(probs,a,mask0)),"gap":float(target_logit-float(logits0[a].item()))} for a in suppress]
    out["suppress_actions_source"]="primary_current_best_direct_plus_current_best_top_policy"
    out["before_target_prob"]=float(probs[target_action].item())
    out["before_target_rank"]=int(rank_of_action(probs,target_action,mask0))
    out["before_primary_suppress_rank"]=int(rank_of_action(probs,primary_action,mask0))
    out["before_primary_gap"]=float(primary_gap)
    out["before_worst_suppress_gap"]=float(worst_gap)
    out["hardness_weight"]=float(hardness)
    out["effective_sample_weight"]=float(sample.get("sample_weight",1.0))*float(hardness)
    out["validation_notes"]="target and all suppress moves legal; suppress_rcs excludes target and duplicates"
    return out

def main():
    args=parse_args()
    if args.max_suppress < 1: raise ValueError("--max-suppress must be >=1")
    device=torch.device("cuda" if torch.cuda.is_available() else "cpu")
    raw=json.loads(args.source_dataset.read_text(encoding="utf-8"))
    samples=raw.get("samples",[])
    model=load_model(args.checkpoint,device)
    model.eval()
    rows=[]; skipped=[]
    for s in samples:
        try: rows.append(build_row(s,model,device,args))
        except Exception as e: skipped.append({"case_id":s.get("case_id"),"reason":str(e)})
    if not rows: raise RuntimeError("no rows written")
    counts=[len(r["suppress_rcs"]) for r in rows]
    ranks=[int(r["before_target_rank"]) for r in rows]
    worst=[float(r["before_worst_suppress_gap"]) for r in rows]
    summary={"rows":len(rows),"suppress_count_min":min(counts),"suppress_count_mean":float(np.mean(counts)),"suppress_count_max":max(counts),"target_rank_gt10":int(sum(x>10 for x in ranks)),"target_rank_gt50":int(sum(x>50 for x in ranks)),"mean_worst_suppress_gap":float(np.mean(worst)),"median_worst_suppress_gap":float(np.median(worst))}
    out={"name":"rapfi_teacher_policy_multisuppress_dataset_corpus8_selected","description":"Policy-only multi-suppress teacher-divergence margin dataset.","source_dataset":str(args.source_dataset),"checkpoint":str(args.checkpoint),"top_k":args.top_k,"max_suppress":args.max_suppress,"margin":args.margin,"summary":summary,"samples":rows,"skipped":skipped}
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print("device:",device)
    print("source_dataset:",args.source_dataset)
    print("checkpoint:",args.checkpoint)
    print("out:",args.out)
    print("source_rows:",len(samples))
    print("written_rows:",len(rows))
    print("skipped_rows:",len(skipped))
    for k,v in summary.items(): print(str(k)+":",v)
    return 0

if __name__ == "__main__":
    raise SystemExit(main())

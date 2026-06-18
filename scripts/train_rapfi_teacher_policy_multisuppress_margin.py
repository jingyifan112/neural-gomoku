from __future__ import annotations
import argparse, csv, json
from pathlib import Path
import numpy as np
import torch
from train_rapfi_teacher_policy_margin import BOARD_SIZE, encode_state, legal_mask_from_board, load_anchor_samples, load_model, masked_softmax, rank_of_action, rc_to_action

def action_to_rc(a):
    return [int(a)//BOARD_SIZE, int(a)%BOARD_SIZE]

def parse_args():
    ap=argparse.ArgumentParser(description="Dry-run diagnostics for policy-only multi-suppress margin dataset.")
    ap.add_argument("--dataset", type=Path, default=Path("analysis/public_benchmark_eval/rapfi_teacher_policy_multisuppress_dataset_corpus8_selected.json"))
    ap.add_argument("--anchor-snapshots", type=Path, default=Path("analysis/public_benchmark_eval/corpus8_selected_board_snapshots.json"))
    ap.add_argument("--init-checkpoint", type=Path, required=True)
    ap.add_argument("--reference-checkpoint", type=Path, default=Path("checkpoints/15x15_current_best.pt"))
    ap.add_argument("--margin", type=float, default=1.0)
    ap.add_argument("--loss-reduction", choices=["mean","max"], default="mean")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--out-csv", type=Path, default=Path("analysis/integration_eval/policy_only_multisuppress_dryrun_metrics.csv"))
    ap.add_argument("--out-report", type=Path, default=Path("analysis/integration_eval/policy_only_multisuppress_dryrun_report.md"))
    return ap.parse_args()

def load_dataset(path):
    d=json.loads(path.read_text(encoding="utf-8"))
    rows=d.get("samples",[])
    if not rows: raise ValueError("empty dataset: "+str(path))
    return d, rows

def diagnose(model, sample, device, margin, loss_reduction):
    board=sample["board"]
    current_player=int(sample["current_player"])
    legal_np=legal_mask_from_board(board)
    target_action=rc_to_action(sample["target_rc"])
    suppress_actions=[rc_to_action(rc) for rc in sample["suppress_rcs"]]
    primary_action=rc_to_action(sample.get("primary_suppress_rc", sample["suppress_rcs"][0]))
    if legal_np[target_action] <= 0: raise ValueError(sample["case_id"]+": target illegal")
    seen=set()
    for a in suppress_actions:
        if legal_np[a] <= 0: raise ValueError(sample["case_id"]+": suppress illegal "+str(action_to_rc(a)))
        if a == target_action: raise ValueError(sample["case_id"]+": suppress equals target")
        if a in seen: raise ValueError(sample["case_id"]+": duplicate suppress "+str(action_to_rc(a)))
        seen.add(a)
    state=torch.tensor(encode_state(board,current_player),dtype=torch.float32,device=device).unsqueeze(0)
    mask=torch.tensor(legal_np,dtype=torch.float32,device=device).unsqueeze(0)
    with torch.no_grad():
        logits,_=model(state)
        probs=masked_softmax(logits,mask)[0]
    logits0=logits[0]
    mask0=mask[0]
    target_logit=float(logits0[target_action].item())
    target_prob=float(probs[target_action].item())
    target_rank=int(rank_of_action(probs,target_action,mask0))
    suppress_records=[]
    hinges=[]
    for a in suppress_actions:
        gap=target_logit-float(logits0[a].item())
        hinge=max(0.0, margin-gap)
        hinges.append(hinge)
        suppress_records.append({"rc":action_to_rc(a),"action":a,"prob":float(probs[a].item()),"rank":int(rank_of_action(probs,a,mask0)),"gap":float(gap),"hinge":float(hinge),"is_primary":int(a==primary_action)})
    primary=next((r for r in suppress_records if r["is_primary"]), suppress_records[0])
    worst=min(suppress_records, key=lambda r: r["gap"])
    if loss_reduction == "max": row_loss=max(hinges)
    else: row_loss=float(np.mean(hinges))
    return {"case_id":sample["case_id"],"target_rc":sample["target_rc"],"target_prob":target_prob,"target_rank":target_rank,"suppress_count":len(suppress_actions),"primary_suppress_rc":primary["rc"],"primary_suppress_rank":primary["rank"],"primary_gap":primary["gap"],"worst_suppress_rc":worst["rc"],"worst_suppress_rank":worst["rank"],"worst_suppress_gap":worst["gap"],"multi_pair_hinge":float(row_loss)}

def write_csv(path, rows):
    path.parent.mkdir(parents=True,exist_ok=True)
    fields=["case_id","target_rc","target_prob","target_rank","suppress_count","primary_suppress_rc","primary_suppress_rank","primary_gap","worst_suppress_rc","worst_suppress_rank","worst_suppress_gap","multi_pair_hinge"]
    with path.open("w",newline="",encoding="utf-8") as f:
        w=csv.DictWriter(f,fieldnames=fields,lineterminator="\n")
        w.writeheader()
        for r in rows: w.writerow({k:r[k] for k in fields})

def write_report(path, args, dataset, rows, anchor_count):
    path.parent.mkdir(parents=True,exist_ok=True)
    ranks=[int(r["target_rank"]) for r in rows]
    primary_gaps=[float(r["primary_gap"]) for r in rows]
    worst_gaps=[float(r["worst_suppress_gap"]) for r in rows]
    losses=[float(r["multi_pair_hinge"]) for r in rows]
    counts=[int(r["suppress_count"]) for r in rows]
    out=[]
    out += ["# Policy-only multi-suppress dry-run report",""]
    out += ["## Scope","","- Dry-run only: no optimizer, no training, no checkpoint save.",f"- Dataset: `{args.dataset}`",f"- Init checkpoint: `{args.init_checkpoint}`",f"- Anchor snapshots: `{args.anchor_snapshots}`",f"- Margin: `{args.margin}`",f"- Loss reduction: `{args.loss_reduction}`",""]
    out += ["## Summary","","| metric | value |","|---|---:|"]
    pairs=[("rows",len(rows)),("anchor rows",anchor_count),("suppress count min",min(counts)),("suppress count mean",round(float(np.mean(counts)),3)),("suppress count max",max(counts)),("top3 target rows",sum(x<=3 for x in ranks)),("top5 target rows",sum(x<=5 for x in ranks)),("top10 target rows",sum(x<=10 for x in ranks)),("target rank > 10",sum(x>10 for x in ranks)),("target rank > 50",sum(x>50 for x in ranks)),("mean target rank",round(float(np.mean(ranks)),3)),("mean primary gap",round(float(np.mean(primary_gaps)),6)),("mean worst suppress gap",round(float(np.mean(worst_gaps)),6)),("median worst suppress gap",round(float(np.median(worst_gaps)),6)),("mean multi-pair hinge",round(float(np.mean(losses)),6))]
    for k,v in pairs: out.append(f"| {k} | {v} |")
    out += ["","## Worst suppress gaps","","| case_id | target_rank | suppress_count | primary_gap | worst_suppress_gap | worst_suppress_rc |","|---|---:|---:|---:|---:|---|"]
    for r in sorted(rows,key=lambda x:float(x["worst_suppress_gap"]))[:15]: out.append(f"| {r['case_id']} | {r['target_rank']} | {r['suppress_count']} | {r['primary_gap']:.6f} | {r['worst_suppress_gap']:.6f} | `{r['worst_suppress_rc']}` |")
    out += ["","## High target-rank tail","","| case_id | target_rank | target_prob | primary_gap | worst_suppress_gap |","|---|---:|---:|---:|---:|"]
    for r in sorted([x for x in rows if int(x["target_rank"])>10],key=lambda x:int(x["target_rank"]),reverse=True): out.append(f"| {r['case_id']} | {r['target_rank']} | {r['target_prob']:.8f} | {r['primary_gap']:.6f} | {r['worst_suppress_gap']:.6f} |")
    out += ["","## Interpretation","","The multi-suppress dataset can be loaded and legally scored. This is still dry-run only. Training should only be implemented after this schema and diagnostics are accepted.","","## Status","","Dry-run only. No training, no checkpoint, no C export, no public benchmark, no promotion.",""]
    path.write_text("\n".join(out),encoding="utf-8")

def main():
    args=parse_args()
    device=torch.device("cuda" if torch.cuda.is_available() else "cpu")
    dataset,samples=load_dataset(args.dataset)
    anchors=load_anchor_samples(args.anchor_snapshots)
    model=load_model(args.init_checkpoint,device)
    model.eval()
    rows=[diagnose(model,s,device,args.margin,args.loss_reduction) for s in samples]
    write_csv(args.out_csv,rows)
    write_report(args.out_report,args,dataset,rows,len(anchors))
    ranks=[int(r["target_rank"]) for r in rows]
    worst=[float(r["worst_suppress_gap"]) for r in rows]
    print("device:",device)
    print("dataset:",args.dataset)
    print("init_checkpoint:",args.init_checkpoint)
    print("rows:",len(rows))
    print("anchor_rows:",len(anchors))
    print("target_rank_top3:",sum(x<=3 for x in ranks))
    print("target_rank_top5:",sum(x<=5 for x in ranks))
    print("target_rank_top10:",sum(x<=10 for x in ranks))
    print("target_rank_gt10:",sum(x>10 for x in ranks))
    print("target_rank_gt50:",sum(x>50 for x in ranks))
    print("mean_worst_suppress_gap:","{:.6f}".format(float(np.mean(worst))))
    print("median_worst_suppress_gap:","{:.6f}".format(float(np.median(worst))))
    print("out_csv:",args.out_csv)
    print("out_report:",args.out_report)
    print("dry-run only; not training or saving checkpoint")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())

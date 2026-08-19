#!/usr/bin/env python3
"""리뷰 커버리지 원장 — 이 env 에 **적용되는** 시나리오 전수와 각 완료여부를 표로 낸다.

operator 최대 실수 = 첫 턴에 이 표를 안 만들고 "몇 개 대표로" 쓰고 완료 선언(6/25=24%).
review-scenario 스킬은 **작업 전 이걸 먼저 실행**해서 적용 대상을 못박고, 끝날 때 다시 실행해
**전부 ✅/⛔ 아니면 완료 아님**을 강제한다.

사용:  coverage_ledger.py --env <envname> --session <session_folder> [--json]
  · env 변형(exp-open/exp-close/inline/llm)은 API(:8080)에서 type+enforce_proxy 로 계산.
  · 적용 = 시나리오 envs 에 그 변형 또는 'ALL' 포함.
  · 완료 = 세션 폴더에 그 id 리포트 존재. 커스텀(C…-*)으로 대체했으면 note 로 표기.
"""
import argparse, json, os, sys, urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))  # …/SDSreviewBLUE
REGISTRY = os.path.join(REPO, "AgentReviewPlugin", "scenario", "registry.json")
SESSIONS = os.path.join(REPO, "Auto_Report", "sessions")
API = os.environ.get("AGENTREVIEW_API", "http://localhost:8080/api/v1").rstrip("/")


def env_variant(envname):
    """API 에서 env 를 읽어 시나리오 envs 와 대조할 변형 문자열을 만든다."""
    try:
        with urllib.request.urlopen(f"{API}/envs", timeout=8) as r:
            envs = json.load(r)
    except Exception as e:
        return None, f"env 조회 실패({type(e).__name__}) — API({API}) 떠있나?"
    e = next((x for x in envs if x.get("name") == envname), None)
    if not e:
        return None, f"env '{envname}' 없음. 있는 것: {[x['name'] for x in envs]}"
    t = (e.get("type") or "").lower()
    opts = e.get("options") or {}
    if t == "gateway":
        return "llm", None
    if t == "inline":
        return "inline", None
    # explicit / mdm / azure → 프록시강제 여부로 exp-open/close
    return ("exp-close" if opts.get("enforce_proxy") else "exp-open"), None


def applies(scn, variant):
    envs = [str(x).lower() for x in scn.get("envs", ["all"])]
    return "all" in envs or variant in envs or "compare" in envs


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--env", required=True)
    ap.add_argument("--session", required=True)
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()

    variant, err = env_variant(a.env)
    if err:
        print("🚨", err); sys.exit(2)

    reg = json.load(open(REGISTRY, encoding="utf-8"))
    scns = reg["scenarios"]
    applicable = [s for s in scns if applies(s, variant)]

    sess_dir = os.path.join(SESSIONS, a.session)
    done_ids = set()
    extras = []
    if os.path.isdir(sess_dir):
        for name in os.listdir(sess_dir):
            if os.path.isfile(os.path.join(sess_dir, name, "report.json")) or \
               os.path.isfile(os.path.join(sess_dir, name, "report.html")):
                done_ids.add(name)
    reg_ids = {s["id"] for s in scns}
    extras = sorted(d for d in done_ids if d not in reg_ids)  # 등록 외(커스텀 대체)

    order = {"S0": 0, "S1": 1, "S2": 2, "S3": 3, "C1": 4, "C": 4}
    applicable.sort(key=lambda s: (order.get(s["id"].split("-")[0], 9), s["id"]))

    rows = []
    for s in applicable:
        status = "done" if s["id"] in done_ids else "todo"
        rows.append({"id": s["id"], "group": s["id"].split("-")[0],
                     "label": s.get("label", ""), "criterion": s.get("criterion", ""),
                     "envs": s.get("envs", []), "status": status})
    n_done = sum(1 for r in rows if r["status"] == "done")

    if a.json:
        print(json.dumps({"env": a.env, "variant": variant, "session": a.session,
                          "applicable": len(rows), "done": n_done,
                          "todo": len(rows) - n_done, "extras": extras, "rows": rows},
                         ensure_ascii=False, indent=1))
        return

    print(f"# 리뷰 커버리지 원장 — env={a.env} (변형: {variant}) · session={a.session}")
    print(f"# 적용 시나리오 {len(rows)}개 · 완료 {n_done} · 미완료 {len(rows)-n_done}\n")
    print(f"{'상태':<4} {'시나리오':<26} {'기준':<10} label")
    print("-" * 78)
    for r in rows:
        mark = "✅" if r["status"] == "done" else "⬜"
        print(f"{mark:<3} {r['id']:<26} {r['criterion']:<10} {r['label'][:34]}")
    if extras:
        print(f"\n[등록 외 커스텀(대체로 인정 가능)]: {extras}")
    if n_done < len(rows):
        todo = [r["id"] for r in rows if r["status"] == "todo"]
        print(f"\n🚨 미완료 {len(todo)}개 — 이거 다 ✅/⛔ 되기 전엔 '완료' 아님:")
        print("   " + " ".join(todo))
    else:
        print("\n✅ 적용 시나리오 전수 완료.")


if __name__ == "__main__":
    main()

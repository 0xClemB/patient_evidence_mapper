from dataclasses import dataclass, asdict
from typing import List, Dict, Any
import pandas as pd

DATA_DIR = "app/backend/data"

@dataclass
class PatientProfile:
    age: int
    sex: str
    disease: str
    disease_activity: str
    comorbidities: List[str]
    prior_treatments: List[str]
    pregnancy_planning: bool = False
    smoking: bool = False
    def to_dict(self): return asdict(self)

def _load(name: str) -> pd.DataFrame:
    return pd.read_csv(f"{DATA_DIR}/{name}.csv")

def _contains_any(text: str, keywords: List[str]) -> bool:
    t = (text or "").lower()
    return any(k.lower() in t for k in keywords if k)

def score_guideline(p: PatientProfile, row: pd.Series):
    if p.disease.lower() != str(row["disease"]).lower():
        return 0.0, ["Different disease"]
    score, reasons = 1.0, ["Disease matches"]
    if "2L" in str(row.get("line_of_therapy","")) and any("methotrexate" in t.lower() or "csdmard" in t.lower() for t in p.prior_treatments):
        score += 0.5; reasons.append("Prior csDMARD suggests 2L fit")
    if p.disease_activity.lower() in str(row.get("population","")).lower():
        score += 0.3; reasons.append("Population mentions disease activity")
    if p.pregnancy_planning and _contains_any(row.get("comorbidity_cautions",""), ["pregnancy","mtx","methotrexate"]):
        score += 0.2; reasons.append("Includes pregnancy cautions")
    for c in p.comorbidities:
        if _contains_any(row.get("comorbidity_cautions",""), [c]):
            score -= 0.3; reasons.append(f"Caution: {c}")
    try:
        # recency boost
        recency_years = max(0, (pd.to_datetime(row.get("date")) - pd.Timestamp("2020-01-01")).days/365.0)
        score += min(0.3, recency_years/10)
    except Exception: pass
    return round(score,3), reasons

def score_trial(p: PatientProfile, row: pd.Series):
    if p.disease.lower() != str(row["disease"]).lower():
        return 0.0, ["Different disease"]
    score, reasons = 1.0, ["Disease matches"]
    pop = " ".join([str(row.get("population","")), str(row.get("title",""))]).lower()
    if ("csdmard" in pop or "methotrexate" in pop or "mtx" in pop) and any(("methotrexate" in t.lower()) or ("csdmard" in t.lower()) for t in p.prior_treatments):
        score += 0.5; reasons.append("Matches MTX/csDMARD inadequate response")
    if p.age >= 65 and _contains_any(str(row.get("key_cautions","")), ["vte","thrombosis","mace"]):
        score -= 0.3; reasons.append("Elderly with VTE/CV caution")
    if any(_contains_any(str(row.get("key_cautions","")), [c]) for c in p.comorbidities):
        score -= 0.2; reasons.append("Comorbidity caution in trial")
    try:
        yr = int(row.get("year")); score += min(0.2, max(0,(yr-2018)/50))
    except Exception: pass
    return round(score,3), reasons

def find_evidence(p: PatientProfile, top_k=5):
    gl = _load("guidelines"); tr = _load("trials"); dr = _load("drugs")
    gl_scores = []
    for _, r in gl.iterrows():
        s, reasons = score_guideline(p, r)
        if s>0: gl_scores.append({**r.to_dict(), "score":s, "reasons":reasons})
    tr_scores = []
    for _, r in tr.iterrows():
        s, reasons = score_trial(p, r)
        if s>0: tr_scores.append({**r.to_dict(), "score":s, "reasons":reasons})
    gl_scores = sorted(gl_scores, key=lambda x:x["score"], reverse=True)[:top_k]
    tr_scores = sorted(tr_scores, key=lambda x:x["score"], reverse=True)[:top_k]
    drugs = []
    for t in tr_scores:
        name = str(t.get("intervention","")).split()[0].strip(",;").lower()
        drow = dr[dr["name"].str.lower()==name]
        if not drow.empty:
            drugs.append({**drow.iloc[0].to_dict(), "source_trial": t.get("id")})
    return {"guidelines": gl_scores, "trials": tr_scores, "drugs": drugs}

def contraindication_flags(p: PatientProfile, drugs_df: pd.DataFrame):
    flags = []
    for _, row in drugs_df.iterrows():
        drug = row["name"]; ci = str(row.get("contraindications","")).lower(); bb = str(row.get("black_box",""))
        for c in p.comorbidities:
            if c and c.lower() in ci:
                flags.append({"drug":drug, "flag":f"Contraindicated with comorbidity: {c}"})
        if p.age >= 65 and any(k in bb.lower() for k in ["thrombosis","mace"]):
            flags.append({"drug":drug, "flag":"Elderly patient – boxed warning mentions thrombosis/MACE"})
        if p.pregnancy_planning and any(k in ci for k in ["pregnancy","teratogenic","methotrexate","mtx"]):
            flags.append({"drug":drug, "flag":"Pregnancy planning: verify teratogenic risks"})
    return {"flags": flags}

def summarize_guideline(g):
    return {"id": g["id"], "summary": f"{g['recommendation']} Monitoring: {g['monitoring']} (Source: {g['source']})."}
def summarize_trial(t):
    return {"id": t["id"], "summary": f"{t['intervention']} vs {t['comparator']} – {t['primary_outcome']}: {t['result_summary']} (Phase {t['phase']}, {t['year']})."}
def generate_patient_plan(patient, guidelines, trials, drugs):
    points = []
    if patient.get("disease_activity","low").lower() in ["moderate","high"]:
        points.append("Treat-to-target; escalate if no remission by 3–6 months.")
    if any(d.get("moa")=="JAK inhibitor" for d in drugs):
        points.append("Assess VTE/CV risk before JAKs; consider TNF/non-JAK biologic if high risk.")
    if patient.get("pregnancy_planning"): points.append("Avoid teratogens; coordinate with obstetrics.")
    return {"plan_summary": " ".join(points) if points else "Optimize csDMARDs and reassess in 8–12 weeks.", "citations": [g["id"] for g in guidelines]+[t["id"] for t in trials]}

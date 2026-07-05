import json
import sys
from pathlib import Path

CBR_PATH = Path(__file__).parent.parent / "cbr_medico"
sys.path.insert(0, str(CBR_PATH))
from cbr_engine import load_cases, retrieve


def list_symptoms() -> dict:
    data = load_cases()
    return {"symptoms": data["symptoms"], "total": len(data["symptoms"])}


def search_medical_cases(symptoms: dict) -> dict:
    data = load_cases()
    symptom_list = data["symptoms"]

    query = {s: int(symptoms.get(s, 0)) for s in symptom_list}
    retrieved = retrieve(query, data, top_k=3)

    results = []
    for sim, case in retrieved:
        results.append({
            "case_id": case["id"],
            "similarity_pct": round(sim * 100, 1),
            "diagnosis": case["diagnosis"],
            "treatment": case["treatment"],
            "symptoms_present_in_case": [
                s for s in symptom_list if case["symptoms"].get(s, 0) == 1
            ],
        })

    present = [s for s, v in symptoms.items() if v]
    return {
        "query_symptoms_present": present,
        "top_matches": results,
        "note": "Ordered by cosine similarity (highest first).",
    }

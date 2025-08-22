from shapely.geometry import shape, Point
import json

# Load India's polygon once (at server start)
with open("data/india.geo.json") as f:
    india_geojson = json.load(f)
india_polygon = shape(india_geojson["features"][0]["geometry"])

def get_country_code(lat, lng):
    point = Point(lng, lat)  # Note: (lng, lat) order
    if india_polygon.contains(point):
        return "DOMESTIC"
    return "INTERNATIONAL"




# app/utils.py
from .models import CoachProfile
import numpy as np

SPECIALTY_VOCAB = [
    "Lose weight", "Get toned", "Increase muscle mass",
    "Improve health and longevity", "Improve as an athlete or competitor"
]

PERSONALITY_VOCAB = [
    "High energy","Knows when to give me tough love","Calm, cool and collected",
    "Always positive","Drill sergeant","Have a sense of humor",
    "Analytical and results-driven","Strictly business",
    "Go the extra mile to personalize my workouts"
]

def multi_hot(items, vocab):
    vec = np.zeros(len(vocab), dtype=float)
    idx = {t.lower(): i for i,t in enumerate(vocab)}
    for it in (items or []):
        i = idx.get(it.lower())
        if i is not None:
            vec[i] = 1.0
    return vec

def jaccard_distance(a, b):
    inter = np.sum((a==1) & (b==1))
    union = np.sum((a==1) | (b==1))
    return 1.0 - (inter/union) if union>0 else 1.0

def normalize_intensity(x): return (x-1)/4.0
def map_level(x): return {"junior":1,"senior":2,"elite":3}[x]

def featurize_coach(coach: CoachProfile):
    return {
        "gender": coach.gender,
        "coach_level": coach.coach_level,
        "intensity": coach.intensity_level,
        "spec_vec": multi_hot(coach.specialties or [], SPECIALTY_VOCAB),
        "pers_vec": multi_hot(coach.personality_traits or [], PERSONALITY_VOCAB),
        "exp_norm": float(coach.experience) / 10.0  # simple scaling, tune later
    }

def featurize_user(user_json: dict):
    return {
        "gender_pref": user_json.get("gender_pref", "no preference"),
        "intensity": user_json.get("intensity", 3),
        "spec_vec": multi_hot(user_json.get("goals", []), SPECIALTY_VOCAB),
        "pers_vec": multi_hot(user_json.get("coach_style", []), PERSONALITY_VOCAB),
        "level_pref": user_json.get("level_pref", "senior"),
        "exp_pref": 0.0  # not from quiz now, can extend later
    }

def custom_distance(user, coach, user_has_injury: bool):
    w_gender, w_injury, w_intensity = 4.0, 3.0, 2.0
    w_specs, w_pers, w_exp, w_lvl = 1.5, 1.0, 0.5, 0.5

    d_gender = 0.0 if (user["gender_pref"]=="no preference" or user["gender_pref"]==coach["gender"]) else 1.0
    d_injury = 1.0 if (user_has_injury and coach["coach_level"]!="elite") else 0.0
    d_intensity = abs(normalize_intensity(user["intensity"]) - normalize_intensity(coach["intensity"]))
    d_specs = jaccard_distance(user["spec_vec"], coach["spec_vec"])
    d_pers  = jaccard_distance(user["pers_vec"], coach["pers_vec"])
    d_exp = abs(user["exp_pref"] - coach["exp_norm"])
    d_lvl = abs(map_level(user["level_pref"]) - map_level(coach["coach_level"])) / 2.0

    return (w_gender*d_gender + w_injury*d_injury + w_intensity*d_intensity
            + w_specs*d_specs + w_pers*d_pers + w_exp*d_exp + w_lvl*d_lvl)

def recommend_coaches(user_json: dict, k=4):
    user = featurize_user(user_json)
    has_injury = user_json.get("has_injury", False)

    coaches = CoachProfile.objects.all()
    scored = []
    for c in coaches:
        coach_vec = featurize_coach(c)
        dist = custom_distance(user, coach_vec, has_injury)
        scored.append((dist, c))
    scored.sort(key=lambda x: x[0])
    return [c for _,c in scored[:k]]

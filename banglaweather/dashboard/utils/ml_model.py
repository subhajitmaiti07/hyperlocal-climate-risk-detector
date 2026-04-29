import os
import joblib
import numpy as np
import pandas as pd

# =========================
# LOAD MODELS
# =========================
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
MODEL_DIR = os.path.join(BASE_DIR, "models_store")

heat_model = joblib.load(os.path.join(MODEL_DIR, "heat_model.pkl"))
storm_model = joblib.load(os.path.join(MODEL_DIR, "thunderstorm_model.pkl"))
pollution_model = joblib.load(os.path.join(MODEL_DIR, "pollution_model.pkl"))
storm_pct_model = joblib.load(os.path.join(MODEL_DIR, "thunderstorm_xgb_model.pkl"))

# =========================
# THRESHOLDS
# =========================
HEAT_HIGH_THRESHOLD = 0.30
HEAT_MED_THRESHOLD = 0.40
STORM_THRESHOLD = 0.30

# =========================
# SAFE INPUT BUILDER
# =========================
def build_input(sample, features):
    values = []
    for col in features:
        if col in sample:
            values.append(sample[col])
        else:
            if col in ["pressure_trend", "precip_mm"]:
                values.append(0)
            elif col == "city_encoded":
                values.append(1)
            elif col == "solar_radiation_Wm2":
                values.append(500)
            else:
                values.append(0)
    return np.array([values])

# =========================
# MAIN PREDICTION
# =========================
def predict_all(weather, air):

    if not weather:
        return None

    weather_df = pd.DataFrame([weather])

    # 🔥 HEAT
    heat_df = weather_df[
        ["temperature_C", "humidity_pct", "hour", "wind_speed_ms", "heat_index"]
    ]

    heat_probs = heat_model.predict_proba(heat_df)[0]

    if heat_probs[2] > HEAT_HIGH_THRESHOLD:
        heat_pred = 2
    elif heat_probs[1] > HEAT_MED_THRESHOLD:
        heat_pred = 1
    else:
        heat_pred = 0

    # 🌩️ STORM RISK
    storm_df = weather_df[
        ["humidity_pct","cloud_cover_pct","wind_speed_ms","hour","pressure_hPa","pressure_trend"]
    ].fillna(0)

    storm_prob = storm_model.predict_proba(storm_df)[0][1]
    storm_pred = 1 if storm_prob > STORM_THRESHOLD else 0

    # 🌫️ POLLUTION
    pollution_pred = 0

    if air:
        air_df = pd.DataFrame([air])

        pollution_df = air_df[
            ["PM2_5_ugm3","PM10_ugm3","NO2_ugm3","CO_ugm3",
             "SO2_ugm3","O3_ugm3","humidity_pct","wind_speed_ms","month","hour"]
        ]

        pollution_probs = pollution_model.predict_proba(pollution_df)[0]

        if pollution_probs[2] > 0.7:
            pollution_pred = 2
        elif pollution_probs[1] > 0.4:
            pollution_pred = 1
        else:
            pollution_pred = 0

    # ⚡ THUNDERSTORM %
    storm_pct_features = [
        'lat','lon','temperature_C','humidity_pct','pressure_hPa',
        'dew_point_C','pressure_trend','solar_radiation_Wm2',
        'wind_speed_ms','cloud_cover_pct','hour','month',
        'wind_direction_deg','wind_dir_sin','wind_dir_cos',
        'et0_mm','precip_mm','city_encoded'
    ]

    X_storm_pct = build_input(weather, storm_pct_features)
    storm_pct = float(storm_pct_model.predict_proba(X_storm_pct)[0][1])

    # smoothing
    storm_pct = 0.7 * storm_pct + 0.15

    return {
        "heat": int(heat_pred),
        "storm": int(storm_pred),
        "pollution": int(pollution_pred),
        "storm_prob": round(storm_pct * 100, 2)
    }
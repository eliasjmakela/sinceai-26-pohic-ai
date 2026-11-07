"""H1 hopper-stage weighing: the per-charge error model, single source of truth for calc/ and scripts/.

Measured charge  m_hat_i = g * (1 - w_i) * m_i * miss_i + e_i      (differential reading: before minus after stroke)
  g      gain of the plate cells after commissioning with test weights; residual sd SIGMA_G0
  w_i    share of the charge NOT carried by the plate when read (wedged against the hopper walls, resting on the ram
         top, bypassing the plate). w_i = W_MAT[material] + delta_device + c_container + s * z_i
  miss_i 0 with probability P_MISS (stroke started before a stable reading), else 1
  e_i    reading noise, sd sqrt(2) * SIGMA_READ_KG (two readings per difference)
Every value is a TEAM ESTIMATE (no hardware exists); low / mid / high bracket our uncertainty. The per-material
mean bridging share is the least known number and the main reason H1 needs fleet self-calibration (H2).
"""

W_MAT = {  # mean share of a charge not carried by the plate at reading time (team estimate)
    "cardboard": 0.06, "plastic_film": 0.05, "mixed_plastic": 0.05,
    "paper": 0.03, "mixed_waste": 0.03, "biowaste": 0.01,
}
CHARGE_KG = {  # kit configs/assumptions.yaml materials.*.input_event_kg (median mass of one loading cycle)
    "cardboard": 18, "paper": 22, "plastic_film": 9, "mixed_plastic": 8, "mixed_waste": 25, "biowaste": 30,
}
CONTAINER_KG = {  # rounded median shared-ticket net per material in the competition data (scripts/charge_sum.py)
    "cardboard": 3000, "paper": 1250, "plastic_film": 1000, "mixed_plastic": 750, "mixed_waste": 2500, "biowaste": 1400,
}
CHARGE_CV = 0.6   # coefficient of variation of charge mass (data p10-p90 of kg per compaction cycle, charge_sum.py)

LEVELS = ("low", "mid", "high")
P = {  # low / mid / high
    "SIGMA_READ_KG": {"low": 0.3, "mid": 0.5, "high": 1.0},   # per reading, at rest, 2-3 s average
    "S_CHARGE":      {"low": 0.05, "mid": 0.10, "high": 0.20},  # per-charge spread of the bridging share
    "TAU_DEVICE":    {"low": 0.02, "mid": 0.03, "high": 0.05},  # device-to-device spread of the bridging share
    "C_CONTAINER":   {"low": 0.02, "mid": 0.03, "high": 0.05},  # container-to-container spread (mix, moisture, users)
    "SIGMA_G0":      {"low": 0.005, "mid": 0.01, "high": 0.02}, # gain residual after test-weight commissioning
    "P_MISS":        {"low": 0.005, "mid": 0.01, "high": 0.03}, # strokes without a valid reading pair
    "W_MAT_REL_UNC": {"low": 0.3, "mid": 0.5, "high": 1.0},     # how wrong our W_MAT guess may be (relative)
    "DRIFT_PER_MONTH": {"low": 0.003, "mid": 0.005, "high": 0.01},  # gain random walk (debris, wear), sd per month
}

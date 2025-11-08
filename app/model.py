import json
import numpy as np
import cv2
from .preprocess_extract import extract_features, extract_features,detect_reference_patches,illumination_normalization,order_points,detect_paper_and_crop,correct_orientation,load_image 

# Este arquivo implementa o pipeline mínimo: carga, detecção simples de retângulo, extração de média RGB

def analyze_image(path: str) -> dict:
    img = load_image(path)

    oriented = correct_orientation(img)
    cropped = detect_paper_and_crop(oriented)
    norm = illumination_normalization(cropped)
    features = extract_features(norm)

    # Modelo placeholder: usa relação linear simples (apenas POC)
    # Substituir por modelo treinado.
    estimate_mg_dl = max(20.0, min(600.0, 1.5 * features['mean_r'] - 0.8 * features['mean_g'] + 0.3 * features['mean_b']))

    result = {
        "glucose_mg_dl": round(estimate_mg_dl, 1),
        "range": categorize(estimate_mg_dl),
        "confidence": 0.6,
        "features": features,
        "processing_steps": ["load","resize","lab_mean","simple_regression"]
    }

    return result


def categorize(val: float) -> str:
    if val < 70:
        return "hipoglicemia"
    if val < 140:
        return "normal"
    if val < 200:
        return "pré-diabetes"
    return "hiperglicemia"
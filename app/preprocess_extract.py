import cv2
import numpy as np
import json

def load_image(path):
    img = cv2.imread(path)
    if img is None:
        raise ValueError('imagem inválida')
    return img

def correct_orientation(img):
    # placeholder: usar EXIF se disponível; aqui assumimos já orientada
    return img

def detect_paper_and_crop(img):
    # converte para gray, blur, edges
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (5,5), 0)
    edged = cv2.Canny(blur, 50, 150)

    contours, _ = cv2.findContours(edged, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
    contours = sorted(contours, key=cv2.contourArea, reverse=True)[:10]
    paper_cnt = None
    for c in contours:
        peri = cv2.arcLength(c, True)
        approx = cv2.approxPolyDP(c, 0.02 * peri, True)
        if len(approx) == 4:
            paper_cnt = approx
            break
    if paper_cnt is None:
        # fallback: retorna imagem inteira
        return img

    pts = paper_cnt.reshape(4, 2)
    rect = order_points(pts)
    (tl, tr, br, bl) = rect
    widthA = np.linalg.norm(br - bl)
    widthB = np.linalg.norm(tr - tl)
    maxWidth = max(int(widthA), int(widthB))

    heightA = np.linalg.norm(tr - br)
    heightB = np.linalg.norm(tl - bl)
    maxHeight = max(int(heightA), int(heightB))

    dst = np.array([[0,0],[maxWidth-1,0],[maxWidth-1,maxHeight-1],[0,maxHeight-1]], dtype='float32')
    M = cv2.getPerspectiveTransform(rect, dst)
    warped = cv2.warpPerspective(img, M, (maxWidth, maxHeight))
    return warped


def order_points(pts):
    rect = np.zeros((4,2), dtype='float32')
    s = pts.sum(axis=1)
    rect[0] = pts[np.argmin(s)]
    rect[2] = pts[np.argmax(s)]
    diff = np.diff(pts, axis=1)
    rect[1] = pts[np.argmin(diff)]
    rect[3] = pts[np.argmax(diff)]
    return rect


def illumination_normalization(img):
    # converte para LAB e aplica CLAHE no canal L
    lab = cv2.cvtColor(img, cv2.COLOR_BGR2LAB)
    L, a, b = cv2.split(lab)
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
    L2 = clahe.apply(L)
    lab2 = cv2.merge((L2, a, b))
    corrected = cv2.cvtColor(lab2, cv2.COLOR_LAB2BGR)
    return corrected


def detect_reference_patches(img, expected_count=4):
    # implementação simplificada: procurar pequenos retângulos com borda preta branca
    # Na prática: usar QR code + posições conhecidas, ou detecção por cor.
    return []


def extract_features(img):
    lab = cv2.cvtColor(img, cv2.COLOR_BGR2LAB)
    mean_bgr = cv2.mean(img)[:3]
    mean_lab = cv2.mean(lab)[:3]
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    mean_hsv = cv2.mean(hsv)[:3]

    features = {
        'mean_b': float(mean_bgr[0]),
        'mean_g': float(mean_bgr[1]),
        'mean_r': float(mean_bgr[2]),
        'mean_L': float(mean_lab[0]),
        'mean_a': float(mean_lab[1]),
        'mean_b_lab': float(mean_lab[2]),
        'mean_h': float(mean_hsv[0]),
        'mean_s': float(mean_hsv[1]),
        'mean_v': float(mean_hsv[2]),
        'rg_ratio': float(mean_bgr[2]/(mean_bgr[1]+1e-6)),
        'rb_ratio': float(mean_bgr[2]/(mean_bgr[0]+1e-6))
    }
    return features

if __name__ == '__main__':
    import sys
    img = load_image(sys.argv[1])
    oriented = correct_orientation(img)
    cropped = detect_paper_and_crop(oriented)
    norm = illumination_normalization(cropped)
    features = extract_features(norm)
    print(json.dumps(features, indent=2))
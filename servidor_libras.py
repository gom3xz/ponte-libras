from collections import deque
import os
import threading
import time
import cv2
from flask import Flask, Response, jsonify, request
from flask_cors import CORS
import joblib
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
from sklearn.neighbors import KNeighborsClassifier

app = Flask(__name__)
CORS(app)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(BASE_DIR, "hand_landmarker.task")
CLASSIFIER_PATH = os.path.join(BASE_DIR, "modelo_libras.joblib")
CONFIDENCE_THRESHOLD = 0.45
HISTORY_SIZE = 8

HAND_CONNECTIONS = [
    (0, 1), (1, 2), (2, 3), (3, 4),
    (0, 5), (5, 6), (6, 7), (7, 8),
    (5, 9), (9, 10), (10, 11), (11, 12),
    (9, 13), (13, 14), (14, 15), (15, 16),
    (13, 17), (0, 17), (17, 18), (18, 19), (19, 20),
]

camera_running = False
current_label = "Nenhum sinal"
lock = threading.Lock()
cap = None
last_landmarks = None
TRAINING_SAMPLES = {}


def _resumo_amostras():
    if not TRAINING_SAMPLES:
        return "Pronto para capturar amostras."
    partes = [f"{k}: {len(v)}" for k, v in TRAINING_SAMPLES.items()]
    return "Amostras → " + " | ".join(partes)


def draw_hand(image, landmarks):
    h, w, _ = image.shape
    points = [(int(lm.x * w), int(lm.y * h)) for lm in landmarks]
    for start_idx, end_idx in HAND_CONNECTIONS:
        cv2.line(image, points[start_idx], points[end_idx], (0, 255, 0), 2)
    for pt in points:
        cv2.circle(image, pt, 4, (0, 0, 255), -1)


def extract_features(landmarks):
    base_x = landmarks[0].x
    base_y = landmarks[0].y
    base_z = landmarks[0].z

    features = []
    max_dist = 0.0

    for lm in landmarks:
        dx = lm.x - base_x
        dy = lm.y - base_y
        dz = lm.z - base_z
        features.extend([dx, dy, dz])
        dist = (dx ** 2 + dy ** 2 + dz ** 2) ** 0.5
        if dist > max_dist:
            max_dist = dist

    if max_dist > 0:
        features = [val / max_dist for val in features]

    return features


def generate_frames():
    global camera_running, current_label, cap, last_landmarks

    if not os.path.exists(MODEL_PATH):
        raise FileNotFoundError("hand_landmarker.task não encontrado na pasta do projeto.")

    if os.path.exists(CLASSIFIER_PATH):
        classifier = joblib.load(CLASSIFIER_PATH)
    else:
        classifier = None

    base_options = python.BaseOptions(model_asset_path=MODEL_PATH)
    options = vision.HandLandmarkerOptions(
        base_options=base_options,
        running_mode=vision.RunningMode.VIDEO,
        num_hands=1,
        min_hand_detection_confidence=0.6,
        min_hand_presence_confidence=0.6,
        min_tracking_confidence=0.6,
    )

    cap = cv2.VideoCapture(0)
    start_time = time.monotonic()
    recent_preds = deque(maxlen=HISTORY_SIZE)

    with vision.HandLandmarker.create_from_options(options) as landmarker:
        while camera_running and cap.isOpened():
            success, frame = cap.read()
            if not success:
                break

            flipped = cv2.flip(frame, 1)
            rgb_image = cv2.cvtColor(flipped, cv2.COLOR_BGR2RGB)
            mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_image)

            timestamp_ms = int((time.monotonic() - start_time) * 1000)
            result = landmarker.detect_for_video(mp_image, timestamp_ms)

            detected_text = "Nenhum sinal"

            if result.hand_landmarks:
                hand_landmarks = result.hand_landmarks[0]
                with lock:
                    last_landmarks = hand_landmarks
                draw_hand(flipped, hand_landmarks)

                if classifier is not None:
                    features = extract_features(hand_landmarks)
                    probs = classifier.predict_proba([features])[0]
                    best_idx = probs.argmax()
                    confidence = probs[best_idx]
                    label = classifier.classes_[best_idx]

                    if confidence >= CONFIDENCE_THRESHOLD:
                        recent_preds.append(label)
                        detected_text = max(set(recent_preds), key=recent_preds.count)
                    else:
                        recent_preds.clear()
                        detected_text = "Incerto"
                else:
                    detected_text = "Modelo não treinado"
            else:
                recent_preds.clear()
                with lock:
                    last_landmarks = None

            with lock:
                current_label = detected_text

            ret, buffer = cv2.imencode(".jpg", flipped)
            if not ret:
                continue

            frame_bytes = buffer.tobytes()
            yield (
                b"--frame\r\n"
                b"Content-Type: image/jpeg\r\n\r\n" + frame_bytes + b"\r\n"
            )

    if cap is not None:
        cap.release()
        cap = None


@app.route("/start", methods=["POST"])
def start_camera():
    global camera_running
    camera_running = True
    return jsonify({"status": "started"})


@app.route("/stop", methods=["POST"])
def stop_camera():
    global camera_running, current_label, cap, last_landmarks
    camera_running = False
    with lock:
        current_label = "Nenhum sinal"
        last_landmarks = None
    if cap is not None:
        cap.release()
        cap = None
    return jsonify({"status": "stopped"})


@app.route("/video_feed")
def video_feed():
    return Response(
        generate_frames(),
        mimetype="multipart/x-mixed-replace; boundary=frame",
    )


@app.route("/prediction")
def prediction():
    with lock:
        label = current_label
    return jsonify({"label": label})


@app.route("/train/sample", methods=["POST"])
def train_sample():
    dados = request.get_json(silent=True) or {}
    label = str(dados.get("label", "")).strip().upper()
    if not label:
        return jsonify({"summary": "Informe um rótulo."}), 400
    with lock:
        lms = last_landmarks
    if lms is None:
        return jsonify({"summary": "Nenhuma mão visível na câmera no momento."}), 400
    TRAINING_SAMPLES.setdefault(label, []).append(extract_features(lms))
    return jsonify({"summary": _resumo_amostras()})


@app.route("/train/fit", methods=["POST"])
def train_fit():
    if len(TRAINING_SAMPLES) < 2:
        return jsonify({"message": "Capture amostras de pelo menos 2 sinais antes de treinar."})
    X, y = [], []
    for label, amostras in TRAINING_SAMPLES.items():
        for feat in amostras:
            X.append(feat)
            y.append(label)
    clf = KNeighborsClassifier(n_neighbors=min(3, len(X)))
    clf.fit(X, y)
    joblib.dump(clf, CLASSIFIER_PATH)
    return jsonify({"message": f"modelo_libras.joblib atualizado com os sinais: {', '.join(TRAINING_SAMPLES.keys())}"})


@app.route("/train/clear", methods=["POST"])
def train_clear():
    TRAINING_SAMPLES.clear()
    return jsonify({"message": "Amostras temporárias limpas."})


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=False, threaded=True)
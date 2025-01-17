from flask import Flask, request, jsonify, render_template
import cv2
import numpy as np
import os
import logging

app = Flask(__name__)

# Set up logging for debugging
logging.basicConfig(level=logging.DEBUG)

# YOLO Configuration
YOLO_CONFIG = os.path.join(os.getcwd(), "yolov3.cfg")
YOLO_WEIGHTS = os.path.join(os.getcwd(), "yolov3.weights")
YOLO_CLASSES = os.path.join(os.getcwd(), "coco.names")

nutrition_data = {
    "banana": {"calories": 89, "carbs": 23, "protein": 1.1, "fat": 0.3, "fiber": 2.6, "vitamin_c": 8.7, "potassium": 358},
    "orange": {"calories": 62, "carbs": 15.4, "protein": 1.2, "fat": 0.2, "fiber": 3.1, "vitamin_c": 53.2, "potassium": 237},
    "apple": {"calories": 95, "carbs": 25, "protein": 0.5, "fat": 0.3, "fiber": 4.4, "vitamin_c": 8.4, "potassium": 195},
}

# Load YOLO model
net = cv2.dnn.readNet(YOLO_WEIGHTS, YOLO_CONFIG)
with open(YOLO_CLASSES, "r") as f:
    classes = f.read().strip().split("\n")


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/upload', methods=['POST'])
def upload_image():
    if 'image' not in request.files:
        return jsonify({"error": "No image file provided"}), 400

    file = request.files['image']
    if file.filename == '':
        return jsonify({"error": "No image selected"}), 400

    upload_folder = "static/uploads"
    if not os.path.exists(upload_folder):
        os.makedirs(upload_folder)  # Ensure the uploads directory exists

    file_path = os.path.join(upload_folder, file.filename)
    try:
        file.save(file_path)
        logging.debug(f"File saved at: {file_path}")
    except Exception as e:
        logging.error(f"Failed to save file: {str(e)}")
        return jsonify({"error": f"Failed to save file: {str(e)}"}), 500

    detections, nutrition = detect_objects(file_path)

    return jsonify({"detections": detections, "nutrition": nutrition})


def detect_objects(image_path):
    image = cv2.imread(image_path)
    height, width, _ = image.shape
    blob = cv2.dnn.blobFromImage(image, 1 / 255.0, (416, 416), swapRB=True, crop=False)
    net.setInput(blob)
    output_layers = [net.getLayerNames()[i - 1] for i in net.getUnconnectedOutLayers()]
    layer_outputs = net.forward(output_layers)

    conf_threshold = 0.5
    nms_threshold = 0.4
    boxes = []
    confidences = []
    labels = []

    for output in layer_outputs:
        for detection in output:
            scores = detection[5:]
            class_id = np.argmax(scores)
            confidence = scores[class_id]
            if confidence > conf_threshold:
                box = detection[:4] * np.array([width, height, width, height])
                (center_x, center_y, w, h) = box.astype("int")
                x = int(center_x - w / 2)
                y = int(center_y - h / 2)
                boxes.append([x, y, int(w), int(h)])
                confidences.append(float(confidence))
                labels.append(classes[class_id])

    indices = cv2.dnn.NMSBoxes(boxes, confidences, conf_threshold, nms_threshold)

    detected_items = []
    if len(indices) > 0:
        for i in indices.flatten():
            detected_items.append(labels[i])

    nutrition_summary = calculate_nutrition(detected_items)
    return detected_items, nutrition_summary


def calculate_nutrition(detections):
    total_calories = 0
    macros = {"Carbs": 0, "Protein": 0, "Fat": 0, "Fiber": 0}
    micros = {"Vitamin C": 0, "Potassium": 0}

    for label in detections:
        if label in nutrition_data:
            item_data = nutrition_data[label]
            total_calories += item_data["calories"]
            macros["Carbs"] += item_data["carbs"]
            macros["Protein"] += item_data["protein"]
            macros["Fat"] += item_data["fat"]
            macros["Fiber"] += item_data["fiber"]
            micros["Vitamin C"] += item_data["vitamin_c"]
            micros["Potassium"] += item_data["potassium"]

    return {
        "total_calories": total_calories,
        "macros": macros,
        "micros": micros
    }


if __name__ == "__main__":
    app.run(debug=True)

import cv2
import threading
from flask import Flask, request, jsonify
import numpy as np
import requests
import base64
import supervision as sv
from rfdetr import RFDETRLarge


class ImageProcessor:
    def __init__(self, model_checkpoint, server_url, flask_host='127.0.0.13', flask_port=8000):
        self.app = Flask(__name__)
        self.server_url = server_url.rstrip('/')  # make sure no double slash
        self.flask_host = flask_host
        self.flask_port = flask_port

        # Load model
        print("Loading RFDETRLarge model...")
        self.model = RFDETRLarge(pretrain_weights=model_checkpoint)
        self.model.optimize_for_inference()

        self.class_names = [
            "-",
            "circular_spline",    
            "wave_generator"    
        ]

        # Color palette
        self.color_palette = sv.ColorPalette.from_hex([
            "#ffff00", "#ff9b00", "#ff66ff", "#3399ff", "#ff66b2", "#ff8080",
            "#b266ff", "#9999ff", "#66ffff", "#33ff99", "#66ff66", "#99ff00"
        ])

        self._last_resolution = None
        self.bbox_annotator = None
        self.label_annotator = None

        self._register_routes()
        print(f"ImageProcessor initialized. Will listen on {flask_host}:{flask_port}")

    def _register_routes(self):
        self.app.add_url_rule('/bev_driver_capture', 'bev_driver', self.get_bev_driver_capture, methods=['POST'])
        self.app.add_url_rule('/right_robot_capture', 'right_robot', self.get_right_robot_capture, methods=['POST'])
        self.app.add_url_rule('/left_robot_capture', 'left_robot', self.get_left_robot_capture, methods=['POST'])
        self.app.add_url_rule('/third_person_camera_capture', 'third_person', self.get_third_person_camera_capture, methods=['POST'])

    def _ensure_annotators(self, frame):
        h, w = frame.shape[:2]
        current_res = (w, h)

        if self._last_resolution == current_res and self.bbox_annotator is not None:
            return

        self._last_resolution = current_res

        text_scale = sv.calculate_optimal_text_scale(resolution_wh=current_res)
        thickness = sv.calculate_optimal_line_thickness(resolution_wh=current_res)

        self.bbox_annotator = sv.BoxAnnotator(
            color=self.color_palette,
            thickness=thickness
        )
        self.label_annotator = sv.LabelAnnotator(
            color=self.color_palette,
            text_color=sv.Color.BLACK,
            text_scale=text_scale*1.4,
            text_thickness=max(1, thickness // 2),
        )

    def preprocess_and_encode_image(self, frame):
        success, buffer = cv2.imencode('.jpg', frame, [int(cv2.IMWRITE_JPEG_QUALITY), 85])
        if not success:
            raise RuntimeError("Failed to encode image to JPEG")
        img_bytes = buffer.tobytes()
        return base64.b64encode(img_bytes).decode('utf-8')

    def detect_and_annotate(self, frame):
        # Run inference
        results = self.model.predict(frame, threshold=0.8)  # lowered a bit – tune as needed

        if results is None or len(results) == 0:
            # return original + empty detections
            return frame, sv.Detections.empty()

        # Convert to supervision format
        detections = sv.Detections(
            xyxy=results.xyxy,
            confidence=results.confidence,
            class_id=results.class_id.astype(int)
        )

        # Create readable labels
        labels = []
        for class_id, confidence in zip(detections.class_id, detections.confidence):
            class_name = self.class_names[class_id] if 0 <= class_id < len(self.class_names) else f"cls_{class_id}"
            labels.append(f"{class_name} {confidence:.2f}")

        # Annotate
        self._ensure_annotators(frame)
        annotated = self.bbox_annotator.annotate(frame.copy(), detections)
        annotated = self.label_annotator.annotate(annotated, detections, labels)

        return annotated, detections

    def publish_image(self, frame, endpoint):
        try:
            url = f"{self.server_url}/{endpoint}"

            # Detect + annotate
            annotated_frame, _ = self.detect_and_annotate(frame)

            # Encode
            base64_image = self.preprocess_and_encode_image(annotated_frame)

            # Send
            payload = {"image": base64_image}
            response = requests.post(url, json=payload, timeout=6)

            if response.status_code in (200, 201):
                print(f"Published to {endpoint} (status {response.status_code})")
            else:
                print(f"Failed {endpoint} status {response.status_code} | {response.text[:120]}")

        except Exception as e:
            print(f"Error publishing to {endpoint}: {str(e)}")

    # ─── Flask handlers ────────────────────────────────────────

    def _handle_capture(self, capture_name):
        try:
            data = request.get_json(silent=True)
            if not data or "image" not in data:
                return jsonify({"error": "No 'image' field in JSON"}), 400

            base64_str = data["image"]
            img_bytes = base64.b64decode(base64_str)
            frame = cv2.imdecode(np.frombuffer(img_bytes, np.uint8), cv2.IMREAD_COLOR)

            if frame is None:
                return jsonify({"error": "Invalid image data"}), 400

            self.publish_image(frame, capture_name)
            return jsonify({"status": "ok"}), 200

        except Exception as e:
            return jsonify({"error": str(e)}), 500

    def get_bev_driver_capture(self):
        return self._handle_capture("bev_driver_capture")

    def get_right_robot_capture(self):
        return self._handle_capture("right_robot_capture")

    def get_left_robot_capture(self):
        return self._handle_capture("left_robot_capture")

    def get_third_person_camera_capture(self):
        return self._handle_capture("third_person_camera_capture")

    def run_server(self):
        print(f"Starting Flask → http://{self.flask_host}:{self.flask_port}")
        self.app.run(
            host=self.flask_host,
            port=self.flask_port,
            threaded=True,
            debug=False
        )

    def start(self):
        thread = threading.Thread(target=self.run_server, daemon=True)
        thread.start()


def main():
    processor = ImageProcessor(
        model_checkpoint="checkpoint_best_total.pth",
        server_url="http://localhost:6000",
        flask_host="127.0.0.13",           # ← most common choice
        flask_port=8000
    )

    processor.start()

    # Keep main thread alive
    print("Press Ctrl+C to stop...")
    try:
        while True:
            import time
            time.sleep(10)
    except KeyboardInterrupt:
        print("\nShutting down...")


if __name__ == "__main__":
    main()

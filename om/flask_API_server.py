import cv2
import numpy as np
import base64
from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import io

# Import your existing recognition and recreation functions
# Make sure image_rec.py and kolam_recreator.py are in the same directory
import image_rec as kolam_recognition 
import kolam_recreator as kolam_recreation

app = Flask(__name__)
CORS(app) # Enable Cross-Origin Resource Sharing

# --- Route for the home page ---
@app.route('/')
def home():
    """
    Serves the main ui.html file when a user visits the root URL.
    """
    # Corrected the filename to 'ui.html' to match your file
    return send_file('ui.html')

@app.route('/analyze', methods=['POST'])
def analyze_image():
    """
    API endpoint to analyze an uploaded Kolam image.
    It receives an image, runs the recognition logic, and returns the design principles.
    """
    if 'image' not in request.files:
        return jsonify({'error': 'No image file provided'}), 400
    
    file = request.files['image']
    
    in_memory_file = io.BytesIO()
    file.save(in_memory_file)
    data = np.frombuffer(in_memory_file.getvalue(), dtype=np.uint8)
    img = cv2.imdecode(data, cv2.IMREAD_COLOR)

    # --- ADDED ERROR HANDLING ---
    # If the image data is invalid, img will be None. This prevents the server from crashing.
    if img is None:
        return jsonify({'error': 'Could not decode image. Please upload a valid image file (e.g., PNG, JPG).'}), 400

    temp_image_path = "temp_uploaded_image.png"
    cv2.imwrite(temp_image_path, img)

    # --- Run Recognition Backend ---
    dots, _ = kolam_recognition.detect_dots(temp_image_path)
    contours, _ = kolam_recognition.detect_contours(temp_image_path)
    principles = kolam_recognition.analyze_principles(dots, contours, img.shape)

    return jsonify(principles)

@app.route('/recreate', methods=['POST'])
def recreate_image():
    """
    API endpoint to recreate a Kolam design from an uploaded image.
    It receives an image, runs the contour detection and recreation logic, 
    and returns the final recreated image.
    """
    if 'image' not in request.files:
        return jsonify({'error': 'No image file provided'}), 400
    
    file = request.files['image']
    in_memory_file = io.BytesIO()
    file.save(in_memory_file)
    data = np.frombuffer(in_memory_file.getvalue(), dtype=np.uint8)
    img = cv2.imdecode(data, cv2.IMREAD_COLOR)
    
    # --- ADDED ERROR HANDLING ---
    # Added the same check here for robustness.
    if img is None:
        return jsonify({'error': 'Could not decode image. Please upload a valid image file (e.g., PNG, JPG).'}), 400
    
    temp_image_path = "temp_uploaded_image.png"
    cv2.imwrite(temp_image_path, img)

    # --- Run Recreation Backend ---
    contours, _ = kolam_recognition.detect_contours(temp_image_path)
    recreated_design = kolam_recreation.recreate_kolam(contours, img.shape)

    # Encode the recreated image to be sent back to the frontend
    _, img_encoded = cv2.imencode('.png', recreated_design)
    
    return send_file(
        io.BytesIO(img_encoded.tobytes()),
        mimetype='image/png',
        as_attachment=False
    )

if __name__ == '__main__':
    # Runs the Flask app on http://127.0.0.1:5000
    print("Starting Flask server... Open http://127.0.0.1:5000 in your browser.")
    app.run(debug=False)


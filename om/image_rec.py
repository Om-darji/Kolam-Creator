import cv2
import numpy as np
import matplotlib.pyplot as plt
from sklearn.cluster import DBSCAN

def detect_dots(image_path):
    """
    Detects dots (pulli) in a Kolam image using more robust thresholding and blob detection.
    
    Args:
        image_path (str): The path to the input image file.

    Returns:
        tuple: A list of keypoints for the detected dots and the image with dots drawn on it.
    """
    img = cv2.imread(image_path, cv2.IMREAD_COLOR)
    if img is None:
        print(f"Error: Could not read image from {image_path}")
        return None, None

    # Convert to grayscale
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    
    # Use adaptive thresholding to better handle variations in lighting and color
    # This is much better than a simple global threshold for this kind of image.
    thresh = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                   cv2.THRESH_BINARY_INV, 11, 2)
    
    # Invert the threshold image so dots are white on a black background
    thresh = 255 - thresh

    # Set up the SimpleBlobDetector parameters for small white dots.
    params = cv2.SimpleBlobDetector_Params()

    # Filter by Area - looking for small dots now.
    params.filterByArea = True
    params.minArea = 5
    params.maxArea = 150

    # Filter by Circularity
    params.filterByCircularity = True
    params.minCircularity = 0.6

    # Filter by Convexity
    params.filterByConvexity = True
    params.minConvexity = 0.85

    # Filter by Inertia
    params.filterByInertia = True
    params.minInertiaRatio = 0.1

    detector = cv2.SimpleBlobDetector_create(params)
    keypoints = detector.detect(thresh)

    img_with_keypoints = cv2.drawKeypoints(img, keypoints, np.array([]), (0, 0, 255),
                                          cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS)

    print(f"Detected {len(keypoints)} dots.")
    return keypoints, img_with_keypoints


def detect_contours(image_path):
    """
    Detects the curves and loops in a Kolam image using contour detection,
    which is far more effective than straight line detection for this art form.
    
    Args:
        image_path (str): The path to the input image file.
        
    Returns:
        tuple: A list of detected contours and the image with contours drawn on it.
    """
    img = cv2.imread(image_path, cv2.IMREAD_COLOR)
    if img is None:
        return None, None
        
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    
    # Use inRange to better isolate only the whitest parts of the image (the lines)
    # This avoids detecting the orange decorations.
    thresh = cv2.inRange(gray, 200, 255)
    
    # Find contours in the thresholded image
    contours, _ = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    
    # Filter out very small contours that are likely noise
    min_contour_area = 50
    filtered_contours = [c for c in contours if cv2.contourArea(c) > min_contour_area]
    
    img_with_contours = img.copy()
    cv2.drawContours(img_with_contours, filtered_contours, -1, (0, 255, 0), 2)
        
    print(f"Detected {len(filtered_contours)} significant contours/curves.")
        
    return filtered_contours, img_with_contours


def analyze_principles(keypoints, contours, image_shape):
    """
    Analyzes the design principles from detected dots and contours.

    Args:
        keypoints (list): List of detected dot keypoints.
        contours (list): List of detected contours.
        image_shape (tuple): The shape of the original image (height, width).

    Returns:
        dict: A dictionary containing the analyzed principles.
    """
    if not keypoints:
        return {"error": "No dots to analyze."}

    coords = np.array([kp.pt for kp in keypoints])
    
    # --- FINAL, MORE ROBUST GRID DETECTION LOGIC ---
    # This uses clustering which is more reliable than calculating differences.
    # This will fix the black screen issue.
    if len(coords) > 1:
        # Find the number of rows by clustering the Y-coordinates.
        # Epsilon is the max distance between points to be considered neighbors. 10 pixels is a good starting point.
        clustering_y = DBSCAN(eps=10, min_samples=1).fit(coords[:, 1].reshape(-1, 1))
        num_rows = len(set(clustering_y.labels_))

        # Find the number of columns by clustering the X-coordinates.
        clustering_x = DBSCAN(eps=10, min_samples=1).fit(coords[:, 0].reshape(-1, 1))
        num_cols = len(set(clustering_x.labels_))
    else:
        num_rows, num_cols = 1, 1
        
    # Add a fallback for cases where the grid is ambiguous
    # (e.g., a perfect diamond shape might confuse the simple clustering)
    if num_rows * num_cols != len(coords):
         # This is a common case for non-rectangular Kolams like the example.
         # We find the total span of the dots and infer the grid from that.
         span_y = np.max(coords[:, 1]) - np.min(coords[:, 1])
         span_x = np.max(coords[:, 0]) - np.min(coords[:, 0])
         if span_y > span_x: # Taller than wide
             num_rows = max(num_rows, num_cols)
             num_cols = num_rows
         else: # Wider than tall or square
             num_cols = max(num_rows, num_cols)
             num_rows = num_cols
         print(f"Warning: Non-rectangular dot pattern detected. Assuming a {num_rows}x{num_cols} grid for recreation.")


    mid_x = image_shape[1] / 2
    left_dots = sum(1 for kp in keypoints if kp.pt[0] < mid_x)
    right_dots = sum(1 for kp in keypoints if kp.pt[0] > mid_x)
    is_symmetric = abs(left_dots - right_dots) <= max(2, len(keypoints) * 0.1)

    return {
        "dot_count": len(keypoints),
        "contour_count": len(contours) if contours is not None else 0,
        "grid": {"rows": num_rows, "cols": num_cols},
        "is_symmetric": is_symmetric
    }


if __name__ == '__main__':
    image_path = 'kolam_input.png' 
    
    try:
        cv2.imread(image_path).shape
    except AttributeError:
        print(f"'{image_path}' not found. Creating a sample image for demonstration.")
        dummy_img = np.zeros((400, 400), dtype=np.uint8)
        for r in range(5):
            for c in range(5):
                cv2.circle(dummy_img, (75 + c * 60, 75 + r * 60), 5, 255, -1)
        cv2.line(dummy_img, (75, 75), (135, 135), 255, 3)
        cv2.imwrite(image_path, dummy_img)


    # 1. Detect Features
    dots_keypoints, img_with_dots = detect_dots(image_path)
    contours_detected, img_with_contours = detect_contours(image_path)
    
    # 2. Analyze Principles
    original_image = cv2.imread(image_path)
    design_principles = analyze_principles(dots_keypoints, contours_detected, original_image.shape)
    print("\n--- Analyzed Principles ---")
    print(design_principles)
    
    # 3. Display Results
    plt.figure(figsize=(18, 6))
    
    plt.subplot(1, 3, 1)
    plt.title('Original Image')
    plt.imshow(cv2.cvtColor(original_image, cv2.COLOR_BGR2RGB))
    plt.axis('off')
    
    plt.subplot(1, 3, 2)
    plt.title('Detected Dots')
    plt.imshow(cv2.cvtColor(img_with_dots, cv2.COLOR_BGR2RGB))
    plt.axis('off')
    
    plt.subplot(1, 3, 3)
    plt.title('Detected Curves & Contours')
    plt.imshow(cv2.cvtColor(img_with_contours, cv2.COLOR_BGR2RGB))
    plt.axis('off')
    
    plt.tight_layout()
    plt.show()


import cv2
import numpy as np
import matplotlib.pyplot as plt
import image_rec # Import the recognition script

def recreate_kolam(contours, image_shape):
    """
    Recreates a Kolam by drawing detected contours and adding decorative dots
    inside closed, circular loops.

    Args:
        contours (list): A list of contours detected by OpenCV.
        image_shape (tuple): The shape of the original image (height, width, channels).

    Returns:
        numpy.ndarray: The generated Kolam image.
    """
    height, width, _ = image_shape
    # Create a black background image with the same dimensions as the original
    recreated_img = np.zeros((height, width, 3), dtype=np.uint8)

    if contours is None or len(contours) == 0:
        print("Error: No contours were provided to recreate the design.")
        return recreated_img

    # Step 1: Draw all the detected contours in white to form the base design
    cv2.drawContours(recreated_img, contours, -1, (255, 255, 255), 2, lineType=cv2.LINE_AA)

    # Step 2: Analyze each contour to find closed loops and add dots
    for c in contours:
        # Calculate area and perimeter to determine the shape's properties
        area = cv2.contourArea(c)
        perimeter = cv2.arcLength(c, True)

        # Avoid division by zero for invalid contours
        if perimeter == 0:
            continue

        # Calculate circularity (a perfect circle is 1.0)
        circularity = (4 * np.pi * area) / (perimeter * perimeter)
        
        # Filter for shapes that are reasonably circular and within a specific size range.
        # This helps identify the decorative loops while ignoring the main structure.
        if circularity > 0.6 and 100 < area < 5000:
            # Calculate the center (centroid) of the contour using image moments
            M = cv2.moments(c)
            if M["m00"] != 0:
                cX = int(M["m10"] / M["m00"])
                cY = int(M["m01"] / M["m00"])
                
                # Draw a small white dot in the center of the loop
                cv2.circle(recreated_img, (cX, cY), 2, (255, 255, 255), -1, lineType=cv2.LINE_AA)

    return recreated_img


if __name__ == '__main__':
    image_path = 'kolam 5.jpg'
    
    # --- Step 1: Get the original image and its contours ---
    print("--- Running Recognition ---")
    original_image = cv2.imread(image_path)
    if original_image is None:
        raise FileNotFoundError(f"Could not find or read {image_path}. Please ensure it is in the same directory.")

    # We only need the contours for this recreation method.
    contours_detected, _ = image_rec.detect_contours(image_path)
    
    # --- Step 2: Recreate a new Kolam based on the detected contours ---
    print("\n--- Running Recreation ---")
    # Pass the detected contours and the original image shape to the new function
    recreated_design = recreate_kolam(contours_detected, original_image.shape)

    # --- Step 3: Display the original and the recreated design side-by-side for comparison ---
    plt.figure(figsize=(12, 6))

    plt.subplot(1, 2, 1)
    plt.title('Original Image')
    plt.imshow(cv2.cvtColor(original_image, cv2.COLOR_BGR2RGB))
    plt.axis('off')
    
    plt.subplot(1, 2, 2)
    plt.title('Recreated Design (from Contours)')
    # The recreated image is already BGR, so we convert it to RGB for correct display
    plt.imshow(cv2.cvtColor(recreated_design, cv2.COLOR_BGR2RGB))
    plt.axis('off')

    plt.tight_layout()
    plt.show()


# import cv2
# import numpy as np


# def preprocess_image(image_path, save_path=None):

#     image = cv2.imread(image_path)

#     sharpening_kernel = np.array([[-1, -1, -1],
#                                   [-1, 9, -1],
#                                   [-1, -1, -1]])
#     sharpened_image = cv2.filter2D(image, -1, sharpening_kernel)

#     contrast_stretched_image = cv2.normalize(
#         sharpened_image, None, 0, 255, cv2.NORM_MINMAX)

#     if save_path:
#         cv2.imwrite(save_path, contrast_stretched_image)

#     return contrast_stretched_image

############################################################################################################
# def preprocess_image(image_path, save_path=None):
#     # Read the image
#     image = cv2.imread(image_path)

#     # Convert to grayscale
#     gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

#     # Apply Gaussian blur to reduce noise (optional)
#     blurred_image = cv2.GaussianBlur(gray_image, (5, 5), 0)

#     # Apply histogram equalization to improve contrast
#     equalized_image = cv2.equalizeHist(blurred_image)

#     # Apply contrast stretching
#     min_val, max_val = np.percentile(equalized_image, (2, 98))
#     contrast_stretched_image = cv2.normalize(
#         equalized_image, None, 0, 255, cv2.NORM_MINMAX)

#     # Apply adaptive thresholding with adjusted parameters
#     threshold_image = cv2.adaptiveThreshold(
#         contrast_stretched_image, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 25, 5
#     )

#     # Apply dilation to connect text components (adjust kernel size if needed)
#     kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (2, 2))
#     dilated_image = cv2.dilate(threshold_image, kernel, iterations=1)

#     if save_path:
#         cv2.imwrite(save_path, dilated_image)

#     return dilated_image

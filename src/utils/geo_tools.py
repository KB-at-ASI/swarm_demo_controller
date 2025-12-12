import numpy as np


def compute_affine_transform(pt_pairs):
    """
    pt_pairs: list of 3 (x, y, lat, lon) tuples

    Returns: an affine transformation matrix mapping x,y coordinates to lat/long
    """
    # Unpack points
    (pt_pair1, pt_pair2, pt_pair3) = pt_pairs
    (x1, y1, lat1, lon1) = pt_pair1
    (x2, y2, lat2, lon2) = pt_pair2
    (x3, y3, lat3, lon3) = pt_pair3

    # Build matrix for affine coefficients
    A = np.array([[x1, y1, 1], [x2, y2, 1], [x3, y3, 1]])

    # Solve for latitude affine coefficients
    L_lat = np.array([lat1, lat2, lat3])
    a, b, c = np.linalg.solve(A, L_lat)

    # Solve for longitude affine coefficients
    L_lon = np.array([lon1, lon2, lon3])
    d, e, f = np.linalg.solve(A, L_lon)

    # Construct 3x3 affine matrix
    affine_transformation_matrix: np.array = np.array([[a, b, c], [d, e, f], [0, 0, 1]])

    return affine_transformation_matrix


def default_affine_transform():
    """Return default 3x3 identity matrix for affine transformation"""
    return np.eye(3)


def img_x_y_to_latlon(
    affine_transformation_matrix: np.array, image_x: float, image_y: float
):
    """Map image coordinates (x, y) → (lat, lon) using affine matrix M"""
    vec = np.array([image_x, image_y, 1])
    lat, lon, _ = affine_transformation_matrix @ vec
    return lat, lon


# NB: This function expects the image-to-latlon transformation (it takes care of inverting it)
def latlon_to_img_x_y(affine_transformation_matrix: np.array, lat: float, lon: float):
    """Map (lat, lon) → image coordinates (x, y) using inverse of M"""
    inverse_affine_transformation_matrix: np.array = np.linalg.inv(
        affine_transformation_matrix
    )
    vec = np.array([lat, lon, 1])
    x, y, _ = inverse_affine_transformation_matrix @ vec
    return x, y

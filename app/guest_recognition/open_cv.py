import cv2 as cv


def output_performance(frame, params, width, height):
    performance = ", ".join(f"{key}: {value}" for key, value in params.items())
    cv.putText(
        frame,
        performance,
        (10, height - 30),
        cv.FONT_HERSHEY_SIMPLEX,
        1,
        (255, 255, 255),
        3,
        cv.LINE_AA,
    )


def output_face(frame, face, level_b, level_c, show_performance):
    x, y, w, h = face
    area = int(w * h)
    if area < (level_b * level_b):
        color = (17, 151, 228)  # Blue
        label = (
            f"{area} area: LEVEL A"
            if show_performance
            else f"{int(area / (level_b * level_b) * 100)}% - get closer"
        )
        thinkness = 3
    elif (level_b * level_b) <= area < (level_c * level_c):
        color = (194, 51, 255)  # Pink
        label = f"{area} area: LEVEL B" if show_performance else f"Wait..."
        thinkness = 4
    else:
        color = (255, 255, 255)  # White
        label = (
            f"{area} area: LEVEL C"
            if show_performance
            else f"{int(area / (level_c * level_c) * 100)}% - get back"
        )
        thinkness = -1

    cv.rectangle(frame, (x, y), (x + w, y + h), color, thinkness)
    cv.putText(
        frame,
        label,
        (x + 10, y - 20),
        cv.FONT_HERSHEY_SIMPLEX,
        1,
        color,
        3,
        cv.LINE_AA,
    )

import cv2 as cv


def output_perfomance(frame, params, width, height):
    perfomance = ", ".join(f"{key}: {value}" for key, value in params.items())
    cv.putText(
        frame,
        perfomance,
        (10, height - 30),
        cv.FONT_HERSHEY_SIMPLEX,
        1,
        (255, 255, 255),
        3,
        cv.LINE_AA,
    )


def output_face(frame, face, area_start, area_back, perfomance):
    x, y, w, h = face
    area = int(w * h / 1000)
    if area < area_start:
        color = (17, 151, 228)  # Blue
        label = (
            f"{area} area - closer"
            if perfomance == "True"
            else f"{int(area / area_start * 100)}% - closer"
        )
        thinkness = 3
    elif area_start <= area < area_back:
        color = (194, 51, 255)  # Pink
        label = f"{area} area - recognition" if perfomance == "True" else f"Wait"
        thinkness = 4
    else:
        color = (255, 255, 255)  # White
        label = (
            f"{area} area - back"
            if perfomance == "True"
            else f"{int(area / area_back * 100)}% - back"
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

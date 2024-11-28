import math
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


def output_face(
    frame,
    face,
    facearea_level_b,
    facearea_level_c,
    show_performance,
    input_label = ""
):
    x, y, w, h = face["rect"]
    facearea = face["area"]
    faceside = int(math.sqrt(facearea))
    if facearea < facearea_level_b:
        color = (17, 151, 228)  # Blue
        label = (
            f"{faceside} side: LEVEL A"
            if show_performance
            else f"{int(facearea / facearea_level_b * 100)}% - get closer"
        )
        thinkness = 3
    elif facearea_level_b <= facearea < facearea_level_c:
        color = (194, 51, 255)  # Pink
        label = f"{faceside} side: LEVEL B" if show_performance else f"Wait..."
        thinkness = 4
    else:
        color = (255, 255, 255)  # White
        label = (
            f"{faceside} side: LEVEL C"
            if show_performance
            else f"{int(facearea / facearea_level_c * 100)}% - get back"
        )
        thinkness = 4
        x -= 25
        y -= 25
        w += 50
        h += 50

    cv.rectangle(frame, (x, y), (x + w, y + h), color, thinkness)
    cv.putText(
        frame,
        f"{input_label}{label}",
        (x + 10, y - 20),
        cv.FONT_HERSHEY_SIMPLEX,
        1,
        color,
        3,
        cv.LINE_AA,
    )


def output_qrcode(
    frame,
    qrcode_rect,
):
    x, y, w, h = qrcode_rect
    color = (194, 51, 255)  # Pink
    thinkness = 4
    cv.rectangle(frame, (x, y), (x + w, y + h), color, thinkness)

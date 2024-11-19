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
):
    x, y, w, h = face
    facearea = w * h
    if facearea < facearea_level_b:
        color = (17, 151, 228)  # Blue
        label = (
            f"{facearea} area: LEVEL A"
            if show_performance
            else f"{int(facearea / facearea_level_b * 100)}% - get closer"
        )
        thinkness = 3
    elif facearea_level_b <= facearea < facearea_level_c:
        color = (194, 51, 255)  # Pink
        label = f"{facearea} area: LEVEL B" if show_performance else f"Wait..."
        thinkness = 4
    else:
        color = (255, 255, 255)  # White
        label = (
            f"{facearea} area: LEVEL C"
            if show_performance
            else f"{int(facearea / facearea_level_c * 100)}% - get back"
        )
        thinkness = -1
        x -= 25
        y -= 25
        w += 50
        h += 50

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

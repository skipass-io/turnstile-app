import os
from enum import Enum
from typing_extensions import Annotated

import typer

from qt import exec


app = typer.Typer()


@app.command()
def run(
    area_start_recognition: Annotated[
        int, typer.Option("--area_start_recognition", "-sr")
    ] = 140,
    area_step_back: Annotated[int, typer.Option("--area_step_back", "-sb")] = 250,
    face_recognition_labels_count: Annotated[
        int, typer.Option("--face_recognition_labels_count", "-lc")
    ] = 20,
    face_recognition_percent: Annotated[
        int, typer.Option("--face_recognition_labels_percent", "-lp")
    ] = 85,
    show_perfomance: Annotated[bool, typer.Option("--perfomans", "-p")] = False,
):
    os.environ["AREA_START_RECOGNITION"] = str(area_start_recognition)
    os.environ["AREA_STEP_BACK"] = str(area_step_back)
    os.environ["FACE_RECOGNITION_LABELS_COUNT"] = str(face_recognition_labels_count)
    os.environ["FACE_RECOGNITION_PERCENT"] = str(face_recognition_percent)
    os.environ["TURNSTILE_PERFOMANCE"] = str(show_perfomance)
    exec()


if __name__ == "__main__":
    app()

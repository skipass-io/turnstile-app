import typer
from qt import exec


app = typer.Typer()


@app.command()
def run():
    exec()


if __name__ == "__main__":
    app()

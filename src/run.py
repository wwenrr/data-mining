import logging
import sys
import os
import typer

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from commands import dataset_command

app = typer.Typer()

app.command(name="dataset")(dataset_command)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    app()
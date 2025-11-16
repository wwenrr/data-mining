import logging
import sys
import os
import typer
from commands import (
    dataset_command,
    analyze_command,
    train_command,
    market_command,
    train_classifier_command,
    forecast_command,
)

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

app = typer.Typer()

app.command(name="dataset")(dataset_command)
app.command(name="analyze")(analyze_command)
app.command(name="train")(train_command)
app.command(name="market")(market_command)
app.command(name="train-classifier")(train_classifier_command)
app.command(name="forecast")(forecast_command)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
    app()

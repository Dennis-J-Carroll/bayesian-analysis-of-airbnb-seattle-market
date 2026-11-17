"""Loader for the small precomputed model artifacts the app reads at runtime.

The app never imports PyMC or ArviZ: every number it shows comes from the
files in outputs/app_artifacts, written by scripts/build_artifacts.py.
"""

import json
from dataclasses import dataclass
from pathlib import Path

import streamlit as st

ARTIFACT_DIR: Path = Path(__file__).resolve().parents[2] / "outputs" / "app_artifacts"


@dataclass(frozen=True)
class Artifacts:
    neighborhoods: dict
    curves: dict
    hyper: dict
    diagnostics: dict
    cleaning: dict


def _read(directory: Path, name: str) -> dict:
    return json.loads((Path(directory) / name).read_text())


@st.cache_resource
def load_artifacts(directory: Path = ARTIFACT_DIR) -> Artifacts:
    return Artifacts(
        neighborhoods=_read(directory, "neighborhoods.json"),
        curves=_read(directory, "curves.json"),
        hyper=_read(directory, "hyper.json"),
        diagnostics=_read(directory, "diagnostics.json"),
        cleaning=_read(directory, "cleaning.json"),
    )


def neighborhood_by_name(art: Artifacts, name: str) -> dict:
    for n in art.neighborhoods["neighborhoods"]:
        if n["name"] == name:
            return n
    raise KeyError(f"Unknown neighborhood: {name}")

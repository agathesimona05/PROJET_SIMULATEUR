"""
app.py
======
Application Flask — Simulateur d'Épargne Long Terme.

Auteurs : Poezevera Clarisse, Simona Agathe, Rivière Clément
Cours   : Python — Projet final, Dauphine
"""

from __future__ import annotations

from flask import Flask, render_template, request, jsonify

from simulator import (
    SimulationParams,
    ValidationError,
    simulate_savings,
    monte_carlo,
)

app = Flask(__name__)


# ─────────────────────────────────────────────────────────────────────────────
# HELPER
# ─────────────────────────────────────────────────────────────────────────────

def _parse_params(data: dict) -> SimulationParams:
    return SimulationParams(
        initial=float(data["initial"]),
        monthly=float(data["monthly"]),
        rate=float(data["rate"]),
        years=int(data["years"]),
        inflation=float(data["inflation"]),
        fees=float(data["fees"]),
    )


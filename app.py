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

# ─────────────────────────────────────────────────────────────────────────────
# ROUTES
# ─────────────────────────────────────────────────────────────────────────────

@app.route("/")
def index():
    """Page principale de l'application."""
    return render_template("site.html")


@app.route("/simulate", methods=["POST"])
def simulate():
    """
    Lance une simulation déterministe et renvoie les séries temporelles.

    Retourne :
        JSON avec capitals, investeds, reals et les métriques clés.
    """
    try:
        data = request.get_json(force=True)
        params = _parse_params(data)
    except (KeyError, TypeError, ValueError) as e:
        return jsonify({"success": False, "error": f"Paramètres invalides : {e}"}), 400
    except ValidationError as e:
        return jsonify({"success": False, "error": str(e)}), 400

    result = simulate_savings(params)

    return jsonify({
        "success": True,
        "capitals":       [round(v, 2) for v in result.capitals],
        "investeds":      [round(v, 2) for v in result.investeds],
        "reals":          [round(v, 2) for v in result.reals],
        "final_capital":  round(result.final_capital, 2),
        "final_real":     round(result.final_real, 2),
        "total_invested": round(result.total_invested, 2),
        "total_interest": round(result.total_interest, 2),
        "gain_pct":       round(result.gain_pct, 2),
        "net_real_rate":  round(params.net_rate, 2),
    })

@app.route("/montecarlo", methods=["POST"])
def run_monte_carlo():
    """
    Lance une simulation Monte Carlo et renvoie la distribution.

    Retourne :
        JSON avec P10 / P50 / P90 et l'histogramme pour le graphique.
    """
    try:
        data = request.get_json(force=True)
        params = _parse_params(data)
        n_runs = int(data.get("n_runs", 500))
    except (KeyError, TypeError, ValueError) as e:
        return jsonify({"success": False, "error": f"Paramètres invalides : {e}"}), 400
    except ValidationError as e:
        return jsonify({"success": False, "error": str(e)}), 400

    if not (50 <= n_runs <= 2000):
        return jsonify({"success": False, "error": "n_runs doit être entre 50 et 2000."}), 400

    mc = monte_carlo(params, n_runs=n_runs)
    labels, counts = mc.histogram(bins=40)

    return jsonify({
        "success":           True,
        "p10":               round(mc.p10, 2),
        "p50":               round(mc.p50, 2),
        "p90":               round(mc.p90, 2),
        "histogram_counts":  counts,
        "histogram_labels":  [round(v, 2) for v in labels],
        "n_runs":            mc.n_runs,
    })


# ─────────────────────────────────────────────────────────────────────────────
# ENTRY POINT
# ─────────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    app.run(debug=True, port=5000)
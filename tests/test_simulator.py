Tests unitaires — simulateur d'épargne.

Couvre :
  - SimulationParams  : construction, validation, propriétés
  - SimulationResult  : propriétés calculées, __len__, __str__
  - MonteCarloResult  : percentiles, histogramme, __len__
  - simulate_savings  : cas nominaux et cas limites
  - monte_carlo       : propriétés statistiques

  import math
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest
from simulator import (
    SimulationParams,
    SimulationResult,
    MonteCarloResult,
    ValidationError,
    simulate_savings,
    monte_carlo,
    _box_muller,
)


# FIXTURES

@pytest.fixture
def params():
    """Paramètres standards pour les tests."""
    return SimulationParams(5000, 200, 7.0, 20, 2.0, 0.5)

@pytest.fixture
def result(params):
    """Résultat déterministe sur les paramètres standards."""
    return simulate_savings(params)

# ─────────────────────────────────────────────────────────────────────────────
# SimulationParams — construction et validation
# ─────────────────────────────────────────────────────────────────────────────

class TestSimulationParams:

    def test_construction_valide(self, params):
        assert params.initial == 5000
        assert params.monthly == 200
        assert params.years == 20

    def test_net_rate(self, params):
        """net_rate = rate - fees - inflation"""
        assert params.net_rate == pytest.approx(7.0 - 0.5 - 2.0)

    def test_monthly_rate(self, params):
        """monthly_rate = (rate - fees) / 100 / 12"""
        expected = (7.0 - 0.5) / 100 / 12
        assert params.monthly_rate == pytest.approx(expected)

    def test_repr_contient_rate(self, params):
        assert "7.0" in repr(params)

    def test_str_contient_annees(self, params):
        assert "20 ans" in str(params)

    # -- Cas d'erreur --

    def test_initial_negatif(self):
        with pytest.raises(ValidationError, match="négatif"):
            SimulationParams(-1, 200, 7, 10, 2, 0.5)

    def test_monthly_negatif(self):
        with pytest.raises(ValidationError, match="mensuel"):
            SimulationParams(1000, -50, 7, 10, 2, 0.5)

    def test_tous_zeros(self):
        with pytest.raises(ValidationError):
            SimulationParams(0, 0, 7, 10, 2, 0.5)

    def test_rate_negatif(self):
        with pytest.raises(ValidationError, match="rendement"):
            SimulationParams(1000, 100, -1, 10, 2, 0.5)

    def test_years_zero(self):
        with pytest.raises(ValidationError, match="durée"):
            SimulationParams(1000, 100, 7, 0, 2, 0.5)

    def test_years_trop_grand(self):
        with pytest.raises(ValidationError, match="durée"):
            SimulationParams(1000, 100, 7, 101, 2, 0.5)
    
    def test_inflation_negative(self):
        with pytest.raises(ValidationError, match="inflation"):
            SimulationParams(1000, 100, 7, 10, -1, 0.5)

    def test_frais_superieurs_au_taux(self):
        with pytest.raises(ValidationError, match="frais"):
            SimulationParams(1000, 100, 3, 10, 2, 5)

    def test_frais_egaux_au_taux(self):
        with pytest.raises(ValidationError, match="frais"):
            SimulationParams(1000, 100, 5, 10, 2, 5)


# ─────────────────────────────────────────────────────────────────────────────
# SimulationResult — propriétés et méthodes spéciales
# ─────────────────────────────────────────────────────────────────────────────

class TestSimulationResult:

    def test_len_retourne_nombre_annees(self, result, params):
        assert len(result) == params.years

    def test_final_capital_est_dernier_element(self, result):
        assert result.final_capital == result.capitals[-1]

    def test_final_real_est_dernier_element(self, result):
        assert result.final_real == result.reals[-1]

    def test_total_interest_calcul(self, result):
        expected = result.final_capital - result.total_invested
        assert result.total_interest == pytest.approx(expected)

    def test_gain_pct_positif(self, result):
        assert result.gain_pct > 0

    def test_capital_croissant(self, result):
        for i in range(1, len(result.capitals)):
            assert result.capitals[i] > result.capitals[i - 1]

    def test_capital_reel_inferieur_au_nominal(self, result):
        """Avec inflation > 0, le capital réel doit être < capital brut."""
        assert result.final_real < result.final_capital

    def test_str_contient_capital_final(self, result):
        assert "Capital final" in str(result)

    def test_repr_contient_final(self, result):
        assert "final=" in repr(result)

    def test_annee_zero_est_capital_initial(self, params):
        r = simulate_savings(params)
        assert r.capitals[0] == params.initial
        assert r.investeds[0] == params.initial
        assert r.reals[0] == params.initial

    def test_sans_inflation_reel_egal_nominal(self):
        p = SimulationParams(5000, 100, 5.0, 10, 0.0, 0.3)
        r = simulate_savings(p)
        assert abs(r.final_real - r.final_capital) < 1e-4

    def test_capitalisation_un_an_sans_versement(self):
        """Vérifie manuellement la formule sur 1 an."""
        p = SimulationParams(10000, 0, 12.0, 1, 0.0, 0.0)
        r = simulate_savings(p)
        # Taux mensuel = 1 %, donc 10000 * 1.01^12
        expected = 10000 * (1.01 ** 12)
        assert abs(r.final_capital - expected) < 0.01
    
    def test_total_investi_sans_versement(self):
        """Sans versement mensuel, le total investi reste constant."""
        p = SimulationParams(10000, 0, 5.0, 10, 1.0, 0.2)
        r = simulate_savings(p)
        assert r.total_invested == pytest.approx(10000)

    def test_total_investi_avec_versements(self):
        """Total investi = initial + monthly * 12 * years."""
        p = SimulationParams(0, 100, 5.0, 10, 1.0, 0.5)
        r = simulate_savings(p)
        expected = 100 * 12 * 10
        assert abs(r.total_invested - expected) < 1

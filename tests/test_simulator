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


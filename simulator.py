from __future__ import annotations

import math
import random

# ─────────────────────────────────────────────────────────────────────────────
# EXCEPTIONS PERSONNALISÉES
# ─────────────────────────────────────────────────────────────────────────────

class ValidationError(ValueError):
    """Levée quand les paramètres fournis sont invalides."""
    pass


# ─────────────────────────────────────────────────────────────────────────────
# CLASSE : SimulationParams
# ─────────────────────────────────────────────────────────────────────────────
lass SimulationParams:
    """
    Paramètres d'une simulation d'épargne.

    Valide les données à l'initialisation et expose une représentation
    claire pour le débogage.

    Attributes:
        initial   : Capital de départ en €.
        monthly   : Versement mensuel en €.
        rate      : Taux de rendement annuel brut en %.
        years     : Durée de l'investissement en années.
        inflation : Taux d'inflation annuel en %.
        fees      : Frais de gestion annuels en %.

    Example:
        >>> p = SimulationParams(5000, 200, 7.0, 20, 2.0, 0.5)
        >>> p.net_rate
        6.5
    """

    def __init__(
        self,
        initial: float,
        monthly: float,
        rate: float,
        years: int,
        inflation: float,
        fees: float,
    ) -> None:
        # On valide avant d'assigner — si ça plante, l'objet n'est pas créé
        self._validate(initial, monthly, rate, years, inflation, fees)

        self.initial = float(initial)
        self.monthly = float(monthly)
        self.rate = float(rate)
        self.years = int(years)
        self.inflation = float(inflation)
        self.fees = float(fees)

        # ── Méthodes spéciales ────────────────────────────────────────────────

    def __repr__(self) -> str:
        """Représentation technique, utile pour le débogage."""
        return (
            f"SimulationParams("
            f"initial={self.initial}, monthly={self.monthly}, "
            f"rate={self.rate}%, years={self.years}, "
            f"inflation={self.inflation}%, fees={self.fees}%)"
        )

    def __str__(self) -> str:
        """Représentation lisible pour l'utilisateur."""
        return (
            f"Simulation sur {self.years} ans — "
            f"capital initial {self.initial:,.0f} € — "
            f"versement {self.monthly:,.0f} €/mois — "
            f"taux net réel {self.net_rate:.2f} %/an"
        )

    # ── Propriétés calculées ──────────────────────────────────────────────

    @property
    def net_rate(self) -> float:
        """Taux net réel = taux brut − frais − inflation."""
        return self.rate - self.fees - self.inflation

    @property
    def monthly_rate(self) -> float:
        """Taux mensuel net = (taux − frais) / 12."""
        return (self.rate - self.fees) / 100 / 12

# ── Validation (méthode privée) ───────────────────────────────────────

    @staticmethod
    def _validate(
        initial: float,
        monthly: float,
        rate: float,
        years: int,
        inflation: float,
        fees: float,
    ) -> None:
        """Valide tous les paramètres, lève ValidationError si besoin."""
        if initial < 0:
            raise ValidationError("Le capital initial ne peut pas être négatif.")
        if monthly < 0:
            raise ValidationError("Le versement mensuel ne peut pas être négatif.")
        if initial == 0 and monthly == 0:
            raise ValidationError(
                "Entrez au moins un capital initial ou un versement mensuel."
            )
        if rate < 0:
            raise ValidationError("Le taux de rendement ne peut pas être négatif.")
        if not (1 <= years <= 100):
            raise ValidationError("La durée doit être comprise entre 1 et 100 ans.")
        if not (0 <= inflation <= 30):
            raise ValidationError("L'inflation doit être comprise entre 0 et 30 %.")
        if not (0 <= fees < rate):
            raise ValidationError(
                "Les frais doivent être ≥ 0 et strictement inférieurs au taux."
            )

# ── Méthodes spéciales ────────────────────────────────────────────────

    def __repr__(self) -> str:
        return (
            f"SimulationResult("
            f"{len(self)} ans, "
            f"final={self.final_capital:,.0f} €, "
            f"réel={self.final_real:,.0f} €)"
        )

    def __str__(self) -> str:
        return (
            f"Capital final  : {self.final_capital:>14,.2f} €\n"
            f"Capital réel   : {self.final_real:>14,.2f} €\n"
            f"Total investi  : {self.total_invested:>14,.2f} €\n"
            f"Intérêts       : {self.total_interest:>14,.2f} €\n"
            f"Plus-value     : {self.gain_pct:>13.1f} %"
        )

    def __len__(self) -> int:
        """Nombre d'années simulées (sans compter l'année 0)."""
        return len(self.capitals) - 1

    # ── Propriétés calculées ──────────────────────────────────────────────

    @property
    def final_capital(self) -> float:
        """Capital brut à la fin de la simulation."""
        return self.capitals[-1]

    @property
    def final_real(self) -> float:
        """Capital réel final, corrigé de l'inflation cumulée."""
        return self.reals[-1]

    @property
    def total_invested(self) -> float:
        """Montant total versé sur toute la durée."""
        return self.investeds[-1]

    @property
    def total_interest(self) -> float:
        """Intérêts générés = capital final − total investi."""
        return self.final_capital - self.total_invested

    @property
    def gain_pct(self) -> float:
        """Plus-value totale en % par rapport au capital investi."""
        if self.total_invested == 0:
            return 0.0
        return (self.final_capital / self.total_invested - 1) * 100

# ─────────────────────────────────────────────────────────────────────────────
# CLASSE : MonteCarloResult
# ─────────────────────────────────────────────────────────────────────────────

class MonteCarloResult:
    """
    Résultat d'une simulation Monte Carlo.

    Attributes:
        finals : Liste triée des capitaux finaux (toutes simulations).
        n_runs : Nombre de trajectoires simulées.

    Example:
        >>> p = SimulationParams(5000, 200, 7.0, 20, 2.0, 0.5)
        >>> mc = monte_carlo(p, n_runs=500)
        >>> mc.p10 < mc.p50 < mc.p90
        True
    """

    def __init__(self, finals: list[float]) -> None:
        if not finals:
            raise ValidationError("La liste de résultats ne peut pas être vide.")
        self.finals = sorted(finals)
        self.n_runs = len(finals)

    def __repr__(self) -> str:
        return (
            f"MonteCarloResult("
            f"n_runs={self.n_runs}, "
            f"p10={self.p10:,.0f} €, "
            f"p50={self.p50:,.0f} €, "
            f"p90={self.p90:,.0f} €)"
        )

    def __str__(self) -> str:
        return (
            f"Monte Carlo ({self.n_runs} simulations)\n"
            f"  Pessimiste (P10) : {self.p10:>12,.0f} €\n"
            f"  Médiane    (P50) : {self.p50:>12,.0f} €\n"
            f"  Optimiste  (P90) : {self.p90:>12,.0f} €"
        )

    def __len__(self) -> int:
        """Nombre de simulations."""
        return self.n_runs

    @property
    def p10(self) -> float:
        """10e percentile — scénario pessimiste."""
        return self._percentile(10)
@property
    def p50(self) -> float:
        """50e percentile — scénario médian."""
        return self._percentile(50)

    @property
    def p90(self) -> float:
        """90e percentile — scénario optimiste."""
        return self._percentile(90)

    def _percentile(self, p: float) -> float:
        """Calcule le p-ième percentile de la distribution."""
        idx = int(p / 100 * self.n_runs)
        return self.finals[min(idx, self.n_runs - 1)]

    def histogram(self, bins: int = 40) -> tuple[list[float], list[int]]:
        """
        Calcule un histogramme de la distribution des capitaux finaux.

        Args:
            bins : Nombre d'intervalles (défaut 40).

        Returns:
            Tuple (labels, counts) — valeurs min de chaque bin et effectifs.
        """
        min_v, max_v = self.finals[0], self.finals[-1]
        step = (max_v - min_v) / bins if max_v > min_v else 1.0

        counts = [0] * bins
        labels = [min_v + i * step for i in range(bins)]

        for v in self.finals:
            idx = min(int((v - min_v) / step), bins - 1)
            counts[idx] += 1

        return labels, counts


# ─────────────────────────────────────────────────────────────────────────────
# FONCTIONS DE SIMULATION
# ─────────────────────────────────────────────────────────────────────────────

def simulate_savings(params: SimulationParams) -> SimulationResult:
    """
    Simule l'évolution du capital par capitalisation composée mensuelle.

    Algorithme :
        Pour chaque année, on itère sur 12 mois :
            capital = capital * (1 + taux_mensuel) + versement_mensuel
        Le capital réel est déflaté par l'inflation cumulée.

    Args:
        params : Paramètres validés de la simulation.

    Returns:
        SimulationResult avec les séries annuelles.

    Example:
        >>> p = SimulationParams(10000, 0, 5.0, 10, 0.0, 0.0)
        >>> r = simulate_savings(p)
        >>> round(r.final_capital, 2)  # 10000 * (1 + 5/12/100)^120
        16470.09
    """
    inflation_rate = params.inflation / 100

    capital = params.initial
    total_invested = params.initial

    capitals  = [capital]
    investeds = [capital]
    reals     = [capital]

    for year in range(1, params.years + 1):
        # Capitalisation mois par mois sur l'année
        for _ in range(12):
            capital *= (1 + params.monthly_rate)
            capital += params.monthly
            total_invested += params.monthly

        # Déflation par l'inflation cumulée
        real_capital = capital / math.pow(1 + inflation_rate, year)

        capitals.append(capital)
        investeds.append(total_invested)
        reals.append(real_capital)

    return SimulationResult(capitals, investeds, reals)

def _box_muller() -> float:
    """
    Génère un nombre aléatoire selon N(0, 1) via l'algorithme Box-Muller.

    Évite toute dépendance à numpy/scipy.

    Returns:
        Flottant tiré d'une loi normale standard.
    """
    u1 = random.random() or 1e-10   # évite log(0)
    u2 = random.random()
    return math.sqrt(-2 * math.log(u1)) * math.cos(2 * math.pi * u2)


def monte_carlo(
    params: SimulationParams,
    n_runs: int = 500,
    volatility: float = 8.0,
) -> MonteCarloResult:
    """
    Simulation Monte Carlo : modélise l'incertitude des marchés.

    À chaque simulation, le taux annuel est tiré selon N(params.rate, volatility).
    Cela représente le fait que les rendements futurs sont inconnus.

    Args:
        params     : Paramètres de base de la simulation.
        n_runs     : Nombre de trajectoires simulées (défaut 500).
        volatility : Écart-type annuel du taux en % (défaut 8 %).

    Returns:
        MonteCarloResult avec la distribution complète et les percentiles.

    Raises:
        ValidationError : Si n_runs < 1.

    Example:
        >>> p = SimulationParams(5000, 200, 7.0, 20, 2.0, 0.5)
        >>> mc = monte_carlo(p, n_runs=100)
        >>> mc.p10 < mc.p50 < mc.p90
        True
    """
    if n_runs < 1:
        raise ValidationError("Le nombre de simulations doit être ≥ 1.")

    finals: list[float] = []


    for _ in range(n_runs):
        capital = params.initial

        for _ in range(params.years):
            # Taux annuel aléatoire autour de la valeur centrale
            random_rate = params.rate + _box_muller() * volatility
            monthly_rate = (random_rate - params.fees) / 100 / 12

            for _ in range(12):
                capital *= (1 + monthly_rate)
                capital += params.monthly

        finals.append(capital)

    return MonteCarloResult(finals)


"""Pure COI/EDO portfolio simulator (testable seam; no Streamlit)."""

from __future__ import annotations

from dataclasses import dataclass

from bondwise.params import BELKA_RATE, COI, EDO, FACE_VALUE, ProductParams


@dataclass(frozen=True)
class YearPoint:
    year: int
    wallet: float
    income: float
    bonds: int
    idle_cash: float
    is_roll: bool = False


@dataclass(frozen=True)
class ProductPath:
    years: list[YearPoint]
    final_wallet: float
    profit: float


@dataclass(frozen=True)
class SimulationResult:
    coi: ProductPath
    edo: ProductPath
    delta_edo_minus_coi: float


def _floor_bonds(lump_sum: float) -> tuple[int, float]:
    bonds = int(lump_sum // FACE_VALUE)
    idle = lump_sum - bonds * FACE_VALUE
    return bonds, idle


def _rate_for_year(product: ProductParams, year_in_cycle: int, inflation: float) -> float:
    if year_in_cycle == 1:
        return product.year1_rate
    return product.margin + max(inflation, 0.0)


def _money(value: float) -> float:
    """Round to grosze (PLN has 2 decimal places)."""
    return round(value, 2)


def _apply_belka(amount: float, belka: bool) -> float:
    if not belka or amount <= 0:
        return _money(amount)
    return _money(amount * (1.0 - BELKA_RATE))


def _early_exit_fee(
    product: ProductParams,
    bonds: int,
    interest: float,
    year_in_cycle: int,
) -> float:
    raw = bonds * product.early_exit_fee_per_bond
    if product.fee_uncapped_after_year1 and year_in_cycle >= 2:
        return raw
    return min(raw, interest)


def _simulate_product(
    product: ProductParams,
    lump_sum: float,
    horizon_years: int,
    inflation: float,
    belka: bool,
) -> ProductPath:
    """Year-1 path: mid-cycle early exit at horizon (tickets #3–#5 extend this)."""
    bonds, idle = _floor_bonds(lump_sum)
    points: list[YearPoint] = []

    # Ticket #2: horizon 1 early-exit path only. Later tickets grow this loop.
    for year in range(1, horizon_years + 1):
        year_in_cycle = ((year - 1) % product.maturity_years) + 1
        rate = _rate_for_year(product, year_in_cycle, inflation)

        if product is COI or product.code.startswith("COI"):
            # COI: annual coupon, no in-bond capitalization. At horizon exit mid-cycle:
            # pay interest for the year, deduct early-exit fee, Belka on interest after fee.
            interest = _money(bonds * FACE_VALUE * rate)
            fee = _money(_early_exit_fee(product, bonds, interest, year_in_cycle))
            after_fee = _money(interest - fee)
            net = _apply_belka(after_fee, belka)
            wallet = _money(bonds * FACE_VALUE + idle + net)
            points.append(
                YearPoint(
                    year=year,
                    wallet=wallet,
                    income=net,
                    bonds=bonds,
                    idle_cash=_money(idle),
                )
            )
        else:
            # EDO: interest capitalizes; paid at exit. Belka once on (interest − fee).
            # Year-1: one year of accrual on face.
            interest = _money(bonds * FACE_VALUE * rate)
            fee = _money(_early_exit_fee(product, bonds, interest, year_in_cycle))
            after_fee = _money(interest - fee)
            net = _apply_belka(after_fee, belka)
            wallet = _money(bonds * FACE_VALUE + idle + net)
            points.append(
                YearPoint(
                    year=year,
                    wallet=wallet,
                    income=net,
                    bonds=bonds,
                    idle_cash=_money(idle),
                )
            )

    final = points[-1].wallet if points else _money(lump_sum)
    return ProductPath(
        years=points,
        final_wallet=final,
        profit=_money(final - lump_sum),
    )


def simulate(
    lump_sum: float,
    horizon_years: int = 1,
    inflation: float = 0.0,
    belka: bool = True,
) -> SimulationResult:
    coi = _simulate_product(COI, lump_sum, horizon_years, inflation, belka)
    edo = _simulate_product(EDO, lump_sum, horizon_years, inflation, belka)
    return SimulationResult(
        coi=coi,
        edo=edo,
        delta_edo_minus_coi=_money(edo.final_wallet - coi.final_wallet),
    )

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


def _money(value: float) -> float:
    """Round to grosze (PLN has 2 decimal places)."""
    return round(value, 2)


def _floor_bonds(lump_sum: float) -> tuple[int, float]:
    bonds = int(lump_sum // FACE_VALUE)
    idle = lump_sum - bonds * FACE_VALUE
    return bonds, idle


def _rate_for_year(product: ProductParams, year_in_cycle: int, inflation: float) -> float:
    if year_in_cycle == 1:
        return product.year1_rate
    return product.margin + max(inflation, 0.0)


def _apply_belka(amount: float, belka: bool) -> float:
    if amount <= 0:
        return _money(amount)
    if not belka:
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
    return min(raw, max(interest, 0.0))


def _buy_bonds(idle: float, bonds: int) -> tuple[int, float]:
    bought = int(idle // FACE_VALUE)
    if bought <= 0:
        return bonds, _money(idle)
    bonds += bought
    idle = _money(idle - bought * FACE_VALUE)
    return bonds, idle


def _simulate_coi(
    lump_sum: float,
    horizon_years: int,
    inflation: float,
    belka: bool,
) -> ProductPath:
    product = COI
    bonds, idle = _floor_bonds(lump_sum)
    points: list[YearPoint] = []
    year_in_cycle = 0

    for year in range(1, horizon_years + 1):
        if bonds == 0 and idle < FACE_VALUE:
            points.append(
                YearPoint(
                    year=year,
                    wallet=_money(idle),
                    income=0.0,
                    bonds=0,
                    idle_cash=_money(idle),
                )
            )
            continue

        if bonds == 0:
            bonds, idle = _buy_bonds(idle, bonds)
            year_in_cycle = 0

        year_in_cycle += 1
        rate = _rate_for_year(product, year_in_cycle, inflation)
        interest = _money(bonds * FACE_VALUE * rate)
        at_horizon = year == horizon_years
        at_maturity = year_in_cycle == product.maturity_years

        if at_maturity:
            # Maturity: full coupon, no fee; reinvest all proceeds into a new COI cycle.
            net = _apply_belka(interest, belka)
            idle = _money(idle + bonds * FACE_VALUE + net)
            bonds = 0
            year_in_cycle = 0
            bonds, idle = _buy_bonds(idle, bonds)
            points.append(
                YearPoint(
                    year=year,
                    wallet=_money(bonds * FACE_VALUE + idle),
                    income=net,
                    bonds=bonds,
                    idle_cash=idle,
                    is_roll=True,
                )
            )
        elif at_horizon:
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
            idle = wallet
            bonds = 0
            year_in_cycle = 0
        else:
            # Hold: Belka on coupon, reinvest net into whole bonds; remainder idle at 0%.
            net = _apply_belka(interest, belka)
            idle = _money(idle + net)
            bonds, idle = _buy_bonds(idle, bonds)
            points.append(
                YearPoint(
                    year=year,
                    wallet=_money(bonds * FACE_VALUE + idle),
                    income=net,
                    bonds=bonds,
                    idle_cash=idle,
                )
            )

    final = points[-1].wallet if points else _money(lump_sum)
    return ProductPath(
        years=points,
        final_wallet=final,
        profit=_money(final - lump_sum),
    )


def _simulate_edo(
    lump_sum: float,
    horizon_years: int,
    inflation: float,
    belka: bool,
) -> ProductPath:
    product = EDO
    bonds, idle = _floor_bonds(lump_sum)
    points: list[YearPoint] = []
    year_in_cycle = 0
    # Accrued capitalized interest outstanding (pre-fee, pre-tax).
    accrued = 0.0
    # Compounding basis per portfolio of bonds (face * bonds grows with capitalization).
    basis = _money(bonds * FACE_VALUE)

    for year in range(1, horizon_years + 1):
        if bonds == 0:
            points.append(
                YearPoint(
                    year=year,
                    wallet=_money(idle),
                    income=0.0,
                    bonds=0,
                    idle_cash=_money(idle),
                )
            )
            continue

        year_in_cycle += 1
        rate = _rate_for_year(product, year_in_cycle, inflation)
        year_interest = _money(basis * rate)
        basis = _money(basis + year_interest)
        accrued = _money(accrued + year_interest)

        at_horizon = year == horizon_years
        at_maturity = year_in_cycle == product.maturity_years

        if at_horizon and not at_maturity:
            fee = _money(_early_exit_fee(product, bonds, accrued, year_in_cycle))
            after_fee = _money(accrued - fee)
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
            idle = wallet
            bonds = 0
            accrued = 0.0
            basis = 0.0
            year_in_cycle = 0
        elif at_maturity:
            net = _apply_belka(accrued, belka)
            idle = _money(idle + bonds * FACE_VALUE + net)
            bonds = 0
            accrued = 0.0
            basis = 0.0
            year_in_cycle = 0
            points.append(
                YearPoint(
                    year=year,
                    wallet=idle,
                    income=net,
                    bonds=0,
                    idle_cash=idle,
                )
            )
        else:
            # Hold: interest stays capitalized inside the bond.
            points.append(
                YearPoint(
                    year=year,
                    wallet=_money(basis + idle),
                    income=0.0,
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
    coi = _simulate_coi(lump_sum, horizon_years, inflation, belka)
    edo = _simulate_edo(lump_sum, horizon_years, inflation, belka)
    return SimulationResult(
        coi=coi,
        edo=edo,
        delta_edo_minus_coi=_money(edo.final_wallet - coi.final_wallet),
    )

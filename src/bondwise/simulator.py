"""Pure COI/EDO portfolio simulator (testable seam; no Streamlit)."""

from __future__ import annotations

from dataclasses import dataclass

from bondwise.params import BELKA_RATE, COI, EDO, FACE_VALUE, ProductParams


@dataclass(frozen=True)
class ExitSnapshot:
    """Counterfactual redeem-at-end-of-year-N economics (pre-hold/roll)."""

    fee: float
    tax: float
    income: float
    cash_out: float
    profit: float


@dataclass(frozen=True)
class YearPoint:
    year: int
    wallet: float
    income: float
    bonds: int
    idle_cash: float
    exit: ExitSnapshot
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


def _exit_tax(after_fee: float, net: float, belka: bool) -> float:
    if not belka or after_fee <= 0:
        return 0.0
    return _money(after_fee - net)


def _make_exit(
    *,
    lump_sum: float,
    bonds: int,
    idle: float,
    interest_base: float,
    year_in_cycle: int,
    at_maturity: bool,
    belka: bool,
    product: ProductParams,
) -> ExitSnapshot:
    fee = (
        0.0
        if at_maturity
        else _money(_early_exit_fee(product, bonds, interest_base, year_in_cycle))
    )
    after_fee = _money(interest_base - fee)
    income = _apply_belka(after_fee, belka)
    tax = _exit_tax(after_fee, income, belka)
    cash_out = _money(bonds * FACE_VALUE + idle + income)
    profit = _money(cash_out - lump_sum)
    return ExitSnapshot(
        fee=fee,
        tax=tax,
        income=income,
        cash_out=cash_out,
        profit=profit,
    )


def _idle_only_exit(lump_sum: float, idle: float) -> ExitSnapshot:
    cash_out = _money(idle)
    return ExitSnapshot(
        fee=0.0,
        tax=0.0,
        income=0.0,
        cash_out=cash_out,
        profit=_money(cash_out - lump_sum),
    )


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
    product: ProductParams = COI,
) -> ProductPath:
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
                    exit=_idle_only_exit(lump_sum, idle),
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
        exit_snap = _make_exit(
            lump_sum=lump_sum,
            bonds=bonds,
            idle=idle,
            interest_base=interest,
            year_in_cycle=year_in_cycle,
            at_maturity=at_maturity,
            belka=belka,
            product=product,
        )

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
                    exit=exit_snap,
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
                    exit=exit_snap,
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
                    exit=exit_snap,
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
    product: ProductParams = EDO,
) -> ProductPath:
    bonds, idle = _floor_bonds(lump_sum)
    points: list[YearPoint] = []
    year_in_cycle = 0
    # Accrued capitalized interest outstanding (pre-fee, pre-tax).
    accrued = 0.0
    # Compounding basis grows with annual capitalization.
    basis = _money(bonds * FACE_VALUE)

    for year in range(1, horizon_years + 1):
        if bonds == 0 and idle < FACE_VALUE:
            points.append(
                YearPoint(
                    year=year,
                    wallet=_money(idle),
                    income=0.0,
                    bonds=0,
                    idle_cash=_money(idle),
                    exit=_idle_only_exit(lump_sum, idle),
                )
            )
            continue

        if bonds == 0:
            bonds, idle = _buy_bonds(idle, bonds)
            basis = _money(bonds * FACE_VALUE)
            accrued = 0.0
            year_in_cycle = 0

        year_in_cycle += 1
        rate = _rate_for_year(product, year_in_cycle, inflation)
        year_interest = _money(basis * rate)
        basis = _money(basis + year_interest)
        accrued = _money(accrued + year_interest)

        at_horizon = year == horizon_years
        at_maturity = year_in_cycle == product.maturity_years
        exit_snap = _make_exit(
            lump_sum=lump_sum,
            bonds=bonds,
            idle=idle,
            interest_base=accrued,
            year_in_cycle=year_in_cycle,
            at_maturity=at_maturity,
            belka=belka,
            product=product,
        )

        if at_maturity:
            # Maturity: pay capitalized interest (no fee); roll proceeds into new EDO.
            net = _apply_belka(accrued, belka)
            idle = _money(idle + bonds * FACE_VALUE + net)
            bonds = 0
            accrued = 0.0
            basis = 0.0
            year_in_cycle = 0
            bonds, idle = _buy_bonds(idle, bonds)
            basis = _money(bonds * FACE_VALUE)
            points.append(
                YearPoint(
                    year=year,
                    wallet=_money(basis + idle),
                    income=net,
                    bonds=bonds,
                    idle_cash=idle,
                    is_roll=True,
                    exit=exit_snap,
                )
            )
        elif at_horizon:
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
                    exit=exit_snap,
                )
            )
            idle = wallet
            bonds = 0
            accrued = 0.0
            basis = 0.0
            year_in_cycle = 0
        else:
            # Hold: interest stays capitalized inside the bond.
            points.append(
                YearPoint(
                    year=year,
                    wallet=_money(basis + idle),
                    income=0.0,
                    bonds=bonds,
                    idle_cash=_money(idle),
                    exit=exit_snap,
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
    coi: ProductParams = COI,
    edo: ProductParams = EDO,
) -> SimulationResult:
    coi_path = _simulate_coi(lump_sum, horizon_years, inflation, belka, coi)
    edo_path = _simulate_edo(lump_sum, horizon_years, inflation, belka, edo)
    return SimulationResult(
        coi=coi_path,
        edo=edo_path,
        delta_edo_minus_coi=_money(edo_path.final_wallet - coi_path.final_wallet),
    )

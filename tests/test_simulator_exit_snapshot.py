"""Counterfactual redeem-at-year-N ExitSnapshot invariants (#21 / #22)."""

from bondwise.simulator import simulate


def test_horizon_year_exit_matches_hold_path_wallet_and_income():
    result = simulate(lump_sum=1000.0, horizon_years=1, inflation=0.03, belka=True)

    coi = result.coi.years[0]
    assert coi.exit.cash_out == coi.wallet
    assert coi.exit.income == coi.income
    assert coi.exit.fee == 20.0
    assert coi.exit.tax == 5.22
    assert coi.exit.profit == 22.28

    edo = result.edo.years[0]
    assert edo.exit.cash_out == edo.wallet
    assert edo.exit.income == edo.income
    assert edo.exit.fee == 30.0
    assert edo.exit.tax == 4.46
    assert edo.exit.profit == 19.04


def test_hold_year_exit_differs_from_wallet_and_uses_pre_reinvest_fee_base():
    # Hold year: exit cash-out != wallet; COI exit fee uses pre-reinvest bonds.
    held = simulate(lump_sum=1000.0, horizon_years=2, inflation=0.0, belka=True)
    coi_y1 = held.coi.years[0]
    assert coi_y1.wallet == 1038.48
    assert coi_y1.income == 38.48
    assert coi_y1.exit.fee == 20.0
    assert coi_y1.exit.tax == 5.22
    assert coi_y1.exit.income == 22.28
    assert coi_y1.exit.cash_out == 1022.28
    assert coi_y1.exit.profit == 22.28
    assert coi_y1.exit.cash_out != coi_y1.wallet

    edo_y1 = held.edo.years[0]
    assert edo_y1.income == 0.0
    assert edo_y1.exit.income == 19.04
    assert edo_y1.exit.cash_out == 1019.04
    assert edo_y1.exit.cash_out != edo_y1.wallet

    # Post-reinvest bonds would yield fee 206; true exit fee uses 100 bonds → 200.
    big = simulate(lump_sum=10000.0, horizon_years=8, inflation=0.025, belka=True)
    coi_big = big.coi.years[0]
    assert coi_big.bonds == 103
    assert coi_big.exit.fee == 200.0
    assert coi_big.exit.tax == 52.25
    assert coi_big.exit.income == 222.75
    assert coi_big.exit.cash_out == 10222.75


def test_maturity_year_exit_fee_zero_and_cash_out_equals_wallet():
    result = simulate(lump_sum=1000.0, horizon_years=4, inflation=0.0, belka=True)
    coi_y4 = result.coi.years[3]
    assert coi_y4.is_roll is True
    assert coi_y4.exit.fee == 0.0
    assert coi_y4.exit.cash_out == coi_y4.wallet
    assert coi_y4.exit.income == coi_y4.income
    assert coi_y4.exit.tax > 0.0


def test_belka_off_exit_tax_is_zero_and_columns_remain():
    result = simulate(lump_sum=1000.0, horizon_years=2, inflation=0.0, belka=False)
    coi = result.coi.years[0]
    edo = result.edo.years[0]
    assert coi.exit.tax == 0.0
    assert edo.exit.tax == 0.0
    assert coi.exit.fee == 20.0
    assert coi.exit.income == 27.5
    assert coi.exit.cash_out == 1027.5
    assert edo.exit.income == 23.5
    assert edo.exit.cash_out == 1023.5

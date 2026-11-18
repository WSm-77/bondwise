"""Reinvest on (default) vs keep-cash off (#reinvest-toggle)."""

from bondwise.simulator import simulate


def test_reinvest_default_matches_explicit_true():
    kwargs = dict(lump_sum=10_000.0, horizon_years=4, inflation=0.0, belka=True)
    defaulted = simulate(**kwargs)
    explicit = simulate(**kwargs, reinvest=True)
    assert defaulted.coi.years[0].bonds == explicit.coi.years[0].bonds == 103
    assert defaulted.coi.final_wallet == explicit.coi.final_wallet
    assert defaulted.edo.final_wallet == explicit.edo.final_wallet


def test_coi_reinvest_off_keeps_coupon_as_idle_no_extra_bonds():
    # 10_000 → 100 bonds. Y1 net coupon 384.75 stays idle; bonds stay 100.
    result = simulate(
        lump_sum=10_000.0, horizon_years=2, inflation=0.0, belka=True, reinvest=False
    )
    y1 = result.coi.years[0]
    assert y1.bonds == 100
    assert y1.idle_cash == 384.75
    assert y1.income == 384.75
    assert y1.wallet == 100 * 100 + 384.75


def test_coi_reinvest_off_maturity_no_roll():
    result = simulate(
        lump_sum=1000.0, horizon_years=4, inflation=0.0, belka=False, reinvest=False
    )
    y4 = result.coi.years[3]
    assert y4.is_roll is False
    assert y4.bonds == 0
    assert y4.idle_cash == y4.wallet
    assert y4.wallet > 1000.0


def test_coi_reinvest_off_past_maturity_stays_idle():
    result = simulate(
        lump_sum=1000.0, horizon_years=6, inflation=0.0, belka=False, reinvest=False
    )
    y4 = result.coi.years[3]
    y5 = result.coi.years[4]
    assert y4.bonds == 0 and y4.is_roll is False
    assert y5.bonds == 0
    assert y5.idle_cash == y4.idle_cash
    assert y5.income == 0.0


def test_edo_reinvest_off_maturity_no_rebuy():
    result = simulate(
        lump_sum=1000.0, horizon_years=10, inflation=0.02, belka=False, reinvest=False
    )
    y10 = result.edo.years[9]
    assert y10.is_roll is False
    assert y10.bonds == 0
    assert y10.idle_cash == y10.wallet
    assert y10.income > 0


def test_edo_reinvest_off_hold_years_unchanged_capitalization():
    # EDO hold path has no coupon payout; reinvest flag must not change y1 hold.
    on = simulate(lump_sum=100.0, horizon_years=2, inflation=0.0, belka=False, reinvest=True)
    off = simulate(
        lump_sum=100.0, horizon_years=2, inflation=0.0, belka=False, reinvest=False
    )
    assert on.edo.years[0].wallet == off.edo.years[0].wallet == 105.35
    assert on.edo.years[0].bonds == off.edo.years[0].bonds == 1


def test_exit_snapshot_pre_hold_buy_with_reinvest_off():
    # Exit uses pre-mutation state; hold-path idle growth must not feed exit fee base.
    held = simulate(
        lump_sum=10_000.0, horizon_years=2, inflation=0.0, belka=True, reinvest=False
    )
    y1 = held.coi.years[0]
    assert y1.bonds == 100
    assert y1.exit.fee == 200.0  # 100 bonds * 2 PLN, not inflated by coupon idle
    assert y1.wallet != y1.exit.cash_out

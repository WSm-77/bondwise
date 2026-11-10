"""COI coupon reinvest and 4-year rolls (#4)."""

from bondwise.simulator import simulate


def test_coi_net_coupon_reinvests_into_whole_bonds():
    # 10_000 PLN → 100 bonds. Y1 coupon gross 475; Belka 19% → net 384.75 → 3 bonds + 84.75 idle
    result = simulate(lump_sum=10_000.0, horizon_years=2, inflation=0.0, belka=True)
    y1 = result.coi.years[0]
    assert y1.bonds == 103
    assert y1.idle_cash == 84.75
    assert y1.income == 384.75
    assert y1.wallet == 103 * 100 + 84.75


def test_coi_exact_4y_maturity_no_early_fee():
    result = simulate(lump_sum=1000.0, horizon_years=4, inflation=0.0, belka=False)
    y4 = result.coi.years[3]
    # At maturity, income is the year-4 coupon only (no fee); wallet is fully cashed then reinvested
    assert y4.income > 0
    # After roll at maturity into new COI, bonds should be > 0 for continuing capital
    assert y4.bonds >= 10
    assert y4.is_roll is True


def test_coi_roll_into_years_5_through_8():
    result = simulate(lump_sum=1000.0, horizon_years=8, inflation=0.02, belka=True)
    assert len(result.coi.years) == 8
    roll_years = [p.year for p in result.coi.years if p.is_roll]
    assert 4 in roll_years
    assert 8 in roll_years
    # Continuous path: every year has a wallet, final > initial after compounding coupons/rolls
    assert result.coi.final_wallet > 1000.0
    assert all(p.wallet > 0 for p in result.coi.years)

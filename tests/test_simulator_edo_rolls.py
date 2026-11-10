"""EDO capitalization and 10-year rolls (#5)."""

from bondwise.simulator import simulate


def test_edo_interest_capitalizes_on_hold_path():
    # 1 bond, 2y hold then we only inspect year 1 hold (horizon 2 exits at y2).
    # At end of year 1 while holding: wallet = 100 * 1.0535 = 105.35, income 0
    result = simulate(lump_sum=100.0, horizon_years=2, inflation=0.0, belka=False)
    assert result.edo.years[0].wallet == 105.35
    assert result.edo.years[0].income == 0.0
    # Year 2 early exit: basis after y2 = 105.35 * (1+0.02) = 107.457 → round
    # accrued = 7.46; fee min(3, 7.46)=3; net 4.46; wallet 104.46
    assert result.edo.years[1].income == 4.46
    assert result.edo.years[1].wallet == 104.46


def test_edo_exact_10y_maturity_no_early_fee():
    result = simulate(lump_sum=1000.0, horizon_years=10, inflation=0.02, belka=False)
    y10 = result.edo.years[9]
    assert y10.is_roll is True
    assert y10.bonds >= 10
    assert y10.income > 0  # full accrued interest paid, no fee


def test_edo_roll_past_year_10():
    result = simulate(lump_sum=1000.0, horizon_years=12, inflation=0.02, belka=True)
    assert len(result.edo.years) == 12
    roll_years = [p.year for p in result.edo.years if p.is_roll]
    assert 10 in roll_years
    assert result.edo.final_wallet > 1000.0
    # After roll, year 11 is a hold year in the new cycle (income 0 while capitalizing)
    assert result.edo.years[10].income == 0.0

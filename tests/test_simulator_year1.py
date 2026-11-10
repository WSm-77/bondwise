"""Year-1 COI vs EDO behavior at the pure simulator seam (#2)."""

from bondwise.simulator import simulate


def test_year1_belka_on_divisible_lump_sum():
    result = simulate(lump_sum=1000.0, horizon_years=1, inflation=0.03, belka=True)

    # 10 bonds @ 100 PLN; idle 0
    # COI: interest 47.50, fee 20, after-fee 27.50, net after Belka 22.28 → wallet 1022.28
    assert result.coi.years[0].year == 1
    assert result.coi.years[0].wallet == 1022.28
    assert result.coi.years[0].income == 22.28
    assert result.coi.years[0].bonds == 10
    assert result.coi.years[0].idle_cash == 0.0

    # EDO: interest 53.50, fee 30, after-fee 23.50, net after Belka 19.04 → wallet 1019.04
    assert result.edo.years[0].wallet == 1019.04
    assert result.edo.years[0].income == 19.04
    assert result.edo.years[0].bonds == 10
    assert result.edo.years[0].idle_cash == 0.0

    assert result.coi.final_wallet == 1022.28
    assert result.edo.final_wallet == 1019.04
    assert result.delta_edo_minus_coi == -3.24


def test_year1_belka_off():
    result = simulate(lump_sum=1000.0, horizon_years=1, inflation=0.03, belka=False)

    # COI: 1000 + 47.50 - 20 = 1027.50; income 27.50
    assert result.coi.years[0].wallet == 1027.5
    assert result.coi.years[0].income == 27.5

    # EDO: 1000 + 53.50 - 30 = 1023.50; income 23.50
    assert result.edo.years[0].wallet == 1023.5
    assert result.edo.years[0].income == 23.5


def test_year1_non_divisible_lump_sum_idle_remainder():
    result = simulate(lump_sum=1050.0, horizon_years=1, inflation=0.0, belka=True)

    # 10 bonds + 50 idle; same bond math as 1000, idle folded into wallet
    assert result.coi.years[0].bonds == 10
    assert result.coi.years[0].idle_cash == 50.0
    assert result.coi.years[0].wallet == 1072.28
    assert result.edo.years[0].idle_cash == 50.0
    assert result.edo.years[0].wallet == 1069.04

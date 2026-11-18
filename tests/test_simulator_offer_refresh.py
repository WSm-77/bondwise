"""COI offer schedule / offer refresh (strategy 6)."""

from bondwise.params import COI, COI_OFFER_REFRESH_DEMO, COI_REFRESH_DEMO_NEXT, ProductParams
from bondwise.simulator import simulate


def test_default_simulate_matches_fixed_coi_injection():
    """No schedule → identical to explicit fixed coi=COI (main-equivalent)."""
    a = simulate(lump_sum=10_000.0, horizon_years=8, inflation=0.025, belka=True)
    b = simulate(
        lump_sum=10_000.0,
        horizon_years=8,
        inflation=0.025,
        belka=True,
        coi=COI,
        coi_offer_schedule=None,
    )
    assert a.coi.final_wallet == b.coi.final_wallet
    assert a.edo.final_wallet == b.edo.final_wallet
    assert a.delta_edo_minus_coi == b.delta_edo_minus_coi


def test_single_entry_schedule_matches_fixed_offer():
    """One-cycle schedule behaves like blind fixed COI for an 8y (two-cycle) path
    because the last entry is reused past the end."""
    fixed = simulate(lump_sum=1000.0, horizon_years=8, inflation=0.02, belka=True)
    scheduled = simulate(
        lump_sum=1000.0,
        horizon_years=8,
        inflation=0.02,
        belka=True,
        coi_offer_schedule=[COI],
    )
    assert scheduled.coi.final_wallet == fixed.coi.final_wallet


def test_schedule_applies_next_offer_only_at_cycle_boundary():
    """Years 1–4 use schedule[0]; after the year-4 roll, years 5–8 use schedule[1]."""
    weak = ProductParams(
        code="WEAK",
        year1_rate=0.01,
        margin=0.0,
        early_exit_fee_per_bond=2.0,
        maturity_years=4,
        fee_uncapped_after_year1=True,
    )
    strong = ProductParams(
        code="STRONG",
        year1_rate=0.20,
        margin=0.10,
        early_exit_fee_per_bond=2.0,
        maturity_years=4,
        fee_uncapped_after_year1=True,
    )
    both_weak = simulate(
        lump_sum=1000.0,
        horizon_years=8,
        inflation=0.0,
        belka=False,
        coi_offer_schedule=[weak, weak],
    )
    refresh = simulate(
        lump_sum=1000.0,
        horizon_years=8,
        inflation=0.0,
        belka=False,
        coi_offer_schedule=[weak, strong],
    )
    # Pre-roll years match (same first offer).
    for i in range(3):
        assert refresh.coi.years[i].wallet == both_weak.coi.years[i].wallet
        assert refresh.coi.years[i].income == both_weak.coi.years[i].income
    # Year 4 is the roll boundary: maturity coupon still on the first offer,
    # then proceeds buy into the next cycle.
    assert refresh.coi.years[3].is_roll is True
    assert refresh.coi.years[3].income == both_weak.coi.years[3].income
    # Post-roll path diverges once the strong offer is live.
    assert refresh.coi.years[4].income > both_weak.coi.years[4].income
    assert refresh.coi.final_wallet > both_weak.coi.final_wallet


def test_demo_schedule_refreshed_coi_beats_edo_where_fixed_loses():
    """Documented demo: 10_000 PLN, 8y, 2.5% inflation, Belka on.

    Fixed COI (blind) loses to EDO; COI_OFFER_REFRESH_DEMO beats EDO after roll.
    """
    lump, hz, inf, belka = 10_000.0, 8, 0.025, True
    fixed = simulate(lump_sum=lump, horizon_years=hz, inflation=inf, belka=belka)
    refreshed = simulate(
        lump_sum=lump,
        horizon_years=hz,
        inflation=inf,
        belka=belka,
        coi_offer_schedule=COI_OFFER_REFRESH_DEMO,
    )
    assert fixed.coi.final_wallet < fixed.edo.final_wallet
    assert refreshed.coi.final_wallet > refreshed.edo.final_wallet
    assert COI_OFFER_REFRESH_DEMO[0] == COI
    assert COI_OFFER_REFRESH_DEMO[1] == COI_REFRESH_DEMO_NEXT
    # Sanity on the hypothetical next-window rates used by the fixture.
    assert COI_REFRESH_DEMO_NEXT.year1_rate == 0.065
    assert COI_REFRESH_DEMO_NEXT.margin == 0.025

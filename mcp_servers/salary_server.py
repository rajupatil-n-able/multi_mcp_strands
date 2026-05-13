from mcp.server.fastmcp import FastMCP

mcp = FastMCP("Salary & HR MCP Server")


# ── Tool 1: Salary Breakup ────────────────────────────────────────────────────
@mcp.tool()
def salary_breakup(annual_ctc: float) -> dict:
    """
    Calculate detailed monthly and annual salary breakup from annual CTC.
    Includes Basic, HRA, PF, Professional Tax, Take-Home etc.
    Example: annual_ctc = 1200000 (12 LPA)
    """
    monthly_ctc = annual_ctc / 12

    basic = monthly_ctc * 0.40
    hra = basic * 0.50
    special_allowance = monthly_ctc * 0.20
    medical_allowance = 1250.0
    travel_allowance = 1600.0

    # Deductions
    employee_pf = basic * 0.12
    employer_pf = basic * 0.12
    professional_tax = 200.0
    income_tax_monthly = (annual_ctc * 0.10) / 12  # approximation

    gross_salary = basic + hra + special_allowance + medical_allowance + travel_allowance
    total_deductions = employee_pf + professional_tax + income_tax_monthly
    take_home = gross_salary - total_deductions

    return {
        "annual_ctc": f"₹{annual_ctc:,.0f}",
        "monthly_ctc": f"₹{monthly_ctc:,.2f}",
        "earnings": {
            "basic": f"₹{basic:,.2f}",
            "hra": f"₹{hra:,.2f}",
            "special_allowance": f"₹{special_allowance:,.2f}",
            "medical_allowance": f"₹{medical_allowance:,.2f}",
            "travel_allowance": f"₹{travel_allowance:,.2f}",
            "gross_salary": f"₹{gross_salary:,.2f}",
        },
        "deductions": {
            "employee_pf_12pct": f"₹{employee_pf:,.2f}",
            "employer_pf_12pct": f"₹{employer_pf:,.2f}",
            "professional_tax": f"₹{professional_tax:,.2f}",
            "income_tax_approx": f"₹{income_tax_monthly:,.2f}",
            "total_deductions": f"₹{total_deductions:,.2f}",
        },
        "net_take_home_monthly": f"₹{take_home:,.2f}",
        "net_take_home_annual": f"₹{take_home * 12:,.2f}",
    }


# ── Tool 2: Tax Slab Calculator ───────────────────────────────────────────────
@mcp.tool()
def tax_calculator(annual_income: float, regime: str = "new") -> dict:
    """
    Calculate income tax based on Indian tax slabs.
    regime: 'new' (default) or 'old'
    Example: annual_income=800000, regime='new'
    """
    tax = 0.0

    if regime == "new":
        slabs = [
            (300000, 0.00),
            (300000, 0.05),
            (300000, 0.10),
            (300000, 0.15),
            (300000, 0.20),
            (float("inf"), 0.30),
        ]
    else:  # old regime
        slabs = [
            (250000, 0.00),
            (250000, 0.05),
            (500000, 0.20),
            (float("inf"), 0.30),
        ]

    remaining = annual_income
    breakdown = []
    for slab, rate in slabs:
        if remaining <= 0:
            break
        taxable = min(remaining, slab)
        slab_tax = taxable * rate
        tax += slab_tax
        breakdown.append(f"₹{taxable:,.0f} @ {int(rate*100)}% = ₹{slab_tax:,.2f}")
        remaining -= taxable

    cess = tax * 0.04
    total_tax = tax + cess

    return {
        "annual_income": f"₹{annual_income:,.0f}",
        "regime": regime,
        "slab_breakdown": breakdown,
        "base_tax": f"₹{tax:,.2f}",
        "cess_4pct": f"₹{cess:,.2f}",
        "total_tax": f"₹{total_tax:,.2f}",
        "monthly_tax": f"₹{total_tax/12:,.2f}",
        "effective_rate": f"{(total_tax/annual_income)*100:.2f}%",
    }


# ── Tool 3: Hike Calculator ───────────────────────────────────────────────────
@mcp.tool()
def hike_calculator(current_ctc: float, hike_percentage: float) -> dict:
    """
    Calculate new CTC after a hike percentage.
    Example: current_ctc=800000, hike_percentage=20
    """
    hike_amount = current_ctc * (hike_percentage / 100)
    new_ctc = current_ctc + hike_amount

    return {
        "current_ctc": f"₹{current_ctc:,.0f}",
        "hike_percentage": f"{hike_percentage}%",
        "hike_amount": f"₹{hike_amount:,.2f}",
        "new_ctc": f"₹{new_ctc:,.2f}",
        "new_monthly": f"₹{new_ctc/12:,.2f}",
    }


# ── Tool 4: Offer Comparator ──────────────────────────────────────────────────
@mcp.tool()
def compare_offers(offer1_ctc: float, offer2_ctc: float,
                   offer1_name: str = "Company A",
                   offer2_name: str = "Company B") -> dict:
    """
    Compare two job offers by CTC and show monthly difference.
    Example: offer1_ctc=1200000, offer2_ctc=1500000
    """
    diff = offer2_ctc - offer1_ctc
    better = offer2_name if diff > 0 else offer1_name
    return {
        offer1_name: f"₹{offer1_ctc:,.0f} p.a. (₹{offer1_ctc/12:,.0f}/mo)",
        offer2_name: f"₹{offer2_ctc:,.0f} p.a. (₹{offer2_ctc/12:,.0f}/mo)",
        "difference": f"₹{abs(diff):,.0f} p.a. (₹{abs(diff)/12:,.0f}/mo)",
        "better_offer": better,
    }


# ── Entry point ───────────────────────────────────────────────────────────────
if __name__ == "__main__":
    mcp.run(transport="stdio")



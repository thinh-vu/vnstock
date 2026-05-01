from vnstock.ui.domains.reference.company import CompanyReference
from vnstock.ui.domains.reference.equity import EquityReference
from vnstock.ui.reference import Reference


def test_reference_instantiation():
    """Test Reference class can be instantiated."""
    ref = Reference()
    assert ref is not None


def test_reference_equity_property():
    """Test Reference.equity returns EquityReference."""
    ref = Reference()
    equity = ref.equity
    assert isinstance(equity, EquityReference)


def test_reference_company_method():
    """Test Reference.company() returns CompanyReference."""
    ref = Reference()
    company = ref.company(symbol="FPT")
    assert isinstance(company, CompanyReference)

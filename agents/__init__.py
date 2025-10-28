"""Init file for agents module"""

from .asset_verification_agent import get_asset_verification_agent
from .asset_valuation_agent import get_asset_valuation_agent
from .onchain_notarization_agent import get_onchain_notarization_agent
from .rwa_education_agent import get_rwa_education_agent
from .rwa_investment_agent import get_rwa_investment_agent

__all__ = [
    "get_asset_verification_agent",
    "get_asset_valuation_agent",
    "get_onchain_notarization_agent",
    "get_rwa_education_agent",
    "get_rwa_investment_agent",
]
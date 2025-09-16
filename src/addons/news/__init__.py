"""
News aggregation addon module initialization.
"""

from .aggregator import *
from .cryptopanic_tools import *
from .dappier_tools import *
from .feargreed_tools import *

__all__ = [
    "NewsAggregator", "get_news_feed", "analyze_sentiment",
    "CryptoPanicClient", "get_cryptopanic_news", 
    "DappierClient", "get_dappier_insights",
    "FearGreedClient", "get_fear_greed_data", "get_fear_greed_history"
]
"""
Suite configuration loader (Proxy).
"""
from .suite.loader import SuiteLoader
from .suite.errors import SuiteLoadError
from .suite import load_suite

__all__ = ["SuiteLoader", "SuiteLoadError", "load_suite"]

"""
SentinelDF Cloud - Enterprise Architecture

This package contains the scalable, production-ready components for
SentinelDF Cloud API service.
"""

__version__ = "3.0.0"

# Version info
VERSION_INFO = {
    "major": 3,
    "minor": 0,
    "patch": 0,
    "release": "stable"
}

# Feature flags
FEATURES = {
    "async_jobs": True,
    "pre_signed_urls": True,
    "onnx_inference": True,
    "auto_scaling": True,
    "multi_region": False,  # Coming soon
    "stripe_billing": False  # Coming soon
}

"""Pytest configuration for the whole test suite.

Registers a default Hypothesis profile so that every property-based test in the
``text-feature-experiments`` layer (properties P1-P15) runs at least 100
iterations, as required by the design and Requirement 15.1.

The profile is registered and immediately loaded so it applies to the entire
suite by default. The active profile can still be overridden per-run via the
``HYPOTHESIS_PROFILE`` environment variable (e.g. a "ci" profile with more
examples, or a "dev" profile with fewer for a faster inner loop).
"""

import os

from hypothesis import HealthCheck, settings

# Minimum number of examples every property test must explore (design: >= 100).
MIN_EXAMPLES = 100

# Default profile: guarantee at least 100 iterations per property test.
settings.register_profile(
    "default",
    max_examples=MIN_EXAMPLES,
    # Property tests here build small DataFrames / feature tables; the default
    # deadline can produce flaky timeouts on slower machines, so disable it and
    # relax the too-slow health check rather than let timing cause failures.
    deadline=None,
    suppress_health_check=[HealthCheck.too_slow],
)

# A heavier profile for thorough/CI runs (opt-in via HYPOTHESIS_PROFILE=ci).
settings.register_profile(
    "ci",
    max_examples=500,
    deadline=None,
    suppress_health_check=[HealthCheck.too_slow],
)

# Load the profile named by HYPOTHESIS_PROFILE, defaulting to "default" so that
# the >= 100 iterations guarantee holds for the whole suite without extra flags.
settings.load_profile(os.environ.get("HYPOTHESIS_PROFILE", "default"))

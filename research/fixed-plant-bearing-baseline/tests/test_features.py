import numpy as np
import pytest

from mineos_bearing_baseline.features import FEATURE_NAMES, extract_features


def test_feature_vector_is_fixed_shape_and_finite():
    t = np.arange(4096, dtype=np.float64)
    signal = np.sin(2 * np.pi * 0.04 * t) + 0.05 * np.sin(2 * np.pi * 0.23 * t)
    features = extract_features(signal)
    assert features.shape == (len(FEATURE_NAMES),)
    assert np.all(np.isfinite(features))
    assert features[1] > 0
    assert np.isclose(features[13:16].sum(), 1.0)


def test_constant_signal_has_finite_features():
    features = extract_features(np.ones(128))
    assert np.all(np.isfinite(features))
    assert features[1] == 0


@pytest.mark.parametrize("signal", [np.ones(8), np.array([1.0, np.nan] * 16)])
def test_invalid_window_is_rejected(signal):
    with pytest.raises(ValueError):
        extract_features(signal)

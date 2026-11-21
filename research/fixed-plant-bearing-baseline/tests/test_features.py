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



def test_envelope_spectrum_recovers_amplitude_modulation_frequency():
    sample_rate = 12000.0
    t = np.arange(4096, dtype=np.float64) / sample_rate
    modulation = 1.0 + 0.7 * np.sin(2 * np.pi * 150.0 * t)
    signal = modulation * np.sin(2 * np.pi * 2400.0 * t)
    features = extract_features(signal, sample_rate_hz=sample_rate)
    dominant_index = FEATURE_NAMES.index("envelope_dominant_frequency_hz")
    band_start = FEATURE_NAMES.index("envelope_energy_0_50hz_ratio")
    assert abs(features[dominant_index] - 150.0) < 5.0
    assert np.isclose(features[band_start:].sum(), 1.0)


def test_envelope_feature_rejects_invalid_sample_rate():
    with pytest.raises(ValueError, match="sample_rate_hz"):
        extract_features(np.ones(128), sample_rate_hz=0)

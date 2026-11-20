"""Deterministic, lightweight time-domain and normalized spectral features."""

from __future__ import annotations

import numpy as np

FEATURE_NAMES = (
    "mean", "std", "rms", "absolute_mean", "peak_to_peak", "skewness",
    "kurtosis_excess", "crest_factor", "shape_factor", "impulse_factor",
    "clearance_factor", "spectral_centroid_nyquist_ratio",
    "dominant_frequency_nyquist_ratio", "spectral_energy_low_ratio",
    "spectral_energy_mid_ratio", "spectral_energy_high_ratio",
)


def extract_features(signal: np.ndarray) -> np.ndarray:
    """Return a fixed feature vector for one finite, one-dimensional signal window.

    Frequency bands are normalized to Nyquist so recordings with different
    documented sample rates have the same feature schema. The sampling rate
    remains part of recording provenance and must not be guessed.
    """
    x = np.asarray(signal, dtype=np.float64).reshape(-1)
    if x.size < 16:
        raise ValueError("A signal window must contain at least 16 samples")
    if not np.all(np.isfinite(x)):
        raise ValueError("Signal window contains NaN or infinite values")

    mean = float(np.mean(x))
    centered = x - mean
    std = float(np.std(centered))
    rms = float(np.sqrt(np.mean(np.square(x))))
    absolute = np.abs(x)
    absolute_mean = float(np.mean(absolute))
    peak = float(np.max(absolute))
    peak_to_peak = float(np.ptp(x))
    eps = np.finfo(np.float64).eps

    if std <= eps:
        skewness = 0.0
        kurtosis_excess = 0.0
    else:
        normalized = centered / std
        skewness = float(np.mean(normalized**3))
        kurtosis_excess = float(np.mean(normalized**4) - 3.0)

    root_mean_square = rms if rms > eps else eps
    absolute_mean_safe = absolute_mean if absolute_mean > eps else eps
    mean_square_root = float(np.mean(np.sqrt(absolute)))
    mean_square_root_sq = mean_square_root**2

    crest_factor = peak / root_mean_square
    shape_factor = root_mean_square / absolute_mean_safe
    impulse_factor = peak / absolute_mean_safe
    clearance_factor = peak / max(mean_square_root_sq, eps)

    spectrum = np.abs(np.fft.rfft(centered)) ** 2
    if spectrum.size > 1:
        spectrum[0] = 0.0
    total_energy = float(np.sum(spectrum))
    if total_energy <= eps:
        centroid_ratio = dominant_ratio = 0.0
        low_ratio = mid_ratio = high_ratio = 0.0
    else:
        normalized_frequency = np.fft.rfftfreq(x.size, d=1.0) / 0.5
        centroid_ratio = float(np.sum(normalized_frequency * spectrum) / total_energy)
        dominant_ratio = float(normalized_frequency[int(np.argmax(spectrum))])
        low_ratio = float(np.sum(spectrum[normalized_frequency < 0.10]) / total_energy)
        mid_ratio = float(
            np.sum(spectrum[(normalized_frequency >= 0.10) & (normalized_frequency < 0.30)])
            / total_energy
        )
        high_ratio = float(np.sum(spectrum[normalized_frequency >= 0.30]) / total_energy)

    values = np.asarray(
        [
            mean, std, rms, absolute_mean, peak_to_peak, skewness, kurtosis_excess,
            crest_factor, shape_factor, impulse_factor, clearance_factor,
            centroid_ratio, dominant_ratio, low_ratio, mid_ratio, high_ratio,
        ],
        dtype=np.float64,
    )
    if values.shape != (len(FEATURE_NAMES),) or not np.all(np.isfinite(values)):
        raise RuntimeError("Feature extraction produced an invalid feature vector")
    return values

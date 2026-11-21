"""Deterministic time-domain, spectral and envelope-spectrum bearing features."""

from __future__ import annotations

import numpy as np
from scipy.signal import hilbert

FEATURE_NAMES = (
    "mean", "std", "rms", "absolute_mean", "peak_to_peak", "skewness",
    "kurtosis_excess", "crest_factor", "shape_factor", "impulse_factor",
    "clearance_factor", "spectral_centroid_nyquist_ratio",
    "dominant_frequency_nyquist_ratio", "spectral_energy_low_ratio",
    "spectral_energy_mid_ratio", "spectral_energy_high_ratio",
    "envelope_rms", "envelope_kurtosis_excess",
    "envelope_spectral_centroid_hz", "envelope_dominant_frequency_hz",
    "envelope_energy_0_50hz_ratio", "envelope_energy_50_100hz_ratio",
    "envelope_energy_100_200hz_ratio", "envelope_energy_200_400hz_ratio",
    "envelope_energy_400_800hz_ratio", "envelope_energy_800_1600hz_ratio",
    "envelope_energy_above_1600hz_ratio",
)


def extract_features(
    signal: np.ndarray,
    *,
    sample_rate_hz: float = 1.0,
) -> np.ndarray:
    """Return a fixed feature vector for one finite, one-dimensional signal window.

    The original spectral features are normalized to Nyquist. Additional envelope
    spectrum features retain physical Hz bands so bearing-modulation energy can be
    compared at the documented acquisition rate. The caller must pass the true
    sample rate; it is never inferred from the signal.
    """
    x = np.asarray(signal, dtype=np.float64).reshape(-1)
    if x.size < 16:
        raise ValueError("A signal window must contain at least 16 samples")
    if not np.all(np.isfinite(x)):
        raise ValueError("Signal window contains NaN or infinite values")
    if not np.isfinite(sample_rate_hz) or sample_rate_hz <= 0:
        raise ValueError("sample_rate_hz must be a finite positive value")

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

    # Hilbert envelope demodulation exposes lower-frequency amplitude modulation
    # caused by rolling-element impacts and bearing defect repetition.
    envelope = np.abs(hilbert(centered))
    envelope_centered = envelope - float(np.mean(envelope))
    envelope_rms = float(np.sqrt(np.mean(np.square(envelope_centered))))
    if envelope_rms <= eps:
        envelope_kurtosis = 0.0
    else:
        envelope_normalized = envelope_centered / envelope_rms
        envelope_kurtosis = float(np.mean(envelope_normalized**4) - 3.0)

    envelope_spectrum = np.abs(np.fft.rfft(envelope_centered)) ** 2
    if envelope_spectrum.size > 1:
        envelope_spectrum[0] = 0.0
    envelope_frequencies = np.fft.rfftfreq(x.size, d=1.0 / sample_rate_hz)
    envelope_total = float(np.sum(envelope_spectrum))
    if envelope_total <= eps:
        envelope_centroid_hz = envelope_dominant_hz = 0.0
        envelope_band_ratios = [0.0] * 7
    else:
        envelope_centroid_hz = float(
            np.sum(envelope_frequencies * envelope_spectrum) / envelope_total
        )
        envelope_dominant_hz = float(
            envelope_frequencies[int(np.argmax(envelope_spectrum))]
        )
        band_edges = (0.0, 50.0, 100.0, 200.0, 400.0, 800.0, 1600.0, np.inf)
        envelope_band_ratios = [
            float(
                np.sum(
                    envelope_spectrum[
                        (envelope_frequencies >= lower)
                        & (envelope_frequencies < upper)
                    ]
                )
                / envelope_total
            )
            for lower, upper in zip(band_edges[:-1], band_edges[1:])
        ]

    values = np.asarray(
        [
            mean, std, rms, absolute_mean, peak_to_peak, skewness, kurtosis_excess,
            crest_factor, shape_factor, impulse_factor, clearance_factor,
            centroid_ratio, dominant_ratio, low_ratio, mid_ratio, high_ratio,
            envelope_rms, envelope_kurtosis, envelope_centroid_hz, envelope_dominant_hz,
            *envelope_band_ratios,
        ],
        dtype=np.float64,
    )
    if values.shape != (len(FEATURE_NAMES),) or not np.all(np.isfinite(values)):
        raise RuntimeError("Feature extraction produced an invalid feature vector")
    return values

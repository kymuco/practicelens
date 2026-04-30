from __future__ import annotations

from practicelens.alignment import AlignmentPath, align_feature_bundles
from practicelens.application.contracts import AnalyzeRequest, AnalyzeResult
from practicelens.application.pipeline import AnalysisPipeline
from practicelens.domain.models import AnalysisConfidence, AnalysisOverview, AnalysisReport, FeatureFlags
from practicelens.features import FeatureBundle, extract_feature_bundle
from practicelens.io import ensure_finite_audio, load_wav_audio
from practicelens.io.models import LoadedAudio
from practicelens.preprocessing import peak_normalize, resample_linear, trim_silence
from practicelens.reporting.artifacts import write_report_artifacts
from practicelens.scoring import score_aligned_features
from practicelens.scoring.models import ScoringBundle


class OfflineReferenceAnalysisPipeline(AnalysisPipeline):
    """Concrete offline reference-aware analysis pipeline for v0.1."""

    def analyze(self, request: AnalyzeRequest) -> AnalyzeResult:
        analysis_input = request.to_analysis_input()
        config = request.config

        reference_audio = self._prepare_audio(load_wav_audio(analysis_input.reference_path), config)
        take_audio = self._prepare_audio(load_wav_audio(analysis_input.take_path), config)

        reference_features = extract_feature_bundle(reference_audio, config)
        take_features = extract_feature_bundle(take_audio, config)
        alignment = align_feature_bundles(reference_features, take_features)
        scoring = score_aligned_features(reference_features, take_features, alignment, config)

        report = AnalysisReport(
            overview=AnalysisOverview(),
            inputs=analysis_input,
            feature_flags=FeatureFlags(),
            scores=scoring.component_scores,
            metrics=scoring.metrics,
            sections=scoring.sections,
            analysis_confidence=_analysis_confidence(reference_features, take_features, alignment, scoring),
            practice_loops=scoring.practice_loops,
            top_strengths=scoring.top_strengths,
            top_weaknesses=scoring.top_weaknesses,
            next_practice_step=scoring.next_practice_step,
            feedback=scoring.feedback,
            artifacts=(),
            summary=scoring.summary,
        )

        if request.out_dir is not None:
            report, _ = write_report_artifacts(report, request.out_dir)

        return AnalyzeResult(report=report)

    def _prepare_audio(self, audio: LoadedAudio, config) -> LoadedAudio:
        audio = ensure_finite_audio(audio)
        samples = audio.samples
        target_rate = config.target_sample_rate
        if audio.sample_rate != target_rate:
            samples = resample_linear(samples, audio.sample_rate, target_rate)
        samples = peak_normalize(samples)
        trimmed = trim_silence(samples, threshold=0.01, pad_samples=max(1, config.hop_length // 4))
        if trimmed:
            samples = trimmed
        return LoadedAudio(
            samples=samples,
            sample_rate=target_rate,
            source_channels=audio.source_channels,
            sample_width_bytes=audio.sample_width_bytes,
        )


def _analysis_confidence(
    reference: FeatureBundle,
    take: FeatureBundle,
    alignment: AlignmentPath,
    scoring: ScoringBundle,
) -> AnalysisConfidence:
    reasons: list[str] = []
    limitations = [
        "PracticeLens v0.1 uses deterministic signal-processing heuristics, not human musical judgment.",
        "Confidence is a sanity note for the current evidence quality, not a scientific accuracy guarantee.",
    ]
    risk_points = 0

    if alignment.coverage_ratio >= 0.85:
        reasons.append("Alignment coverage is broad enough for a stable reference-aware comparison.")
    else:
        reasons.append("Alignment coverage is limited, so some score conclusions may be weaker.")
        risk_points += 1

    reference_voicing = _voiced_ratio(reference)
    take_voicing = _voiced_ratio(take)
    if min(reference_voicing, take_voicing) >= 0.35:
        reasons.append("Voiced-frame coverage is sufficient for pitch-related feedback.")
    else:
        reasons.append("Voiced-frame coverage is low, so pitch-related feedback may be less reliable.")
        risk_points += 1

    if len(reference.onset_times_s) >= 2 and len(take.onset_times_s) >= 2:
        reasons.append("Onset evidence is present for rhythm-oriented feedback.")
    else:
        reasons.append("Onset evidence is sparse, so rhythm-oriented feedback may be less reliable.")
        risk_points += 1

    if scoring.sections:
        reasons.append("Section reports were produced, so local practice guidance has supporting spans.")
    else:
        reasons.append("No section reports were produced, so local practice guidance is limited.")
        risk_points += 1

    if risk_points == 0:
        level = "high"
    elif risk_points <= 2:
        level = "medium"
    else:
        level = "low"

    return AnalysisConfidence(level=level, reasons=tuple(reasons), limitations=tuple(limitations))


def _voiced_ratio(bundle: FeatureBundle) -> float:
    if not bundle.voiced_mask:
        return 0.0
    return sum(1 for voiced in bundle.voiced_mask if voiced) / float(len(bundle.voiced_mask))

from __future__ import annotations

from practicelens.alignment import align_feature_bundles
from practicelens.application.contracts import AnalyzeRequest, AnalyzeResult
from practicelens.application.pipeline import AnalysisPipeline
from practicelens.domain.models import AnalysisOverview, AnalysisReport, FeatureFlags
from practicelens.features import extract_feature_bundle
from practicelens.io import ensure_finite_audio, load_wav_audio
from practicelens.io.models import LoadedAudio
from practicelens.preprocessing import peak_normalize, resample_linear, trim_silence
from practicelens.reporting.artifacts import write_report_artifacts
from practicelens.scoring import score_aligned_features


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

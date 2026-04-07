from __future__ import annotations

from html import escape

from practicelens.domain.models import AnalysisReport


def report_to_svg(report: AnalysisReport) -> str:
    """Render a compact SVG summary of component and section scores."""

    width = 860
    height = 520
    bar_left = 250
    bar_width = 430
    bar_top = 134
    bar_height = 24
    bar_gap = 22

    overall_score = sum(score.score * score.weight for score in report.scores)
    take_name = escape(report.inputs.take_path.name)
    band_label = _score_band(overall_score)

    parts: list[str] = []
    parts.append(
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" '
        f'viewBox="0 0 {width} {height}">'
    )
    parts.append('<rect width="100%" height="100%" fill="#ffffff" />')
    parts.append(
        '<rect x="20" y="18" width="820" height="82" fill="#f8fafc" '
        'stroke="#dbe4ee" rx="14" />'
    )
    parts.append(
        '<text x="40" y="48" font-size="24" font-family="Arial" font-weight="700">'
        'PracticeLens Summary'
        '</text>'
    )
    parts.append(
        f'<text x="40" y="72" font-size="14" font-family="Arial" fill="#4b5563">'
        f'Take: {take_name}'
        '</text>'
    )
    parts.append(
        f'<text x="40" y="92" font-size="12" font-family="Arial" fill="#6b7280">'
        f'Performance band: {band_label}'
        '</text>'
    )
    parts.append(
        '<text x="708" y="58" font-size="14" font-family="Arial" fill="#6b7280">'
        'Overall score'
        '</text>'
    )
    parts.append(
        f'<text x="708" y="86" font-size="28" font-family="Arial" font-weight="700">'
        f'{overall_score:.1f}/100'
        '</text>'
    )

    parts.append(
        '<text x="40" y="122" font-size="16" font-family="Arial" font-weight="700">'
        'Component balance'
        '</text>'
    )
    for tick, x in ((0, bar_left), (50, bar_left + bar_width / 2), (100, bar_left + bar_width)):
        parts.append(
            f'<text x="{x:.1f}" y="122" font-size="11" font-family="Arial" fill="#94a3b8" '
            f'text-anchor="middle">{tick}</text>'
        )

    for index, score in enumerate(report.scores):
        y = bar_top + index * (bar_height + bar_gap)
        filled_width = max(0.0, min(bar_width, bar_width * score.score / 100.0))
        label = escape(_metric_label(score.name.value))
        weight_pct = int(round(score.weight * 100))
        parts.append(
            f'<text x="40" y="{y + 12}" font-size="14" font-family="Arial" font-weight="700">'
            f'{label}'
            '</text>'
        )
        parts.append(
            f'<text x="40" y="{y + 29}" font-size="12" font-family="Arial" fill="#6b7280">'
            f'Weight {weight_pct}%'
            '</text>'
        )
        parts.append(
            f'<rect x="{bar_left}" y="{y}" width="{bar_width}" height="{bar_height}" '
            'fill="#e5e7eb" rx="5" />'
        )
        parts.append(
            f'<rect x="{bar_left}" y="{y}" width="{filled_width:.1f}" height="{bar_height}" '
            'fill="#4f46e5" rx="5" />'
        )
        parts.append(
            f'<text x="{bar_left + bar_width + 18}" y="{y + 17}" font-size="13" '
            f'font-family="Arial">{score.score:.1f}</text>'
        )

    section_title_y = 316
    parts.append(
        f'<text x="40" y="{section_title_y}" font-size="16" font-family="Arial" font-weight="700">'
        'Section trend'
        '</text>'
    )
    if report.sections:
        chart_left = 40
        chart_top = 334
        chart_width = 760
        chart_height = 126
        parts.append(
            f'<rect x="{chart_left}" y="{chart_top}" width="{chart_width}" height="{chart_height}" '
            'fill="#f8fafc" stroke="#dbe4ee" rx="10" />'
        )
        for tick in (25, 50, 75, 100):
            y = chart_top + chart_height - (chart_height * tick / 100.0)
            parts.append(
                f'<line x1="{chart_left}" y1="{y:.1f}" x2="{chart_left + chart_width}" y2="{y:.1f}" '
                'stroke="#e5e7eb" stroke-dasharray="4 4" />'
            )
            parts.append(
                f'<text x="{chart_left + chart_width + 10}" y="{y + 4:.1f}" font-size="11" '
                f'font-family="Arial" fill="#94a3b8">{tick}</text>'
            )

        section_points = []
        denominator = max(1, len(report.sections) - 1)
        for index, section in enumerate(report.sections):
            section_avg = sum(score.score for score in section.component_scores) / max(
                1, len(section.component_scores)
            )
            x = chart_left + (chart_width * index / denominator)
            y = chart_top + chart_height - (chart_height * section_avg / 100.0)
            section_points.append((x, y, section.index, section_avg))
        path_d = " ".join(
            f'{"M" if index == 0 else "L"} {x:.1f} {y:.1f}'
            for index, (x, y, _, _) in enumerate(section_points)
        )
        parts.append(
            f'<path d="{path_d}" fill="none" stroke="#059669" stroke-width="3" />'
        )
        for x, y, section_index, section_avg in section_points:
            parts.append(
                f'<circle cx="{x:.1f}" cy="{y:.1f}" r="5" fill="#059669" stroke="#ffffff" stroke-width="2" />'
            )
            parts.append(
                f'<text x="{x:.1f}" y="{chart_top + chart_height + 22}" text-anchor="middle" '
                f'font-size="12" font-family="Arial">S{section_index}</text>'
            )
            parts.append(
                f'<text x="{x:.1f}" y="{y - 10:.1f}" text-anchor="middle" font-size="11" '
                f'font-family="Arial" fill="#065f46">{section_avg:.0f}</text>'
            )
    else:
        parts.append(
            '<text x="40" y="346" font-size="13" font-family="Arial" fill="#6b7280">'
            'No section summaries were generated for this report.'
            '</text>'
        )

    parts.append('</svg>')
    return ''.join(parts)


def _metric_label(raw_name: str) -> str:
    return raw_name.replace('_', ' ').title()


def _score_band(score: float) -> str:
    if score >= 90.0:
        return 'Excellent'
    if score >= 80.0:
        return 'Strong'
    if score >= 70.0:
        return 'Promising'
    return 'Needs Work'

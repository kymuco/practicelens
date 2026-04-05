from __future__ import annotations

from html import escape

from practicelens.domain.models import AnalysisReport


def report_to_svg(report: AnalysisReport) -> str:
    """Render a compact SVG summary of component and section scores."""

    width = 720
    height = 420
    bar_left = 170
    bar_width = 420
    top = 70
    bar_height = 24
    bar_gap = 18

    overall_score = sum(score.score * score.weight for score in report.scores)
    parts: list[str] = []
    parts.append(
        (
            f'<svg xmlns="http://www.w3.org/2000/svg" '
            f'width="{width}" height="{height}" '
            f'viewBox="0 0 {width} {height}">'
        )
    )
    parts.append('<rect width="100%" height="100%" fill="#ffffff" />')
    parts.append(
        '<text x="24" y="36" font-size="22" font-family="Arial">'
        'PracticeLens Summary'
        '</text>'
    )
    parts.append(
        f'<text x="24" y="58" font-size="14" font-family="Arial">'
        f'Overall score: {overall_score:.1f}/100'
        '</text>'
    )

    for index, score in enumerate(report.scores):
        y = top + index * (bar_height + bar_gap)
        filled_width = max(0.0, min(bar_width, bar_width * score.score / 100.0))
        parts.append(
            f'<text x="24" y="{y + 17}" font-size="13" font-family="Arial">'
            f'{escape(score.name.value)}'
            '</text>'
        )
        parts.append(
            f'<rect x="{bar_left}" y="{y}" width="{bar_width}" '
            f'height="{bar_height}" fill="#e5e7eb" rx="4" />'
        )
        parts.append(
            f'<rect x="{bar_left}" y="{y}" width="{filled_width:.1f}" '
            f'height="{bar_height}" fill="#4f46e5" rx="4" />'
        )
        parts.append(
            f'<text x="{bar_left + bar_width + 12}" y="{y + 17}" '
            f'font-size="13" font-family="Arial">{score.score:.1f}</text>'
        )

    section_base_y = 270
    parts.append(
        f'<text x="24" y="{section_base_y - 16}" font-size="16" '
        'font-family="Arial">Section averages</text>'
    )
    if report.sections:
        chart_left = 40
        chart_top = section_base_y
        chart_width = 620
        chart_height = 100
        parts.append(
            f'<rect x="{chart_left}" y="{chart_top}" width="{chart_width}" '
            f'height="{chart_height}" fill="#f9fafb" stroke="#d1d5db" />'
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
        parts.append(f'<path d="{path_d}" fill="none" stroke="#059669" stroke-width="2" />')
        for x, y, section_index, section_avg in section_points:
            parts.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="4" fill="#059669" />')
            parts.append(
                f'<text x="{x:.1f}" y="{chart_top + chart_height + 18}" '
                f'text-anchor="middle" font-size="12" font-family="Arial">'
                f'S{section_index}</text>'
            )
            parts.append(
                f'<text x="{x:.1f}" y="{y - 8:.1f}" text-anchor="middle" '
                f'font-size="11" font-family="Arial">{section_avg:.0f}</text>'
            )

    parts.append('</svg>')
    return ''.join(parts)

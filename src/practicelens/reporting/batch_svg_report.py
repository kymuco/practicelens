from __future__ import annotations

from html import escape

from practicelens.application.contracts import BatchCompareResult


def batch_compare_result_to_svg(result: BatchCompareResult) -> str:
    """Render a compact SVG summary for batch comparison results."""

    width = 920
    row_height = 52
    header_height = 96
    ranking_top = 148
    chart_height = max(180, len(result.entries) * row_height + 28)
    height = ranking_top + chart_height + 44
    best_score = result.entries[0].overall_score if result.entries else 0.0
    best_take = result.entries[0].take_path.name if result.entries else "-"

    parts: list[str] = []
    parts.append(
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" '
        f'viewBox="0 0 {width} {height}">'
    )
    parts.append('<rect width="100%" height="100%" fill="#ffffff" />')
    parts.append(
        '<rect x="20" y="18" width="880" height="92" fill="#f8fafc" '
        'stroke="#dbe4ee" rx="14" />'
    )
    parts.append(
        '<text x="40" y="48" font-size="24" font-family="Arial" font-weight="700">'
        'PracticeLens Batch Compare'
        '</text>'
    )
    parts.append(
        f'<text x="40" y="72" font-size="14" font-family="Arial" fill="#4b5563">'
        f'Reference: {escape(result.reference_path.name)}'
        '</text>'
    )
    parts.append(
        f'<text x="40" y="92" font-size="12" font-family="Arial" fill="#6b7280">'
        f'Compared takes: {len(result.entries)}'
        '</text>'
    )
    parts.append(
        '<text x="680" y="48" font-size="14" font-family="Arial" fill="#6b7280">'
        'Best take'
        '</text>'
    )
    parts.append(
        f'<text x="680" y="74" font-size="20" font-family="Arial" font-weight="700">'
        f'{escape(best_take)}'
        '</text>'
    )
    parts.append(
        f'<text x="680" y="96" font-size="12" font-family="Arial" fill="#6b7280">'
        f'Best score: {best_score:.1f}/100'
        '</text>'
    )

    parts.append(
        '<text x="40" y="136" font-size="16" font-family="Arial" font-weight="700">'
        'Take ranking'
        '</text>'
    )
    parts.append(
        '<text x="280" y="136" font-size="11" font-family="Arial" fill="#94a3b8">'
        'Score bars are shown against a 0–100 scale.'
        '</text>'
    )

    chart_left = 280
    chart_width = 500
    for tick, x in ((0, chart_left), (50, chart_left + chart_width / 2), (100, chart_left + chart_width)):
        parts.append(
            f'<text x="{x:.1f}" y="152" font-size="11" font-family="Arial" fill="#94a3b8" '
            f'text-anchor="middle">{tick}</text>'
        )

    for index, entry in enumerate(result.entries):
        y = ranking_top + index * row_height
        filled_width = max(0.0, min(chart_width, chart_width * entry.overall_score / 100.0))
        delta = best_score - entry.overall_score
        bar_fill = '#4f46e5' if entry.rank == 1 else '#93c5fd'
        parts.append(
            f'<text x="40" y="{y + 14}" font-size="14" font-family="Arial" font-weight="700">'
            f'#{entry.rank} {escape(entry.take_path.name)}'
            '</text>'
        )
        parts.append(
            f'<text x="40" y="{y + 32}" font-size="12" font-family="Arial" fill="#6b7280">'
            f'Delta vs best: {delta:.1f}'
            '</text>'
        )
        parts.append(
            f'<rect x="{chart_left}" y="{y}" width="{chart_width}" height="22" fill="#e5e7eb" rx="5" />'
        )
        parts.append(
            f'<rect x="{chart_left}" y="{y}" width="{filled_width:.1f}" height="22" fill="{bar_fill}" rx="5" />'
        )
        parts.append(
            f'<text x="{chart_left + chart_width + 18}" y="{y + 15}" font-size="13" '
            f'font-family="Arial">{entry.overall_score:.1f}</text>'
        )

    parts.append('</svg>')
    return ''.join(parts)

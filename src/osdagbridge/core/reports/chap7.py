from typing import Optional

from osdagbridge.core.reports.report_utils import _fig_embed
from osdagbridge.core.reports.styles import TABLE, build_longtable


def ch7_quantities(input_dict, fig_paths: Optional[dict] = None):
    fig_paths = fig_paths or {}
    pad = TABLE.row_pad_pt

    items = [
        ("1", "Structural Steel (IS 2062) for Girders", "steel_girders"),
        ("2(a)", "Cross Bracing - Top Chord", "bracing_top"),
        ("2(b)", "Cross Bracing - Bottom Chord", "bracing_bot"),
        ("2(c)", "Cross Bracing - Diagonal Chord", "bracing_diag"),
        ("3", "Concrete (M40) for Deck Slab", "concrete_deck"),
        ("4", "Reinforcement Steel (Fe 500)", "rebar_deck"),
        ("5", "Shear Stud Connectors", "shear_studs"),
        ("6", "Crash Barrier", "crash_barrier"),
    ]

    rows = []
    for sn, desc, pfx in items:
        vol_f = str(input_dict.get(f"{pfx}_vol_formula", "N.A."))
        qty = str(input_dict.get(f"{pfx}_qty", "N.A."))
        vol_t = str(input_dict.get(f"{pfx}_vol_total", "N.A."))
        wt_s = str(input_dict.get(f"{pfx}_wt_single", "N.A."))
        wt_t = str(input_dict.get(f"{pfx}_wt_total", "N.A."))
        rows.append(
            f"{sn} & {desc} & {vol_f} & {qty} & {vol_t} & {wt_s} & {wt_t} \\\\[{pad}pt]\n\\hline"
        )

    boq_table = build_longtable(
        col_spec="|C{1.0cm}|L{3.8cm}|C{2.8cm}|C{1.6cm}|C{1.8cm}|C{1.8cm}|C{1.8cm}|",
        caption="Bill of Materials (Steel, Concrete, and Reinforcement Quantities)",
        header_cells=[
            r"\textbf{S.N.}",
            r"\textbf{Item Description}",
            r"\textbf{Volume}",
            r"\textbf{Quantity}",
            r"\textbf{Total Volume}",
            r"\textbf{Weight (MT)}",
            r"\textbf{Total Weight (MT)}",
        ],
        body_tex="\n".join(rows),
        compact=True,
        note="Note: Volumes are in m\\textsuperscript{3} and weights are in Metric Tonnes (MT).",
    )

    mat_chart_block = _fig_embed(
        fig_paths.get("material_quantities"),
        "Material Take-off Summary: Structural Steel Tonnage (MT) by Component and Concrete Volume (m\\textsuperscript{3}) vs. Reinforcement Steel Weight (MT).",
        width=r"0.92\textwidth",
    )

    return (
        r"""
\chapter{Material Take-off \& Quantity Summary}
\label{ch:material-takeoff}

This section summarizes the estimated material quantities (structural steel tonnage, deck concrete volume, reinforcement steel weight, and shear connectors) for the designed superstructure.
"""
        + boq_table
        + "\n\\vspace{0.8em}\n"
        + mat_chart_block
    )
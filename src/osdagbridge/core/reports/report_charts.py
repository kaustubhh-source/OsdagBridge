"""
Programmatic Matplotlib Chart Generators for OsdagBridge Design Reports.
Generates high-DPI PNG assets for:
  - Section 5.5: Overall Utilization Ratio (UR = Demand / Capacity) Summary
  - Chapter 7:   Material Take-off & Quantity Summary (Steel Tonnage, Concrete vs. Rebar)
"""

import os
from typing import Dict, Optional

from matplotlib.backends.backend_agg import FigureCanvasAgg
from matplotlib.figure import Figure

from osdagbridge.core.reports.styles import COLORS
from osdagbridge.core.utils.common import (
    KEY_MP_ED_TYPE,
    KEY_UTIL_FLEXURE,
    KEY_UTIL_INTERACTION,
    KEY_UTIL_LTB,
    KEY_UTIL_SHEAR,
)


def _safe_float(val) -> Optional[float]:
    if val is None:
        return None
    s = str(val).strip()
    if not s or s.upper() in {"N.A.", "N/A", "NONE", "---", "-"}:
        return None
    try:
        return float(s)
    except (TypeError, ValueError):
        return None


def _max_member_ur(pair_designs: dict) -> Optional[float]:
    """Extract maximum Utilization Ratio across cross-bracing or end-diaphragm results."""
    if not isinstance(pair_designs, dict) or not pair_designs:
        return None
    try:
        from osdagbridge.core.bridge_types.plate_girder.results_data import _extract_osdag_summary
    except Exception:
        return None

    best = None
    for members in pair_designs.values():
        if not isinstance(members, dict):
            continue
        for force_types in members.values():
            if not isinstance(force_types, dict):
                continue
            for raw in force_types.values():
                eff = _safe_float(_extract_osdag_summary(raw or {}).get("efficiency"))
                if eff is not None and (best is None or eff > best):
                    best = eff
    return best


def extract_component_urs(input_dict: dict, output_dict: dict) -> Dict[str, Optional[float]]:
    """
    Collect governing Utilization Ratios (UR = Demand / Capacity) for the four
    primary structural elements:
      1. Steel Plate Girders
      2. Concrete Deck Slab
      3. Cross Bracing
      4. End Diaphragms
    """
    out = output_dict or {}
    inp = input_dict or {}
    design_results = out.get("design_results", {}) or {}
    per_girder = design_results.get("per_girder", {}) or {}

    # 1. Steel Plate Girders
    girder_ur = None
    for g_id, g_data in per_girder.items():
        if str(g_id).startswith("EB"):
            continue
        for chk in (g_data.get("checks") or []):
            dcr = _safe_float(chk.get("dcr"))
            if dcr is not None and (girder_ur is None or dcr > girder_ur):
                girder_ur = dcr

    if girder_ur is None:
        for k in (KEY_UTIL_FLEXURE, KEY_UTIL_SHEAR, KEY_UTIL_INTERACTION, KEY_UTIL_LTB):
            pct = _safe_float(out.get(k))
            if pct is not None:
                ratio = pct / 100.0
                if girder_ur is None or ratio > girder_ur:
                    girder_ur = ratio

    # 2. Concrete Deck Slab
    deck_ur = None
    deck_res = out.get("deck_design_results", {}) or {}
    for k, v in deck_res.items():
        if str(k).startswith("ur_"):
            val = _safe_float(v)
            if val is not None and (deck_ur is None or val > deck_ur):
                deck_ur = val

    if deck_ur is None:
        deck_rpt = out.get("deck_report_values", {}) or {}
        if deck_rpt:
            from osdagbridge.core.utils.common import (
                KEY_DD_MU_BOT,
                KEY_DD_MU_TOP,
                KEY_DD_M_ULS_HOG,
                KEY_DD_M_ULS_SAG,
                KEY_DD_PUNCH_VED,
                KEY_DD_SHEAR_VED,
                KEY_DD_SHEAR_VRDC,
                KEY_DD_VRD_C_MPA,
            )
            pairs = [
                (KEY_DD_M_ULS_SAG, KEY_DD_MU_BOT),
                (KEY_DD_M_ULS_HOG, KEY_DD_MU_TOP),
                (KEY_DD_PUNCH_VED, KEY_DD_VRD_C_MPA),
                (KEY_DD_SHEAR_VED, KEY_DD_SHEAR_VRDC),
            ]
            for dem_k, cap_k in pairs:
                dem = _safe_float(deck_rpt.get(dem_k))
                cap = _safe_float(deck_rpt.get(cap_k))
                if dem is not None and cap is not None and cap > 0:
                    r = dem / cap
                    if deck_ur is None or r > deck_ur:
                        deck_ur = r

    # 3. Cross Bracing
    cb_ur = _max_member_ur(out.get("crossbracing_design_results", {}) or {})

    # 4. End Diaphragms
    ed_ur = _max_member_ur(out.get("end_diaphragm_design_results", {}) or {})
    if ed_ur is None:
        ed_type = ""
        for k, v in inp.items():
            if str(k).startswith(KEY_MP_ED_TYPE) and v:
                ed_type = str(v).strip().lower()
                break
        if "brac" in ed_type and cb_ur is not None:
            ed_ur = cb_ur

    return {
        "Steel Plate\nGirders": girder_ur,
        "Concrete\nDeck Slab": deck_ur,
        "Cross\nBracing": cb_ur,
        "End\nDiaphragms": ed_ur,
    }


def generate_ur_summary_chart(input_dict: dict, output_dict: dict, save_path: str) -> Optional[str]:
    """
    Generate Utilization Ratio (UR = Demand / Capacity) bar chart for Section 5.5
    with a distinct red dashed threshold line at UR = 1.0.
    """
    ur_map = extract_component_urs(input_dict, output_dict)
    labels = list(ur_map.keys())
    raw_vals = list(ur_map.values())

    plot_vals = [v if v is not None else 0.0 for v in raw_vals]
    bar_colors = []
    for v in raw_vals:
        if v is None:
            bar_colors.append("#CBD5E1")
        elif v > 1.0:
            bar_colors.append(f"#{COLORS.fail_red_hex}")
        elif v >= 0.90:
            bar_colors.append(f"#{COLORS.warn_amber_hex}")
        else:
            bar_colors.append(f"#{COLORS.primary_hex}")

    fig = Figure(figsize=(7.6, 4.0), dpi=300)
    FigureCanvasAgg(fig)
    ax = fig.add_subplot(111)

    bars = ax.bar(labels, plot_vals, width=0.48, color=bar_colors, edgecolor="#374151", linewidth=0.8, zorder=3)

    # Red dashed threshold line at UR = 1.0
    ax.axhline(
        1.0,
        color=f"#{COLORS.fail_red_hex}",
        linestyle="--",
        linewidth=1.6,
        zorder=4,
        label="Limit Threshold (UR = 1.0)",
    )

    y_max = max([1.25] + [v * 1.22 for v in plot_vals])
    ax.set_ylim(0, y_max)
    ax.set_ylabel("Utilization Ratio (UR = Demand / Capacity)", fontsize=10, fontweight="bold", color="#1F2937")
    ax.set_title("Overall Component Utilization Ratio Summary", fontsize=11.5, fontweight="bold", pad=12, color="#111827")
    ax.grid(axis="y", linestyle=":", alpha=0.6, zorder=0)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)

    # Annotate bar values above each bar
    for bar, raw in zip(bars, raw_vals):
        h = bar.get_height()
        if raw is None:
            txt = "N/A"
        else:
            status = "PASS" if raw <= 1.0 else "FAIL"
            txt = f"{raw:.2f}\n({status})"
        ax.annotate(
            txt,
            xy=(bar.get_x() + bar.get_width() / 2.0, h),
            xytext=(0, 4),
            textcoords="offset points",
            ha="center",
            va="bottom",
            fontsize=8.5,
            fontweight="bold",
            color="#1F2937",
        )

    ax.legend(loc="upper right", frameon=True, fontsize=9)
    fig.tight_layout()
    fig.savefig(save_path, dpi=300)
    return save_path


def generate_material_quantity_charts(quantities: dict, save_path: str) -> Optional[str]:
    """
    Generate two-panel Chapter 7 Material Take-off visualization:
      - Left panel:  Structural Steel Tonnage (Girders, Cross Bracing, End Diaphragms) in MT
      - Right panel: Concrete Volume (m^3) vs. Reinforcement Steel Weight (MT)
    """
    q = quantities or {}

    girder_mt = _safe_float(q.get("steel_girders_wt_total")) or 0.0
    cb_top = _safe_float(q.get("bracing_top_wt_total")) or 0.0
    cb_bot = _safe_float(q.get("bracing_bot_wt_total")) or 0.0
    cb_diag = _safe_float(q.get("bracing_diag_wt_total")) or 0.0
    cb_total_mt = cb_top + cb_bot + cb_diag
    ed_total_mt = _safe_float(q.get("end_diaphragm_wt_total")) or 0.0

    conc_m3 = _safe_float(q.get("concrete_deck_vol_total")) or 0.0
    rebar_mt = _safe_float(q.get("rebar_deck_wt_total")) or 0.0

    fig = Figure(figsize=(8.4, 3.9), dpi=300)
    FigureCanvasAgg(fig)

    # --- Panel 1: Structural Steel Tonnage (MT) ---
    ax1 = fig.add_subplot(121)
    steel_labels = ["Plate\nGirders", "Cross\nBracing", "End\nDiaphragms"]
    steel_vals = [girder_mt, cb_total_mt, ed_total_mt]
    steel_colors = [f"#{COLORS.primary_hex}", f"#{COLORS.primary_dark_hex}", "#64748B"]

    bars1 = ax1.bar(steel_labels, steel_vals, width=0.48, color=steel_colors, edgecolor="#374151", linewidth=0.8, zorder=3)
    ax1.set_ylabel("Weight (Metric Tonnes, MT)", fontsize=9.5, fontweight="bold", color="#1F2937")
    ax1.set_title("Structural Steel Tonnage", fontsize=10.5, fontweight="bold", pad=10, color="#111827")
    ax1.set_ylim(0, max([1.0] + [v * 1.25 for v in steel_vals]))
    ax1.grid(axis="y", linestyle=":", alpha=0.6, zorder=0)
    ax1.spines["top"].set_visible(False)
    ax1.spines["right"].set_visible(False)

    for bar, val in zip(bars1, steel_vals):
        lbl = f"{val:.2f} MT" if val > 0 else "0.00 MT"
        ax1.annotate(
            lbl,
            xy=(bar.get_x() + bar.get_width() / 2.0, bar.get_height()),
            xytext=(0, 4),
            textcoords="offset points",
            ha="center",
            va="bottom",
            fontsize=8.2,
            fontweight="bold",
            color="#1F2937",
        )

    # --- Panel 2: Concrete Volume (m^3) vs. Reinforcement Steel Weight (MT) ---
    ax2 = fig.add_subplot(122)
    ax2_twin = ax2.twinx()

    b_conc = ax2.bar([0], [conc_m3], width=0.38, color="#3B82F6", edgecolor="#1E3A8A", linewidth=0.8, zorder=3, label="Concrete (m³)")
    b_rebar = ax2_twin.bar([1], [rebar_mt], width=0.38, color="#F59E0B", edgecolor="#78350F", linewidth=0.8, zorder=3, label="Rebar Steel (MT)")

    ax2.set_xticks([0, 1])
    ax2.set_xticklabels(["Deck Concrete\nVolume (m³)", "Reinforcement\nSteel (MT)"], fontsize=9)
    ax2.set_ylabel("Concrete Volume (m³)", fontsize=9.5, fontweight="bold", color="#1D4ED8")
    ax2_twin.set_ylabel("Reinforcement Weight (MT)", fontsize=9.5, fontweight="bold", color="#B45309")
    ax2.set_title("Concrete Volume vs. Rebar Weight", fontsize=10.5, fontweight="bold", pad=10, color="#111827")

    ax2.set_ylim(0, max(1.0, conc_m3 * 1.25))
    ax2_twin.set_ylim(0, max(1.0, rebar_mt * 1.25))
    ax2.grid(axis="y", linestyle=":", alpha=0.6, zorder=0)
    ax2.spines["top"].set_visible(False)
    ax2_twin.spines["top"].set_visible(False)

    ax2.annotate(
        f"{conc_m3:.2f} m³",
        xy=(b_conc[0].get_x() + b_conc[0].get_width() / 2.0, conc_m3),
        xytext=(0, 4),
        textcoords="offset points",
        ha="center",
        va="bottom",
        fontsize=8.5,
        fontweight="bold",
        color="#1D4ED8",
    )
    ax2_twin.annotate(
        f"{rebar_mt:.2f} MT",
        xy=(b_rebar[0].get_x() + b_rebar[0].get_width() / 2.0, rebar_mt),
        xytext=(0, 4),
        textcoords="offset points",
        ha="center",
        va="bottom",
        fontsize=8.5,
        fontweight="bold",
        color="#B45309",
    )

    fig.tight_layout()
    fig.savefig(save_path, dpi=300)
    return save_path
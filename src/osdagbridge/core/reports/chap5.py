# =============================================================================
# Chapter 5: Design Checks
# Refactored to use centralized styles.py (repeating headers + clean page breaks)
# and Section 5.5 Utilization Ratio visualization.
# =============================================================================
from __future__ import annotations
from typing import TYPE_CHECKING, Optional

from osdagbridge.core.utils.common import (
    KEY_DD_AS_BOT,
    KEY_DD_AS_LONG,
    KEY_DD_AS_MIN,
    KEY_DD_AS_REQ_BOT,
    KEY_DD_AS_REQ_TOP,
    KEY_DD_AS_TOP,
    KEY_DD_COVER_OK,
    KEY_DD_DIA_BOT,
    KEY_DD_D_BOT,
    KEY_DD_FY,
    KEY_DD_GAMMA_DL,
    KEY_DD_GAMMA_LL,
    KEY_DD_HAS_OVERHANG,
    KEY_DD_IMPACT_FACTOR,
    KEY_DD_MIN_COVER,
    KEY_DD_MU_BOT,
    KEY_DD_MU_OH,
    KEY_DD_MU_TOP,
    KEY_DD_M_BARRIER,
    KEY_DD_M_DL,
    KEY_DD_M_DL_OH,
    KEY_DD_M_LL,
    KEY_DD_M_LL_OH,
    KEY_DD_M_ULS_HOG,
    KEY_DD_M_ULS_OH,
    KEY_DD_M_ULS_SAG,
    KEY_DD_PUNCH_C1,
    KEY_DD_PUNCH_C2,
    KEY_DD_PUNCH_OK,
    KEY_DD_PUNCH_U1,
    KEY_DD_PUNCH_VED,
    KEY_DD_PUNCH_VED_KN,
    KEY_DD_SHEAR_OK,
    KEY_DD_SHEAR_VED,
    KEY_DD_SHEAR_VRDC,
    KEY_DD_SPACING_MAX,
    KEY_DD_SPAN,
    KEY_DD_SPC_BOT,
    KEY_DD_TYRE_LENGTH,
    KEY_DD_TYRE_WIDTH,
    KEY_DD_VEHICLE,
    KEY_DD_VRD_C_MPA,
    KEY_DD_WDL,
    KEY_DD_WHEEL_LOAD,
    KEY_DD_WK_BOT,
    KEY_DD_WK_LIMIT,
    KEY_DD_WK_OH,
    KEY_DD_WK_TOP,
    KEY_DECK_CONCRETE_GRADE_BASIC,
    KEY_DESIGN_MODE,
    KEY_DS_BOTTOM_CLEAR_COVER,
    KEY_DS_REINF_MATERIAL,
    KEY_DS_STUD_DIAMETER,
    KEY_DS_TOP_CLEAR_COVER,
    KEY_MATERIAL_DECK_FCK,
    KEY_MATERIAL_DECK_FCTM,
    KEY_MP_ED_TYPE,
    KEY_SD_BOTTOM_FLANGE_THICKNESS,
    KEY_SD_BOTTOM_FLANGE_WIDTH,
    KEY_SD_BS_FCD,
    KEY_SD_BS_FCDW_LC,
    KEY_SD_BS_FCDW_WB,
    KEY_SD_BS_FPSD,
    KEY_SD_BS_R,
    KEY_SD_CLASS_FLANGE,
    KEY_SD_CLASS_WEB,
    KEY_SD_COMPOSITE_IZ,
    KEY_SD_DEFL_LIVE,
    KEY_SD_DEFL_TOTAL,
    KEY_SD_EFFECTIVE_SLAB_WIDTH,
    KEY_SD_FLANGE_CLASS_LIMIT,
    KEY_SD_FLANGE_SLENDERNESS,
    KEY_SD_HIGH_SHEAR,
    KEY_SD_IS_FQ,
    KEY_SD_IS_FQD,
    KEY_SD_IS_IYS_MIN,
    KEY_SD_IS_IYS_PROV,
    KEY_SD_LTB_CHI,
    KEY_SD_LTB_LAMBDA,
    KEY_SD_LTB_MB,
    KEY_SD_LTB_MCR,
    KEY_SD_MDV,
    KEY_SD_MD_CAPACITY,
    KEY_SD_MN_AXIAL,
    KEY_SD_MN_MOMENT,
    KEY_SD_MN_RATIO,
    KEY_SD_MU_APPLIED,
    KEY_SD_PANEL_CD,
    KEY_SD_PNA_DEPTH,
    KEY_SD_SC_D_LIMIT,
    KEY_SD_SC_EDGE_DIST,
    KEY_SD_SC_Qr_kN,
    KEY_SD_SC_Qu_kN,
    KEY_SD_SC_REQ_EDGE_DIST,
    KEY_SD_SC_SL1,
    KEY_SD_SC_SL2,
    KEY_SD_SC_SR,
    KEY_SD_SECTION_CLASS,
    KEY_SD_SECTION_PROP_AREA,
    KEY_SD_SECTION_PROP_IZ,
    KEY_SD_SECTION_PROP_ZUZ,
    KEY_SD_SECTION_PROP_ZZ,
    KEY_SD_SHEAR_AV,
    KEY_SD_SHEAR_KV,
    KEY_SD_SHEAR_LAMBDA_W,
    KEY_SD_SHEAR_TAU_B,
    KEY_SD_SHEAR_VCR,
    KEY_SD_SHEAR_VU,
    KEY_SD_STIFF_END_COUNT,
    KEY_SD_STIFF_END_THICK,
    KEY_SD_STIFF_INT_SPACING,
    KEY_SD_STIFF_INT_THICK,
    KEY_SD_STIFF_LONG,
    KEY_SD_STIFF_METHOD,
    KEY_SD_STRESS_STEEL,
    KEY_SD_STRESS_STEEL_ALLOWABLE,
    KEY_SD_TOP_FLANGE_THICKNESS,
    KEY_SD_TOP_FLANGE_WIDTH,
    KEY_SD_TOTAL_DEPTH,
    KEY_SD_TS_VL,
    KEY_SD_TS_VRD,
    KEY_SD_ULS_PER_GIRDER,
    KEY_SD_WEB_CLASS_LIMIT,
    KEY_SD_WEB_SLENDERNESS,
    KEY_SD_WEB_THICKNESS,
    KEY_SPAN,
    KEY_TS_DECK_OVERHANG,
    KEY_TS_DECK_THICKNESS,
    KEY_TS_NO_OF_GIRDERS,
    KEY_UTIL_FLEXURE,
    KEY_UTIL_INTERACTION,
    KEY_UTIL_LTB,
    KEY_UTIL_SHEAR,
)

from osdagbridge.core.reports.report_utils import _tex, _render_value, get_girder_entries, _fig_embed
from osdagbridge.core.reports.styles import TABLE, build_longtable

if TYPE_CHECKING:
    pass


def ch5_design_checks(checks_data, bridge, fig_paths: Optional[dict] = None) -> str:
    """Chapter 5 — Design Checks."""
    fig_paths = fig_paths or {}
    pad = TABLE.row_pad_pt

    girder_entries = get_girder_entries(bridge.input_dict)
    if not girder_entries:
        n = int(bridge.input_dict.get(KEY_TS_NO_OF_GIRDERS, 1))
        girder_entries = [(f"Girder {i}", "M1") for i in range(1, n + 1)]

    deck_rpt = bridge.output_dict.get("deck_report_values", {}) or {}

    # Table 5.1 rows (keep each girder multirow block unsplit via \\*)
    t51_rows = []
    for lbl, _ in girder_entries:
        t51_rows.append(
            r"\multirow{13}{*}{\makecell{" + _tex(lbl) + r"}} & \textnormal{Depth, D (mm)} & " + _render_value(bridge.output_dict, KEY_SD_TOTAL_DEPTH) + rf" \\*[{pad}pt]\cline{{2-3}}" + "\n"
            r" & \textnormal{Top Flange Width, $b_f$ (mm)} & " + _render_value(bridge.output_dict, KEY_SD_TOP_FLANGE_WIDTH) + rf" \\*[{pad}pt]\cline{{2-3}}" + "\n"
            r" & \textnormal{Bottom Flange Width, $b_f$ (mm)} & " + _render_value(bridge.output_dict, KEY_SD_BOTTOM_FLANGE_WIDTH) + rf" \\*[{pad}pt]\cline{{2-3}}" + "\n"
            r" & \textnormal{Top Flange Thickness, $t_f$ (mm)} & " + _render_value(bridge.output_dict, KEY_SD_TOP_FLANGE_THICKNESS) + rf" \\*[{pad}pt]\cline{{2-3}}" + "\n"
            r" & \textnormal{Bottom Flange Thickness, $t_f$ (mm)} & " + _render_value(bridge.output_dict, KEY_SD_BOTTOM_FLANGE_THICKNESS) + rf" \\*[{pad}pt]\cline{{2-3}}" + "\n"
            r" & \textnormal{Web Thickness, $t_w$ (mm)} & " + _render_value(bridge.output_dict, KEY_SD_WEB_THICKNESS) + rf" \\*[{pad}pt]\cline{{2-3}}" + "\n"
            r" & \textnormal{Gross Area, A (cm$^2$)} & " + _render_value(bridge.output_dict, KEY_SD_SECTION_PROP_AREA) + rf" \\*[{pad}pt]\cline{{2-3}}" + "\n"
            r" & \textnormal{Moment of Inertia, $I_z$ (cm$^4$)} & " + _render_value(bridge.output_dict, KEY_SD_SECTION_PROP_IZ) + rf" \\*[{pad}pt]\cline{{2-3}}" + "\n"
            r" & \textnormal{Elastic Section Modulus, $Z_{ez}$ (cm$^3$)} & " + _render_value(bridge.output_dict, KEY_SD_SECTION_PROP_ZZ) + rf" \\*[{pad}pt]\cline{{2-3}}" + "\n"
            r" & \textnormal{Plastic Section Modulus, $Z_{pz}$ (cm$^3$)} & " + _render_value(bridge.output_dict, KEY_SD_SECTION_PROP_ZUZ) + rf" \\*[{pad}pt]\cline{{2-3}}" + "\n"
            r" & \textnormal{Effective Slab Width, $b_{eff}$ (mm)} & " + _render_value(bridge.output_dict, KEY_SD_EFFECTIVE_SLAB_WIDTH) + rf" \\*[{pad}pt]\cline{{2-3}}" + "\n"
            r" & \textnormal{Transformed Composite $I_z$ (cm$^4$)} & " + _render_value(bridge.output_dict, KEY_SD_COMPOSITE_IZ) + rf" \\*[{pad}pt]\cline{{2-3}}" + "\n"
            r" & \textnormal{Depth to Plastic Neutral Axis (mm)} & " + _render_value(bridge.output_dict, KEY_SD_PNA_DEPTH) + rf" \\[{pad}pt]\hline"
        )
    t51_table = build_longtable(
        col_spec="|C{2.4cm}|L{7.8cm}|>{\\centering\\arraybackslash}p{4.6cm}|",
        caption="Girder Section Properties (Final Optimized / User-selected)",
        header_cells=[r"\textbf{Girder}", r"\textbf{Property}", r"\textbf{Value}"],
        body_tex="\n".join(t51_rows),
    )

    # Table 5.2 rows
    t52_rows = []
    for lbl, _ in girder_entries:
        t52_rows.append(
            r"\multirow{3}{*}{\makecell{" + _tex(lbl) + r"}} & Top Flange & " + _render_value(bridge.output_dict, KEY_SD_FLANGE_SLENDERNESS) + " & " + _render_value(bridge.output_dict, KEY_SD_FLANGE_CLASS_LIMIT) + " & " + _render_value(bridge.output_dict, KEY_SD_CLASS_FLANGE) + rf" \\*[{pad}pt]\cline{{2-5}}" + "\n"
            r" & Web & " + _render_value(bridge.output_dict, KEY_SD_WEB_SLENDERNESS) + " & " + _render_value(bridge.output_dict, KEY_SD_WEB_CLASS_LIMIT) + " & " + _render_value(bridge.output_dict, KEY_SD_CLASS_WEB) + rf" \\*[{pad}pt]\cline{{2-5}}" + "\n"
            r" & Overall Section & --- & --- & " + _render_value(bridge.output_dict, KEY_SD_SECTION_CLASS) + rf" \\[{pad}pt]\hline"
        )
    t52_table = build_longtable(
        col_spec="|C{2.2cm}|L{3.0cm}|C{3.3cm}|C{2.5cm}|>{\\centering\\arraybackslash}p{3.8cm}|",
        caption="Girder Section Classification",
        header_cells=[r"\textbf{Girder}", r"\textbf{Element}", r"\textbf{Slenderness Ratio}", r"\textbf{Class Limit}", r"\textbf{Classification}"],
        body_tex="\n".join(t52_rows),
        note="Note: IS 800:2007 Table 2",
    )

    # Table 5.3 rows (Moment Capacity)
    try:
        _flex_ur = float(bridge.output_dict.get(KEY_UTIL_FLEXURE)) / 100.0
        _flex_ur_str = f"{_flex_ur:.2f}"
        _flex_status = "PASS" if _flex_ur <= 1.0 else r"\textcolor{red}{FAIL}"
    except (TypeError, ValueError):
        _flex_ur_str = ""
        _flex_status = "---"
    t53_rows = []
    for lbl, _ in girder_entries:
        t53_rows.append(
            r"\multirow{3}{*}{\makecell{" + _tex(lbl) + r"}} & Applied Moment, $M_u$ & Governing LC (ULS) & " + _render_value(bridge.output_dict, KEY_SD_MU_APPLIED, " kN-m") + rf" & --- \\*[{pad}pt]\cline{{2-5}}" + "\n"
            r" & Design Moment Capacity, $M_d$ & IRC 22 Cl. 603.3.1 & " + _render_value(bridge.output_dict, KEY_SD_MD_CAPACITY, " kN-m") + rf" & --- \\*[{pad}pt]\cline{{2-5}}" + "\n"
            r" & Utilization Ratio, $M_u / M_d$ & $M_u / M_d$ & " + _flex_ur_str + " & " + _flex_status + rf" \\[{pad}pt]\hline"
        )
    t53_table = build_longtable(
        col_spec="|C{2.2cm}|C{3.4cm}|C{3.3cm}|>{\\centering\\arraybackslash}p{4.0cm}|C{1.8cm}|",
        caption="Moment Capacity Check",
        header_cells=[r"\textbf{Girder}", r"\textbf{Parameter}", r"\textbf{Formula}", r"\textbf{Value}", r"\textbf{Status}"],
        body_tex="\n".join(t53_rows),
        note="Note: IRC 22 Cl. 603.3.1, IS 800 Cl. 8.2.1",
    )

    # Table 5.4 rows (Shear Capacity)
    try:
        _shear_ur = float(bridge.output_dict.get(KEY_UTIL_SHEAR)) / 100.0
        _shear_ur_str = f"{_shear_ur:.2f}"
        _shear_status = "PASS" if _shear_ur <= 1.0 else r"\textcolor{red}{FAIL}"
    except (TypeError, ValueError):
        _shear_ur_str = ""
        _shear_status = "---"
    t54_rows = []
    for lbl, _ in girder_entries:
        t54_rows.append(
            r"\multirow{8}{*}{\makecell{" + _tex(lbl) + r"}} & Applied Shear, $V_u$ & Governing LC (ULS) & " + _render_value(bridge.output_dict, KEY_SD_SHEAR_VU, " kN") + rf" & --- \\*[{pad}pt]\cline{{2-5}}" + "\n"
            r" & Shear Area, $A_v$ & $d_w \times t_w$ & " + _render_value(bridge.output_dict, KEY_SD_SHEAR_AV, " mm$^2$") + rf" & --- \\*[{pad}pt]\cline{{2-5}}" + "\n"
            r" & Panel Aspect Ratio, c/d & --- & " + _render_value(bridge.output_dict, KEY_SD_PANEL_CD) + rf" & --- \\*[{pad}pt]\cline{{2-5}}" + "\n"
            r" & Shear Buckling Coefficient, $k_v$ & IS 800 Cl. 8.4.2.2 & " + _render_value(bridge.output_dict, KEY_SD_SHEAR_KV) + rf" & --- \\*[{pad}pt]\cline{{2-5}}" + "\n"
            r" & Web Slenderness, $\lambda_w$ & $\sqrt{f_{yw}/(\sqrt{3}\,\tau_{cr})}$ & " + _render_value(bridge.output_dict, KEY_SD_SHEAR_LAMBDA_W) + rf" & --- \\*[{pad}pt]\cline{{2-5}}" + "\n"
            r" & Design Shear Stress, $\tau_b$ & IRC 22 Cl. 603.3.3.2 & " + _render_value(bridge.output_dict, KEY_SD_SHEAR_TAU_B, " MPa") + rf" & --- \\*[{pad}pt]\cline{{2-5}}" + "\n"
            r" & Shear Buckling Resistance, $V_{cr}$ & $A_v \times \tau_b$ & " + _render_value(bridge.output_dict, KEY_SD_SHEAR_VCR, " kN") + rf" & --- \\*[{pad}pt]\cline{{2-5}}" + "\n"
            r" & Utilization Ratio, $V_u / V_d$ & $V_u / V_d$ & " + _shear_ur_str + " & " + _shear_status + rf" \\[{pad}pt]\hline"
        )
    t54_table = build_longtable(
        col_spec="|C{2.2cm}|C{3.4cm}|C{3.3cm}|>{\\centering\\arraybackslash}p{4.0cm}|C{1.8cm}|",
        caption="Shear Capacity Check",
        header_cells=[r"\textbf{Girder}", r"\textbf{Parameter}", r"\textbf{Formula}", r"\textbf{Value}", r"\textbf{Status}"],
        body_tex="\n".join(t54_rows),
        note="Note: IS 800 Cl. 8.4, IRC 22 Cl. 603.3.3.2",
    )

    # Table 5.5 rows (Interaction Checks)
    def _interaction_status(ratio):
        if ratio < 0.90:
            return "PASS"
        elif ratio < 1.00:
            return "WARN"
        return r"\textcolor{red}{FAIL}"

    try:
        _mv_ur = float(bridge.output_dict.get(KEY_UTIL_INTERACTION)) / 100.0
        _mv_ur_str = f"{_mv_ur:.2f}"
        _mv_status = _interaction_status(_mv_ur)
    except (TypeError, ValueError):
        _mv_ur_str = ""
        _mv_status = "---"

    _mn_r = bridge.output_dict.get(KEY_SD_MN_RATIO)
    _mn_ax = bridge.output_dict.get(KEY_SD_MN_AXIAL)
    _mn_mo = bridge.output_dict.get(KEY_SD_MN_MOMENT)
    if _mn_r is None or _mn_ax is None or _mn_mo is None:
        _mn_cond = _mn_val = _mn_status = "N/A"
    else:
        _mn_cond = f"{_mn_ax:.2f} + {_mn_mo:.2f} = {_mn_r:.3f}"
        _mn_val = f"{_mn_r:.3f}"
        _mn_status = _interaction_status(_mn_r)

    t55_rows = []
    for lbl, _ in girder_entries:
        t55_rows.append(
            r"\multirow{4}{*}{\makecell{" + _tex(lbl) + r"}} & High Shear Condition? & $V_u > 0.6\,V_d$ & " + _render_value(bridge.output_dict, KEY_SD_HIGH_SHEAR) + rf" & --- \\*[{pad}pt]\cline{{2-5}}" + "\n"
            r" & Reduced Moment Capacity, $M_{dv}$ & IRC 22 Cl. 603.3.3.3 & " + _render_value(bridge.output_dict, KEY_SD_MDV, " kN-m") + rf" & --- \\*[{pad}pt]\cline{{2-5}}" + "\n"
            r" & Interaction Check: $M_u \leq M_{dv}$ & --- & " + _mv_ur_str + " & " + _mv_status + rf" \\*[{pad}pt]\cline{{2-5}}" + "\n"
            r" & Interaction Check: $N_u/N_{Rd} + M_u/M_{dv} \leq 1.0$ & " + _mn_cond + " & " + _mn_val + " & " + _mn_status + rf" \\[{pad}pt]\hline"
        )
    t55_table = build_longtable(
        col_spec="|C{2.2cm}|C{3.4cm}|C{3.3cm}|>{\\centering\\arraybackslash}p{4.0cm}|C{1.8cm}|",
        caption="Interaction Checks (M-V and M-N)",
        header_cells=[r"\textbf{Girder}", r"\textbf{Check}", r"\textbf{Condition}", r"\textbf{Value}", r"\textbf{Status}"],
        body_tex="\n".join(t55_rows),
        note="Note: IRC 22 Cl. 603.3.3.3",
    )

    # Table 5.6 rows (LTB Check)
    try:
        _ltb_ur = float(bridge.output_dict.get(KEY_UTIL_LTB)) / 100.0
        _ltb_ur_str = f"{_ltb_ur:.2f}"
        _ltb_status = _interaction_status(_ltb_ur)
    except (TypeError, ValueError):
        _ltb_ur_str = ""
        _ltb_status = "---"

    t56_rows = []
    for lbl, _ in girder_entries:
        t56_rows.append(
            r"\multirow{5}{*}{\makecell{" + _tex(lbl) + r"}} & Elastic Critical Moment, $M_{cr}$ & IRC 22 Cl. 603.3.3.1 & " + _render_value(bridge.output_dict, KEY_SD_LTB_MCR, " kN-m") + rf" & --- \\*[{pad}pt]\cline{{2-5}}" + "\n"
            r" & Non-dim. Slenderness, $\bar{\lambda}_{LT}$ & $\sqrt{M_p / M_{cr}}$ & " + _render_value(bridge.output_dict, KEY_SD_LTB_LAMBDA) + rf" & --- \\*[{pad}pt]\cline{{2-5}}" + "\n"
            r" & LTB Reduction Factor, $\chi_{LT}$ & IS 800 Cl. 8.2.2 & " + _render_value(bridge.output_dict, KEY_SD_LTB_CHI) + rf" & --- \\*[{pad}pt]\cline{{2-5}}" + "\n"
            r" & LTB Resistance, $M_b$ & $\chi_{LT}\,M_p / \gamma_{m0}$ & " + _render_value(bridge.output_dict, KEY_SD_LTB_MB, " kN-m") + rf" & --- \\*[{pad}pt]\cline{{2-5}}" + "\n"
            r" & $M_u \leq M_b$ & $M_u / M_b$ & " + _ltb_ur_str + " & " + _ltb_status + rf" \\[{pad}pt]\hline"
        )
    t56_table = build_longtable(
        col_spec="|C{2.2cm}|C{3.4cm}|C{3.3cm}|>{\\centering\\arraybackslash}p{4.0cm}|C{1.8cm}|",
        caption="Lateral Torsional Buckling Check -- Construction Stage",
        header_cells=[r"\textbf{Girder}", r"\textbf{Parameter}", r"\textbf{Formula}", r"\textbf{Value}", r"\textbf{Status}"],
        body_tex="\n".join(t56_rows),
        note="Note: IRC 22 Cl. 603.3.3.1, IS 800 Cl. 8.2.2",
    )

    # Table 5.7 rows (Stiffener Design Summary)
    t57_rows = []
    for lbl, _ in girder_entries:
        t57_rows.append(
            r"\multirow{6}{*}{\makecell{" + _tex(lbl) + r"}} & \textnormal{Shear Buckling Design Method} & " + _render_value(bridge.output_dict, KEY_SD_STIFF_METHOD) + rf" \\*[{pad}pt]\cline{{2-3}}" + "\n"
            r" & \textnormal{Intermediate Stiffener Thickness (mm)} & " + _render_value(bridge.output_dict, KEY_SD_STIFF_INT_THICK) + rf" \\*[{pad}pt]\cline{{2-3}}" + "\n"
            r" & \textnormal{Intermediate Stiffener Spacing (mm)} & " + _render_value(bridge.output_dict, KEY_SD_STIFF_INT_SPACING) + rf" \\*[{pad}pt]\cline{{2-3}}" + "\n"
            r" & \textnormal{End Panel Stiffener Thickness (mm)} & " + _render_value(bridge.output_dict, KEY_SD_STIFF_END_THICK) + rf" \\*[{pad}pt]\cline{{2-3}}" + "\n"
            r" & \textnormal{No. of End Panel Stiffeners} & " + _render_value(bridge.output_dict, KEY_SD_STIFF_END_COUNT) + rf" \\*[{pad}pt]\cline{{2-3}}" + "\n"
            r" & \textnormal{Longitudinal Stiffeners} & " + _render_value(bridge.output_dict, KEY_SD_STIFF_LONG) + rf" \\[{pad}pt]\hline"
        )
    t57_table = build_longtable(
        col_spec="|C{2.4cm}|L{6.5cm}|>{\\arraybackslash}p{6.0cm}|",
        caption="Stiffener Design Summary",
        header_cells=[r"\textbf{Girder}", r"\textbf{Parameter}", r"\textbf{Value}"],
        body_tex="\n".join(t57_rows),
    )

    # Table 5.8 (Intermediate Stiffener Checks — Custom mode only)
    def _ge_status(provided, required):
        try:
            return "PASS" if float(provided) >= float(required) else r"\textcolor{red}{FAIL}"
        except (TypeError, ValueError):
            return "---"

    _iys_status = _ge_status(bridge.output_dict.get(KEY_SD_IS_IYS_PROV), bridge.output_dict.get(KEY_SD_IS_IYS_MIN))
    _fqd_status = _ge_status(bridge.output_dict.get(KEY_SD_IS_FQD), bridge.output_dict.get(KEY_SD_IS_FQ))
    t58_rows = []
    for lbl, _ in girder_entries:
        t58_rows.append(
            r"\multirow{2}{*}{\makecell{" + _tex(lbl) + r"}} & Min. Moment of Inertia, $I_s$ & " + _render_value(bridge.output_dict, KEY_SD_IS_IYS_MIN, " mm$^4$") + " & " + _render_value(bridge.output_dict, KEY_SD_IS_IYS_PROV, " mm$^4$") + " & " + _iys_status + rf" \\*[{pad}pt]\cline{{2-5}}" + "\n"
            r" & Buckling Resistance, $F_{qd} \geq F_q$ & " + _render_value(bridge.output_dict, KEY_SD_IS_FQ, " kN") + " & " + _render_value(bridge.output_dict, KEY_SD_IS_FQD, " kN") + " & " + _fqd_status + rf" \\[{pad}pt]\hline"
        )

    _is_custom = str(bridge.input_dict.get(KEY_DESIGN_MODE, "Optimized")).strip().lower() in {"custom", "customized"}
    if _is_custom:
        t58_block = build_longtable(
            col_spec="|C{2.2cm}|C{3.4cm}|C{3.3cm}|>{\\centering\\arraybackslash}p{4.0cm}|C{1.8cm}|",
            caption="Intermediate Stiffener Checks",
            header_cells=[r"\textbf{Girder}", r"\textbf{Check}", r"\textbf{Required}", r"\textbf{Provided}", r"\textbf{Status}"],
            body_tex="\n".join(t58_rows),
            note="Note: IS 800 Cl. 8.7.1.2",
        )
    else:
        t58_block = ""

    # Table 5.9 (End Panel / Bearing Stiffener Checks)
    _bs_r = bridge.output_dict.get(KEY_SD_BS_R)

    def _bs_check(resist_key):
        prov = bridge.output_dict.get(resist_key)
        if prov is None or float(prov) <= 0.0 or _bs_r is None:
            return ("N/A", "N/A", "N/A")
        req_s = f"{_bs_r} kN"
        prov_s = f"{prov} kN"
        status = "PASS" if float(prov) >= float(_bs_r) else r"\textcolor{red}{FAIL}"
        return (req_s, prov_s, status)

    _wb_req, _wb_prov, _wb_st = _bs_check(KEY_SD_BS_FCDW_WB)
    _lc_req, _lc_prov, _lc_st = _bs_check(KEY_SD_BS_FCDW_LC)
    _ps_req, _ps_prov, _ps_st = _bs_check(KEY_SD_BS_FPSD)
    _cb_req, _cb_prov, _cb_st = _bs_check(KEY_SD_BS_FCD)
    t59_rows = []
    for lbl, _ in girder_entries:
        t59_rows.append(
            r"\multirow{4}{*}{\makecell{" + _tex(lbl) + r"}} & Web Buckling Resistance & " + _wb_req + " & " + _wb_prov + " & " + _wb_st + rf" \\*[{pad}pt]\cline{{2-5}}" + "\n"
            r" & Local Crushing Resistance & " + _lc_req + " & " + _lc_prov + " & " + _lc_st + rf" \\*[{pad}pt]\cline{{2-5}}" + "\n"
            r" & Bearing Capacity & " + _ps_req + " & " + _ps_prov + " & " + _ps_st + rf" \\*[{pad}pt]\cline{{2-5}}" + "\n"
            r" & Column Buckling Resistance & " + _cb_req + " & " + _cb_prov + " & " + _cb_st + rf" \\[{pad}pt]\hline"
        )
    t59_table = build_longtable(
        col_spec="|C{2.2cm}|L{3.5cm}|C{3.3cm}|>{\\centering\\arraybackslash}p{4.0cm}|C{1.8cm}|",
        caption="End Panel Stiffener Checks",
        header_cells=[r"\textbf{Girder}", r"\textbf{Check}", r"\textbf{Required}", r"\textbf{Provided}", r"\textbf{Status}"],
        body_tex="\n".join(t59_rows),
        note="Note: IS 800 Cl. 8.4.2.2",
    )

    # Table 5.10 (Serviceability — Deflection Checks)
    def _defl_status(actual, allowable):
        try:
            return "PASS" if float(actual) <= float(allowable) else r"\textcolor{red}{FAIL}"
        except (TypeError, ValueError):
            return "---"

    def _dfmt(v, nd=2):
        try:
            return f"{float(v):.{nd}f}"
        except (TypeError, ValueError):
            return ""

    try:
        _span_m = float(bridge.input_dict.get(KEY_SPAN))
        _allow_live_mm = _span_m * 1000.0 / 800.0
        _allow_total_mm = _span_m * 1000.0 / 600.0
    except (TypeError, ValueError):
        _allow_live_mm = _allow_total_mm = None
    _allow_live_str = f"L/800 = {_allow_live_mm:.1f} mm" if _allow_live_mm is not None else ""
    _allow_total_str = f"L/600 = {_allow_total_mm:.1f} mm" if _allow_total_mm is not None else ""

    t510_rows = []
    for _gi, (lbl, _) in enumerate(girder_entries, start=1):
        _live_mm = bridge.output_dict.get(f"{KEY_SD_DEFL_LIVE}.G{_gi}")
        _total_mm = bridge.output_dict.get(f"{KEY_SD_DEFL_TOTAL}.G{_gi}")
        t510_rows.append(
            r"\multirow{2}{*}{\makecell{" + _tex(lbl) + r"}} & Live Load Deflection, $\delta_{LL}$ (mm) & "
            + _allow_live_str + " & " + _dfmt(_live_mm, nd=3) + " & " + _defl_status(_live_mm, _allow_live_mm) + rf" \\*[{pad}pt]\cline{{2-5}}" + "\n"
            r" & Total Load Deflection, $\delta_{total}$ (mm) & "
            + _allow_total_str + " & " + _dfmt(_total_mm, nd=3) + " & " + _defl_status(_total_mm, _allow_total_mm) + rf" \\[{pad}pt]\hline"
        )
    t510_table = build_longtable(
        col_spec="|C{2.2cm}|L{3.5cm}|C{3.3cm}|>{\\centering\\arraybackslash}p{3.5cm}|C{2.3cm}|",
        caption="Serviceability -- Deflection Checks",
        header_cells=[r"\textbf{Girder}", r"\textbf{Check}", r"\textbf{Allowable}", r"\textbf{Actual}", r"\textbf{Status}"],
        body_tex="\n".join(t510_rows),
        note="Note: IRC 22 Cl. 604.3.2",
    )

    # Table 5.11 (SLS Stress Limitation)
    def _mpa(v):
        s = _dfmt(v, nd=2)
        return (s + " MPa") if s else ""

    def _stress_status(actual, allow):
        try:
            return "PASS" if float(actual) <= float(allow) else r"\textcolor{red}{FAIL}"
        except (TypeError, ValueError):
            return "---"

    _dr_511 = bridge.output_dict.get("design_results", {}) or {}
    _steel_sigma = _dr_511.get(KEY_SD_STRESS_STEEL)
    _steel_allow = _dr_511.get(KEY_SD_STRESS_STEEL_ALLOWABLE)
    _steel_sig_str = _mpa(_steel_sigma)
    _steel_alw_str = _mpa(_steel_allow)
    _steel_status = _stress_status(_steel_sigma, _steel_allow)

    t511_rows = []
    for lbl, _ in girder_entries:
        t511_rows.append(
            r"\makecell{" + _tex(lbl) + r"} & Structural Steel ($0.9\,f_y$) & "
            + _steel_alw_str + " & " + _steel_sig_str + " & " + _steel_status + rf" \\[{pad}pt]\hline"
        )
    t511_table = build_longtable(
        col_spec="|C{2.2cm}|L{3.5cm}|C{3.3cm}|>{\\centering\\arraybackslash}p{3.5cm}|C{2.3cm}|",
        caption="Serviceability -- Maximum Stress Limitation",
        header_cells=[r"\textbf{Girder}", r"\textbf{Element}", r"\textbf{Allowable Stress}", r"\textbf{Actual Stress}", r"\textbf{Status}"],
        body_tex="\n".join(t511_rows),
    )

    # Table 5.12 (Fatigue Assessment)
    _fat_cat = ((bridge.output_dict.get("design_results", {}) or {}).get(KEY_SD_ULS_PER_GIRDER, {}) or {}).get("fatigue", {}) or {}

    def _fat_status(s):
        if s is None or str(s).strip() == "":
            return "---"
        return r"\textcolor{red}{" + str(s) + "}" if "FAIL" in str(s).upper() else str(s)

    t512_rows = []
    for _gi, (lbl, _) in enumerate(girder_entries, start=1):
        _g = _fat_cat.get(f"G{_gi}", {}) or {}
        t512_rows.append(
            r"\makecell{" + _tex(lbl) + r"} & "
            + _mpa(_g.get("demand")) + " & "
            + _mpa(_g.get("capacity")) + " & "
            + _dfmt(_g.get("ur"), nd=2) + " & "
            + _fat_status(_g.get("status")) + rf" \\[{pad}pt]\hline"
        )
    t512_table = build_longtable(
        col_spec="|C{2.2cm}|C{3.4cm}|C{3.4cm}|>{\\centering\\arraybackslash}p{3.4cm}|C{2.4cm}|",
        caption="Serviceability -- Fatigue Assessment",
        header_cells=[r"\textbf{Girder}", r"\textbf{Stress Range, $\Delta\sigma$ (MPa)}", r"\textbf{Fatigue Limit, $f_{fd}$ (MPa)}", r"\textbf{Utilization Ratio}", r"\textbf{Status}"],
        body_tex="\n".join(t512_rows),
        note="Note: IRC 22 Cl. 605 --- governing of normal and shear fatigue (worst by DCR). Capacity reduction factor $\\mu_r$ applied where plate thickness > 25 mm.",
    )

    # Table 5.13 (Girder Design Summary)
    _pg_summary = (bridge.output_dict.get("design_results", {}) or {}).get("per_girder", {}) or {}

    def _with_unit(value, unit):
        s = _dfmt(value, nd=2)
        if not s:
            return ""
        return (s + " " + unit) if unit and str(unit) not in ("-", "–") else s

    g_summary_rows = []
    for _gi, (lbl, _) in enumerate(girder_entries, start=1):
        g_data = _pg_summary.get(f"G{_gi}", {}) or {}
        checks = g_data.get("checks") or []
        if not checks:
            g_summary_rows.append(_tex(lbl) + rf" &  &  &  &  &  &  \\[{pad}pt]\hline")
            continue

        ctrl = max(checks, key=lambda c: c.get("dcr") or 0.0)
        ctrl_lc, best_dcr = None, None
        for lc_name, lc_data in (g_data.get("per_lc") or {}).items():
            if str(lc_name).lower().startswith("envelope"):
                continue
            for chk in lc_data.get("checks") or []:
                if chk.get("id") == ctrl.get("check_id"):
                    d = chk.get("dcr") or 0.0
                    if best_dcr is None or d > best_dcr:
                        best_dcr, ctrl_lc = d, lc_name
        if ctrl_lc is None:
            ctrl_lc = (g_data.get("demand") or {}).get("governing_combination") or ""

        g_summary_rows.append(
            _tex(lbl) + " & " + _tex(str(ctrl_lc)) + " & " + _tex(str(ctrl.get("name", "")))
            + " & " + _with_unit(ctrl.get("demand"), ctrl.get("demand_unit"))
            + " & " + _with_unit(ctrl.get("capacity"), ctrl.get("capacity_unit"))
            + " & " + _dfmt(ctrl.get("dcr"), nd=3)
            + " & " + _fat_status(ctrl.get("status")) + rf" \\[{pad}pt]\hline"
        )
    t513_table = build_longtable(
        col_spec="|C{1.6cm}|>{\\centering\\arraybackslash}p{3.6cm}|C{2.4cm}|C{2.0cm}|C{2.1cm}|C{1.6cm}|C{1.5cm}|",
        caption="Girder Design Summary (DCR / Utilization Ratio)",
        header_cells=[r"\textbf{Girder}", r"\textbf{Controlling LC / Combination}", r"\textbf{Controlling Check}", r"\textbf{Demand}", r"\textbf{Capacity}", r"\textbf{UR}", r"\textbf{Status}"],
        body_tex="\n".join(g_summary_rows),
        compact=True,
        note="Note: UR = Demand / Capacity. A value $\\leq 1.0$ indicates a passing check. The controlling check is the criterion with the highest UR for each girder.",
    )

    # Table 5.14 (Shear Connector Capacity)
    _dr_sc = bridge.output_dict.get("design_results", {}) or {}

    def _kn(v):
        s = _dfmt(v, nd=2)
        return (s + " kN") if s else ""

    t514_body = (
        r"Design Resistance, $Q_u$ & \footnotesize\makecell{$Q_u=\min(Q_{u,s},\,Q_{u,c})$\\[3pt]$Q_{u,s}=\dfrac{0.8\,f_u\,(\pi d^2/4)}{\gamma_v}$\\[3pt]$Q_{u,c}=\dfrac{0.29\,\alpha\,d^2\sqrt{f_{ck}\,E_{cm}}}{\gamma_v}$} & "
        + _kn(_dr_sc.get(KEY_SD_SC_Qu_kN)) + rf" & IRC 22 Cl. 606.3.1 (Eq. 6.1) \\[{pad}pt]\hline" + "\n"
        r"Fatigue Shear Resistance, $Q_r$ & IRC 22 Table 8 ($\phi d$, $N_{sc}$) & "
        + _kn(_dr_sc.get(KEY_SD_SC_Qr_kN)) + rf" & IRC 22 Cl. 606.3.2 (Table 8) \\[{pad}pt]\hline"
    )
    t514_table = build_longtable(
        col_spec="|L{3.6cm}|C{5.4cm}|>{\\centering\\arraybackslash}p{2.6cm}|L{3.2cm}|",
        caption="Shear Connector Capacity",
        header_cells=[r"\textbf{Parameter}", r"\textbf{Formula}", r"\textbf{Value}", r"\textbf{Reference}"],
        body_tex=t514_body,
    )

    # Table 5.15 (Shear Connector Spacing)
    def _mm(v):
        s = _dfmt(v, nd=1)
        return (s + " mm") if s else ""

    _sc_prov = _dr_sc.get("stud_spacing_provided_mm")
    _sc_prov_str = _mm(_sc_prov)

    def _sp_row(crit, req):
        return crit + " & " + _mm(req) + " & " + _sc_prov_str + " & " + _defl_status(_sc_prov, req) + rf" \\[{pad}pt]\hline"

    t515_body = "\n".join([
        _sp_row("ULS Shear (SL1)", _dr_sc.get(KEY_SD_SC_SL1)),
        _sp_row("Full Composite (SL2)", _dr_sc.get(KEY_SD_SC_SL2)),
        _sp_row("SLS Fatigue (SR)", _dr_sc.get(KEY_SD_SC_SR)),
        _sp_row("Max Spacing Limit (IRC 22)", _dr_sc.get("stud_spacing_max_mm")),
    ])
    t515_table = build_longtable(
        col_spec="|L{3.5cm}|>{\\centering\\arraybackslash}p{4.4cm}|>{\\centering\\arraybackslash}p{4.4cm}|C{2.2cm}|",
        caption="Shear Connector Spacing",
        header_cells=[r"\textbf{Criterion}", r"\textbf{Governing Spacing}", r"\textbf{Actual Spacing Provided}", r"\textbf{Status}"],
        body_tex=t515_body,
        note="Note: IRC 22 Cl. 606.4, 606.9. Governing spacing $= \\min(S_{L1}, S_{L2}, S_R)$.",
    )

    # Table 5.16 (Transverse Shear and Detailing Checks)
    def _cm2m(v):
        s = _dfmt(v, nd=2)
        return (s + r" cm$^2$/m") if s else ""

    def _knm(v):
        s = _dfmt(v, nd=2)
        return (s + " kN/m") if s else ""

    _ts_vl = _dr_sc.get(KEY_SD_TS_VL)
    _ts_vrd = _dr_sc.get(KEY_SD_TS_VRD)
    if _ts_vl is not None and _ts_vrd is not None:
        try:
            _ts_vl_f = float(_ts_vl)
            _ts_vrd_f = float(_ts_vrd)
            _ts_ur_str = f"{_ts_vl_f / _ts_vrd_f:.2f}" if _ts_vrd_f > 0.0 else "---"
        except (TypeError, ValueError):
            _ts_ur_str = "---"
    else:
        _ts_ur_str = "---"
    _ts_ok = _dr_sc.get("transverse_shear_ok")
    _ts_status = (r"\textcolor{red}{FAIL}" if _ts_ok is False else "PASS") if _ts_ok is not None else "---"

    _ast_req = _dr_sc.get("Ast_required_cm2_per_m")
    _dd_516 = bridge.output_dict.get("deck_design_results", {}) or {}
    try:
        _ast_prov = (float(_dd_516.get("rebar_bottom_area") or 0) + float(_dd_516.get("rebar_top_area") or 0)) / 100.0
    except (TypeError, ValueError):
        _ast_prov = None
    _stud_d = bridge.input_dict.get(KEY_DS_STUD_DIAMETER)
    _d_lim = _dr_sc.get(KEY_SD_SC_D_LIMIT)
    _edge = _dr_sc.get(KEY_SD_SC_EDGE_DIST)
    _edge_req = _dr_sc.get(KEY_SD_SC_REQ_EDGE_DIST)

    def _row516(check, value, status):
        return check + " & " + value + " & " + status + rf" \\[{pad}pt]\hline"

    t516_body = "\n".join([
        _row516(r"\textnormal{Longitudinal Shear per unit length, $V_L$}", _knm(_ts_vl), "---"),
        _row516(r"\textnormal{Transverse Shear Capacity of Slab, $V_{Rd}$}", _knm(_ts_vrd), "---"),
        _row516(r"\textnormal{Transverse Shear Check}", r"$V_L/V_{Rd}$ = " + _ts_ur_str, _ts_status),
        _row516(r"\textnormal{Min. Transverse Reinforcement, $A_{st,min}$}", r"Required " + _cm2m(_ast_req) + r", Provided " + _cm2m(_ast_prov), _defl_status(_ast_req, _ast_prov)),
        _row516(r"\textnormal{Stud Diameter $\leq 2\,t_f$}", r"$d$ = " + _mm(_stud_d) + r" $\leq 2t_f$ = " + _mm(_d_lim), _defl_status(_stud_d, _d_lim)),
        _row516(r"\textnormal{Stud Edge Distance}", r"Provided " + _mm(_edge) + r" (req. $\geq$ " + _mm(_edge_req) + r")", _defl_status(_edge_req, _edge)),
    ])
    t516_table = build_longtable(
        col_spec="|L{5.5cm}|>{\\arraybackslash}p{7.2cm}|C{2.1cm}|",
        caption="Transverse Shear and Detailing Checks",
        header_cells=[r"\textbf{Check}", r"\textbf{Value}", r"\textbf{Status}"],
        body_tex=t516_body,
        note="Note: IRC 22 Cl. 606.6, 606.10.",
    )

    # Cross Bracing & End Diaphragm Tables
    cb_forces_rows = []
    pairs = bridge.get_cb_pairs()
    if not pairs:
        cb_forces_rows.append(rf"Between Girders & Diagonal &  &  &  &  \\[{pad}pt]\hline")
    else:
        for pair in pairs:
            pair_id = pair.replace("-", "")
            row_items = []
            for member, label in [("diagonal", "Diagonal"), ("chord", "Top / Bottom chord")]:
                force_str, ftype = bridge.get_cb_governing_force(pair, member)
                conn_type = bridge.get_cb_connection(pair, member, ftype)
                section = bridge.get_cb_section(pair, member, ftype)
                if member == "diagonal":
                    pfx = f"transverse_member_design.cb.section_properties.bracing.{pair_id}"
                else:
                    pfx = f"transverse_member_design.cb.section_properties.bottom_chord.{pair_id}"
                    if bridge.output_dict.get(f"{pfx}.A") is None:
                        pfx = f"transverse_member_design.cb.section_properties.top_chord.{pair_id}"
                area_cm2 = bridge.output_dict.get(f"{pfx}.A")
                rv_cm = bridge.output_dict.get(f"{pfx}.rv")
                area_str = f"{float(area_cm2) * 100:.1f}" if area_cm2 is not None else ""
                rmin_str = f"{float(rv_cm) * 10:.1f}" if rv_cm is not None else ""
                row_items.append((label, conn_type, section, area_str, rmin_str))

            cb_forces_rows.append(
                r"\multirow{2}{*}{\makecell{" + _tex(pair) + r"}} & " + " & ".join(row_items[0]) + rf" \\*[{pad}pt]\cline{{2-6}}" + "\n"
                r" & " + " & ".join(row_items[1]) + rf" \\[{pad}pt]\hline"
            )
    cb_forces_content = "\n".join(cb_forces_rows)

    def get_status_str(slnd_str, limit):
        try:
            v = float(slnd_str)
            return r"\textcolor{black}{PASS}" if v <= limit else r"\textcolor{red}{FAIL}"
        except (ValueError, TypeError):
            return ""

    cb_slenderness_rows = []
    if not pairs:
        cb_slenderness_rows.append(rf"Between Girders & Diagonal & C &  &  &  ---  \\[{pad}pt]\hline")
    else:
        for pair in pairs:
            kl_diag = bridge.get_cb_effective_length("diagonal")
            slnd_diag = bridge.get_cb_slenderness(pair, "diagonal")
            status_diag = get_status_str(slnd_diag, 250)

            kl_tc = bridge.get_cb_effective_length("chord")
            slnd_tc = bridge.get_cb_slenderness(pair, "chord")
            status_tc = get_status_str(slnd_tc, 250)

            kl_bc = bridge.get_cb_effective_length("chord")
            slnd_bc = bridge.get_cb_slenderness(pair, "chord")
            status_bc = get_status_str(slnd_bc, 400)

            top_chord_enabled = bridge.output_dict.get("member_properties.cross_bracing_details.top_chord", True)
            bottom_chord_enabled = bridge.output_dict.get("member_properties.cross_bracing_details.bottom_chord", True)

            sub_rows = [f"Diagonal & C & {kl_diag} & {slnd_diag} & 250 --- {status_diag}"]
            if top_chord_enabled:
                sub_rows.append(f"Top chord & C & {kl_tc} & {slnd_tc} & 250 --- {status_tc}")
            if bottom_chord_enabled:
                sub_rows.append(f"Bottom chord & T & {kl_bc} & {slnd_bc} & 400 --- {status_bc}")

            num_rows = len(sub_rows)
            block = []
            for idx, sr in enumerate(sub_rows):
                prefix = (r"\multirow{" + str(num_rows) + r"}{*}{\makecell{" + _tex(pair) + r"}} & ") if idx == 0 else " & "
                suffix = rf" \\[{pad}pt]\hline" if idx == num_rows - 1 else rf" \\*[{pad}pt]\cline{{2-6}}"
                block.append(prefix + sr + suffix)
            cb_slenderness_rows.append("\n".join(block))
    cb_slenderness_content = "\n".join(cb_slenderness_rows)

    cb_capacity_rows = []
    for pair in pairs:
        rows_for_pair = []
        for member, label in [("diagonal", "Diagonal"), ("chord", "Chord")]:
            force_str, ftype = bridge.get_cb_governing_force(pair, member)
            section = bridge.get_cb_section(pair, member, ftype)
            gov_lc = bridge.get_cb_gov_lc(pair, member, ftype)
            capacity = bridge.get_cb_capacity(pair, member, ftype)
            ur = bridge.get_cb_efficiency(pair, member, ftype)
            status = bridge.get_cb_status(pair, member, ftype)
            rows_for_pair.append(
                label + " & " + section + " & " + gov_lc + " & " + force_str + " & " + capacity + " & " + ur + " & " + status
            )
        cb_capacity_rows.append(
            r"\multirow{2}{*}{\makecell{" + _tex(pair) + r"}} & " + rows_for_pair[0] + rf" \\*[{pad}pt]\cline{{2-8}}" + "\n"
            r" & " + rows_for_pair[1] + rf" \\[{pad}pt]\hline"
        )
    cb_capacity_content = "\n".join(cb_capacity_rows)

    t518_table = build_longtable(
        col_spec="|C{2.0cm}|L{2.2cm}|L{2.2cm}|C{2.5cm}|C{2.0cm}|C{2.0cm}|",
        caption="Cross Bracing --- Connection and Section Properties",
        header_cells=[r"\textbf{Panel}", r"\textbf{Member}", r"\textbf{Connection}", r"\textbf{Section}", r"\textbf{$A_g$ (mm²)}", r"\textbf{$r_{min}$ (mm)}"],
        body_tex=cb_forces_content,
        compact=True,
        note="Note: $A_g$ = gross cross-sectional area; $r_{min}$ = minimum radius of gyration.",
    )
    t519_table = build_longtable(
        col_spec="|C{2.1cm}|L{2.2cm}|C{2.0cm}|C{2.5cm}|C{2.2cm}|>{\\centering\\arraybackslash}p{3.6cm}|",
        caption="Cross Bracing --- Slenderness Ratio Check (IS~800 Cl.~3.8)",
        header_cells=[r"\textbf{Panel}", r"\textbf{Member}", r"\textbf{Nature}", r"\textbf{Eff.\ Length $KL$ (mm)}", r"\textbf{$KL/r$}", r"\textbf{Limit / Status}"],
        body_tex=cb_slenderness_content,
        note="Note: Limit = 250 for compression members, 400 for tension members. $K = 1.0$ for members with both ends pinned.",
    )
    t520_table = build_longtable(
        col_spec="|C{1.9cm}|L{1.8cm}|C{2.2cm}|C{2.8cm}|C{1.8cm}|C{1.8cm}|C{1.1cm}|C{1.5cm}|",
        caption="Cross Bracing Design --- Capacity Summary",
        header_cells=[r"\textbf{Panel}", r"\textbf{Member}", r"\textbf{Section}", r"\textbf{Governing LC}", r"\textbf{Demand (kN)}", r"\textbf{Capacity (kN)}", r"\textbf{UR}", r"\textbf{Status}"],
        body_tex=cb_capacity_content,
        compact=True,
        note="Note: Designed per IS 800 Cl. 7 (compression) and Cl. 6 (tension). OsdagBridge cross-bracing module used.",
    )

    t521a_table = build_longtable(
        col_spec="|C{2.0cm}|L{2.2cm}|L{2.2cm}|C{2.5cm}|C{2.0cm}|C{2.0cm}|",
        caption="End Diaphragm --- Connection and Section Properties",
        header_cells=[r"\textbf{Panel}", r"\textbf{Member}", r"\textbf{Connection}", r"\textbf{Section}", r"\textbf{$A_g$ (mm²)}", r"\textbf{$r_{min}$ (mm)}"],
        body_tex=cb_forces_content,
        compact=True,
        note="Note: $A_g$ = gross cross-sectional area; $r_{min}$ = minimum radius of gyration.",
    )
    t521b_table = build_longtable(
        col_spec="|C{2.1cm}|L{2.2cm}|C{2.0cm}|C{2.5cm}|C{2.2cm}|>{\\centering\\arraybackslash}p{3.6cm}|",
        caption="End Diaphragm --- Slenderness Ratio Check (IS~800 Cl.~3.8)",
        header_cells=[r"\textbf{Panel}", r"\textbf{Member}", r"\textbf{Nature}", r"\textbf{Eff.\ Length $KL$ (mm)}", r"\textbf{$KL/r$}", r"\textbf{Limit / Status}"],
        body_tex=cb_slenderness_content,
        note="Note: Limit = 250 for compression members, 400 for tension members. $K = 1.0$ for members with both ends pinned.",
    )
    t521c_table = build_longtable(
        col_spec="|C{1.9cm}|L{1.8cm}|C{2.2cm}|C{2.8cm}|C{1.8cm}|C{1.8cm}|C{1.1cm}|C{1.5cm}|",
        caption="End Diaphragm Design --- Capacity Summary",
        header_cells=[r"\textbf{Panel}", r"\textbf{Member}", r"\textbf{Section}", r"\textbf{Governing LC}", r"\textbf{Demand (kN)}", r"\textbf{Capacity (kN)}", r"\textbf{UR}", r"\textbf{Status}"],
        body_tex=cb_capacity_content,
        compact=True,
        note="Note: Designed per IS 800 Cl. 7 (compression) and Cl. 6 (tension). OsdagBridge cross-bracing module used.",
    )

    # Deck slab helpers
    _dk_has = bool(deck_rpt)
    _dk_oh = bool(deck_rpt.get(KEY_DD_HAS_OVERHANG))
    _DKPH = r"\placeholder{---}"

    def _dkv(key, default=0.0):
        v = deck_rpt.get(key)
        if v is None or v == "":
            return default
        try:
            return float(v)
        except (TypeError, ValueError):
            return default

    def _dkf(key, nd=2, scale=1.0):
        if not _dk_has:
            return _DKPH
        v = deck_rpt.get(key)
        if v is None or v == "":
            return _DKPH
        try:
            return f"{float(v) * scale:.{nd}f}"
        except (TypeError, ValueError):
            return str(v)

    def _dks(ok):
        return ("PASS" if ok else "FAIL") if _dk_has else "---"

    def _dkoh(key, nd=2, scale=1.0, unit=""):
        if not _dk_has:
            return _DKPH
        if not _dk_oh:
            return "N/A"
        return _dkf(key, nd=nd, scale=scale) + unit

    _dk_wks = [_dkv(KEY_DD_WK_BOT), _dkv(KEY_DD_WK_TOP)]
    if _dk_oh:
        _dk_wks.append(_dkv(KEY_DD_WK_OH))
    _dk_gov_wk = max(_dk_wks)
    _dk_gov_wk_str = f"{_dk_gov_wk:.4f}" if _dk_has else _DKPH
    _dk_crack_ok = _dk_has and _dk_gov_wk <= _dkv(KEY_DD_WK_LIMIT)

    # Deck tables (5.17a - 5.17g)
    t517a_body = "\n".join([
        r"\textnormal{Effective Span of Deck Slab, $l_{eff}$} & " + _dkf(KEY_DD_SPAN, nd=0, scale=1000.0) + rf" mm (girder spacing, c/c) \\[{pad}pt]\hline",
        r"\textnormal{Deck Thickness, $t_s$} & " + _render_value(bridge.input_dict, KEY_TS_DECK_THICKNESS) + rf" mm \\[{pad}pt]\hline",
        r"\textnormal{Clear Cover (IRC 112 Cl. 15.2)} & Top " + _render_value(bridge.input_dict, KEY_DS_TOP_CLEAR_COVER) + r" / Bottom " + _render_value(bridge.input_dict, KEY_DS_BOTTOM_CLEAR_COVER) + rf" mm \\[{pad}pt]\hline",
        r"\textnormal{Concrete Grade (IRC 112 Cl. 6.4)} & " + _render_value(bridge.input_dict, KEY_DECK_CONCRETE_GRADE_BASIC) + r" ($f_{ck}$ = " + _render_value(bridge.input_dict, KEY_MATERIAL_DECK_FCK) + r" MPa, $f_{ctm}$ = " + _render_value(bridge.input_dict, KEY_MATERIAL_DECK_FCTM) + rf" MPa) \\[{pad}pt]\hline",
        r"\textnormal{Reinforcement Grade (IRC 112 Cl. 6.2)} & " + _render_value(bridge.input_dict, KEY_DS_REINF_MATERIAL) + r" ($f_y$ = " + _dkf(KEY_DD_FY, nd=0) + rf" MPa) \\[{pad}pt]\hline",
        r"\textnormal{Dead Load per Unit Area, $w_{DL}$} & " + _dkf(KEY_DD_WDL, nd=2) + rf" kN/m² (slab self-weight) \\[{pad}pt]\hline",
        r"\textnormal{IRC 6 Wheel Load (Class A / 70R)} & " + _dkf(KEY_DD_WHEEL_LOAD, nd=1) + rf" kN \\[{pad}pt]\hline",
        r"\textnormal{Tyre Contact Width (IRC 6 Annex~A)} & " + _dkf(KEY_DD_TYRE_WIDTH, nd=0, scale=1000.0) + rf" mm (transverse) \\[{pad}pt]\hline",
        r"\textnormal{Impact Factor (IRC 6 Cl. 208.2)} & " + _dkf(KEY_DD_IMPACT_FACTOR, nd=3) + rf" \\[{pad}pt]\hline",
        r"\textnormal{Governing Live Load Case} & " + _dkf(KEY_DD_VEHICLE) + rf" \\[{pad}pt]\hline",
    ])
    t517a_table = build_longtable(
        col_spec="|L{5.8cm}|p{9.2cm}|",
        caption="Deck Slab --- Loading and Geometry",
        header_cells=[r"\textbf{Parameter}", r"\textbf{Value}"],
        body_tex=t517a_body,
    )

    t517b_body = (
        r"\multirow{5}{*}{\makecell{At Midspan\\(Sagging)}} & Transverse BM (DL), $M_{T,DL}$ & $w_{DL}\,l_{eff}^2/10$ & " + _dkf(KEY_DD_M_DL, nd=2) + rf" kN-m/m & --- \\*[{pad}pt]\cline{{2-5}}" + "\n"
        r" & Transverse BM (LL), $M_{T,LL}$ & Effective width (IRC 112 B3.1) & " + _dkf(KEY_DD_M_LL, nd=2) + rf" kN-m/m & --- \\*[{pad}pt]\cline{{2-5}}" + "\n"
        r" & Total Design BM, $M_{u,sag}$ & " + _dkf(KEY_DD_GAMMA_DL, nd=2) + r" DL + " + _dkf(KEY_DD_GAMMA_LL, nd=2) + r" LL & " + _dkf(KEY_DD_M_ULS_SAG, nd=2) + rf" kN-m/m & --- \\*[{pad}pt]\cline{{2-5}}" + "\n"
        r" & Effective depth, $d$ & $t_s - c_{nom} - \phi/2$ & " + _dkf(KEY_DD_D_BOT, nd=1) + rf" mm & --- \\*[{pad}pt]\cline{{2-5}}" + "\n"
        r" & Moment Capacity, $M_{Rd}$ & IRC 112 Cl. 12.2 & " + _dkf(KEY_DD_MU_BOT, nd=2) + r" kN-m/m & " + _dks(_dkv(KEY_DD_MU_BOT) >= _dkv(KEY_DD_M_ULS_SAG)) + rf" \\[{pad}pt]\hline" + "\n"
        r"\multirow{3}{*}{\makecell{At Support\\(Hogging)}} & Total Design BM, $M_{u,hog}$ & " + _dkf(KEY_DD_GAMMA_DL, nd=2) + r" DL + " + _dkf(KEY_DD_GAMMA_LL, nd=2) + r" LL (at support) & " + _dkf(KEY_DD_M_ULS_HOG, nd=2) + rf" kN-m/m & --- \\*[{pad}pt]\cline{{2-5}}" + "\n"
        r" & Required Top Steel, $A_{st,top}$ & $M_u / (0.87\,f_y\,d)$ & " + _dkf(KEY_DD_AS_REQ_TOP, nd=0) + rf" mm²/m & --- \\*[{pad}pt]\cline{{2-5}}" + "\n"
        r" & Moment Capacity, $M_{Rd}$ & IRC 112 Cl. 12.2 & " + _dkf(KEY_DD_MU_TOP, nd=2) + r" kN-m/m & " + _dks(_dkv(KEY_DD_MU_TOP) >= _dkv(KEY_DD_M_ULS_HOG)) + rf" \\[{pad}pt]\hline"
    )
    t517b_table = build_longtable(
        col_spec="|C{2.8cm}|C{3.4cm}|C{3.0cm}|>{\\centering\\arraybackslash}p{4.0cm}|C{1.8cm}|",
        caption="Deck Slab --- Flexure Check: Interior Panel (Pigeaud's Method)",
        header_cells=[r"\textbf{Location}", r"\textbf{Parameter}", r"\textbf{Formula / Reference}", r"\textbf{Value}", r"\textbf{Status}"],
        body_tex=t517b_body,
        note="Note: IRC 112 Cl. 12.2. Distribution (longitudinal) reinforcement designed for 20\\% of main steel moment (IRC 21 Cl. 305.18).",
    )

    t517c_body = "\n".join([
        r"Overhang Length, $l_{oh}$ & --- & " + _render_value(bridge.input_dict, KEY_TS_DECK_OVERHANG, " m") + rf" & --- \\[{pad}pt]\hline",
        r"Crash Barrier Load Moment & IRC 6 Cl. 206.4 & " + _dkoh(KEY_DD_M_BARRIER, nd=2, unit=" kN-m/m") + rf" & --- \\[{pad}pt]\hline",
        r"Dead Load Moment & $w_{DL}\,l_{oh}^2/2$ + railing & " + _dkoh(KEY_DD_M_DL_OH, nd=2, unit=" kN-m/m") + rf" & --- \\[{pad}pt]\hline",
        r"Live Load Moment (eccentric wheel) & Wheel load $\times$ arm & " + _dkoh(KEY_DD_M_LL_OH, nd=2, unit=" kN-m/m") + rf" & --- \\[{pad}pt]\hline",
        r"Total Hogging Moment, $M_{u,oh}$ & " + _dkf(KEY_DD_GAMMA_DL, nd=2) + r" DL + " + _dkf(KEY_DD_GAMMA_LL, nd=2) + r" (LL + CB) & " + _dkoh(KEY_DD_M_ULS_OH, nd=2, unit=" kN-m/m") + rf" & --- \\[{pad}pt]\hline",
        r"Moment Capacity (top steel), $M_{Rd,oh}$ & IRC 112 Cl. 12.2 & " + _dkoh(KEY_DD_MU_OH, nd=2, unit=" kN-m/m") + r" & " + (_dks(_dkv(KEY_DD_MU_OH) >= _dkv(KEY_DD_M_ULS_OH)) if _dk_oh else ("N/A" if _dk_has else "---")) + rf" \\[{pad}pt]\hline",
    ])
    t517c_table = build_longtable(
        col_spec="|L{5.5cm}|C{3.5cm}|>{\\centering\\arraybackslash}p{4.2cm}|C{1.8cm}|",
        caption="Deck Slab --- Cantilever Overhang Flexure Check",
        header_cells=[r"\textbf{Parameter}", r"\textbf{Formula}", r"\textbf{Value}", r"\textbf{Status}"],
        body_tex=t517c_body,
        note="Note: IRC 6 Cl. 206.4 crash barrier loads applied at kerb face; IRC 112 Cl. 12.2 flexure.",
    )

    t517d_body = "\n".join([
        r"Design Wheel Load (ULS), $V_{Ed}$ & $\gamma_Q\,(1+IF)\,P_w$ & " + _dkf(KEY_DD_PUNCH_VED_KN, nd=1) + rf" kN & --- \\[{pad}pt]\hline",
        r"Tyre Contact Area & $a \times b$ (IRC 6 Annex~A) & " + _dkf(KEY_DD_TYRE_WIDTH, nd=0, scale=1000.0) + r" $\times$ " + _dkf(KEY_DD_TYRE_LENGTH, nd=0) + rf" mm & --- \\[{pad}pt]\hline",
        r"Loaded Area at mid-depth, $b_0$ & $c_1 \times c_2$ (incl.\ WC dispersion) & " + _dkf(KEY_DD_PUNCH_C1, nd=0) + r" $\times$ " + _dkf(KEY_DD_PUNCH_C2, nd=0) + rf" mm & --- \\[{pad}pt]\hline",
        r"Control Perimeter, $u_1$ & $2(c_1+c_2) + 4\pi d$ & " + _dkf(KEY_DD_PUNCH_U1, nd=0) + rf" mm & --- \\[{pad}pt]\hline",
        r"Punching Shear Stress, $v_{Ed}$ & $V_{Ed} / (u_1\,d)$ & " + _dkf(KEY_DD_PUNCH_VED, nd=3) + rf" MPa & --- \\[{pad}pt]\hline",
        r"Punching Resistance, $v_{Rd,c}$ & IRC 112 Eq.\ 10.1 & " + _dkf(KEY_DD_VRD_C_MPA, nd=3) + rf" MPa & --- \\[{pad}pt]\hline",
        r"Punching Shear Check & $v_{Ed} \leq v_{Rd,c}$ & " + (f"{_dkv(KEY_DD_PUNCH_VED) / _dkv(KEY_DD_VRD_C_MPA):.2f}" if (_dk_has and _dkv(KEY_DD_VRD_C_MPA) > 0) else _DKPH) + r" & " + _dks(bool(deck_rpt.get(KEY_DD_PUNCH_OK))) + rf" \\[{pad}pt]\hline",
    ])
    t517d_table = build_longtable(
        col_spec="|L{5.5cm}|C{3.5cm}|>{\\centering\\arraybackslash}p{4.2cm}|C{1.8cm}|",
        caption="Deck Slab --- Punching Shear Check (IRC~112 Cl.~10.4.6)",
        header_cells=[r"\textbf{Parameter}", r"\textbf{Formula / Reference}", r"\textbf{Value}", r"\textbf{Status}"],
        body_tex=t517d_body,
        note="Note: Punching shear reinforcement not typically required for deck slabs with $d \\geq 200$ mm and adequate longitudinal reinforcement.",
    )

    t517e_body = "\n".join([
        r"\textnormal{Min. Reinforcement for Crack Control, $A_{s,min}$} & " + _dkf(KEY_DD_AS_MIN, nd=0) + rf" mm²/m [IRC 112 Cl. 16.5.1] \\[{pad}pt]\hline",
        r"\textnormal{Provided Reinforcement (bottom)} & $\phi$" + _dkf(KEY_DD_DIA_BOT, nd=0) + r" @ " + _dkf(KEY_DD_SPC_BOT, nd=0) + r" mm c/c (" + _dkf(KEY_DD_AS_BOT, nd=0) + rf" mm²/m) \\[{pad}pt]\hline",
        r"\textnormal{Max. Permissible Crack Width} & " + _dkf(KEY_DD_WK_LIMIT, nd=2) + rf" mm \\[{pad}pt]\hline",
        r"\textnormal{Calculated Crack Width, $w_k$ (governing)} & " + _dk_gov_wk_str + rf" mm \\[{pad}pt]\hline",
        r"\textnormal{Crack Width Check} & " + _dks(_dk_crack_ok) + rf" \\[{pad}pt]\hline",
    ])
    t517e_table = build_longtable(
        col_spec="|L{6.8cm}|>{\\arraybackslash}p{8.2cm}|",
        caption="Crack Width Check (Deck Slab)",
        header_cells=[r"\textbf{Parameter}", r"\textbf{Value / Reference}"],
        body_tex=t517e_body,
    )

    t517f_body = "\n".join([
        r"Design Shear per unit width, $V_{Ed}$ & $\gamma_{DL} V_{DL} + \gamma_{LL}(1{+}IF)V_{LL}$ & " + _dkf(KEY_DD_SHEAR_VED, nd=2) + rf" kN/m & --- \\[{pad}pt]\hline",
        r"Effective depth, $d$ & $t_s - c_{nom} - \phi/2$ & " + _dkf(KEY_DD_D_BOT, nd=1) + rf" mm & --- \\[{pad}pt]\hline",
        r"Size factor, $k$ & $1 + \sqrt{200/d} \leq 2.0$ & " + (f"{min(1.0 + (200.0 / _dkv(KEY_DD_D_BOT)) ** 0.5, 2.0):.3f}" if (_dk_has and _dkv(KEY_DD_D_BOT) > 0) else _DKPH) + rf" & --- \\[{pad}pt]\hline",
        r"Long.\ reinforcement ratio, $\rho_l$ & $A_{sl}/(b_w\,d) \leq 0.02$ & " + (f"{min(_dkv(KEY_DD_AS_BOT) / (1000.0 * _dkv(KEY_DD_D_BOT)), 0.02):.4f}" if (_dk_has and _dkv(KEY_DD_D_BOT) > 0) else _DKPH) + rf" & --- \\[{pad}pt]\hline",
        r"Shear resistance (no stirrups), $V_{Rd,c}$ & $v_{Rd,c}\,b_w\,d$ (Cl.\ 10.3.2) & " + _dkf(KEY_DD_SHEAR_VRDC, nd=2) + rf" kN/m & --- \\[{pad}pt]\hline",
        r"One-Way Shear Check & $V_{Ed} \leq V_{Rd,c}$ & " + (f"{_dkv(KEY_DD_SHEAR_VED) / _dkv(KEY_DD_SHEAR_VRDC):.2f}" if (_dk_has and _dkv(KEY_DD_SHEAR_VRDC) > 0) else _DKPH) + r" & " + _dks(bool(deck_rpt.get(KEY_DD_SHEAR_OK))) + rf" \\[{pad}pt]\hline",
    ])
    t517f_table = build_longtable(
        col_spec="|L{5.5cm}|C{3.5cm}|>{\\centering\\arraybackslash}p{4.2cm}|C{1.8cm}|",
        caption="One-Way (Beam) Shear Check (Deck Slab)",
        header_cells=[r"\textbf{Parameter}", r"\textbf{Formula / Reference}", r"\textbf{Value}", r"\textbf{Status}"],
        body_tex=t517f_body,
        note="Note: IRC 112 Cl. 10.3.2. Shear reinforcement not provided in deck slabs; capacity relies on concrete and main reinforcement.",
    )

    t517g_body = "\n".join([
        rf"\multicolumn{{4}}{{|l|}}{{\rowcolor{{osdagSubHeaderBg}}\textbf{{Main Reinforcement --- Bottom (Transverse)}}}} \\[{pad}pt]\hline",
        r"Required Area, $A_{st,req}$ (mm²/m) & " + _dkf(KEY_DD_AS_REQ_BOT, nd=0) + r" mm²/m & " + _dkf(KEY_DD_AS_BOT, nd=0) + r" mm²/m & " + _dks(_dkv(KEY_DD_AS_BOT) >= _dkv(KEY_DD_AS_REQ_BOT)) + rf" \\[{pad}pt]\hline",
        r"Bar Diameter $\times$ Spacing & $\phi \geq 10$ mm (IRC 112) & $\phi$" + _dkf(KEY_DD_DIA_BOT, nd=0) + r" @ " + _dkf(KEY_DD_SPC_BOT, nd=0) + rf" mm c/c & --- \\[{pad}pt]\hline",
        r"Min.\ Reinforcement $A_{s,min}$ (IRC 112 Cl. 16.3.1) & " + _dkf(KEY_DD_AS_MIN, nd=0) + r" mm²/m & " + _dkf(KEY_DD_AS_BOT, nd=0) + r" mm²/m & " + _dks(_dkv(KEY_DD_AS_BOT) >= _dkv(KEY_DD_AS_MIN)) + rf" \\[{pad}pt]\hline",
        r"Max.\ Bar Spacing (IRC 112 Cl. 16.3.2) & " + _dkf(KEY_DD_SPACING_MAX, nd=0) + r" mm & " + _dkf(KEY_DD_SPC_BOT, nd=0) + r" mm & " + _dks(0.0 < _dkv(KEY_DD_SPC_BOT) <= _dkv(KEY_DD_SPACING_MAX)) + rf" \\[{pad}pt]\hline",
        rf"\multicolumn{{4}}{{|l|}}{{\rowcolor{{osdagSubHeaderBg}}\textbf{{Distribution Reinforcement --- Longitudinal}}}} \\[{pad}pt]\hline",
        r"Required Area, $A_{st,dist}$ (mm²/m) & $\geq 20\%$ of main steel & " + _dkf(KEY_DD_AS_LONG, nd=0) + r" mm²/m & " + _dks(_dkv(KEY_DD_AS_LONG) >= max(0.20 * _dkv(KEY_DD_AS_BOT), _dkv(KEY_DD_AS_MIN))) + rf" \\[{pad}pt]\hline",
        rf"\multicolumn{{4}}{{|l|}}{{\rowcolor{{osdagSubHeaderBg}}\textbf{{Top Reinforcement (Support / Cantilever Overhang)}}}} \\[{pad}pt]\hline",
        r"Required Area, $A_{st,top}$ (mm²/m) & " + _dkf(KEY_DD_AS_REQ_TOP, nd=0) + r" mm²/m & " + _dkf(KEY_DD_AS_TOP, nd=0) + r" mm²/m & " + _dks(_dkv(KEY_DD_AS_TOP) >= _dkv(KEY_DD_AS_REQ_TOP)) + rf" \\[{pad}pt]\hline",
        rf"\multicolumn{{4}}{{|l|}}{{\rowcolor{{osdagSubHeaderBg}}\textbf{{Cover and Detailing}}}} \\[{pad}pt]\hline",
        r"Clear Cover (IRC 112 Cl. 15.2) & $\geq$ " + _dkf(KEY_DD_MIN_COVER, nd=0) + r" mm (Table 14.2) & Top " + _render_value(bridge.input_dict, KEY_DS_TOP_CLEAR_COVER) + r" / Bottom " + _render_value(bridge.input_dict, KEY_DS_BOTTOM_CLEAR_COVER) + r" mm & " + _dks(bool(deck_rpt.get(KEY_DD_COVER_OK))) + rf" \\[{pad}pt]\hline",
    ])
    t517g_table = build_longtable(
        col_spec="|L{5.5cm}|>{\\centering\\arraybackslash}p{3.9cm}|>{\\centering\\arraybackslash}p{3.9cm}|C{1.8cm}|",
        caption="Reinforcement Detailing Summary (Deck Slab)",
        header_cells=[r"\textbf{Parameter}", r"\textbf{Required / Limit}", r"\textbf{Provided}", r"\textbf{Status}"],
        body_tex=t517g_body,
        note="Note: IRC 112 Cl. 16.3, IS 456 Cl. 26.5. All reinforcement provisions satisfy strength and detailing requirements.",
    )

    # Table 5.22 (Overall Design Check Summary)
    _pg_522 = (bridge.output_dict.get("design_results", {}) or {}).get("per_girder", {}) or {}

    def _vu_522(v, unit):
        s = _dfmt(v, nd=2)
        if not s:
            return ""
        u = (unit or "").strip()
        return (s + " " + u) if u else s

    def _ur_522(v):
        try:
            f = float(v)
        except (TypeError, ValueError):
            return ""
        s = f"{f:.2f}"
        return (r"\textcolor{red}{" + s + "}") if f > 1.0 else s

    def _lc_short(lc):
        return _tex(str(lc).strip())

    def _gov_lc_in_522(g, check_ids):
        gd = _pg_522.get(g) or {}
        best = None
        for _lc, _ld in (gd.get("per_lc") or {}).items():
            if str(_lc).lower().startswith("envelope"):
                continue
            for _chk in (_ld.get("checks") or []):
                if _chk.get("id") in check_ids:
                    _d = _chk.get("dcr") or 0.0
                    if best is None or _d > best[0]:
                        best = (_d, _lc)
        return _lc_short(best[1]) if best else "---"

    def _dcr_row(check_ids, fallback_unit=""):
        best = None
        for g, gd in _pg_522.items():
            if str(g).startswith("EB"):
                continue
            for chk in (gd.get("checks") or []):
                if chk.get("check_id") in check_ids:
                    d = chk.get("dcr") or 0.0
                    if best is None or d > best[0]:
                        best = (d, chk.get("demand"), chk.get("capacity"), chk.get("demand_unit") or "", chk.get("capacity_unit") or "", g)
        if best is not None:
            d, dem, cap, du, cu, g = best
            return (_gov_lc_in_522(g, check_ids), _vu_522(dem, du) or "---", _vu_522(cap, cu) or "---", _ur_522(d) or "---")
        best = None
        for g, gd in _pg_522.items():
            if str(g).startswith("EB"):
                continue
            for _lc, _ld in (gd.get("per_lc") or {}).items():
                if str(_lc).lower().startswith("envelope"):
                    continue
                for chk in (_ld.get("checks") or []):
                    if chk.get("id") in check_ids:
                        d = chk.get("dcr") or 0.0
                        if best is None or d > best[0]:
                            best = (d, chk.get("demand"), chk.get("capacity"), _lc)
        if best is None:
            return ("---", "---", "---", "---")
        d, dem, cap, _lc = best
        return (_lc_short(_lc), _vu_522(dem, fallback_unit) or "---", _vu_522(cap, fallback_unit) or "---", _ur_522(d) or "---")

    _cb_pairs_522 = bridge.get_cb_pairs()

    def _cb_row(force_type):
        best = None
        for pair in _cb_pairs_522:
            for member in ("diagonal", "chord"):
                cap = bridge.get_cb_capacity(pair, member, force_type)
                eff = bridge.get_cb_efficiency(pair, member, force_type)
                try:
                    ur = float(eff)
                except (TypeError, ValueError):
                    continue
                if best is None or ur > best[0]:
                    best = (ur, pair, member, cap)
        if best is None:
            return ("---", "---", "---", "---")
        ur, pair, member, cap = best
        gov = bridge.get_cb_gov_lc(pair, member, force_type) or "---"
        dem = f"{float(cap) * ur:.2f} kN" if cap else "---"
        cap_s = (cap + " kN") if cap else "---"
        return (gov, dem, cap_s, _ur_522(ur))

    def _cb_slender_row():
        best = None
        for pair in _cb_pairs_522:
            for member in ("diagonal", "chord"):
                s = bridge.get_cb_slenderness(pair, member)
                try:
                    sf = float(s)
                except (TypeError, ValueError):
                    continue
                lim = 400.0 if member == "chord" else 250.0
                ratio = sf / lim
                if best is None or ratio > best[0]:
                    best = (ratio, sf, lim)
        if best is None:
            return ("---", "---", "---", "---")
        ratio, sf, lim = best
        return ("---", f"{sf:.1f}", f"{lim:.0f}", _ur_522(ratio))

    def _row522(label, cells):
        c = [x if x else "---" for x in cells]
        return label + " & " + " & ".join(c) + rf" \\[{pad}pt]\hline"

    _deck_combo = (r"Basic ULS: " + _tex(f"{_dkv(KEY_DD_GAMMA_DL):g}DL + {_dkv(KEY_DD_GAMMA_LL):g}LL")) if _dk_has else "---"

    def _deck_row(dem_key, cap_key, unit, is_oh=False):
        if not _dk_has:
            return ("---", "---", "---", "---")
        if is_oh and not _dk_oh:
            return (_deck_combo, "N/A", "N/A", "N/A")
        dem = _dkv(dem_key)
        cap = _dkv(cap_key)
        ur = (dem / cap) if cap > 0 else None
        return (_deck_combo, f"{dem:.2f} {unit}", f"{cap:.2f} {unit}", _ur_522(ur))

    def _row522_msg(label, msg):
        return label + r" & \multicolumn{4}{c|}{" + msg + rf"}} \\[{pad}pt]\hline"

    _ed_type = ""
    for _k, _v in bridge.input_dict.items():
        if str(_k).startswith(KEY_MP_ED_TYPE) and _v:
            _ed_type = str(_v)
            break
    _ed_is_cb = "brac" in _ed_type.strip().lower()
    if _ed_is_cb:
        _ed_moment_row = _row522(r"End Diaphragm --- Moment", _cb_row("compression"))
        _ed_shear_row = _row522(r"End Diaphragm --- Shear", _cb_row("tension"))
    else:
        _ed_msg = r"Rolled / Welded section --- design to be added"
        _ed_moment_row = _row522_msg(r"End Diaphragm --- Moment", _ed_msg)
        _ed_shear_row = _row522_msg(r"End Diaphragm --- Shear", _ed_msg)

    def _gov_sls_frequent():
        best = None
        for _g, _gd in _pg_522.items():
            if str(_g).startswith("EB"):
                continue
            for _lc, _ld in (_gd.get("per_lc") or {}).items():
                if "frequent" not in str(_lc).lower():
                    continue
                _d = _ld.get("max_dcr") or 0.0
                if best is None or _d > best[0]:
                    best = (_d, _lc)
        return _tex(str(best[1]).strip()) if best else "Frequent SLS"

    _wk_lim = _dkv(KEY_DD_WK_LIMIT)
    _crack_cells = (
        (_gov_sls_frequent() if _dk_has else "---"),
        (f"{_dk_gov_wk:.3f} mm" if _dk_has else "---"),
        (f"{_wk_lim:.3f} mm" if _dk_has else "---"),
        (_ur_522(_dk_gov_wk / _wk_lim) if (_dk_has and _wk_lim > 0) else "---"),
    )

    _t522 = [
        _row522(r"Girder --- Moment", _dcr_row({1})),
        _row522(r"Girder --- Shear", _dcr_row({2})),
        _row522(r"Girder --- LTB (constr.)", _dcr_row({5})),
        _row522(r"Girder --- Deflection", _dcr_row({13, 14}, fallback_unit="mm")),
        _row522(r"Girder --- Stress", _dcr_row({11}, fallback_unit="MPa")),
        _row522(r"Girder --- Fatigue", _dcr_row({8, 9}, fallback_unit="MPa")),
        _row522(r"Transverse Shear (slab)", _dcr_row({16})),
        _row522(r"Crack Width (slab)", _crack_cells),
        _row522(r"Deck --- Flexure (sagging)", _deck_row(KEY_DD_M_ULS_SAG, KEY_DD_MU_BOT, "kN-m/m")),
        _row522(r"Deck --- Flexure (hogging)", _deck_row(KEY_DD_M_ULS_HOG, KEY_DD_MU_TOP, "kN-m/m")),
        _row522(r"Deck --- Cantilever Overhang", _deck_row(KEY_DD_M_ULS_OH, KEY_DD_MU_OH, "kN-m/m", is_oh=True)),
        _row522(r"Deck --- Punching Shear", _deck_row(KEY_DD_PUNCH_VED, KEY_DD_VRD_C_MPA, "MPa")),
        _row522(r"Deck --- One-Way Shear", _deck_row(KEY_DD_SHEAR_VED, KEY_DD_SHEAR_VRDC, "kN/m")),
        _row522(r"Cross Bracing --- Compression", _cb_row("compression")),
        _row522(r"Cross Bracing --- Tension", _cb_row("tension")),
        _row522(r"Cross Bracing --- Slenderness", _cb_slender_row()),
        _ed_moment_row,
        _ed_shear_row,
    ]
    t522_table = build_longtable(
        col_spec="|C{3.4cm}|L{4.5cm}|C{2.3cm}|C{2.3cm}|>{\\centering\\arraybackslash}p{1.6cm}|",
        caption="Overall Design Check Summary --- All Members",
        header_cells=[r"\textbf{Member / Check}", r"\textbf{Governing Load Combo}", r"\textbf{Demand}", r"\textbf{Capacity}", r"\textbf{UR}"],
        body_tex="\n".join(_t522),
        note="Note: UR = Demand / Capacity. All values $\\leq 1.0$ indicate passing checks. The governing check for each component is highlighted in the individual design check sections above.",
    )

    ur_chart_block = _fig_embed(
        fig_paths.get("ur_summary"),
        "Component Utilization Ratio (UR = Demand / Capacity) Summary across Primary Bridge Elements. Red dashed line indicates the code limit threshold (UR = 1.0).",
        width=r"0.86\textwidth",
    )

    return (
        r"""
\chapter{Design Checks}

This section presents all structural design checks performed by OsdagBridge. For each member, the demand from the governing load combination, the code-based capacity, and the utilization ratio are tabulated. All checks reference IS 800:2007 and IRC 22:2014 unless stated otherwise.

\section{Plate Girder Design}
\label{sec:plate-girder}
"""
        + t51_table
        + t52_table
        + t53_table
        + t54_table
        + t55_table
        + t56_table
        + t57_table
        + t58_block
        + t59_table
        + t510_table
        + t511_table
        + t512_table
        + t513_table
        + t514_table
        + t515_table
        + t516_table
        + r"""
% ===========================
\section{Deck Slab Design}
\label{sec:deck-design}
% ===========================

The reinforced concrete deck slab is designed per IRC~112:2011 (flexure, shear, crack width) and IRC~22:2014 (composite construction). Wheel loads are distributed using Pigeaud's method. The deck is checked for flexure in the transverse and longitudinal directions, punching shear, one-way (beam) shear, crack width, and reinforcement detailing.
"""
        + t517a_table
        + t517b_table
        + t517c_table
        + t517d_table
        + t517e_table
        + t517f_table
        + t517g_table
        + r"""
% ===========================
\section{Cross Bracing Design}
\label{sec:cross-bracing}
% ===========================

Cross bracing between adjacent plate girders provides lateral stability during construction, resists transverse loads (wind, seismic, braking) in service, and prevents lateral torsional buckling of the girders. Members are designed per IS~800:2007 Cl.~7 (compression) and Cl.~6 (tension). Forces are derived from the grillage model under the governing load combination (DL + LL + WL).
"""
        + t518_table
        + t519_table
        + t520_table
        + r"""
% ===========================
\section{End Diaphragm Design}
\label{sec:end-diaphragm}
% ===========================

End diaphragms at the supports transfer transverse loads to the bearings, restrain the bottom flanges against lateral displacement, and maintain the girder cross-section geometry during construction and in service. They are designed per IS~800:2007 and IRC~24:2010 Cl.~507.
"""
        + t521a_table
        + t521b_table
        + t521c_table
        + r"""
% ===========================
\section{Overall Design Check Summary}
\label{sec:overall-summary}
% ===========================
"""
        + t522_table
        + "\n\\vspace{0.8em}\n"
        + ur_chart_block
    )
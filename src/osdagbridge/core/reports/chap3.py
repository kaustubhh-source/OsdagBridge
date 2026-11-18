# =============================================================================
# Chapter 3: Loads and Load Combinations
# Refactored to use centralized styles.py and separate Vehicle / Footpath tables.
# =============================================================================

from osdagbridge.core.utils.common import (
    KEY_CARRIAGEWAY_WIDTH,
    KEY_CARRIAGEWAY_WIDTH,
    KEY_CB_LOAD,
    KEY_FOOTPATH,
    KEY_LL_CUSTOM_VEHICLES,
    KEY_LL_FOOTPATH_PRESSURE_MODE,
    KEY_LL_FOOTPATH_PRESSURE_VALUE,
    KEY_LL_IRC_70R_BOGIE,
    KEY_LL_IRC_70R_TRACKED,
    KEY_LL_IRC_70R_WHEELED,
    KEY_LL_IRC_AA_TRACKED,
    KEY_LL_IRC_AA_WHEELED,
    KEY_LL_IRC_CLASS_A,
    KEY_LL_IRC_CLASS_FATIGUE,
    KEY_LL_IRC_CLASS_SV,
    KEY_MATERIAL_DECK_DENSITY,
    KEY_MATERIAL_GIRDER_DENSITY,
    KEY_PL_SELF_WEIGHT_FACTOR,
    KEY_RL_LOAD_VALUE,
    KEY_SL_DAMPING,
    KEY_SL_DEAD_LOAD_MODE,
    KEY_SL_DEAD_LOAD_VALUE,
    KEY_SL_HORIZONTAL_COEFF,
    KEY_SL_IMPORTANCE_FACTOR,
    KEY_SL_LIVE_LOAD_MODE,
    KEY_SL_LIVE_LOAD_VALUE,
    KEY_SL_SEISMIC_ZONE,
    KEY_SL_SOIL_TYPE,
    KEY_SL_SPECTRAL_COEFF,
    KEY_SL_TIME_PERIOD,
    KEY_SL_VERTICAL_COEFF,
    KEY_SL_ZONE_FACTOR,
    KEY_SPAN,
    KEY_TL_BRIDGE_TEMP_MAX,
    KEY_TL_BRIDGE_TEMP_MIN,
    KEY_TL_HIGHEST_MAX_TEMP,
    KEY_TL_LOWEST_MIN_TEMP,
    KEY_TL_TEMP_FALL,
    KEY_TL_TEMP_RISE,
    KEY_TS_FOOTPATH_WIDTH,
    KEY_WC_LD_LANE_TABLE_COUNT,
    KEY_WC_MATERIAL,
    KEY_WC_THICKNESS,
    KEY_WL_AVG_EXPOSED_HEIGHT,
    KEY_WL_BASIC_WIND_SPEED,
    KEY_WL_HOURLY_MEAN_WIND,
    KEY_WL_HOURLY_WIND_PRESSURE,
    KEY_WL_LONGITUDINAL_WIND_FORCE,
    KEY_WL_TERRAIN_TYPE,
    KEY_WL_TRANSVERSE_WIND_FORCE,
    KEY_WL_VERTICAL_WIND_FORCE,
)

from osdagbridge.core.reports.report_utils import _tex, _render_value
from osdagbridge.core.reports.styles import TABLE, build_longtable


def _fmt_num(val, nd=2, fallback="---"):
    if val in (None, ""):
        return fallback
    try:
        return f"{float(val):.{nd}f}"
    except (TypeError, ValueError):
        return _tex(val)


def ch3_loads(input_dict):
    pad = f"\\\\[{TABLE.row_pad_pt}pt]\n\\hline\n"

    # 1. Vehicle Live Load parameters
    vehicles = []
    if input_dict.get(KEY_LL_IRC_CLASS_A):
        vehicles.append("Class A")
    if input_dict.get(KEY_LL_IRC_70R_WHEELED):
        vehicles.append("Class 70R (Wheeled)")
    if input_dict.get(KEY_LL_IRC_70R_TRACKED):
        vehicles.append("Class 70R (Tracked)")
    if input_dict.get(KEY_LL_IRC_AA_WHEELED):
        vehicles.append("Class AA (Wheeled)")
    if input_dict.get(KEY_LL_IRC_AA_TRACKED):
        vehicles.append("Class AA (Tracked)")
    if input_dict.get(KEY_LL_IRC_CLASS_SV):
        vehicles.append("Class SV")
    if input_dict.get(KEY_LL_IRC_70R_BOGIE):
        vehicles.append("Class 70R (Bogie)")
    if input_dict.get(KEY_LL_IRC_CLASS_FATIGUE):
        vehicles.append("Class Fatigue")

    custom = input_dict.get(KEY_LL_CUSTOM_VEHICLES)
    if custom and isinstance(custom, list):
        for c in custom:
            if isinstance(c, dict) and c.get("name"):
                vehicles.append(c["name"])
            elif isinstance(c, str):
                vehicles.append(c)

    vehicles_str = ", ".join(vehicles) if vehicles else "IRC Class A / Class 70R (Default)"

    from osdagbridge.core.utils.codes.irc6_2017 import IRC6_2017

    span = input_dict.get(KEY_SPAN)
    impact_factor_str = "---"
    if span not in (None, ""):
        try:
            span_m = float(span)
            factors = []
            if input_dict.get(KEY_LL_IRC_CLASS_A) or not vehicles:
                im_a = IRC6_2017.cl_208_2_impact_factor(span_m)
                factors.append(f"Class A: {1.0 + im_a:.3f}")
            is_wheeled_heavy = (
                input_dict.get(KEY_LL_IRC_70R_WHEELED)
                or input_dict.get(KEY_LL_IRC_AA_WHEELED)
                or input_dict.get(KEY_LL_IRC_70R_BOGIE)
            )
            is_tracked_heavy = (
                input_dict.get(KEY_LL_IRC_70R_TRACKED)
                or input_dict.get(KEY_LL_IRC_AA_TRACKED)
            )
            if is_wheeled_heavy or is_tracked_heavy or not vehicles:
                im_aa = IRC6_2017.cl_208_3_impact_factor(span_m)
                factors.append(f"Class AA/70R: {1.0 + im_aa:.3f}")
            if factors:
                impact_factor_str = ", ".join(factors)
        except Exception:
            impact_factor_str = "---"
            
    lanes = input_dict.get(KEY_WC_LD_LANE_TABLE_COUNT) or (IRC6_2017.table_6(float(input_dict[KEY_CARRIAGEWAY_WIDTH])) if input_dict.get(KEY_CARRIAGEWAY_WIDTH) not in (None, "") else None)
    if lanes in (None, ""):
        cw_val = input_dict.get(KEY_CARRIAGEWAY_WIDTH)
        if cw_val not in (None, ""):
            try:
                lanes = IRC6_2017.table_6(float(cw_val))
            except Exception:
                lanes = None

    lanes_str = str(lanes) if lanes not in (None, "") else "---"
    braking_force_str = "---"
    if lanes not in (None, ""):
        try:
            lanes_int = int(lanes)
            braking_force_t = IRC6_2017.cl_211_2_braking_force(lanes_int)
            braking_force_kN = braking_force_t * 9.81
            braking_force_str = f"{braking_force_kN:.2f} ({braking_force_t:.2f} tonnes)"
        except Exception:
            braking_force_str = "---"

    # 2. Separate Footpath Live Load parameters (IRC 6 Cl. 206.1)
    fp_config = str(input_dict.get(KEY_FOOTPATH, "None") or "None").strip()
    has_footpath = fp_config.lower() not in ("", "none", "no")
    fp_width_raw = input_dict.get(KEY_TS_FOOTPATH_WIDTH)
    fp_mode_raw = str(input_dict.get(KEY_LL_FOOTPATH_PRESSURE_MODE, "") or "").strip()
    fp_val_raw = input_dict.get(KEY_LL_FOOTPATH_PRESSURE_VALUE)

    fp_pressure_num = None
    if fp_val_raw not in (None, ""):
        try:
            fp_pressure_num = float(fp_val_raw)
        except (TypeError, ValueError):
            fp_pressure_num = None

    if fp_pressure_num is None and has_footpath:
        try:
            fp_pressure_num = float(IRC6_2017.cl_206_1_footway_load())
        except Exception:
            fp_pressure_num = 4.0  # IRC 6 Cl. 206.1 standard pedestrian load

    if has_footpath:
        fp_mode_disp = _tex(fp_mode_raw) if fp_mode_raw else "Automatic (IRC 6 Cl. 206.1)"
        fp_width_disp = _fmt_num(fp_width_raw, nd=2)
        fp_press_disp = f"{fp_pressure_num:.2f}" if fp_pressure_num is not None else "---"
        try:
            w_f = float(fp_width_raw)
            fp_line_disp = f"{fp_pressure_num * w_f:.2f}" if fp_pressure_num is not None else "---"
        except (TypeError, ValueError):
            fp_line_disp = "---"
    else:
        fp_mode_disp = "Not Applicable"
        fp_width_disp = "0.00"
        fp_press_disp = "0.00"
        fp_line_disp = "0.00"

    # 3. Wind Load (WL)
    vz_val = input_dict.get(KEY_WL_HOURLY_MEAN_WIND)
    pz_val = input_dict.get(KEY_WL_HOURLY_WIND_PRESSURE)
    if not vz_val or not pz_val:
        try:
            _vb = input_dict.get(KEY_WL_BASIC_WIND_SPEED) or input_dict.get("wind_speed")
            _h = input_dict.get(KEY_WL_AVG_EXPOSED_HEIGHT)
            _ter = {
                "Plain Terrain": "plain",
                "Terrain with Obstructions": "obstructed",
            }.get(str(input_dict.get(KEY_WL_TERRAIN_TYPE, "")).strip(), "plain")
            _res = IRC6_2017.table_12(float(_h), _ter, float(_vb))
            if not vz_val:
                vz_val = _res.get("Vz")
            if not pz_val:
                pz_val = _res.get("Pz")
        except Exception:
            pass

    # 4. Seismic Load (EL)
    sl_zone_factor = input_dict.get(KEY_SL_ZONE_FACTOR)
    sl_spectral = input_dict.get(KEY_SL_SPECTRAL_COEFF)
    sl_ah = input_dict.get(KEY_SL_HORIZONTAL_COEFF)
    sl_av = input_dict.get(KEY_SL_VERTICAL_COEFF)
    if not sl_ah or not sl_zone_factor:
        try:
            _zone = input_dict.get(KEY_SL_SEISMIC_ZONE) or input_dict.get("seismic_zone")
            _zmap = {"1": "I", "2": "II", "3": "III", "4": "IV", "5": "V"}
            _z = str(_zone).strip().upper()
            if _z.isdigit():
                _z = _zmap.get(_z)
            _smap = {"Type I – Rocky or Hard": 1, "Type II – Medium Soil": 2, "Type III – Soft Soil": 3}
            _st = _smap.get(str(input_dict.get(KEY_SL_SOIL_TYPE, "")), 1)
            _tp = input_dict.get(KEY_SL_TIME_PERIOD)
            _damp = input_dict.get(KEY_SL_DAMPING) or "5"
            _dl_v = input_dict.get(KEY_SL_DEAD_LOAD_VALUE)
            _ll_v = input_dict.get(KEY_SL_LIVE_LOAD_VALUE)
            _dead = float(_dl_v) if str(input_dict.get(KEY_SL_DEAD_LOAD_MODE, "")) == "Custom" and _dl_v else 0.0
            _live = float(_ll_v) if str(input_dict.get(KEY_SL_LIVE_LOAD_MODE, "")) == "Custom" and _ll_v else 0.0
            _res = IRC6_2017.cl_218_5_1(
                zone=f"Zone {_z}",
                soil_type=_st,
                dead_load_kN=_dead,
                live_load_kN=_live,
                period_T=float(_tp) if _tp else None,
                damping_percent=float(_damp),
            )
            if not sl_zone_factor:
                sl_zone_factor = _res.get("Z")
            if not sl_spectral:
                sl_spectral = _res.get("Sa_g_adjusted")
            if not sl_ah:
                sl_ah = _res.get("Ah")
            if not sl_av:
                sl_av = round(_res.get("Ah", 0) * 2 / 3, 4)
        except Exception:
            pass

    # 5. Temperature Load (TL)
    tl_temp_min = input_dict.get(KEY_TL_BRIDGE_TEMP_MIN)
    tl_temp_max = input_dict.get(KEY_TL_BRIDGE_TEMP_MAX)
    tl_rise = input_dict.get(KEY_TL_TEMP_RISE)
    tl_fall = input_dict.get(KEY_TL_TEMP_FALL)
    if not tl_temp_min or not tl_temp_max:
        try:
            _tmax = input_dict.get(KEY_TL_HIGHEST_MAX_TEMP) or input_dict.get("shade_temp_max")
            _tmin = input_dict.get(KEY_TL_LOWEST_MIN_TEMP) or input_dict.get("shade_temp_min")
            if _tmax and _tmin:
                _res = IRC6_2017.cl_215_2_effective_bridge_temperature(
                    float(_tmax), float(_tmin), "metallic", False
                )
                _bt_min = _res.get("T_min", 0)
                _bt_max = _res.get("T_max", 0)
                _mean = (_bt_max + _bt_min) / 2.0
                tl_temp_min = f"{_bt_min:.2f}"
                tl_temp_max = f"{_bt_max:.2f}"
                tl_rise = f"{_bt_max - _mean:.2f}"
                tl_fall = f"{_mean - _bt_min:.2f}"
        except Exception:
            pass

    # 6. Load Combinations (Table 3.8)
    _LOAD_LABEL_MAP = {
        "dead_load": "DL",
        "surfacing": "SIDL",
        "live_load": "LL",
        "wind_load": "WL",
        "thermal_load": "TL",
        "vehicle_collision": "VC",
        "barge_impact": "BI",
        "floating_bodies": "FB",
        "seismic": "EQ",
    }

    def _fmt_factors(factors):
        parts = []
        for load, val in factors.items():
            label = _LOAD_LABEL_MAP.get(load, load.upper())
            if isinstance(val, dict):
                add = val.get("adding")
                rel = val.get("relieving")
                add_s = f"{add:.2f}" if add is not None else "--"
                rel_s = f"{rel:.2f}" if rel is not None else "--"
                parts.append(f"{label}({add_s}/{rel_s})")
            else:
                if val is None:
                    continue
                parts.append(f"{label}({val:.2f})")
        return " + ".join(parts)

    uls_combos = IRC6_2017.uls_load_combinations()
    sls_combos = IRC6_2017.sls_load_combinations()
    lc_rows = []
    for i, combo in enumerate(uls_combos, start=1):
        lc_rows.append(f"ULS-{i:02d} & Ultimate Limit State & {_fmt_factors(combo['factors'])} {pad}")
    for i, combo in enumerate(sls_combos, start=1):
        lc_rows.append(f"SLS-{i:02d} & Serviceability Limit State & {_fmt_factors(combo['factors'])} {pad}")

    # Build standardized tables with repeating headers and Unit columns
    t_dl_body = (
        f"\\textnormal{{Steel Self-Weight Density}} & {_render_value(input_dict, KEY_MATERIAL_GIRDER_DENSITY)} & kN/m\\textsuperscript{{3}} {pad}"
        f"\\textnormal{{Concrete Deck Density}} & {_render_value(input_dict, KEY_MATERIAL_DECK_DENSITY)} & kN/m\\textsuperscript{{3}} {pad}"
        f"\\textnormal{{Self-Weight Factor}} & {_render_value(input_dict, KEY_PL_SELF_WEIGHT_FACTOR)} & --- {pad}"
    )
    t_dl = build_longtable(
        col_spec="|L{5.8cm}|L{6.5cm}|C{2.5cm}|",
        caption="Dead Load -- Self Weight",
        header_cells=[r"\textbf{Parameter}", r"\textbf{Value}", r"\textbf{Unit}"],
        body_tex=t_dl_body,
    )

    t_dw_body = (
        f"\\textnormal{{Wearing Course Material}} & {_render_value(input_dict, KEY_WC_MATERIAL)} & --- {pad}"
        f"\\textnormal{{Wearing Course Thickness}} & {_render_value(input_dict, KEY_WC_THICKNESS)} & mm {pad}"
        f"\\textnormal{{Crash Barrier Load (per barrier)}} & {_render_value(input_dict, KEY_CB_LOAD)} & kN/m {pad}"
        f"\\textnormal{{Railing Load\\sdstar{{}}}} & {_render_value(input_dict, KEY_RL_LOAD_VALUE)} & kN/m {pad}"
    )
    t_dw = build_longtable(
        col_spec="|L{5.8cm}|L{6.5cm}|C{2.5cm}|",
        caption="Dead Load for Surfacing (DW)",
        header_cells=[r"\textbf{Parameter}", r"\textbf{Value}", r"\textbf{Unit}"],
        body_tex=t_dw_body,
    )

    # Separate Table A: Vehicle Live Loads
    t_veh_body = (
        f"\\textnormal{{Design Traffic Lanes (IRC 5 Cl. 104.3.1)}} & {_tex(lanes_str)} & lanes {pad}"
        f"\\textnormal{{IRC 6 Design Vehicles Considered}} & {_tex(vehicles_str)} & --- {pad}"
        f"\\textnormal{{Dynamic Impact Factor (IRC 6 Cl. 208)}} & {_tex(impact_factor_str)} & factor {pad}"
        f"\\textnormal{{Longitudinal Braking Force (IRC 6 Cl. 211)}} & {_tex(braking_force_str)} & kN {pad}"
    )
    t_veh = build_longtable(
        col_spec="|L{5.8cm}|L{6.5cm}|C{2.5cm}|",
        caption="Vehicle Live Loads (LL --- Vehicular)",
        header_cells=[r"\textbf{Parameter}", r"\textbf{Value}", r"\textbf{Unit}"],
        body_tex=t_veh_body,
        note="Note: Vehicular live loads, multi-lane reduction factors, and dynamic impact allowances applied per IRC 6:2017 Cl. 204 and Cl. 208.",
    )

    # Separate Table B: Footpath Live Loads
    t_fp_body = (
        f"\\textnormal{{Footpath Configuration}} & {_tex(fp_config)} & --- {pad}"
        f"\\textnormal{{Footpath Clear Width}} & {fp_width_disp} & m {pad}"
        f"\\textnormal{{Load Specification Mode}} & {fp_mode_disp} & --- {pad}"
        f"\\textnormal{{Footpath Live Load Intensity}} & {fp_press_disp} & kN/m\\textsuperscript{{2}} {pad}"
        f"\\textnormal{{Equivalent Footpath Line Load (per side)}} & {fp_line_disp} & kN/m {pad}"
    )
    t_fp = build_longtable(
        col_spec="|L{5.8cm}|L{6.5cm}|C{2.5cm}|",
        caption="Footpath Live Loads (LL --- Pedestrian)",
        header_cells=[r"\textbf{Parameter}", r"\textbf{Value}", r"\textbf{Unit}"],
        body_tex=t_fp_body,
        note="Note: Pedestrian live load intensity evaluated separately from vehicular carriageway loading per IRC 6:2017 Cl. 206.1.",
    )

    t_wl_body = (
        f"\\textnormal{{Basic Wind Speed, $V_b$ (Project Location)}} & {_render_value(input_dict, 'wind_speed')} & m/s {pad}"
        f"\\textnormal{{Terrain Category}} & {_render_value(input_dict, KEY_WL_TERRAIN_TYPE)} & --- {pad}"
        f"\\textnormal{{Average Exposed Height, $H$}} & {_render_value(input_dict, KEY_WL_AVG_EXPOSED_HEIGHT)} & m {pad}"
        f"\\textnormal{{Hourly Mean Wind Speed, $V_z$}} & {_fmt_num(vz_val, nd=2)} & m/s {pad}"
        f"\\textnormal{{Hourly Wind Pressure, $P_z$}} & {_fmt_num(pz_val, nd=2)} & N/m\\textsuperscript{{2}} {pad}"
        f"\\textnormal{{Transverse Wind Force}} & {_render_value(input_dict, KEY_WL_TRANSVERSE_WIND_FORCE)} & kN {pad}"
        f"\\textnormal{{Longitudinal Wind Force}} & {_render_value(input_dict, KEY_WL_LONGITUDINAL_WIND_FORCE)} & kN {pad}"
        f"\\textnormal{{Vertical Wind Force}} & {_render_value(input_dict, KEY_WL_VERTICAL_WIND_FORCE)} & kN {pad}"
    )
    t_wl = build_longtable(
        col_spec="|L{5.8cm}|L{6.5cm}|C{2.5cm}|",
        caption="Wind Load (WL) --- per IRC 6",
        header_cells=[r"\textbf{Parameter}", r"\textbf{Value}", r"\textbf{Unit}"],
        body_tex=t_wl_body,
    )

    t_el_body = (
        f"\\textnormal{{Seismic Zone (Project Location)}} & {_render_value(input_dict, 'seismic_zone')} & --- {pad}"
        f"\\textnormal{{Zone Factor, $Z$}} & {_fmt_num(sl_zone_factor, nd=4)} & --- {pad}"
        f"\\textnormal{{Importance Factor, $I$}} & {_render_value(input_dict, KEY_SL_IMPORTANCE_FACTOR)} & --- {pad}"
        f"\\textnormal{{Type of Soil}} & {_render_value(input_dict, KEY_SL_SOIL_TYPE)} & --- {pad}"
        f"\\textnormal{{Spectral Acceleration Coefficient, $S_a/g$}} & {_fmt_num(sl_spectral, nd=4)} & --- {pad}"
        f"\\textnormal{{Horizontal Seismic Coefficient, $A_h$}} & {_fmt_num(sl_ah, nd=4)} & --- {pad}"
        f"\\textnormal{{Vertical Seismic Coefficient, $A_v$}} & {_fmt_num(sl_av, nd=4)} & --- {pad}"
    )
    t_el = build_longtable(
        col_spec="|L{5.8cm}|L{6.5cm}|C{2.5cm}|",
        caption="Earthquake Load (EL) --- per IRC 6",
        header_cells=[r"\textbf{Parameter}", r"\textbf{Value}", r"\textbf{Unit}"],
        body_tex=t_el_body,
    )

    t_tl_body = (
        f"\\textnormal{{Maximum Shade Temperature}} & {_render_value(input_dict, 'shade_temp_max')} & $^\\circ$C {pad}"
        f"\\textnormal{{Minimum Shade Temperature}} & {_render_value(input_dict, 'shade_temp_min')} & $^\\circ$C {pad}"
        f"\\textnormal{{Effective Bridge Temp. Range}} & {_fmt_num(tl_temp_min, nd=2)} to {_fmt_num(tl_temp_max, nd=2)} & $^\\circ$C {pad}"
        f"\\textnormal{{Temperature Rise / Fall for Design}} & +{_fmt_num(tl_rise, nd=2)} / \\textminus{{}}{_fmt_num(tl_fall, nd=2)} & $^\\circ$C {pad}"
    )
    t_tl = build_longtable(
        col_spec="|L{5.8cm}|L{6.5cm}|C{2.5cm}|",
        caption="Temperature Load (TL) --- per IRC 6",
        header_cells=[r"\textbf{Parameter}", r"\textbf{Value}", r"\textbf{Unit}"],
        body_tex=t_tl_body,
    )

    t_lc = build_longtable(
        col_spec="|C{2.4cm}|L{4.2cm}|L{8.2cm}|",
        caption="Load Combinations (IRC 6:2017)",
        header_cells=[r"\textbf{Combo ID}", r"\textbf{Limit State}", r"\textbf{Load Factors \& Cases}"],
        body_tex="".join(lc_rows),
        compact=True,
        note="Note: All IRC 6 load combinations are auto-generated by OsdagBridge. User-defined custom combinations, if any, are appended.",
    )

    return (
        r"""
\chapter{Loads and Load Combinations}

This section summarizes all permanent, transient, and environmental loads applied to the bridge, with vehicular and pedestrian footpath live loads tabulated separately per IRC 6:2017.

"""
        + t_dl
        + t_dw
        + t_veh
        + t_fp
        + t_wl
        + t_el
        + t_tl
        + t_lc
    )
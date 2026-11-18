# =============================================================================
# OsdagBridge — Report Generator  
# Refactored to use centralized styles.py (Single Source of Truth) and
# programmatic Matplotlib charts (report_charts.py) for Sections 5.5 & Ch. 7.
# =============================================================================

import os, shutil, logging, datetime, tempfile, subprocess
from dataclasses import dataclass, field
from typing import Optional, List

from osdagbridge.core.utils.common import (
    KEY_DESIGN_MODE,
    KEY_SPAN,
    KEY_TL_BRIDGE_TEMP_MAX,
    KEY_TL_BRIDGE_TEMP_MIN,
    KEY_TL_HIGHEST_MAX_TEMP,
    KEY_TL_LOWEST_MIN_TEMP,
    KEY_TL_TEMP_FALL,
    KEY_TL_TEMP_RISE
)

from osdagbridge.core.reports.report_utils import _tex
from osdagbridge.core.reports.styles import (
    PAGE,
    get_color_definitions,
    get_geometry_options,
    get_table_defaults,
)
from osdagbridge.core.reports.report_charts import (
    generate_material_quantity_charts,
    generate_ur_summary_chart,
)
from .executive_summary import executive_summary
from .chap1 import ch1_project_info
from .chap2 import ch2_input_parameters
from .chap3 import ch3_loads
from .chap4 import ch4_analysis
from .chap5 import ch5_design_checks
from .chap6 import ch6_drawings
from .chap7 import ch7_quantities
from .chap8 import ch8_design_log
from .chap9 import references

logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════════════════════════
# PREAMBLE (Driven by styles.py Single Source of Truth)
# ═══════════════════════════════════════════════════════════════════════════════

def preamble(project_name, job_number, report_date, report_version='Rev 0'):
    pn = _tex(project_name)
    jn = _tex(job_number)
    rd = _tex(report_date)
    rv = _tex(report_version)
    return (
        r"\documentclass[" + str(PAGE.font_size_pt) + r"pt," + PAGE.paper_size + r"]{report}" + "\n\n"
        r"% Packages" + "\n"
        r"\usepackage[" + get_geometry_options() + r"]{geometry}" + "\n"
        r"""\usepackage{graphicx}
\usepackage{amsmath}
\usepackage{amssymb}
\usepackage{booktabs}
\usepackage{array}
\usepackage{tabularx}
\usepackage{float}
\usepackage{fancyhdr}
\usepackage[hidelinks]{hyperref}
\usepackage[table]{xcolor}
\usepackage{setspace}
\usepackage{enumitem}
\usepackage{caption}

\captionsetup{
    labelfont=bf,
    justification=raggedright,
    singlelinecheck=false,
    format=plain
}
\usepackage{subcaption}
\usepackage{multirow}
\usepackage{colortbl}
\usepackage{longtable}
\setlength{\LTleft}{\fill}
\setlength{\LTright}{\fill}
\usepackage{titlesec}
\usepackage{titletoc}
\usepackage{lastpage}
\usepackage{makecell}
\usepackage{etoolbox}
\usepackage{needspace}

\numberwithin{table}{chapter}
\numberwithin{figure}{chapter}
"""
        + get_table_defaults()
        + "\n"
        + get_color_definitions()
        + r"""
\fancypagestyle{main}{
  \fancyhf{}
  \fancyhead[L]{""" + pn + r""" $|$ """ + jn + r"""}
  \fancyhead[R]{""" + rd + r""" $|$ """ + rv + r"""}
  \fancyfoot[L]{Osdag $|$ FOSSEE $|$ Indian Institute of Technology Bombay}
  \fancyfoot[R]{Page \thepage\ of \pageref{LastPage}}
  \renewcommand{\headrule}{\color{osdagGreen}\hrule width\headwidth height 1pt \vspace{2pt}}
  \renewcommand{\footrule}{%
    \ifbool{hasSDonPage}{%
      \vspace{-20pt}%
      \hbox to \headwidth{\textcolor{black}{\footnotesize\textit{* Software default value}}\hfil}%
      \vspace{4pt}%
    }{%
      \vspace{-8pt}%
    }%
    \color{osdagGreen}\hrule width\headwidth height 1pt \vspace{6pt}%
  }
}
\fancypagestyle{plain}{
  \fancyhf{}
  \fancyhead[L]{""" + pn + r""" $|$ """ + jn + r"""}
  \fancyhead[R]{""" + rd + r""" $|$ """ + rv + r"""}
  \fancyfoot[L]{Osdag $|$ FOSSEE $|$ Indian Institute of Technology Bombay}
  \fancyfoot[R]{Page \thepage\ of \pageref{LastPage}}
  \renewcommand{\headrule}{\color{osdagGreen}\hrule width\headwidth height 1pt \vspace{2pt}}
  \renewcommand{\footrule}{%
    \ifbool{hasSDonPage}{%
      \vspace{-20pt}%
      \hbox to \headwidth{\textcolor{black}{\footnotesize\textit{* Software default value}}\hfil}%
      \vspace{4pt}%
    }{%
      \vspace{-8pt}%
    }%
    \color{osdagGreen}\hrule width\headwidth height 1pt \vspace{6pt}%
  }
}
\fancypagestyle{firstpage}{
  \fancyhf{}
  \renewcommand{\headrulewidth}{0pt}
  \fancyfoot[L]{Osdag $|$ FOSSEE $|$ Indian Institute of Technology Bombay}
  \fancyfoot[R]{Page \thepage\ of \pageref{LastPage}}
  \renewcommand{\footrule}{\vspace{-8pt}\color{osdagGreen}\hrule width\headwidth height 1pt \vspace{6pt}}
}
\pagestyle{main}
\setstretch{""" + str(PAGE.line_stretch) + r"""}

% Custom Commands
\newcommand{\placeholder}[1]{\textit{\textless #1\textgreater}}
\newcommand{\todo}[1]{\colorbox{yellow}{TODO: #1}}
\newcolumntype{L}[1]{>{\raggedright\arraybackslash}p{#1}}
\newcolumntype{C}[1]{>{\centering\arraybackslash}p{#1}}
\newcolumntype{R}[1]{>{\raggedleft\arraybackslash}p{#1}}

% Software-default asterisk
\newcommand{\sdstar}{\textsuperscript{*}}
\newbool{hasSDonPage}
\boolfalse{hasSDonPage}
\newcommand{\markSD}{\global\booltrue{hasSDonPage}}
\renewcommand{\sdstar}{\textsuperscript{*}\markSD{}}
\AddToHook{shipout/before}{\global\boolfalse{hasSDonPage}}

\title{\Large\textbf{OsdagBridge} \\ \normalsize Open Source Software for Steel Girder Bridge Design \\ \vspace{2cm} \large Design Report}
\author{}
\date{}

\begin{document}
"""
    )


# ═══════════════════════════════════════════════════════════════════════════════
# TITLE PAGE
# ═══════════════════════════════════════════════════════════════════════════════

def title_page(m, osdag_logo, org_logo):
    if osdag_logo:
        lhs = r'\includegraphics[width=\linewidth,keepaspectratio]{' + osdag_logo.replace('\\', '/') + r'}'
    else:
        lhs = r'\textit{(Osdag Logo)}'

    if org_logo:
        rhs = r'\includegraphics[width=\linewidth,height=2.2cm,keepaspectratio]{' + org_logo.replace('\\', '/') + r'}'
    else:
        rhs = r''

    logos_tex = r"""\noindent
\begin{minipage}[c]{0.6\textwidth}
\raggedright
""" + lhs + r"""
\end{minipage}%
\hfill
\begin{minipage}[c]{0.35\textwidth}
\raggedleft
""" + rhs + r"""
\end{minipage}
\\[1cm]
"""

    return r"""
\begin{titlepage}
\thispagestyle{firstpage}
\centering
\vspace*{1.5cm}
""" + logos_tex + r"""
{\Huge \textbf{OsdagBridge}}\\[0.3cm]
{\large Open Source Software for Steel Girder Bridge Design}\\[1.5cm]
{\Large Design Report}\\[1.5cm]
\begin{tabular}{|L{4cm}|L{10cm}|}
\hline
\textbf{Project Name} & """ + _tex(m.project_name) + r""" \\
\hline
\textbf{Project Location} & """ + _tex(m.project_location) + r""" \\
\hline
\textbf{Author / Designer} & """ + _tex(m.designer) + r""" \\
\hline
\textbf{Reviewer} & """ + _tex(m.reviewer) + r""" \\
\hline
\textbf{Organization} & """ + _tex(m.company) + r""" \\
\hline
\textbf{Client Name and Organization} & """ + _tex(m.client) + r""" \\
\hline
\textbf{Job Number} & """ + _tex(m.job_number) + r""" \\
\hline
\textbf{Date} & """ + _tex(m.report_date) + r""" \\
\hline
\textbf{Report Version} & """ + (_tex(m.subtitle) if m.subtitle else '') + r""" \\
\hline
\end{tabular}
\end{titlepage}
"""


# ═══════════════════════════════════════════════════════════════════════════════
# TOC
# ═══════════════════════════════════════════════════════════════════════════════

def toc_section():
    return r"""
% Chapter / TOC Formatting
\titleformat{\chapter}[block]
  {\normalfont\Large\bfseries\centering}{\thechapter}{1em}{}
\titlespacing*{\chapter}{0pt}{0pt}{10pt}
\setcounter{tocdepth}{2}

% TOC styling using titletoc
\titlecontents{chapter}[1.5em]
  {\normalfont\vspace{2pt}}
  {\contentslabel{1.5em}}
  {\hspace*{-1.5em}}
  {\hfill\contentspage}

\titlecontents{section}[3.8em]
  {\normalfont}
  {\contentslabel{2.3em}}
  {\hspace*{-2.3em}}
  {\hfill\contentspage}

\titlecontents{subsection}[7.0em]
  {\normalfont}
  {\contentslabel{3.2em}}
  {\hspace*{-3.2em}}
  {\hfill\contentspage}

\newpage
\renewcommand{\contentsname}{\centering\Large\bfseries Table of Contents}
\tableofcontents
"""


# ---------------------------------------------------------------------------
# Public data-classes
# ---------------------------------------------------------------------------

@dataclass
class ReportMetadata:
    project_name: str
    project_location: str
    designer: str
    client: str
    company: str
    group_name: str = ''
    subtitle: str = ''
    job_number: str = ''
    additional_comments: str = ''
    logo_path: Optional[str] = None
    report_date: str = ''
    reviewer: str = ''


@dataclass
class ReportOptions:
    sections: List[str]
    include_figures: bool
    include_toc: bool
    include_pdf: bool


@dataclass
class ReportRequest:
    metadata: ReportMetadata
    options: ReportOptions
    output_dir: str
    file_stem: str


@dataclass
class ReportFigures:
    plan:                   Optional[str] = None
    cross_section:          Optional[str] = None
    final_geometry:         Optional[str] = None
    longitudinal_elevation: Optional[str] = None
    girder_3d:              Optional[str] = None
    girder_front:           Optional[str] = None
    girder_top:             Optional[str] = None
    girder_end:             Optional[str] = None
    bm_envelope:            Optional[str] = None
    sf_envelope:            Optional[str] = None
    defl_ll:                Optional[str] = None
    shear_connector:        Optional[str] = None
    cross_bracing:          Optional[str] = None


@dataclass
class ReportPayload:
    metadata:         ReportMetadata
    options:          ReportOptions
    inputs:           dict
    analysis_summary: dict
    design_checks:    list
    figures:          ReportFigures
    log_entries:      List[str] = field(default_factory=list)
    output_dict:      dict = field(default_factory=dict)
    figure_data:      dict = field(default_factory=dict)


@dataclass
class ReportResult:
    pdf_path: Optional[str]
    tex_path: Optional[str]


class ReportDataBridge:
    """Centralized data extraction for the OsdagBridge report."""

    def __init__(self, output_dict: dict, input_dict: dict, payload: "ReportPayload"):
        self.output_dict = output_dict
        self.input_dict = input_dict
        self.payload = payload

    def _cb_forces_dict(self) -> dict:
        return self.output_dict.get("crossbracing_forces_dict", {})

    def _cb_pair_designs(self) -> dict:
        return self.output_dict.get("crossbracing_design_results", {})

    def _cb_osdag(self, pair: str, member: str, force_type: str) -> dict:
        from osdagbridge.core.bridge_types.plate_girder.results_data import _extract_osdag_summary
        try:
            raw = self._cb_pair_designs()[pair][member][force_type]
            return _extract_osdag_summary(raw or {})
        except (KeyError, TypeError):
            return {}

    def get_cb_pairs(self) -> list:
        try:
            return sorted(self._cb_forces_dict().get("pairs", {}).keys())
        except Exception:
            return []

    def get_cb_geometry(self) -> dict:
        return self._cb_forces_dict().get("geometry", {})

    def get_cb_brace_type(self) -> str:
        try:
            return self._cb_forces_dict().get("brace_type", "X")
        except Exception:
            return "X"

    def get_cb_force(self, pair: str, member: str, force_type: str) -> str:
        try:
            pairs = self._cb_forces_dict()["pairs"][pair]
            key = f"diag_{force_type}_kN" if member == "diagonal" else f"chord_{force_type}_kN"
            val = pairs.get(key)
            if val is not None:
                return f"{val:.3f}"
        except (KeyError, TypeError):
            pass
        return ""

    def get_cb_nature(self, pair: str, member: str) -> str:
        try:
            pairs = self._cb_forces_dict()["pairs"][pair]
            t_key = "diag_tension_kN" if member == "diagonal" else "chord_tension_kN"
            c_key = "diag_compression_kN" if member == "diagonal" else "chord_compression_kN"
            has_t = pairs.get(t_key) is not None
            has_c = pairs.get(c_key) is not None
            if has_t and has_c:
                return "T / C"
            if has_t:
                return "T"
            if has_c:
                return "C"
        except (KeyError, TypeError):
            pass
        return ""

    def get_cb_governing_force(self, pair: str, member: str) -> tuple:
        try:
            pairs = self._cb_forces_dict()["pairs"][pair]
            t_key = "diag_tension_kN" if member == "diagonal" else "chord_tension_kN"
            c_key = "diag_compression_kN" if member == "diagonal" else "chord_compression_kN"
            t_val = pairs.get(t_key)
            c_val = pairs.get(c_key)
            if t_val is not None and c_val is not None:
                if abs(c_val) >= abs(t_val):
                    return (f"{c_val:.3f}", "compression")
                return (f"{t_val:.3f}", "tension")
            if c_val is not None:
                return (f"{c_val:.3f}", "compression")
            if t_val is not None:
                return (f"{t_val:.3f}", "tension")
        except (KeyError, TypeError):
            pass
        return ("", "compression")

    def get_cb_section(self, pair: str, member: str, force_type: str) -> str:
        val = self._cb_osdag(pair, member, force_type).get("section")
        return _tex(val) if val else ""

    def get_cb_capacity(self, pair: str, member: str, force_type: str) -> str:
        val = self._cb_osdag(pair, member, force_type).get("capacity_kN")
        return f"{float(val):.3f}" if val is not None else ""

    def get_cb_efficiency(self, pair: str, member: str, force_type: str) -> str:
        val = self._cb_osdag(pair, member, force_type).get("efficiency")
        return f"{float(val):.3f}" if val is not None else ""

    def get_cb_slenderness(self, pair: str, member: str) -> str:
        for ft in ("compression", "tension"):
            val = self._cb_osdag(pair, member, ft).get("slenderness")
            if val is not None:
                return f"{float(val):.1f}"
        return ""

    def get_cb_status(self, pair: str, member: str, force_type: str) -> str:
        try:
            val = self._cb_osdag(pair, member, force_type).get("efficiency")
            if val is not None:
                ur = float(val)
                if ur <= 1.0:
                    return r"\textcolor{black}{PASS}"
                return r"\textcolor{red}{FAIL}"
        except (TypeError, ValueError):
            pass
        return ""

    def get_cb_gov_lc(self, pair: str, member: str, force_type: str) -> str:
        try:
            pfx = "diag" if member == "diagonal" else "chord"
            key = f"{pfx}_{force_type}_gov_lc"
            val = self._cb_forces_dict()["pairs"][pair].get(key)
            return _tex(val) if val else ""
        except (KeyError, TypeError):
            return ""

    def get_cb_connection(self, pair: str, member: str, force_type: str) -> str:
        val = self._cb_osdag(pair, member, force_type).get("connection")
        return str(val) if val else ""

    def get_cb_effective_length(self, member: str) -> str:
        try:
            geom = self.get_cb_geometry()
            if member == "diagonal":
                L_m = geom.get("diagonal_length_m", 0)
            else:
                L_m = geom.get("horiz_proj_m", 0)
            return f"{L_m * 1000:.0f}"
        except (TypeError, ValueError):
            return ""

    def get_cb_alpha_deg(self) -> str:
        try:
            return f"{self.get_cb_geometry().get('alpha_deg', 0):.2f}"
        except Exception:
            return ""


def _format_project_location(pl_data):
    if not pl_data:
        return ''
    if isinstance(pl_data, str):
        try:
            import ast
            pl_dict = ast.literal_eval(pl_data)
        except Exception:
            return pl_data
    elif isinstance(pl_data, dict):
        pl_dict = pl_data
    else:
        return str(pl_data)

    method = pl_dict.get('method')
    data = pl_dict.get('data', {})

    if method == 'location_name':
        dist = data.get('district', '')
        state = data.get('state', '')
        if dist and state:
            return f"{dist}, {state}"
        return dist or state or r''
    elif method == 'map':
        lat = data.get('latitude', '')
        lon = data.get('longitude', '')
        if lat and lon:
            try:
                from osdagbridge.core.bridge_types.plate_girder.ui_fields_project_location import DB_PATH
                from osdagbridge.core.data.project_location.database import Database
                db = Database(DB_PATH)
                db.connect()
                nearest = db.get_nearest_station_temperature(float(lat), float(lon))
                db.close()
                if nearest:
                    return f"{nearest['station']}, {nearest['state']}"
            except Exception as e:
                logger.warning(f"Reverse geocode error: {e}")
            return f"Lat: {lat}°, Lon: {lon}°"
        return 'Map Location'
    elif method == 'custom_data':
        return 'Custom Location Data'

    return str(pl_data)


def build_report_payload(request, input_dict, output_dict):
    try:
        rd = request.metadata.report_date or datetime.date.today().isoformat()
        lp = request.metadata.logo_path
        raw_pl = request.metadata.project_location or input_dict.get('project.location') or ''
        pl = _format_project_location(raw_pl)

        md = ReportMetadata(
            project_name=request.metadata.project_name,
            project_location=pl,
            designer=request.metadata.designer,
            client=request.metadata.client,
            company=request.metadata.company,
            group_name=request.metadata.group_name,
            subtitle=request.metadata.subtitle,
            job_number=request.metadata.job_number,
            additional_comments=request.metadata.additional_comments,
            logo_path=lp,
            report_date=rd,
            reviewer=getattr(request.metadata, 'reviewer', ''),
        )

        try:
            import ast
            if isinstance(raw_pl, str) and '{' in raw_pl:
                pl_dict = ast.literal_eval(raw_pl)
            elif isinstance(raw_pl, dict):
                pl_dict = raw_pl
            else:
                pl_dict = {}

            if pl_dict and isinstance(pl_dict, dict):
                data = pl_dict.get('data', {})
                weather = pl_dict.get('weather_data', {})

                lat_val = data.get('latitude') or weather.get('latitude')
                lon_val = data.get('longitude') or weather.get('longitude')

                if 'latitude' not in input_dict and lat_val:
                    input_dict['latitude'] = lat_val
                if 'longitude' not in input_dict and lon_val:
                    input_dict['longitude'] = lon_val

                if 'seismic_zone' not in input_dict and weather.get('zone'):
                    input_dict['seismic_zone'] = weather.get('zone')
                if 'wind_speed' not in input_dict and weather.get('wind_speed'):
                    input_dict['wind_speed'] = weather.get('wind_speed')
                if 'shade_temp_max' not in input_dict and weather.get('max_temp'):
                    input_dict['shade_temp_max'] = weather.get('max_temp')
                if 'shade_temp_min' not in input_dict and weather.get('min_temp'):
                    input_dict['shade_temp_min'] = weather.get('min_temp')
        except Exception as e:
            logger.warning(f"Failed to parse project location data: {e}")

        for _tkey in (KEY_TL_BRIDGE_TEMP_MIN, KEY_TL_BRIDGE_TEMP_MAX,
                      KEY_TL_TEMP_RISE, KEY_TL_TEMP_FALL):
            if not input_dict.get(_tkey) and output_dict.get(_tkey):
                input_dict[_tkey] = output_dict[_tkey]

        if not input_dict.get(KEY_TL_BRIDGE_TEMP_MIN):
            try:
                max_str = input_dict.get(KEY_TL_HIGHEST_MAX_TEMP) or input_dict.get('shade_temp_max')
                min_str = input_dict.get(KEY_TL_LOWEST_MIN_TEMP) or input_dict.get('shade_temp_min')
                if max_str and min_str:
                    from osdagbridge.core.utils.codes.irc6_2017 import IRC6_2017
                    res = IRC6_2017.cl_215_2_effective_bridge_temperature(
                        float(max_str), float(min_str), 'metallic', False)
                    t_min = res.get('T_min', 0)
                    t_max = res.get('T_max', 0)
                    mean = (t_max + t_min) / 2.0
                    input_dict[KEY_TL_BRIDGE_TEMP_MIN] = f"{t_min:.2f}"
                    input_dict[KEY_TL_BRIDGE_TEMP_MAX] = f"{t_max:.2f}"
                    input_dict[KEY_TL_TEMP_RISE] = f"{t_max - mean:.2f}"
                    input_dict[KEY_TL_TEMP_FALL] = f"{mean - t_min:.2f}"
            except Exception as _te:
                logger.warning(f"Could not compute temperature values for report: {_te}")

        asum = {}
        if output_dict:
            asum = output_dict.get('analysis_summary', {})

        dc = []
        le = []
        if output_dict:
            if 'design_checks' in output_dict:
                dc = output_dict['design_checks']
            if 'design_log' in output_dict:
                le = output_dict['design_log']

        if not le:
            try:
                from osdagbridge.core.utils.logger import bridge_logger
                le = bridge_logger.get_success_log()
            except Exception as _le:
                logger.warning("Could not read design log from logger: %s", _le)

        return ReportPayload(
            metadata=md,
            options=request.options,
            inputs=input_dict,
            analysis_summary=asum,
            design_checks=dc,
            figures=ReportFigures(),
            log_entries=le,
            output_dict=output_dict or {},
        )

    except Exception as exc:
        logger.warning("build_report_payload error: %s", exc)
        return ReportPayload(
            metadata=request.metadata,
            options=request.options,
            inputs={},
            analysis_summary={},
            design_checks=[],
            figures=ReportFigures(),
            log_entries=[],
            output_dict={},
        )


from osdagbridge.core.boq.boq_generator import calculate_material_quantities


def generate_report(payload, request):
    """Compile the full OsdagBridge Design Report to PDF (+ .tex source)."""
    tex_path = None
    try:
        compiler = 'pdflatex'
        try:
            import importlib
            module = importlib.import_module('osdag_latex_env.__main__')
            latex_env = getattr(module, 'OsdagLatexEnv')()
            if latex_env.pdflatex:
                compiler = str(latex_env.pdflatex)
                if latex_env.bin_dir:
                    os.environ['PATH'] = str(latex_env.bin_dir) + os.pathsep + os.environ.get('PATH', '')
        except Exception as e:
            logger.info("osdag_latex_env not found or failed to load. (%s)", e)

        logger.info("Compiler: %s", compiler)
        os.makedirs(request.output_dir, exist_ok=True)

        pdf_path = os.path.join(request.output_dir, request.file_stem + '.pdf')
        tex_path = os.path.join(request.output_dir, request.file_stem + '.tex')

        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_images = os.path.join(tmp_dir, 'images')
            os.makedirs(tmp_images, exist_ok=True)
            fig_paths = {}
            for attr, img_bytes in list(payload.figure_data.items()):
                if img_bytes:
                    p = os.path.join(tmp_images, attr + '.png')
                    with open(p, 'wb') as fh:
                        fh.write(img_bytes)
                    fig_paths[attr] = p.replace('\\', '/')
            payload.figure_data.clear()

            tmp_assets = os.path.join(tmp_dir, 'assets')
            os.makedirs(tmp_assets, exist_ok=True)

            osdag_logo_src = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'data', 'ResourceFiles', 'vectors', 'Osdag Logo.png')
            iit_logo_src = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'assets', 'IIT Bombay Logo.png')

            osdag_logo_latex = None
            if os.path.exists(osdag_logo_src):
                shutil.copy2(osdag_logo_src, os.path.join(tmp_assets, 'osdag_logo.png'))
                osdag_logo_latex = 'assets/osdag_logo.png'

            org_logo_latex = None
            org_logo_src = (
                payload.metadata.logo_path
                if (payload.metadata.logo_path and os.path.exists(payload.metadata.logo_path))
                else (iit_logo_src if os.path.exists(iit_logo_src) else None)
            )
            if org_logo_src:
                shutil.copy2(org_logo_src, os.path.join(tmp_assets, 'org_logo.png'))
                org_logo_latex = 'assets/org_logo.png'

            # Compute and inject quantities for Chapter 7
            quantities = calculate_material_quantities(payload.inputs, payload.output_dict)
            payload.inputs.update(quantities)

            # Generate programmatic Matplotlib charts (Section 5.5 & Chapter 7)
            try:
                ur_chart_path = os.path.join(tmp_images, 'ur_summary.png')
                if generate_ur_summary_chart(payload.inputs, payload.output_dict, ur_chart_path):
                    fig_paths['ur_summary'] = ur_chart_path.replace('\\', '/')
            except Exception as _ur_exc:
                logger.warning("Failed to generate UR summary chart: %s", _ur_exc)

            try:
                mat_chart_path = os.path.join(tmp_images, 'material_quantities.png')
                if generate_material_quantity_charts(quantities, mat_chart_path):
                    fig_paths['material_quantities'] = mat_chart_path.replace('\\', '/')
            except Exception as _mat_exc:
                logger.warning("Failed to generate material quantity chart: %s", _mat_exc)

            bridge = ReportDataBridge(payload.output_dict, payload.inputs, payload)
            span_m = float(payload.inputs.get(KEY_SPAN, 0) or 0)

            doc_parts = []
            doc_parts.append(
                preamble(
                    payload.metadata.project_name,
                    payload.metadata.job_number,
                    payload.metadata.report_date,
                    payload.metadata.subtitle or 'Rev 0',
                )
            )
            doc_parts.append(title_page(payload.metadata, osdag_logo_latex, org_logo_latex))

            if payload.options.include_toc:
                doc_parts.append(toc_section())

            secs = payload.options.sections

            doc_parts.append(executive_summary(payload.inputs, payload.output_dict, fig_paths))
            doc_parts.append(ch1_project_info(payload.metadata))
            doc_parts.append(ch2_input_parameters(payload.metadata, payload.inputs, payload.output_dict))

            if 'loads' in secs:
                doc_parts.append(ch3_loads(payload.inputs))
            if 'analysis' in secs:
                doc_parts.append(ch4_analysis(payload.analysis_summary, fig_paths, bridge, span_m))
            if 'design_checks' in secs:
                doc_parts.append(ch5_design_checks(payload.design_checks, bridge, fig_paths))
            if 'drawings' in secs and payload.options.include_figures:
                doc_parts.append(ch6_drawings(fig_paths))

            doc_parts.append(ch7_quantities(payload.inputs, fig_paths))
            doc_parts.append(ch8_design_log(payload.log_entries, payload.inputs))
            doc_parts.append(references())
            doc_parts.append(r"\end{document}")

            full_tex = "\n".join(doc_parts)

            tmp_tex = os.path.join(tmp_dir, request.file_stem + '.tex')
            tmp_pdf = os.path.join(tmp_dir, request.file_stem + '.pdf')

            with open(tmp_tex, 'w', encoding='utf-8') as f:
                f.write(full_tex)

            for _ in range(2):
                try:
                    kwargs = {
                        'cwd': tmp_dir,
                        'stdout': subprocess.PIPE,
                        'stderr': subprocess.PIPE,
                        'check': False,
                        'env': os.environ.copy(),
                    }
                    if os.name == 'nt':
                        kwargs['creationflags'] = subprocess.CREATE_NO_WINDOW

                    res = subprocess.run(
                        [compiler, '-interaction=nonstopmode', request.file_stem + '.tex'],
                        **kwargs,
                    )
                except Exception as exc:
                    logger.warning(f"pdflatex run failed: {exc}")

            if os.path.exists(tmp_tex):
                shutil.copy2(tmp_tex, tex_path)
            if os.path.exists(tmp_pdf):
                shutil.copy2(tmp_pdf, pdf_path)

        if os.path.exists(pdf_path):
            logger.info("Report generated: %s", pdf_path)
            return ReportResult(pdf_path=pdf_path, tex_path=tex_path)

        logger.error("pdflatex ran but no PDF was produced.")
        if 'res' in locals():
            logger.error("pdflatex STDOUT:\n%s", res.stdout.decode('utf-8', 'ignore'))
            logger.error("pdflatex STDERR:\n%s", res.stderr.decode('utf-8', 'ignore'))
        return ReportResult(pdf_path=None, tex_path=tex_path)

    except Exception as exc:
        logger.error("generate_report failed: %s", exc, exc_info=True)
        if tex_path and os.path.exists(tex_path):
            return ReportResult(pdf_path=None, tex_path=tex_path)
        return ReportResult(pdf_path=None, tex_path=None)
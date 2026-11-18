"""
Centralized Formatting & Style System (Single Source of Truth)
for OsdagBridge LaTeX Design Reports.
"""

from dataclasses import dataclass
from typing import List, Optional


@dataclass(frozen=True)
class ColorPalette:
    primary_hex: str = "91B014"        # Osdag signature green
    primary_dark_hex: str = "6E870F"   # Darker green accent
    header_bg_hex: str = "F3F7E6"      # Soft green tint for table headers
    sub_header_bg_hex: str = "F7F9F2"  # Subtle section row tint
    border_gray_hex: str = "BFBFBF"
    text_dark_hex: str = "1F2937"
    pass_green_hex: str = "15803D"
    warn_amber_hex: str = "B45309"
    fail_red_hex: str = "DC2626"


@dataclass(frozen=True)
class PageGeometry:
    paper_size: str = "a4paper"
    font_size_pt: int = 12
    top_in: float = 1.00
    bottom_in: float = 1.18          # Extra bottom clearance prevents footer bleed
    left_in: float = 0.90
    right_in: float = 0.90
    head_height_pt: int = 16
    head_sep_pt: int = 18
    foot_skip_pt: int = 34           # Reserves dedicated space above green footrule
    line_stretch: float = 1.15


@dataclass(frozen=True)
class TableStyle:
    tabcolsep_pt: float = 5.5
    compact_tabcolsep_pt: float = 3.5
    array_stretch: float = 1.18
    compact_array_stretch: float = 1.22
    extra_row_height_pt: float = 1.0
    rule_width_pt: float = 0.5
    lt_pre_pt: int = 4
    lt_post_pt: int = 8
    needspace_table_lines: int = 6
    needspace_longtable_lines: int = 7
    row_pad_pt: int = 6


COLORS = ColorPalette()
PAGE = PageGeometry()
TABLE = TableStyle()


def get_geometry_options() -> str:
    return (
        f"{PAGE.paper_size}, "
        f"top={PAGE.top_in}in, "
        f"bottom={PAGE.bottom_in}in, "
        f"left={PAGE.left_in}in, "
        f"right={PAGE.right_in}in, "
        f"headheight={PAGE.head_height_pt}pt, "
        f"headsep={PAGE.head_sep_pt}pt, "
        f"footskip={PAGE.foot_skip_pt}pt"
    )


def get_color_definitions() -> str:
    return (
        f"\\definecolor{{osdagGreen}}{{HTML}}{{{COLORS.primary_hex}}}\n"
        f"\\definecolor{{osdagGreenDark}}{{HTML}}{{{COLORS.primary_dark_hex}}}\n"
        f"\\definecolor{{osdagHeaderBg}}{{HTML}}{{{COLORS.header_bg_hex}}}\n"
        f"\\definecolor{{osdagSubHeaderBg}}{{HTML}}{{{COLORS.sub_header_bg_hex}}}\n"
        f"\\definecolor{{osdagPass}}{{HTML}}{{{COLORS.pass_green_hex}}}\n"
        f"\\definecolor{{osdagWarn}}{{HTML}}{{{COLORS.warn_amber_hex}}}\n"
        f"\\definecolor{{osdagFail}}{{HTML}}{{{COLORS.fail_red_hex}}}\n"
    )


def get_table_defaults() -> str:
    return (
        f"\\setlength{{\\tabcolsep}}{{{TABLE.tabcolsep_pt}pt}}\n"
        f"\\renewcommand{{\\arraystretch}}{{{TABLE.array_stretch}}}\n"
        f"\\setlength{{\\LTpre}}{{{TABLE.lt_pre_pt}pt}}\n"
        f"\\setlength{{\\LTpost}}{{{TABLE.lt_post_pt}pt}}\n"
        f"\\setlength{{\\arrayrulewidth}}{{{TABLE.rule_width_pt}pt}}\n"
        f"\\setlength{{\\extrarowheight}}{{{TABLE.extra_row_height_pt}pt}}\n"
        f"\\BeforeBeginEnvironment{{table}}{{\\needspace{{{TABLE.needspace_table_lines}\\baselineskip}}}}\n"
        f"\\BeforeBeginEnvironment{{longtable}}{{\\needspace{{{TABLE.needspace_longtable_lines}\\baselineskip}}}}\n"
    )

def build_longtable(
    col_spec: str,
    caption: str,
    header_cells: List[str],
    body_tex: str,
    label: Optional[str] = None,
    compact: bool = False,
    note: Optional[str] = None,
    sub_header_row: Optional[str] = None,
) -> str:
    """
    Build a standardized LaTeX longtable with:
    - Repeating column headers across every page break (\\endfirsthead / \\endhead)
    - Equal-height \\endfoot / \\endlastfoot to prevent orphan headers at page bottoms
    - Centralized brand header shading and cell padding
    """
    hdr_row = " & ".join(header_cells) + f" \\\\[{TABLE.row_pad_pt}pt]\n\\hline\n"
    if sub_header_row:
        hdr_row += sub_header_row + "\n"

    cap_line = f"\\caption{{\\textbf{{{caption}}}}}"
    if label:
        cap_line += f"\\label{{{label}}}"
    cap_line += "\\\\\n"

    wrap_start = ""
    wrap_end = ""
    if compact:
        wrap_start = (
            "\\begingroup\n"
            "\\footnotesize\n"
            f"\\setlength{{\\tabcolsep}}{{{TABLE.compact_tabcolsep_pt}pt}}\n"
            f"\\renewcommand{{\\arraystretch}}{{{TABLE.compact_array_stretch}}}\n"
        )
        wrap_end = "\\endgroup\n"

    clean_body = body_tex.strip()
    if clean_body.endswith(r"\hline"):
        clean_body = clean_body[:-6].rstrip()

    note_block = f"\\noindent\\textit{{{note}}}\n" if note else ""

    return (
        f"\\vspace{{0.8em}}\n"
        f"{wrap_start}"
        f"\\begin{{longtable}}{{{col_spec}}}\n"
        f"{cap_line}"
        f"\\hline\n"
        f"\\rowcolor{{osdagHeaderBg}}\n"
        f"{hdr_row}"
        f"\\endfirsthead\n"
        f"\\hline\n"
        f"\\rowcolor{{osdagHeaderBg}}\n"
        f"{hdr_row}"
        f"\\endhead\n"
        f"\\hline\n"
        f"\\endfoot\n"
        f"\\hline\n"
        f"\\endlastfoot\n"
        f"{clean_body}\n"
        f"\\end{{longtable}}\n"
        f"{wrap_end}"
        f"{note_block}"
    )
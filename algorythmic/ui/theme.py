"""
Feuille de style de l'application.

Un thème sombre et neutre : l'interface ne doit pas attirer l'oeil plus que
ce qu'elle produit.

@author epyidev
"""

from __future__ import annotations

BACKGROUND = "#14161a"
SURFACE = "#1c1f25"
SURFACE_RAISED = "#242832"
BORDER = "#31353f"
TEXT = "#e6e8ec"
TEXT_MUTED = "#8b919c"
ACCENT = "#c8a24a"
ACCENT_PRESSED = "#a9861f"
DANGER = "#b4544a"

STYLE_SHEET = f"""
QWidget {{
    background-color: {BACKGROUND};
    color: {TEXT};
    font-family: "Segoe UI", "Inter", sans-serif;
    font-size: 13px;
}}
QGroupBox {{
    background-color: {SURFACE};
    border: 1px solid {BORDER};
    border-radius: 8px;
    margin-top: 14px;
    padding: 14px 12px 12px 12px;
    font-weight: 600;
}}
QGroupBox::title {{
    subcontrol-origin: margin;
    left: 12px;
    padding: 0 4px;
    color: {TEXT_MUTED};
    text-transform: uppercase;
    font-size: 11px;
    letter-spacing: 1px;
}}
QLabel[role="subtitle"] {{
    color: {TEXT_MUTED};
}}
QLabel[role="value"] {{
    color: {ACCENT};
    font-variant-numeric: tabular-nums;
}}
QComboBox, QSpinBox, QDoubleSpinBox, QLineEdit {{
    background-color: {SURFACE_RAISED};
    border: 1px solid {BORDER};
    border-radius: 6px;
    padding: 5px 8px;
    selection-background-color: {ACCENT};
    selection-color: {BACKGROUND};
}}
QComboBox:focus, QSpinBox:focus, QDoubleSpinBox:focus, QLineEdit:focus {{
    border-color: {ACCENT};
}}
QComboBox QAbstractItemView {{
    background-color: {SURFACE_RAISED};
    border: 1px solid {BORDER};
    selection-background-color: {ACCENT};
    selection-color: {BACKGROUND};
}}
QPushButton {{
    background-color: {SURFACE_RAISED};
    border: 1px solid {BORDER};
    border-radius: 6px;
    padding: 6px 14px;
}}
QPushButton:hover {{
    border-color: {ACCENT};
}}
QPushButton:disabled {{
    color: {TEXT_MUTED};
    border-color: {BORDER};
}}
QPushButton[role="primary"] {{
    background-color: {ACCENT};
    border-color: {ACCENT};
    color: {BACKGROUND};
    font-weight: 600;
    padding: 8px 18px;
}}
QPushButton[role="primary"]:hover {{
    background-color: {ACCENT_PRESSED};
    border-color: {ACCENT_PRESSED};
}}
QPushButton[role="primary"]:disabled {{
    background-color: {SURFACE_RAISED};
    border-color: {BORDER};
    color: {TEXT_MUTED};
}}
QPushButton[role="danger"]:hover {{
    border-color: {DANGER};
    color: {DANGER};
}}
QSlider::groove:horizontal {{
    height: 4px;
    background: {BORDER};
    border-radius: 2px;
}}
QSlider::sub-page:horizontal {{
    background: {ACCENT};
    border-radius: 2px;
}}
QSlider::handle:horizontal {{
    background: {TEXT};
    width: 12px;
    height: 12px;
    margin: -5px 0;
    border-radius: 6px;
}}
QProgressBar {{
    background-color: {SURFACE_RAISED};
    border: 1px solid {BORDER};
    border-radius: 6px;
    height: 18px;
    text-align: center;
    color: {TEXT_MUTED};
}}
QProgressBar::chunk {{
    background-color: {ACCENT};
    border-radius: 5px;
}}
QPlainTextEdit {{
    background-color: {SURFACE_RAISED};
    border: 1px solid {BORDER};
    border-radius: 6px;
    font-family: "Cascadia Mono", "Consolas", monospace;
    font-size: 12px;
    color: {TEXT_MUTED};
}}
"""

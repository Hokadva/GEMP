"""Main styles of programm"""

SLIDERSTYLE = """
    QSlider::groove:horizontal {
        height: 6px;
        background: #3a3a3a;
        border-radius: 3px;
    }
    QSlider::sub-page:horizontal {
        background: white;
        border-radius: 3px;
    }
    QSlider::handle:horizontal {
        background: transparent;
        width: 0px;
        margin: 0;
    }
"""

STYLES = {
    "slider_style": SLIDERSTYLE
}

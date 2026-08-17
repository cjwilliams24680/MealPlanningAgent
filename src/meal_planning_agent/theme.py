"""Bistro Chalkboard theme: charcoal slate, warm amber, handwritten chalk headings."""

import gradio as gr

_CHARCOAL = "#2B2B28"
_CHARCOAL_LIGHT = "#35342F"
_CHARCOAL_LIGHTER = "#403E38"
_CHALK = "#F2EEE3"
_CHALK_SUBDUED = "#B8B3A4"
_AMBER = "#E8B44F"
_AMBER_BRIGHT = "#F0C46A"
_AMBER_SOFT = "rgba(232, 180, 79, 0.15)"
_WARM_GRAY_BORDER = "#4A4840"


def bistro_theme() -> gr.themes.Base:
    # Caveat is in the font stack only so Gradio loads it from Google Fonts;
    # Karla stays the effective body font and BISTRO_CSS applies Caveat to headings.
    theme = gr.themes.Base(
        radius_size=gr.themes.sizes.radius_md,
        # gradio 6.20's Font.__eq__ crashes on Font-vs-str comparisons, which
        # launch() triggers by comparing this theme to every built-in. Keep this
        # list at exactly 4 Font entries: Glass's 5-string font stack is then
        # skipped on length, and the 4-length built-ins hit a safe Font-vs-Font
        # mismatch at index 0.
        font=[
            gr.themes.GoogleFont("Karla"),
            gr.themes.GoogleFont("Caveat"),
            gr.themes.Font("system-ui"),
            gr.themes.Font("sans-serif"),
        ],
    )
    # Light and _dark variants are pinned to the same values so the chalkboard
    # look holds regardless of the visitor's browser color-scheme preference.
    return theme.set(
        body_background_fill=_CHARCOAL,
        body_background_fill_dark=_CHARCOAL,
        body_text_color=_CHALK,
        body_text_color_dark=_CHALK,
        body_text_color_subdued=_CHALK_SUBDUED,
        body_text_color_subdued_dark=_CHALK_SUBDUED,
        background_fill_primary=_CHARCOAL,
        background_fill_primary_dark=_CHARCOAL,
        background_fill_secondary=_CHARCOAL_LIGHT,
        background_fill_secondary_dark=_CHARCOAL_LIGHT,
        block_background_fill=_CHARCOAL_LIGHT,
        block_background_fill_dark=_CHARCOAL_LIGHT,
        block_border_color=_WARM_GRAY_BORDER,
        block_border_color_dark=_WARM_GRAY_BORDER,
        block_label_text_color=_CHALK_SUBDUED,
        block_label_text_color_dark=_CHALK_SUBDUED,
        block_label_background_fill=_CHARCOAL_LIGHT,
        block_label_background_fill_dark=_CHARCOAL_LIGHT,
        block_title_text_color=_CHALK,
        block_title_text_color_dark=_CHALK,
        panel_background_fill=_CHARCOAL_LIGHT,
        panel_background_fill_dark=_CHARCOAL_LIGHT,
        panel_border_color=_WARM_GRAY_BORDER,
        panel_border_color_dark=_WARM_GRAY_BORDER,
        input_background_fill=_CHARCOAL_LIGHT,
        input_background_fill_dark=_CHARCOAL_LIGHT,
        input_background_fill_focus=_CHARCOAL_LIGHTER,
        input_background_fill_focus_dark=_CHARCOAL_LIGHTER,
        input_border_color=_WARM_GRAY_BORDER,
        input_border_color_dark=_WARM_GRAY_BORDER,
        input_border_color_focus=_AMBER,
        input_border_color_focus_dark=_AMBER,
        input_placeholder_color=_CHALK_SUBDUED,
        input_placeholder_color_dark=_CHALK_SUBDUED,
        border_color_primary=_WARM_GRAY_BORDER,
        border_color_primary_dark=_WARM_GRAY_BORDER,
        border_color_accent=_AMBER,
        border_color_accent_dark=_AMBER,
        color_accent=_AMBER,
        color_accent_soft=_AMBER_SOFT,
        color_accent_soft_dark=_AMBER_SOFT,
        button_primary_background_fill=_AMBER,
        button_primary_background_fill_dark=_AMBER,
        button_primary_background_fill_hover=_AMBER_BRIGHT,
        button_primary_background_fill_hover_dark=_AMBER_BRIGHT,
        button_primary_text_color=_CHARCOAL,
        button_primary_text_color_dark=_CHARCOAL,
        button_secondary_background_fill=_CHARCOAL_LIGHTER,
        button_secondary_background_fill_dark=_CHARCOAL_LIGHTER,
        button_secondary_background_fill_hover=_WARM_GRAY_BORDER,
        button_secondary_background_fill_hover_dark=_WARM_GRAY_BORDER,
        button_secondary_text_color=_CHALK,
        button_secondary_text_color_dark=_CHALK,
        link_text_color=_AMBER,
        link_text_color_dark=_AMBER,
        link_text_color_hover=_AMBER_BRIGHT,
        link_text_color_hover_dark=_AMBER_BRIGHT,
    )


BISTRO_CSS = f"""
h1 {{
    font-family: 'Caveat', cursive;
    font-size: 2.6rem;
    color: {_AMBER};
    letter-spacing: 0.02em;
}}

.message.bot, .message-row.bot-row .message {{
    background: {_CHARCOAL_LIGHT};
    color: {_CHALK};
}}

.message.user, .message-row.user-row .message {{
    color: {_CHALK};
}}

/* Meal plans and shopping lists arrive as markdown; render their headings like chalk menu sections */
.message h2, .message h3 {{
    font-family: 'Caveat', cursive;
    color: {_AMBER};
    border-bottom: 1px dashed {_WARM_GRAY_BORDER};
    padding-bottom: 0.15em;
}}

.message h2 {{
    font-size: 1.9rem;
}}

.message h3 {{
    font-size: 1.5rem;
}}

.message ul li, .message ol li {{
    color: {_CHALK};
}}
"""

"""Bistro Chalkboard theme: charcoal slate, warm amber, handwritten chalk headings."""

import gradio as gr

CHARCOAL = "#2B2B28"
CHARCOAL_LIGHT = "#35342F"
CHARCOAL_LIGHTER = "#403E38"
CHALK = "#F2EEE3"
CHALK_SUBDUED = "#B8B3A4"
AMBER = "#E8B44F"
AMBER_BRIGHT = "#F0C46A"
AMBER_SOFT = "rgba(232, 180, 79, 0.15)"
AMBER_FAINT = "rgba(232, 180, 79, 0.07)"
WARM_GRAY_BORDER = "#4A4840"


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
        body_background_fill=CHARCOAL,
        body_background_fill_dark=CHARCOAL,
        body_text_color=CHALK,
        body_text_color_dark=CHALK,
        body_text_color_subdued=CHALK_SUBDUED,
        body_text_color_subdued_dark=CHALK_SUBDUED,
        background_fill_primary=CHARCOAL,
        background_fill_primary_dark=CHARCOAL,
        background_fill_secondary=CHARCOAL_LIGHT,
        background_fill_secondary_dark=CHARCOAL_LIGHT,
        block_background_fill=CHARCOAL_LIGHT,
        block_background_fill_dark=CHARCOAL_LIGHT,
        block_border_color=WARM_GRAY_BORDER,
        block_border_color_dark=WARM_GRAY_BORDER,
        block_label_text_color=CHALK_SUBDUED,
        block_label_text_color_dark=CHALK_SUBDUED,
        block_label_background_fill=CHARCOAL_LIGHT,
        block_label_background_fill_dark=CHARCOAL_LIGHT,
        block_title_text_color=CHALK,
        block_title_text_color_dark=CHALK,
        panel_background_fill=CHARCOAL_LIGHT,
        panel_background_fill_dark=CHARCOAL_LIGHT,
        panel_border_color=WARM_GRAY_BORDER,
        panel_border_color_dark=WARM_GRAY_BORDER,
        input_background_fill=CHARCOAL_LIGHT,
        input_background_fill_dark=CHARCOAL_LIGHT,
        input_background_fill_focus=CHARCOAL_LIGHTER,
        input_background_fill_focus_dark=CHARCOAL_LIGHTER,
        input_border_color=WARM_GRAY_BORDER,
        input_border_color_dark=WARM_GRAY_BORDER,
        input_border_color_focus=AMBER,
        input_border_color_focus_dark=AMBER,
        input_placeholder_color=CHALK_SUBDUED,
        input_placeholder_color_dark=CHALK_SUBDUED,
        border_color_primary=WARM_GRAY_BORDER,
        border_color_primary_dark=WARM_GRAY_BORDER,
        border_color_accent=AMBER,
        border_color_accent_dark=AMBER,
        color_accent=AMBER,
        color_accent_soft=AMBER_SOFT,
        color_accent_soft_dark=AMBER_SOFT,
        button_primary_background_fill=AMBER,
        button_primary_background_fill_dark=AMBER,
        button_primary_background_fill_hover=AMBER_BRIGHT,
        button_primary_background_fill_hover_dark=AMBER_BRIGHT,
        button_primary_text_color=CHARCOAL,
        button_primary_text_color_dark=CHARCOAL,
        button_secondary_background_fill=CHARCOAL_LIGHTER,
        button_secondary_background_fill_dark=CHARCOAL_LIGHTER,
        button_secondary_background_fill_hover=WARM_GRAY_BORDER,
        button_secondary_background_fill_hover_dark=WARM_GRAY_BORDER,
        button_secondary_text_color=CHALK,
        button_secondary_text_color_dark=CHALK,
        link_text_color=AMBER,
        link_text_color_dark=AMBER,
        link_text_color_hover=AMBER_BRIGHT,
        link_text_color_hover_dark=AMBER_BRIGHT,
    )


BISTRO_CSS = f"""
h1 {{
    font-family: 'Caveat', cursive;
    font-size: 2.6rem;
    color: {AMBER};
    letter-spacing: 0.02em;
}}

.message.bot, .message-row.bot-row .message {{
    background: {CHARCOAL_LIGHT};
    color: {CHALK};
}}

.message.user, .message-row.user-row .message {{
    color: {CHALK};
}}

/* Meal plans and shopping lists arrive as markdown; render their headings like chalk menu sections */
.message h2, .message h3 {{
    font-family: 'Caveat', cursive;
    color: {AMBER};
    border-bottom: 1px dashed {WARM_GRAY_BORDER};
    padding-bottom: 0.15em;
}}

.message h2 {{
    font-size: 1.9rem;
}}

.message h3 {{
    font-size: 1.5rem;
}}

.message ul li, .message ol li {{
    color: {CHALK};
}}
"""

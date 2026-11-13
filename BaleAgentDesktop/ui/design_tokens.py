"""Bale Agent Desktop v2.1 visual tokens."""

LIGHT = {
    "name": "Pearl Atmosphere",
    "canvas": "#F3F4FA",
    "canvas_deep": "#E8ECF6",
    "surface": "#FFFFFF",
    "surface_soft": "#F7F8FC",
    "surface_raised": "#FFFFFF",
    "glass": (255, 255, 255, 112),
    "glass_raised": (255, 255, 255, 150),
    "text": "#2D3047",
    "muted": "#6F748D",
    "subtle": "#9298AA",
    "line": "#DDE2EF",
    "line_strong": "#C8D0E4",
    "primary": "#B9B9F1",
    "primary_hover": "#C9C9F7",
    "primary_soft": "#E9EAFB",
    "mint": "#75BDA8",
    "mint_soft": "#E5F4EF",
    "blue": "#82B7E5",
    "blue_soft": "#EAF3FB",
    "rose": "#D49BB5",
    "rose_soft": "#F8EDF2",
    "butter": "#C6A96C",
    "butter_soft": "#F7F1E4",
    "danger": "#C77F91",
    "danger_soft": "#F8EDEF",
    "success": "#5FAD91",
    "warning": "#B78D50",
    "shadow": (83, 93, 132, 26),
}

DARK = {
    "name": "Nocturne Glass",
    "canvas": "#111625",
    "canvas_deep": "#1A2037",
    "surface": "#202940",
    "surface_soft": "#1A2439",
    "surface_raised": "#26314A",
    "glass": (160, 176, 238, 48),
    "glass_raised": (176, 190, 246, 76),
    "text": "#F4F3FC",
    "muted": "#B6BCD2",
    "subtle": "#8E98B3",
    "line": "#48516F",
    "line_strong": "#697494",
    "primary": "#C4C4FA",
    "primary_hover": "#D7D7FF",
    "primary_soft": "#353A5A",
    "mint": "#A5E0CF",
    "mint_soft": "#213E3C",
    "blue": "#A8D0F2",
    "blue_soft": "#263B52",
    "rose": "#E5BBD0",
    "rose_soft": "#433342",
    "butter": "#E5D2A9",
    "butter_soft": "#403B2F",
    "danger": "#E2A1B1",
    "danger_soft": "#49333E",
    "success": "#A5E0CF",
    "warning": "#E5D2A9",
    "shadow": (0, 0, 0, 104),
}

SPACING = {"xs": 4, "sm": 8, "md": 12, "lg": 16, "xl": 24, "2xl": 32, "3xl": 40}
RADIUS = {"sm": 10, "md": 14, "lg": 18, "xl": 24, "2xl": 30}


def palette(dark: bool) -> dict:
    return DARK if dark else LIGHT

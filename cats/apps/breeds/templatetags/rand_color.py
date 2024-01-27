import random

from django import template

register = template.Library()


@register.simple_tag(name="color")
def color_filter(color_type="pastel"):
    pastel_colors = ["#ffb3ba", "#ffdfba", "#ffffba", "#baffc9", "#bae1ff"]
    solid_colors = ["#C41E3A", "#AC1EE7", "#353e2d", "#FF8D11", "#1E59E7"]
    match color_type:
        case "pastel":
            color_group = pastel_colors
        case "solid":
            color_group = solid_colors
        case _:
            color_group = pastel_colors

    idx = random.randint(0, len(color_group) - 1)
    return color_group[idx]

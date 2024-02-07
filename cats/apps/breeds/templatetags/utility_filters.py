import random

from django import template

register = template.Library()


@register.filter(name="color")
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


@register.filter(name="replace")
def replace_filter(value, args):
    try:
        old_phrase, new_phrase = args.split(":")
        return value.replace(old_phrase, new_phrase)
    except ValueError:
        return value


@register.filter(name="range")
def range_filter(value):
    return range(value)


@register.filter(name="minus")
def minus(value, arg):
    try:
        return value - arg
    except (TypeError, ValueError):
        return value


@register.filter(name="check_indicator_template")
def check_indicator_filter(value):
    if value:
        return "<i class='fa-regular fa-circle-check' style='color: #269043;'></i>"
    else:
        return "<i class='fa-regular fa-circle-xmark' style='color:#C41E3A;'></i>"

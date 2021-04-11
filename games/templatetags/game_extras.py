from django import template
from django.utils.safestring import mark_safe

register = template.Library()


@register.simple_tag(takes_context=True)
def game_title(context, game):
    return mark_safe(game.html_title(user=context['request'].user))


@register.simple_tag(takes_context=True)
def game_badge(context, game):
    return mark_safe(game.html_badge(user=context['request'].user))

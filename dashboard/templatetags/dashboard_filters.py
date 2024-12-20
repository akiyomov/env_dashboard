from django import template

register = template.Library()

@register.filter
def sub(value, arg):
    return float(value) - float(arg)

@register.filter
def get_item(dictionary, key):
    try:
        return dictionary.get(key)
    except:
        return None
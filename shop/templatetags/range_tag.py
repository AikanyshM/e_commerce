from django import template

register = template.Library()

@register.filter(name='range_tag')
def range_tag(number):
    return range(1, number)

    

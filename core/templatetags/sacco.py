from django import template

register = template.Library()


@register.filter
def ugx(value):
    """Format whole shillings as 'UGX 850,000'; None counts as zero."""
    return f"UGX {value or 0:,}"

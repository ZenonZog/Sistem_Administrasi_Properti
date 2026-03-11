from django import template

register = template.Library()

@register.filter(name='rupiah')
def rupiah(value):
    try:
        value = float(value)
        # Pisahkan ribuan dengan titik
        return f"Rp {value:,.0f}".replace(',', '.')
    except (ValueError, TypeError):
        return value

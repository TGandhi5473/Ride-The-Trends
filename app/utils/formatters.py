def human_format(num):
    """Converts large numbers into readable strings (e.g., 1.2M)."""
    num = float('{:.3g}'.format(num))
    magnitude = 0
    while abs(num) >= 1000:
        magnitude += 1
        num /= 1000.0
    return '{}{}'.format('{:f}'.format(num).rstrip('0').rstrip('.'), ['', 'K', 'M', 'B', 'T'][magnitude])

def format_date_simple(dt):
    """Formats a datetime object for clean UI display."""
    if dt is None: return "N/A"
    return dt.strftime("%b %d, %Y")

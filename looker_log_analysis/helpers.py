def calc_remaining(start, end, ct, total):
    """Calculate remaining time based on processed rows"""
    elapsed = (end - start).total_seconds()
    avg_call_time = elapsed / ct
    est_completed_time = avg_call_time * total
    return est_completed_time - elapsed


def should_skip(line_text):
    """Logical test for whether a specific line should be skipped
    Returns Boolean """
    skips = ('#', 'uri', 'org')
    return line_text.strip().startswith(skips)

def setup_years(start_year, n):
    """Produce a tuple of years, starting with start_year
    and going back n years. The output is in the format 
    (YYYY-, YYYY-, ...)
    Used to validate which loglines begin with a year
    """
    output = [f"{start_year}-"]
    for i in range(int(n), 0, -1):
        output.append(f"{start_year - i}-")
    return tuple(output)
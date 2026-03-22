import os


def generate_report(results_path: str) -> str:
    """Generate a very small HTML report placeholder from results.

    For now this is a shim that writes a small HTML file referencing the
    provided results JSON. This function is intended to be expanded later.
    """
    if not os.path.exists(results_path):
        raise FileNotFoundError(results_path)
    out = os.path.splitext(results_path)[0] + "_report.html"
    with open(out, 'w', encoding='utf-8') as f:
        f.write(f"<html><body><h1>Report for {os.path.basename(results_path)}</h1>\n")
        f.write(f"<p>Source: {results_path}</p>\n")
        f.write("</body></html>\n")
    return out

import os
from model_benchmarking.report import generate_report


def test_generate_report_creates_file(tmp_path):
    src = tmp_path / "results.json"
    src.write_text('{"ok": true}')
    out = generate_report(str(src))
    assert os.path.exists(out)
    content = open(out, 'r', encoding='utf-8').read()
    assert "Report for results.json" in content

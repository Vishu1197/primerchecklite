"""JSON and HTML report generation."""
from __future__ import annotations

import html
import json
from pathlib import Path
from typing import Any


def to_json(result: dict[str, Any]) -> str:
    return json.dumps(result, indent=2, ensure_ascii=False)


def write_json(result: dict[str, Any], path: str | Path) -> None:
    Path(path).write_text(to_json(result) + "\n", encoding="utf-8")


def to_html(result: dict[str, Any]) -> str:
    def rows(label: str, item: dict[str, Any]) -> str:
        excluded = {"sequence", "statuses"}
        output = [f"<h3>{html.escape(label)}</h3><table><tbody>"]
        output.append(f"<tr><th>Sequence (5′ to 3′)</th><td><code>{html.escape(item.get('sequence',''))}</code></td></tr>")
        for key, value in item.items():
            if key in excluded:
                continue
            status = item.get("statuses", {}).get(key, "not_evaluated")
            cls = "review" if status == "review" else "ok"
            output.append(f'<tr><th>{html.escape(key.replace("_"," ").title())}</th><td class="{cls}">{html.escape(str(value))}</td></tr>')
        output.append("</tbody></table>")
        return "".join(output)
    warnings = "".join(f"<li>{html.escape(w)}</li>" for w in result.get("warnings", [])) or "<li>No configured threshold warnings.</li>"
    limitations = "".join(f"<li>{html.escape(x)}</li>" for x in result.get("limitations", []))
    return f"""<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width">
<title>PrimerCheck Lite report</title><style>
body{{font:16px/1.55 system-ui,sans-serif;max-width:980px;margin:32px auto;padding:0 18px;color:#172554;background:#f6f8ff}}
h1{{color:#4338ca}}table{{border-collapse:collapse;width:100%;background:white;margin:10px 0 24px}}th,td{{text-align:left;padding:9px;border:1px solid #dbeafe}}th{{background:#eef2ff}}.ok{{color:#047857}}.review{{color:#b91c1c;font-weight:600}}.panel{{background:white;border-radius:12px;padding:18px;margin:16px 0}}
</style></head><body><h1>PrimerCheck Lite</h1><p>Primer screening report. Review all results in the context of your assay.</p>
<div class="panel">{rows("Forward primer", result["forward"])}{rows("Reverse primer", result["reverse"])}{rows("Primer pair", result["pair"])}</div>
<div class="panel"><h2>Items to review</h2><ul>{warnings}</ul></div>
<div class="panel"><h2>Amplicon check</h2><pre>{html.escape(json.dumps(result.get("amplicon"), indent=2))}</pre></div>
<div class="panel"><h2>Limitations</h2><ul>{limitations}</ul></div></body></html>"""


def write_html(result: dict[str, Any], path: str | Path) -> None:
    Path(path).write_text(to_html(result), encoding="utf-8")

"""Essentials in core/delivery.py: multi-outlet bullets move to the top section. Run: venv/bin/python test_essentials.py"""
from core.delivery import ESSENTIALS, _build_sections_html


def art(n, *sources):
    return {"url": f"https://x/{n}", "title": f"t{n}", "sources": list(sources)}


digest = {
    "Italy": {"text": "- solo [1]\n- due [2]\n- tre [3]\n- niente tag",
              "articles": [art(1, "ANSA"), art(2, "ANSA", "Repubblica"), art(3, "ANSA", "Libero", "Il Fatto")],
              "summaries": ["a", "b", "c"]},
    "United States": {"text": "- due [1]", "articles": [art(4, "BBC", "NPR")], "summaries": ["d"]},
}
html = _build_sections_html(digest, ["Italy", "United States"])
ess, rest = html.split('<section class="category">', 1)
assert 'id="essentials"' in ess
# most outlets first, ties in page order; single-outlet and untagged bullets stay put
assert ess.index("tre") < ess.index("due") < ess.index("x/4")
assert "solo" not in ess and "solo" in rest and "niente tag" in rest
assert 'data-section="Italy"' in ess and "Italy · 3 fonti" in ess
# moved, not copied
assert html.count("x/2") == 2 and "x/2" not in rest  # data-urls + the source link
# a section left empty by the move is dropped
assert "<h2>United States</h2>" not in html

many = {"Italy": {"text": "\n".join(f"- s{i} [{i + 1}]" for i in range(20)),
                  "articles": [art(i, "A", "B") for i in range(20)], "summaries": [""] * 20},
        "Europe": {"text": "\n".join(f"- e{i} [{i + 1}]" for i in range(20)),
                   "articles": [art(100 + i, "A", "B") for i in range(20)], "summaries": [""] * 20}}
ess = _build_sections_html(many, ["Italy", "Europe"]).split('<section class="category">', 1)[0]
assert ess.count("<li ") == 8  # 4 per section cap, fewer than ESSENTIALS left
assert ESSENTIALS == 10
# nothing with 2+ outlets: no Essentials section
assert 'id="essentials"' not in _build_sections_html({"Italy": digest["Italy"] | {"text": "- solo [1]"}}, ["Italy"])
print("ok")

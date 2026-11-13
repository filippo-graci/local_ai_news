"""Full-text filter in core/ingestion.py: paywalled pages and teasers are dropped. Run: venv/bin/python test_paywall.py"""
from core.ingestion import MIN_BODY_WORDS, PAYWALL_RE, has_full_text

assert PAYWALL_RE.search('{"@type":"NewsArticle","isAccessibleForFree": false,')
assert PAYWALL_RE.search('"isAccessibleForFree":"False"')
assert not PAYWALL_RE.search('"isAccessibleForFree": true')
assert not PAYWALL_RE.search("<p>nessun marcatore</p>")
assert not has_full_text({"body": "Titolo e due righe di anteprima. " * 3})
assert has_full_text({"body": "parola " * MIN_BODY_WORDS})
assert not has_full_text({"body": ""})
print("ok")

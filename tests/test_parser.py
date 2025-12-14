from src.olx_scraper.parser import parse_listings


SAMPLE_HTML = """
<html>
  <body>
    <a href="/item/12345" data-id="12345"><div class="_1Uo0O">$100</div>Bike for sale</a>
    <a href="/item/67890" data-id="67890"><div class="_1Uo0O">$200</div>Phone</a>
    </body>
</html>
"""




def test_parse_listings():
    results = parse_listings(SAMPLE_HTML, base_url="https://example.com")
    assert len(results) == 2
    assert results[0].id == "12345"
    
    assert "chair" in results[0].title
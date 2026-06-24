from aspose_html import URL


url = URL("https://example.com/articles?category=html")
url.search_params.set("page", "2")

print(str(url))

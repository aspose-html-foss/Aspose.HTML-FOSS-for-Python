from aspose_html.html_document import HTMLDocument
from aspose_html.dom import FormData


def test_form_data_snapshot_and_basic_methods():
    doc = HTMLDocument.parse("<form><input name='a' value='1'><input name='b' value='2'></form>")
    form = doc.query_selector("form")
    fd = FormData(form)
    assert list(fd) == [("a", "1"), ("b", "2")]
    form.query_selector("input").value = "9"
    assert fd.get("a") == "1"
    fd.append("a", "x")
    assert fd.get_all("a") == ["1", "x"]
    fd.set("a", "z")
    assert fd.get_all("a") == ["z"]
    fd.delete("a")
    assert fd.has("a") is False

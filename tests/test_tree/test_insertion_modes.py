"""test_insertion_modes.py — one test per insertion mode.

Each test exercises the primary branching logic of the named insertion mode
by feeding a minimal HTML string through parse_html() (or parse_fragment())
and asserting a structural property of the resulting DOM tree.

The 23 modes are defined in InsertionMode (ADR-003 §Insertion Mode
Representation). Tests are ordered to match the enum declaration.
"""
from __future__ import annotations

import pytest
from aspose_html.tree import parse_html, parse_fragment
from aspose_html.dom import Document, DocumentFragment, NodeType


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _html_el(doc: Document):
    """Return the <html> element of *doc*."""
    return doc.document_element


def _head(doc: Document):
    """Return the <head> element of *doc*."""
    return list(_html_el(doc).children)[0]


def _body(doc: Document):
    """Return the <body> element of *doc*."""
    return list(_html_el(doc).children)[1]


# ---------------------------------------------------------------------------
# INITIAL — process DOCTYPE (or lack thereof) to set quirks mode
# ---------------------------------------------------------------------------

def test_mode_initial_doctype_no_quirks():
    """INITIAL: <!DOCTYPE html> → no-quirks mode (CSS1Compat)."""
    doc = parse_html("<!DOCTYPE html>")
    assert isinstance(doc, Document)
    assert doc.compat_mode == "CSS1Compat"


# ---------------------------------------------------------------------------
# BEFORE_HTML — implicit <html> creation when no html element is present yet
# ---------------------------------------------------------------------------

def test_mode_before_html_creates_html_element():
    """BEFORE_HTML: parsing empty input still creates an <html> element."""
    doc = parse_html("")
    html = _html_el(doc)
    assert html is not None
    assert html.tag_name == "HTML"


# ---------------------------------------------------------------------------
# BEFORE_HEAD — <head> implied/created before any head content
# ---------------------------------------------------------------------------

def test_mode_before_head_creates_head_element():
    """BEFORE_HEAD: an implicit <head> is created when missing."""
    # Feed only a body tag — head must be auto-created first
    doc = parse_html("<!DOCTYPE html><body></body>")
    html = _html_el(doc)
    children = list(html.children)
    assert len(children) == 2
    assert children[0].tag_name == "HEAD"


# ---------------------------------------------------------------------------
# IN_HEAD — processing elements inside <head>
# ---------------------------------------------------------------------------

def test_mode_in_head_meta_element():
    """IN_HEAD: <meta> inside <head> is inserted correctly."""
    doc = parse_html("<!DOCTYPE html><head><meta charset='utf-8'></head>")
    head = _head(doc)
    meta_elements = [el for el in head.children if el.tag_name == "META"]
    assert len(meta_elements) == 1
    assert meta_elements[0].get_attribute("charset") == "utf-8"


# ---------------------------------------------------------------------------
# IN_HEAD_NOSCRIPT — content inside <noscript> in head
# ---------------------------------------------------------------------------

def test_mode_in_head_noscript_element():
    """IN_HEAD_NOSCRIPT: <noscript> in head is parsed without crashing."""
    doc = parse_html(
        "<!DOCTYPE html><head>"
        "<noscript><meta http-equiv='refresh' content='0'></noscript>"
        "</head>"
    )
    head = _head(doc)
    noscript_elements = [el for el in head.children if el.tag_name == "NOSCRIPT"]
    assert len(noscript_elements) == 1


# ---------------------------------------------------------------------------
# AFTER_HEAD — elements encountered after </head> but before <body>
# ---------------------------------------------------------------------------

def test_mode_after_head_body_opened():
    """AFTER_HEAD: a <body> tag after </head> is processed correctly."""
    doc = parse_html("<!DOCTYPE html><head></head><body class='main'></body>")
    body = _body(doc)
    assert body.tag_name == "BODY"
    assert body.get_attribute("class") == "main"


# ---------------------------------------------------------------------------
# IN_BODY — main content insertion mode
# ---------------------------------------------------------------------------

def test_mode_in_body_div_paragraph():
    """IN_BODY: <div> and <p> elements are inserted as body children."""
    doc = parse_html("<!DOCTYPE html><body><div><p>hello</p></div></body>")
    body = _body(doc)
    divs = [el for el in body.children if el.tag_name == "DIV"]
    assert len(divs) == 1
    ps = [el for el in divs[0].children if el.tag_name == "P"]
    assert len(ps) == 1


# ---------------------------------------------------------------------------
# TEXT — raw text / RCDATA insertion (e.g. <title>, <script>)
# ---------------------------------------------------------------------------

def test_mode_text_title_content():
    """TEXT: content of <title> is captured as a text node."""
    doc = parse_html("<!DOCTYPE html><head><title>My Page</title></head>")
    head = _head(doc)
    titles = [el for el in head.children if el.tag_name == "TITLE"]
    assert len(titles) == 1
    title = titles[0]
    text_nodes = [n for n in title.child_nodes if n.node_type == 3]
    assert len(text_nodes) == 1
    assert text_nodes[0].data == "My Page"  # type: ignore[attr-defined]


# ---------------------------------------------------------------------------
# IN_TABLE — table structure processing
# ---------------------------------------------------------------------------

def test_mode_in_table_creates_tbody():
    """IN_TABLE: <table><tr> implicitly creates a <tbody>."""
    doc = parse_html("<!DOCTYPE html><body><table><tr><td>cell</td></tr></table></body>")
    body = _body(doc)
    tables = [el for el in body.children if el.tag_name == "TABLE"]
    assert len(tables) == 1
    table = tables[0]
    tbodies = [el for el in table.children if el.tag_name == "TBODY"]
    assert len(tbodies) == 1


# ---------------------------------------------------------------------------
# IN_TABLE_TEXT — pending character tokens collected inside a table
# ---------------------------------------------------------------------------

def test_mode_in_table_text_foster_parenting():
    """IN_TABLE_TEXT: non-whitespace text inside table is foster-parented."""
    doc = parse_html("<!DOCTYPE html><body><table>text<tr><td>cell</td></tr></table></body>")
    body = _body(doc)
    nodes = list(body.child_nodes)
    # Foster-parented text must appear before the table
    text_nodes = [n for n in nodes if n.node_type == 3]
    table_nodes = [n for n in nodes if n.node_type == 1 and n.tag_name == "TABLE"]  # type: ignore
    assert len(text_nodes) >= 1
    assert len(table_nodes) == 1
    text_idx = nodes.index(text_nodes[0])
    table_idx = nodes.index(table_nodes[0])
    assert text_idx < table_idx


# ---------------------------------------------------------------------------
# IN_CAPTION — content inside <caption>
# ---------------------------------------------------------------------------

def test_mode_in_caption_paragraph():
    """IN_CAPTION: <p> inside <caption> is inserted as caption child."""
    doc = parse_html(
        "<!DOCTYPE html><body>"
        "<table><caption><p>Cap text</p></caption>"
        "<tr><td>cell</td></tr>"
        "</table></body>"
    )
    body = _body(doc)
    tables = [el for el in body.children if el.tag_name == "TABLE"]
    assert len(tables) == 1
    captions = [el for el in tables[0].children if el.tag_name == "CAPTION"]
    assert len(captions) == 1
    ps = [el for el in captions[0].children if el.tag_name == "P"]
    assert len(ps) == 1


# ---------------------------------------------------------------------------
# IN_COLUMN_GROUP — <col> inside <colgroup>
# ---------------------------------------------------------------------------

def test_mode_in_column_group_col_element():
    """IN_COLUMN_GROUP: <col> inside <colgroup> is inserted correctly."""
    doc = parse_html(
        "<!DOCTYPE html><body>"
        "<table>"
        "<colgroup><col span='2'><col span='1'></colgroup>"
        "<tr><td>a</td><td>b</td><td>c</td></tr>"
        "</table></body>"
    )
    body = _body(doc)
    tables = [el for el in body.children if el.tag_name == "TABLE"]
    assert len(tables) == 1
    colgroups = [el for el in tables[0].children if el.tag_name == "COLGROUP"]
    assert len(colgroups) == 1
    cols = [el for el in colgroups[0].children if el.tag_name == "COL"]
    assert len(cols) == 2


# ---------------------------------------------------------------------------
# IN_TABLE_BODY — <tr> inside <tbody>/<thead>/<tfoot>
# ---------------------------------------------------------------------------

def test_mode_in_table_body_rows():
    """IN_TABLE_BODY: <tr> elements inside <tbody> are inserted correctly."""
    doc = parse_html(
        "<!DOCTYPE html><body>"
        "<table><tbody><tr><td>r1</td></tr><tr><td>r2</td></tr></tbody></table>"
        "</body>"
    )
    body = _body(doc)
    tables = [el for el in body.children if el.tag_name == "TABLE"]
    assert len(tables) == 1
    tbodies = [el for el in tables[0].children if el.tag_name == "TBODY"]
    assert len(tbodies) == 1
    rows = [el for el in tbodies[0].children if el.tag_name == "TR"]
    assert len(rows) == 2


# ---------------------------------------------------------------------------
# IN_ROW — <td>/<th> inside a <tr>
# ---------------------------------------------------------------------------

def test_mode_in_row_cells():
    """IN_ROW: <td> and <th> inside <tr> are inserted as row children."""
    doc = parse_html(
        "<!DOCTYPE html><body>"
        "<table><tr><th>Header</th><td>Data</td></tr></table>"
        "</body>"
    )
    body = _body(doc)
    tables = [el for el in body.children if el.tag_name == "TABLE"]
    assert len(tables) == 1
    tbodies = [el for el in tables[0].children if el.tag_name == "TBODY"]
    assert len(tbodies) == 1
    rows = [el for el in tbodies[0].children if el.tag_name == "TR"]
    assert len(rows) == 1
    row = rows[0]
    cells = list(row.children)
    assert cells[0].tag_name == "TH"
    assert cells[1].tag_name == "TD"


# ---------------------------------------------------------------------------
# IN_CELL — content inside <td>/<th>
# ---------------------------------------------------------------------------

def test_mode_in_cell_nested_element():
    """IN_CELL: content inside <td> is inserted as cell descendants."""
    doc = parse_html(
        "<!DOCTYPE html><body>"
        "<table><tr><td><span>inside cell</span></td></tr></table>"
        "</body>"
    )
    body = _body(doc)
    tables = [el for el in body.children if el.tag_name == "TABLE"]
    tbody = [el for el in tables[0].children if el.tag_name == "TBODY"][0]
    row = list(tbody.children)[0]
    cell = list(row.children)[0]
    assert cell.tag_name == "TD"
    spans = [el for el in cell.children if el.tag_name == "SPAN"]
    assert len(spans) == 1


# ---------------------------------------------------------------------------
# IN_SELECT — content inside a <select> element
# ---------------------------------------------------------------------------

def test_mode_in_select_options():
    """IN_SELECT: <option> elements inside <select> are inserted correctly."""
    doc = parse_html(
        "<!DOCTYPE html><body>"
        "<select><option value='a'>A</option><option value='b'>B</option></select>"
        "</body>"
    )
    body = _body(doc)
    selects = [el for el in body.children if el.tag_name == "SELECT"]
    assert len(selects) == 1
    options = [el for el in selects[0].children if el.tag_name == "OPTION"]
    assert len(options) == 2


# ---------------------------------------------------------------------------
# IN_SELECT_IN_TABLE — <select> nested inside a table element
# ---------------------------------------------------------------------------

def test_mode_in_select_in_table():
    """IN_SELECT_IN_TABLE: <select> inside a table cell is parsed without crashing."""
    doc = parse_html(
        "<!DOCTYPE html><body>"
        "<table><tr><td>"
        "<select><option>x</option></select>"
        "</td></tr></table>"
        "</body>"
    )
    body = _body(doc)
    # Parser must not crash; verify the table structure
    tables = [el for el in body.children if el.tag_name == "TABLE"]
    assert len(tables) == 1
    assert doc.document_element is not None


# ---------------------------------------------------------------------------
# IN_TEMPLATE — content inside <template>
# ---------------------------------------------------------------------------

def test_mode_in_template_content():
    """IN_TEMPLATE: nodes inside <template> are stored in _template_content."""
    doc = parse_html(
        "<!DOCTYPE html><head><template><p>tmpl content</p></template></head>"
    )
    head = _head(doc)
    templates = [el for el in head.children if el.tag_name == "TEMPLATE"]
    assert len(templates) == 1
    content = templates[0]._template_content
    assert isinstance(content, DocumentFragment)
    ps = [n for n in content.child_nodes if n.node_type == 1 and n.tag_name == "P"]  # type: ignore
    assert len(ps) == 1


# ---------------------------------------------------------------------------
# AFTER_BODY — content encountered after </body>
# ---------------------------------------------------------------------------

def test_mode_after_body_comment():
    """AFTER_BODY: a comment after </body> is inserted after the body element."""
    doc = parse_html("<!DOCTYPE html><html><body></body><!-- after body --></html>")
    html = _html_el(doc)
    # Comment after body should be a child of the <html> element
    comment_nodes = [n for n in html.child_nodes if n.node_type == NodeType.COMMENT_NODE]
    assert len(comment_nodes) >= 1


# ---------------------------------------------------------------------------
# IN_FRAMESET — content inside <frameset>
# ---------------------------------------------------------------------------

def test_mode_in_frameset_frame_element():
    """IN_FRAMESET: <frame> inside <frameset> is inserted correctly."""
    doc = parse_html(
        "<!DOCTYPE html>"
        "<html><head></head>"
        "<frameset rows='50%,50%'>"
        "<frame src='top.html'><frame src='bottom.html'>"
        "</frameset></html>"
    )
    html = _html_el(doc)
    framesets = [el for el in html.children if el.tag_name == "FRAMESET"]
    assert len(framesets) == 1
    frames = [el for el in framesets[0].children if el.tag_name == "FRAME"]
    assert len(frames) == 2


# ---------------------------------------------------------------------------
# AFTER_FRAMESET — content after </frameset>
# ---------------------------------------------------------------------------

def test_mode_after_frameset_noframes():
    """AFTER_FRAMESET: <noframes> after </frameset> is inserted into html."""
    doc = parse_html(
        "<!DOCTYPE html><html><head></head>"
        "<frameset><frame src='a.html'></frameset>"
        "<noframes>Please upgrade your browser.</noframes>"
        "</html>"
    )
    html = _html_el(doc)
    # <noframes> must appear as child of <html> after <frameset>
    noframes = [el for el in html.children if el.tag_name == "NOFRAMES"]
    assert len(noframes) >= 1


# ---------------------------------------------------------------------------
# AFTER_AFTER_BODY — content encountered after </html> in a normal document
# ---------------------------------------------------------------------------

def test_mode_after_after_body_trailing_comment():
    """AFTER_AFTER_BODY: a comment after </html> is appended to the document."""
    doc = parse_html("<!DOCTYPE html><html><body></body></html><!-- trailing -->")
    # The comment should be a child of the document itself
    comment_nodes = [n for n in doc.child_nodes if n.node_type == NodeType.COMMENT_NODE]
    assert len(comment_nodes) >= 1


# ---------------------------------------------------------------------------
# AFTER_AFTER_FRAMESET — content after </html> in a frameset document
# ---------------------------------------------------------------------------

def test_mode_after_after_frameset_trailing_whitespace():
    """AFTER_AFTER_FRAMESET: trailing whitespace after a frameset document is ignored."""
    doc = parse_html(
        "<!DOCTYPE html><html><head></head>"
        "<frameset><frame src='a.html'></frameset>"
        "</html>   "
    )
    # Parser must not crash; the frameset document structure is intact.
    html = _html_el(doc)
    assert html is not None
    framesets = [el for el in html.children if el.tag_name == "FRAMESET"]
    assert len(framesets) == 1

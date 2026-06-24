"""User-Agent default stylesheet — default ``display`` per element type.

This is the **second worked slice** under the M7 spec-transcription-plus-WPT
build method (,  §4), following the  display-classifier
slice. It supplies the missing User-Agent (UA) cascade origin so that
:meth:`Element.get_computed_style` returns the HTML-standard default
``display`` for an element (``div`` → ``block``, ``li`` → ``list-item``,
``table`` → ``table``, ``head``/``script`` → ``none``, …) instead of the CSS
§2 initial value ``inline`` for everything.

Scope is **default ``display`` only** (): margins, fonts,
``list-style-*``, ``white-space``, presentational-hint attribute mappings, and
the form-control ``display`` rules (§15.3.5 / Form controls) are deliberately
out of scope and recorded for future slices.

Provenance (). Every entry below is transcribed **verbatim** from the
WHATWG HTML Rendering spec, cached at ``docs/specs/html-rendering/``
(``FETCHED.txt``: source <https://html.spec.whatwg.org/multipage/rendering.html>,
fetched 2026-05-26T04:15:45Z, sha256 ``aecf826742c661a498548753b6640708527a4445b92c7fd60a7b4b6c9d65b59e``,
size 359602 bytes). Each table entry names the §15.3.x subsection it was
transcribed from. No value is hand-authored from memory; a tag with no §15.3
``display`` rule is **absent** from the table and falls through to the CSS §2
initial ``inline`` (this is correct, not an omission — §15.3 defines no
``display`` for ``span``/``a``/``em``/… so ``inline`` is their right default).

Leaf module (, mirrors the ``_style.py`` discipline): no runtime
``aspose_html`` imports at module load; :class:`Element` is imported only under
``TYPE_CHECKING``.
"""
from __future__ import annotations

from types import MappingProxyType
from typing import TYPE_CHECKING, Iterator, Mapping

if TYPE_CHECKING:  # pragma: no cover - typing only, no runtime import
    from aspose_html.dom._element import Element


#: Lower-case tag name → UA default ``display`` string, transcribed verbatim
#: from WHATWG HTML §15.3. Immutable module-level constant ( — a
#: ``MappingProxyType`` cannot be mutated). Each entry is annotated with the
#: §15.3.x subsection it was transcribed from ( citation discipline).
#:
#: Tags deliberately ABSENT (no §15.3 ``display`` rule → CSS §2 initial
#: ``inline``): ``span``, ``a``, ``em``, ``strong``, ``cite``, ``dfn``, ``i``,
#: ``var``, ``b``, ``code``, ``kbd``, ``samp``, ``tt``, ``big``, ``small``,
#: ``sub``, ``sup``, and every unknown/custom tag.
_UA_DISPLAY: Mapping[str, str] = MappingProxyType(
    {
        # --- §15.3.1 Hidden elements (index.html lines 200-203) ----------
        #     area, base, basefont, datalist, head, link, meta, noembed,
        #     noframes, param, rp, script, style, template, title {
        #       display: none; }
        "area": "none",
        "base": "none",
        "basefont": "none",
        "datalist": "none",
        "head": "none",
        "link": "none",
        "meta": "none",
        "noembed": "none",
        "noframes": "none",
        "param": "none",
        "rp": "none",
        "script": "none",
        "style": "none",
        "template": "none",
        "title": "none",
        # (input[type=hidden i] { display: none !important } — the one
        #  in-scope attribute selector — is handled in ua_declarations_for,
        #  NOT as a type-selector entry here.)
        # --- §15.3.2 The page (index.html line 226) ----------------------
        #     html, body { display: block; }
        "html": "block",
        "body": "block",
        # --- §15.3.3 Flow content (index.html lines 345-348, 412-414) ----
        #     address, blockquote, center, dialog, div, figure, figcaption,
        #     footer, form, header, hr, legend, listing, main, p, plaintext,
        #     pre, search, xmp { display: block; }
        "address": "block",
        "blockquote": "block",
        "center": "block",
        "dialog": "block",
        "div": "block",
        "figure": "block",
        "figcaption": "block",
        "footer": "block",
        "form": "block",
        "header": "block",
        "hr": "block",
        "legend": "block",
        "listing": "block",
        "main": "block",
        "p": "block",
        "plaintext": "block",
        "pre": "block",
        "search": "block",
        "xmp": "block",
        #     slot { display: contents; }
        "slot": "contents",
        # --- §15.3.4 Phrasing content (index.html lines 471-472) ---------
        #     ruby { display: ruby; }
        #     rt { display: ruby-text; }
        # (The other §15.3.4 rules set font-*/vertical-align, NOT display,
        #  so cite/dfn/em/i/var/b/strong/code/kbd/samp/tt/big/small/sub/sup
        #  carry no UA display and resolve to the §2 initial inline.)
        "ruby": "ruby",
        "rt": "ruby-text",
        # --- §15.3.6 Sections and headings (index.html lines 656-658) ----
        #     article, aside, :heading, hgroup, nav, section {
        #       display: block; }
        # The :heading pseudo-class matches the heading elements h1-h6 in
        # HTML; transcribed to the concrete tag list (this slice has no
        # :heading matcher and §15.3.6 intends exactly h1-h6).
        "article": "block",
        "aside": "block",
        "h1": "block",
        "h2": "block",
        "h3": "block",
        "h4": "block",
        "h5": "block",
        "h6": "block",
        "hgroup": "block",
        "nav": "block",
        "section": "block",
        # --- §15.3.7 Lists (index.html lines 679-680) --------------------
        #     dir, dd, dl, dt, menu, ol, ul { display: block; }
        #     li { display: list-item; text-align: match-parent; }
        # (text-align is not a display rule and is out of scope; only the
        #  display value is transcribed.)
        "dir": "block",
        "dd": "block",
        "dl": "block",
        "dt": "block",
        "menu": "block",
        "ol": "block",
        "ul": "block",
        "li": "list-item",
        # --- §15.3.8 Tables (index.html lines 773-781) -------------------
        #     table { display: table; }
        #     caption { display: table-caption; }
        #     colgroup, colgroup[hidden] { display: table-column-group; }
        #     col, col[hidden] { display: table-column; }
        #     thead, thead[hidden] { display: table-header-group; }
        #     tbody, tbody[hidden] { display: table-row-group; }
        #     tfoot, tfoot[hidden] { display: table-footer-group; }
        #     tr, tr[hidden] { display: table-row; }
        #     td, th { display: table-cell; }
        # The [hidden] variants set the same display as the bare type
        # selector, so the bare type-selector mapping suffices for the
        # display default.
        "table": "table",
        "caption": "table-caption",
        "colgroup": "table-column-group",
        "col": "table-column",
        "thead": "table-header-group",
        "tbody": "table-row-group",
        "tfoot": "table-footer-group",
        "tr": "table-row",
        "td": "table-cell",
        "th": "table-cell",
    }
)


def ua_display_for(tag_name: str) -> str | None:
    """Return the UA default ``display`` for *tag_name*, or ``None``.

    *tag_name* is matched case-insensitively (lower-cased). Returns the
    verbatim §15.3 ``display`` string for a tag with a UA rule, or ``None``
    when §15.3 defines no ``display`` default for it — in which case the
    caller falls through to the CSS §2 initial value ``inline``.

    Pure and deterministic.

    Examples
    --------
    >>> ua_display_for("div")
    'block'
    >>> ua_display_for("DIV")
    'block'
    >>> ua_display_for("li")
    'list-item'
    >>> ua_display_for("td")
    'table-cell'
    >>> ua_display_for("head")
    'none'
    >>> ua_display_for("span") is None
    True
    >>> ua_display_for("my-custom-element") is None
    True
    """
    return _UA_DISPLAY.get(tag_name.strip().lower())


def ua_declarations_for(element: "Element") -> Iterator[tuple[str, str, bool]]:
    """Yield ``(property, value, important)`` UA declarations for *element*.

    Reads the element's tag name (``local_name``, already lower-case) and,
    for the one in-scope attribute selector, its ``type`` attribute. Reads
    only — never mutates DOM structure ().

    Yields at most a single ``display`` declaration:

    * ``("display", "none", True)`` for ``input[type=hidden i]`` — the one
      in-scope ``!important`` UA rule (§15.3.1). Handled as a narrow
      special case (tag is ``input`` and the ``type`` attribute equals
      ``hidden``, ASCII case-insensitive), NOT via general attribute-selector
      machinery.
    * ``("display", <value>, False)`` for a type-selector match in
      :data:`_UA_DISPLAY`.

    Yields nothing when no UA rule matches (caller relies on the §2 initial).

    Examples
    --------
    >>> from aspose_html.dom import Document
    >>> doc = Document()
    >>> div = doc.create_element("div")
    >>> list(ua_declarations_for(div))
    [('display', 'block', False)]
    >>> span = doc.create_element("span")
    >>> list(ua_declarations_for(span))
    []
    >>> hidden = doc.create_element("input")
    >>> hidden.set_attribute("type", "hidden")
    >>> list(ua_declarations_for(hidden))
    [('display', 'none', True)]
    >>> text_input = doc.create_element("input")
    >>> text_input.set_attribute("type", "text")
    >>> list(ua_declarations_for(text_input))
    []
    """
    tag = element.local_name.lower()

    # §15.3.1: input[type=hidden i] { display: none !important; }
    # Narrow special case for the one in-scope attribute selector — NOT a
    # general attribute-selector matcher. ASCII case-insensitive `type`
    # comparison per the `i` flag in the spec selector.
    if tag == "input":
        type_attr = element.get_attribute("type")
        if type_attr is not None and type_attr.strip().lower() == "hidden":
            yield ("display", "none", True)
            return
        # Other input types have no in-scope UA display rule; `input`
        # itself is not in _UA_DISPLAY, so nothing is yielded → §2 initial.
        return

    value = _UA_DISPLAY.get(tag)
    if value is not None:
        yield ("display", value, False)

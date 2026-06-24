# Public API

This document summarizes the primary public surface of Aspose.HTML FOSS for Python.

## Top-Level Package

- `aspose_html.HTMLDocument`
- `aspose_html.serialise`
- `aspose_html.DOMParser`
- `aspose_html.XMLSerializer`
- `aspose_html.URL`
- `aspose_html.URLSearchParams`
- `aspose_html.URLParseError`

## HTML Documents

- `HTMLDocument.parse(html, *, encoding=None, base_url=None)`
- `HTMLDocument.parse_fragment(html, context_element=None, *, encoding=None)`
- `HTMLDocument.load(path)`

## DOM

Important classes are exported from `aspose_html.dom`:

- Core nodes: `Document`, `Element`, `Node`, `DocumentFragment`, `DocumentType`, `Attr`
- Character data: `Text`, `Comment`, `CDATASection`, `ProcessingInstruction`
- Collections: `NodeList`, `HTMLCollection`, `NamedNodeMap`, `HTMLOptionsCollection`
- DOM parsing and serialization: `DOMParser`, `XMLSerializer`
- Events: `Event`, `CustomEvent`, `MouseEvent`, `KeyboardEvent`, `FocusEvent`, `InputEvent`, `ErrorEvent`
- Traversal and ranges: `TreeWalker`, `NodeIterator`, `Range`, `StaticRange`, `Selection`
- HTML elements: `HTMLElement` and common specialized element classes such as `HTMLAnchorElement`, `HTMLFormElement`, `HTMLInputElement`, `HTMLSelectElement`, `HTMLTableElement`, and related table/list/text/media classes

## CSS And CSSOM

- `aspose_html.css.parse`
- `aspose_html.cssom.CSSStyleSheet`
- CSS rule and declaration objects exported from `aspose_html.cssom`
- `Element.get_computed_style()` for document-oriented style workflows

## URL

- `aspose_html.URL`
- `aspose_html.URLSearchParams`
- `aspose_html.URLParseError`

## JavaScript Bridge

The `aspose_html.js` package is optional and requires the `quickjs` extra:

```bash
pip install aspose-html-foss[js]
```

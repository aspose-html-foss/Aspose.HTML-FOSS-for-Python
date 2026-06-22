"""Sectioning and structural element classes.

Contains ``HTMLHtmlElement``, ``HTMLHeadElement``, ``HTMLBodyElement``,
``HTMLBRElement``, ``HTMLHRElement``, ``HTMLPreElement``, ``HTMLModElement``,
``HTMLDetailsElement``, ``HTMLDialogElement``, ``HTMLSummaryElement``,
``HTMLMenuElement``, ``HTMLTemplateElement``, ``HTMLNavElement``,
``HTMLSectionElement``, ``HTMLArticleElement``, ``HTMLAsideElement``,
``HTMLHeaderElement``, ``HTMLFooterElement``, ``HTMLMainElement``,
``HTMLFigureElement``, ``HTMLFigCaptionElement``, ``HTMLAddressElement``,
``HTMLWBRElement``, ``HTMLNoScriptElement``, ``HTMLMarkElement``,
``HTMLSmallElement``, ``HTMLRubyElement``.

See ADR-304 for the split rationale.
"""
from __future__ import annotations

from aspose_html.dom._html_element import HTMLElement


# ---------------------------------------------------------------------------
# HTMLDetailsElement  (BACK-43 / ADR-037)
# ---------------------------------------------------------------------------

class HTMLDetailsElement(HTMLElement):
    """HTML ``<details>`` disclosure widget element.

    Reflects IDL attribute: open (boolean presence attribute).

    Examples
    --------
    >>> from aspose_html.dom import Document
    >>> doc = Document()
    >>> det = doc.create_element("details")
    >>> isinstance(det, HTMLDetailsElement)
    True
    >>> det.open
    False
    >>> det.open = True
    >>> det.open
    True
    """

    __slots__ = ()

    @property
    def name(self) -> str:
        """The ``name`` attribute value, or ``''`` when absent.

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> doc = Document()
        >>> det = doc.create_element("details")
        >>> det.name
        ''
        >>> det.name = "faq-group"
        >>> det.name
        'faq-group'
        """
        return self.get_attribute("name") or ""

    @name.setter
    def name(self, value: str) -> None:
        self.set_attribute("name", value)

    @property
    def open(self) -> bool:
        """Boolean presence attribute ``open``.

        ``open`` is not a Python keyword, so no aliasing is needed.
        Per WHATWG HTML §4.11.1.

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> doc = Document()
        >>> det = doc.create_element("details")
        >>> det.open
        False
        >>> det.open = True
        >>> det.open
        True
        >>> det.open = False
        >>> det.open
        False
        """
        return self.has_attribute("open")

    @open.setter
    def open(self, value: bool) -> None:
        if value:
            self.set_attribute("open", "")
        else:
            self.remove_attribute("open")


# ---------------------------------------------------------------------------
# HTMLDialogElement  (BACK-43 / ADR-037)
# ---------------------------------------------------------------------------

class HTMLDialogElement(HTMLElement):
    """HTML ``<dialog>`` modal/non-modal dialog element.

    Reflects IDL attribute: open (boolean presence attribute).

    Examples
    --------
    >>> from aspose_html.dom import Document
    >>> doc = Document()
    >>> dlg = doc.create_element("dialog")
    >>> isinstance(dlg, HTMLDialogElement)
    True
    >>> dlg.open
    False
    >>> dlg.open = True
    >>> dlg.open
    True
    """

    __slots__ = ()

    @property
    def open(self) -> bool:
        """Boolean presence attribute ``open``.

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> doc = Document()
        >>> dlg = doc.create_element("dialog")
        >>> dlg.open
        False
        >>> dlg.open = True
        >>> dlg.open
        True
        """
        return self.has_attribute("open")

    @open.setter
    def open(self, value: bool) -> None:
        if value:
            self.set_attribute("open", "")
        else:
            self.remove_attribute("open")

    # --- return_value / show / show_modal / close (BACK-229 / ADR-212) ---

    @property
    def return_value(self) -> str:
        """The dialog's return value set by ``close()``.

        Reflects the ``returnvalue`` content attribute.  Returns ``""`` when
        the attribute is absent.

        WHATWG HTML §4.11.1.

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> doc = Document()
        >>> dlg = doc.create_element("dialog")
        >>> dlg.return_value
        ''
        >>> dlg.return_value = 'cancel'
        >>> dlg.return_value
        'cancel'
        """
        return self.get_attribute("returnvalue") or ""

    @return_value.setter
    def return_value(self, value: str) -> None:
        self.set_attribute("returnvalue", value)

    def show(self) -> None:
        """Open the dialog element in non-modal mode (headless stub).

        Sets the ``open`` presence attribute.  In a headless environment there
        is no visual rendering, modal blocking, or top-layer behavior.

        WHATWG HTML §4.11.1.  .NET parity: ``HTMLDialogElement.Show()``.

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> doc = Document()
        >>> dlg = doc.create_element("dialog")
        >>> dlg.open
        False
        >>> dlg.show()
        >>> dlg.open
        True
        """
        self.set_attribute("open", "")

    def show_modal(self) -> None:
        """Open the dialog element in modal mode (headless stub).

        Sets the ``open`` presence attribute.  In a headless environment there
        is no top-layer, backdrop, or focus trapping.  The behavior is
        identical to ``show()``.

        WHATWG HTML §4.11.1.  .NET parity: ``HTMLDialogElement.ShowModal()``.

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> doc = Document()
        >>> dlg = doc.create_element("dialog")
        >>> dlg.show_modal()
        >>> dlg.open
        True
        """
        self.set_attribute("open", "")

    def close(self, return_value: str = "") -> None:
        """Close the dialog and optionally record a return value.

        Removes the ``open`` presence attribute and sets the ``returnvalue``
        content attribute to *return_value*.

        WHATWG HTML §4.11.1.  .NET parity: ``HTMLDialogElement.Close(returnValue)``.

        Parameters
        ----------
        return_value:
            String to store as the dialog's return value.  Default ``""``.

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> doc = Document()
        >>> dlg = doc.create_element("dialog")
        >>> dlg.show()
        >>> dlg.close("ok")
        >>> dlg.open
        False
        >>> dlg.return_value
        'ok'
        """
        self.remove_attribute("open")
        self.set_attribute("returnvalue", return_value)


# ---------------------------------------------------------------------------
# Structural + semantic subclasses (BACK-58)
# ---------------------------------------------------------------------------

class HTMLHtmlElement(HTMLElement):
    """HTML ``<html>`` document element (structural subclass).

    Examples
    --------
    >>> from aspose_html.dom import Document
    >>> doc = Document()
    >>> isinstance(doc.create_element("html"), HTMLHtmlElement)
    True
    """

    __slots__ = ()


class HTMLHeadElement(HTMLElement):
    """HTML ``<head>`` element (structural subclass).

    Examples
    --------
    >>> from aspose_html.dom import Document
    >>> doc = Document()
    >>> isinstance(doc.create_element("head"), HTMLHeadElement)
    True
    """

    __slots__ = ()


class HTMLBodyElement(HTMLElement):
    """HTML ``<body>`` element (structural subclass).

    Examples
    --------
    >>> from aspose_html.dom import Document
    >>> doc = Document()
    >>> isinstance(doc.create_element("body"), HTMLBodyElement)
    True
    """

    __slots__ = ()

    @property
    def background(self) -> str:
        """Reflect the ``background`` content attribute (WHATWG HTML §4.3.1).

        Examples
        --------
        >>> from aspose_html.dom._document import Document
        >>> doc = Document(); el = doc.create_element('body')
        >>> el.background
        ''
        """
        return self.get_attribute("background") or ""

    @background.setter
    def background(self, value: str) -> None:
        self.set_attribute("background", value)

    @property
    def bg_color(self) -> str:
        """Reflect the ``bgcolor`` content attribute (WHATWG HTML §4.3.1).

        Examples
        --------
        >>> from aspose_html.dom._document import Document
        >>> doc = Document(); el = doc.create_element('body')
        >>> el.bg_color
        ''
        """
        return self.get_attribute("bgcolor") or ""

    @bg_color.setter
    def bg_color(self, value: str) -> None:
        self.set_attribute("bgcolor", value)

    @property
    def text(self) -> str:
        """Reflect the ``text`` content attribute (WHATWG HTML §4.3.1).

        Examples
        --------
        >>> from aspose_html.dom._document import Document
        >>> doc = Document(); el = doc.create_element('body')
        >>> el.text
        ''
        """
        return self.get_attribute("text") or ""

    @text.setter
    def text(self, value: str) -> None:
        self.set_attribute("text", value)

    @property
    def link(self) -> str:
        """Reflect the ``link`` content attribute (WHATWG HTML §4.3.1).

        Examples
        --------
        >>> from aspose_html.dom._document import Document
        >>> doc = Document(); el = doc.create_element('body')
        >>> el.link
        ''
        """
        return self.get_attribute("link") or ""

    @link.setter
    def link(self, value: str) -> None:
        self.set_attribute("link", value)

    @property
    def v_link(self) -> str:
        """Reflect the ``vlink`` content attribute (WHATWG HTML §4.3.1).

        Examples
        --------
        >>> from aspose_html.dom._document import Document
        >>> doc = Document(); el = doc.create_element('body')
        >>> el.v_link
        ''
        """
        return self.get_attribute("vlink") or ""

    @v_link.setter
    def v_link(self, value: str) -> None:
        self.set_attribute("vlink", value)

    @property
    def a_link(self) -> str:
        """Reflect the ``alink`` content attribute (WHATWG HTML §4.3.1).

        Examples
        --------
        >>> from aspose_html.dom._document import Document
        >>> doc = Document(); el = doc.create_element('body')
        >>> el.a_link
        ''
        """
        return self.get_attribute("alink") or ""

    @a_link.setter
    def a_link(self, value: str) -> None:
        self.set_attribute("alink", value)


class HTMLBRElement(HTMLElement):
    """HTML ``<br>`` line-break element (structural subclass).

    Examples
    --------
    >>> from aspose_html.dom import Document
    >>> doc = Document()
    >>> isinstance(doc.create_element("br"), HTMLBRElement)
    True
    """

    __slots__ = ()


class HTMLHRElement(HTMLElement):
    """HTML ``<hr>`` thematic-break element (structural subclass).

    Examples
    --------
    >>> from aspose_html.dom import Document
    >>> doc = Document()
    >>> isinstance(doc.create_element("hr"), HTMLHRElement)
    True
    """

    __slots__ = ()


class HTMLPreElement(HTMLElement):
    """HTML ``<pre>`` preformatted text element (structural subclass).

    Also used for legacy tags ``<listing>`` and ``<xmp>`` in registry dispatch.

    Examples
    --------
    >>> from aspose_html.dom import Document
    >>> doc = Document()
    >>> isinstance(doc.create_element("pre"), HTMLPreElement)
    True
    """

    __slots__ = ()



class HTMLModElement(HTMLElement):
    """HTML ``<ins>``/``<del>`` modification element.

    Reflects IDL attributes: ``cite`` and ``date_time`` (``datetime`` attribute).
    """

    __slots__ = ()

    @property
    def cite(self) -> str:
        """The ``cite`` attribute value, or ``''`` when absent.

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> doc = Document()
        >>> mod = doc.create_element("ins")
        >>> mod.cite
        ''
        >>> mod.cite = "https://example.com/changelog"
        >>> mod.cite
        'https://example.com/changelog'
        """
        return self.get_attribute("cite") or ""

    @cite.setter
    def cite(self, value: str) -> None:
        self.set_attribute("cite", value)

    @property
    def date_time(self) -> str:
        """The ``datetime`` attribute value, or ``''`` when absent.

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> doc = Document()
        >>> mod = doc.create_element("del")
        >>> mod.date_time
        ''
        >>> mod.date_time = "2026-05-05"
        >>> mod.get_attribute("datetime")
        '2026-05-05'
        """
        return self.get_attribute("datetime") or ""

    @date_time.setter
    def date_time(self, value: str) -> None:
        self.set_attribute("datetime", value)


# ---------------------------------------------------------------------------
# Embedding elements — SPEC-049 / ADR-053
# ---------------------------------------------------------------------------


class HTMLNavElement(HTMLElement):
    """HTML ``<nav>`` element.

    Examples
    --------
    >>> from aspose_html.dom import Document, HTMLNavElement
    >>> isinstance(Document().create_element("nav"), HTMLNavElement)
    True
    """

    __slots__ = ()


class HTMLSectionElement(HTMLElement):
    """HTML ``<section>`` element."""

    __slots__ = ()


class HTMLArticleElement(HTMLElement):
    """HTML ``<article>`` element."""

    __slots__ = ()


class HTMLAsideElement(HTMLElement):
    """HTML ``<aside>`` element."""

    __slots__ = ()


class HTMLHeaderElement(HTMLElement):
    """HTML ``<header>`` element."""

    __slots__ = ()


class HTMLFooterElement(HTMLElement):
    """HTML ``<footer>`` element."""

    __slots__ = ()


class HTMLMainElement(HTMLElement):
    """HTML ``<main>`` element."""

    __slots__ = ()


class HTMLFigureElement(HTMLElement):
    """HTML ``<figure>`` element."""

    __slots__ = ()


class HTMLFigCaptionElement(HTMLElement):
    """HTML ``<figcaption>`` element."""

    __slots__ = ()


class HTMLAddressElement(HTMLElement):
    """HTML ``<address>`` element."""

    __slots__ = ()


class HTMLWBRElement(HTMLElement):
    """HTML ``<wbr>`` element."""

    __slots__ = ()


class HTMLNoScriptElement(HTMLElement):
    """HTML ``<noscript>`` element."""

    __slots__ = ()


class HTMLMarkElement(HTMLElement):
    """HTML ``<mark>`` element."""

    __slots__ = ()


class HTMLSmallElement(HTMLElement):
    """HTML ``<small>`` element."""

    __slots__ = ()


class HTMLRubyElement(HTMLElement):
    """HTML ``<ruby>``/``<rt>``/``<rp>`` element."""

    __slots__ = ()



# ---------------------------------------------------------------------------
# HTMLSummaryElement  (BACK-187 / ADR-170)
# ---------------------------------------------------------------------------

class HTMLSummaryElement(HTMLElement):
    """Represents an HTML ``<summary>`` element.

    The ``<summary>`` element is a disclosure summary for a ``<details>``
    widget. It carries no IDL-reflected attributes beyond those inherited
    from :class:`HTMLElement`.

    Examples
    --------
    >>> from aspose_html.dom import Document
    >>> doc = Document()
    >>> el = doc.create_element("summary")
    >>> from aspose_html.dom import HTMLSummaryElement
    >>> isinstance(el, HTMLSummaryElement)
    True
    >>> el.tag_name
    'SUMMARY'
    """

    __slots__ = ()


# ---------------------------------------------------------------------------
# HTMLMenuElement  (BACK-187 / ADR-170)
# ---------------------------------------------------------------------------

class HTMLMenuElement(HTMLElement):
    """Represents an HTML ``<menu>`` element.

    The ``<menu>`` element represents a toolbar consisting of its contents
    (WHATWG HTML §4.11.1). It carries no IDL-reflected attributes beyond
    those inherited from :class:`HTMLElement`.

    Examples
    --------
    >>> from aspose_html.dom import Document
    >>> doc = Document()
    >>> el = doc.create_element("menu")
    >>> from aspose_html.dom import HTMLMenuElement
    >>> isinstance(el, HTMLMenuElement)
    True
    >>> el.tag_name
    'MENU'
    """

    __slots__ = ()


# ---------------------------------------------------------------------------
# HTMLTemplateElement  (BACK-44 / ADR-038)
# ---------------------------------------------------------------------------

class HTMLTemplateElement(HTMLElement):
    """HTML ``<template>`` element holding inert content.

    The ``content`` property returns the ``DocumentFragment`` that holds the
    template's child nodes.  For parsed templates the fragment is populated
    by the tree builder (ADR-003).  For programmatically created templates
    the first access to ``content`` creates an empty ``DocumentFragment``
    owned by the element's owner document (or a standalone fragment if the
    element is detached).

    Examples
    --------
    >>> from aspose_html.dom import Document
    >>> doc = Document()
    >>> tmpl = doc.create_element("template")
    >>> isinstance(tmpl, HTMLTemplateElement)
    True
    >>> from aspose_html.dom._document_fragment import DocumentFragment
    >>> isinstance(tmpl.content, DocumentFragment)
    True
    >>> tmpl.content is tmpl.content
    True
    """

    __slots__ = ()

    @property
    def content(self) -> "DocumentFragment":
        """The template's content ``DocumentFragment``.

        For templates parsed from HTML, this returns the ``DocumentFragment``
        populated by the tree builder (ADR-003).  For programmatically created
        templates, the first access creates an empty ``DocumentFragment``
        and caches it in the ``_template_content`` slot.

        Subsequent calls always return the same fragment object.

        Returns
        -------
        DocumentFragment
            The content fragment (never ``None``).

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> doc = Document()
        >>> tmpl = doc.create_element("template")
        >>> tmpl.content is tmpl.content
        True
        >>> from aspose_html.dom._document_fragment import DocumentFragment
        >>> isinstance(tmpl.content, DocumentFragment)
        True
        """
        from aspose_html.dom._document_fragment import DocumentFragment  # noqa: PLC0415

        # Use getattr defensively — _template_content is declared in Element.__slots__
        # but may be uninitialized in edge cases (e.g. deserialization). See ADR-038.
        tc = getattr(self, "_template_content", None)
        if tc is None:
            doc = self._owner_document
            if doc is not None:
                tc = doc.create_document_fragment()
            else:
                tc = DocumentFragment()
            # Write directly to the inherited slot.  object.__setattr__ is used for
            # explicitness and safety under hypothetical future __setattr__ overrides.
            # Both this form and self._template_content = tc work with __slots__. See ADR-038.
            object.__setattr__(self, "_template_content", tc)
        return tc  # type: ignore[return-value]

    def _clone_self(self) -> "HTMLTemplateElement":
        """Clone this template element (attributes only, no content).

        Overrides HTMLElement._clone_self() to create the typed clone.
        Content cloning is handled by clone_node() below.  See ADR-038.
        """
        # Create a shallow clone with attributes via parent class dispatch.
        clone: HTMLTemplateElement = super()._clone_self()  # type: ignore[assignment]
        # _template_content is NOT copied here — content is only copied in
        # clone_node(deep=True), per WHATWG DOM cloning-steps for <template>.
        return clone

    def clone_node(self, deep: bool = False) -> "HTMLTemplateElement":
        """Return a copy of this template element.

        When *deep* is ``True``, also deep-clones the ``content``
        ``DocumentFragment`` (which is not a regular child and would not
        be covered by the base ``clone_node`` child loop).

        Per WHATWG HTML §4.12.3 template cloning steps.

        Parameters
        ----------
        deep : bool, optional
            If ``True``, clone the entire subtree including template content.
            Defaults to ``False``.

        Returns
        -------
        HTMLTemplateElement
            A new template element with the same attributes and, when deep,
            the same content.

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> doc = Document()
        >>> tmpl = doc.create_element("template")
        >>> clone = tmpl.clone_node(deep=True)
        >>> isinstance(clone, HTMLTemplateElement)
        True
        >>> clone is not tmpl
        True
        """
        clone: HTMLTemplateElement = super().clone_node(deep=deep)  # type: ignore[assignment]
        if deep and self._template_content is not None:
            # Deep-clone the content fragment and assign to the clone's slot.
            # This must be done AFTER super().clone_node() has called _clone_self()
            # (which created the clone) and iterated _children (empty for template).
            cloned_frag = self._template_content.clone_node(deep=True)
            object.__setattr__(clone, "_template_content", cloned_frag)
        return clone


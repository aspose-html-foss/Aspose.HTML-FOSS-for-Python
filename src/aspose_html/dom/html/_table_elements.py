"""Table element classes.

Contains ``HTMLTableElement``, ``HTMLTableSectionElement``,
``HTMLTableRowElement``, ``HTMLTableCellElement``,
``HTMLTableCaptionElement``, ``HTMLTableColElement``.

See ADR-304 for the split rationale.
"""
from __future__ import annotations

import re

from aspose_html.dom._html_element import HTMLElement


# ---------------------------------------------------------------------------
# HTMLTableElement and table-related subclasses  (BACK-35 / ADR-031)
# ---------------------------------------------------------------------------

class HTMLTableElement(HTMLElement):
    """HTML ``<table>`` element.

    Provides live collection properties for navigating table structure.

    Examples
    --------
    >>> from aspose_html.dom import Document, HTMLTableElement
    >>> doc = Document()
    >>> table = doc.create_element("table")
    >>> isinstance(table, HTMLTableElement)
    True
    """

    __slots__ = ()

    @property
    def border(self) -> str:
        """String IDL attribute reflecting ``'border'``. Default ``""``."""
        return self.get_attribute("border") or ""

    @border.setter
    def border(self, value: str) -> None:
        self.set_attribute("border", value)

    @property
    def width(self) -> str:
        """String IDL attribute reflecting ``'width'``. Default ``""``."""
        return self.get_attribute("width") or ""

    @width.setter
    def width(self, value: str) -> None:
        self.set_attribute("width", value)

    @property
    def summary(self) -> str:
        """String IDL attribute reflecting ``'summary'``. Default ``""``."""
        return self.get_attribute("summary") or ""

    @summary.setter
    def summary(self, value: str) -> None:
        self.set_attribute("summary", value)

    @property
    def frame(self) -> str:
        """Reflect the ``frame`` content attribute (WHATWG HTML §4.9.1).

        Examples
        --------
        >>> from aspose_html.dom._document import Document
        >>> doc = Document(); el = doc.create_element('table')
        >>> el.frame
        ''
        >>> el.set_attribute('frame', 'box'); el.frame
        'box'
        """
        return self.get_attribute("frame") or ""

    @frame.setter
    def frame(self, value: str) -> None:
        self.set_attribute("frame", value)

    @property
    def rules(self) -> str:
        """Reflect the ``rules`` content attribute (WHATWG HTML §4.9.1).

        Examples
        --------
        >>> from aspose_html.dom._document import Document
        >>> doc = Document(); el = doc.create_element('table')
        >>> el.rules
        ''
        """
        return self.get_attribute("rules") or ""

    @rules.setter
    def rules(self, value: str) -> None:
        self.set_attribute("rules", value)

    @property
    def bg_color(self) -> str:
        """Reflect the ``bgcolor`` content attribute (WHATWG HTML §4.9.1).

        Examples
        --------
        >>> from aspose_html.dom._document import Document
        >>> doc = Document(); el = doc.create_element('table')
        >>> el.bg_color
        ''
        """
        return self.get_attribute("bgcolor") or ""

    @bg_color.setter
    def bg_color(self, value: str) -> None:
        self.set_attribute("bgcolor", value)

    @property
    def cell_padding(self) -> str:
        """Reflect the ``cellpadding`` content attribute (WHATWG HTML §4.9.1).

        Examples
        --------
        >>> from aspose_html.dom._document import Document
        >>> doc = Document(); el = doc.create_element('table')
        >>> el.cell_padding
        ''
        """
        return self.get_attribute("cellpadding") or ""

    @cell_padding.setter
    def cell_padding(self, value: str) -> None:
        self.set_attribute("cellpadding", value)

    @property
    def cell_spacing(self) -> str:
        """Reflect the ``cellspacing`` content attribute (WHATWG HTML §4.9.1).

        Examples
        --------
        >>> from aspose_html.dom._document import Document
        >>> doc = Document(); el = doc.create_element('table')
        >>> el.cell_spacing
        ''
        """
        return self.get_attribute("cellspacing") or ""

    @cell_spacing.setter
    def cell_spacing(self, value: str) -> None:
        self.set_attribute("cellspacing", value)

    @property
    def caption(self) -> "HTMLTableCaptionElement | None":
        """First ``<caption>`` direct child, or ``None``."""
        for child in self._children:
            if getattr(child, "_tag_name", None) == "CAPTION":
                return child  # type: ignore[return-value]
        return None

    @property
    def t_head(self) -> "HTMLTableSectionElement | None":
        """First ``<thead>`` direct child, or ``None``."""
        for child in self._children:
            if getattr(child, "_tag_name", None) == "THEAD":
                return child  # type: ignore[return-value]
        return None

    @property
    def t_foot(self) -> "HTMLTableSectionElement | None":
        """First ``<tfoot>`` direct child, or ``None``."""
        for child in self._children:
            if getattr(child, "_tag_name", None) == "TFOOT":
                return child  # type: ignore[return-value]
        return None

    @property
    def t_bodies(self) -> object:
        """Live collection of ``<tbody>`` direct children."""
        from aspose_html.dom._collections import _SubtreeHTMLCollection  # noqa: PLC0415
        self_ref = self
        return _SubtreeHTMLCollection(
            self,
            lambda el: getattr(el, "_tag_name", None) == "TBODY"
            and el._parent is self_ref,
        )

    @property
    def tbodies(self) -> object:
        """Alias for :attr:`t_bodies` (WHATWG HTML §4.9.1 IDL name ``tBodies``).

        Returns the same live collection of ``<tbody>`` direct children.
        Provided so that code using the camelCase IDL spelling works identically
        to code using the snake_case spelling.

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> doc = Document()
        >>> table = doc.create_element("table")
        >>> len(table.tbodies)
        0
        """
        return self.t_bodies

    @property
    def rows(self) -> object:
        """Live collection of all ``<tr>`` elements in tree order."""
        from aspose_html.dom._collections import _SubtreeHTMLCollection  # noqa: PLC0415
        return _SubtreeHTMLCollection(
            self,
            lambda el: getattr(el, "_tag_name", None) == "TR",
        )

    def insert_row(self, index: int = -1) -> "HTMLTableRowElement":
        """Insert a new ``<tr>`` at *index* in the table's rows collection.

        Returns the inserted :class:`HTMLTableRowElement`.
        ``index=-1`` or ``index==len(rows)`` appends to the last ``<tbody>``
        (or ``<thead>`` if no ``<tbody>`` exists, or directly to the table if
        no sections exist).

        Raises :exc:`IndexSizeError` when ``index < -1`` or
        ``index > len(rows)``.

        Examples
        --------
        >>> from aspose_html.dom import Document, HTMLTableRowElement
        >>> doc = Document()
        >>> table = doc.create_element("table")
        >>> tr = table.insert_row()
        >>> isinstance(tr, HTMLTableRowElement)
        True
        >>> len(list(table.rows))
        1
        """
        from aspose_html.dom._exceptions import IndexSizeError  # noqa: PLC0415

        row_list = list(self.rows)
        n = len(row_list)
        if index < -1 or index > n:
            raise IndexSizeError("Index out of range")

        new_tr = self.owner_document.create_element("tr")

        if index == -1 or index == n:
            # Append case: find last tbody, else thead, else append directly.
            last_tbody = None
            for child in self._children:
                tag = getattr(child, "_tag_name", None)
                if tag == "TBODY":
                    last_tbody = child
            if last_tbody is not None:
                last_tbody.append_child(new_tr)
            elif self.t_head is not None:
                self.t_head.append_child(new_tr)  # type: ignore[union-attr]
            else:
                self.append_child(new_tr)
        else:
            ref_row = row_list[index]
            ref_row._parent.insert_before(new_tr, ref_row)  # type: ignore[union-attr]

        return new_tr  # type: ignore[return-value]

    def delete_row(self, index: int) -> None:
        """Remove the ``<tr>`` at *index* from the table's rows collection.

        Raises :exc:`IndexSizeError` when ``index < 0`` or
        ``index >= len(rows)``.

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> doc = Document()
        >>> table = doc.create_element("table")
        >>> _ = table.insert_row()
        >>> table.delete_row(0)
        >>> len(list(table.rows))
        0
        """
        from aspose_html.dom._exceptions import IndexSizeError  # noqa: PLC0415

        row_list = list(self.rows)
        if index < 0 or index >= len(row_list):
            raise IndexSizeError("Index out of range")
        row = row_list[index]
        row._parent.remove_child(row)  # type: ignore[union-attr]

    def create_caption(self) -> "HTMLTableCaptionElement":
        """Return or create the ``<caption>`` direct child.

        If a ``<caption>`` already exists as a direct child, returns it.
        Otherwise creates a new ``<caption>`` element, inserts it as the
        first child of this table, and returns it.

        Examples
        --------
        >>> from aspose_html.dom import Document, HTMLTableCaptionElement
        >>> doc = Document()
        >>> table = doc.create_element("table")
        >>> cap = table.create_caption()
        >>> isinstance(cap, HTMLTableCaptionElement)
        True
        >>> table.create_caption() is cap
        True
        """
        existing = self.caption
        if existing is not None:
            return existing  # type: ignore[return-value]
        new_cap = self.owner_document.create_element("caption")
        first = self.first_child
        if first is not None:
            self.insert_before(new_cap, first)
        else:
            self.append_child(new_cap)
        return new_cap  # type: ignore[return-value]

    def delete_caption(self) -> None:
        """Remove the first ``<caption>`` direct child. No-op if none.

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> doc = Document()
        >>> table = doc.create_element("table")
        >>> table.delete_caption()
        >>> table.caption is None
        True
        """
        existing = self.caption
        if existing is not None:
            self.remove_child(existing)

    def create_t_head(self) -> "HTMLTableSectionElement":
        """Return or create the ``<thead>`` direct child.

        If a ``<thead>`` already exists as a direct child, returns it.
        Otherwise creates a new ``<thead>`` element and inserts it before
        the first ``<tbody>`` or ``<tfoot>`` child (or appends if none),
        then returns it.

        Examples
        --------
        >>> from aspose_html.dom import Document, HTMLTableSectionElement
        >>> doc = Document()
        >>> table = doc.create_element("table")
        >>> thead = table.create_t_head()
        >>> isinstance(thead, HTMLTableSectionElement)
        True
        >>> table.create_t_head() is thead
        True
        """
        existing = self.t_head
        if existing is not None:
            return existing  # type: ignore[return-value]
        new_thead = self.owner_document.create_element("thead")
        # Insert before first tbody or tfoot, else append.
        ref = None
        for child in self._children:
            tag = getattr(child, "_tag_name", None)
            if tag in ("TBODY", "TFOOT"):
                ref = child
                break
        if ref is not None:
            self.insert_before(new_thead, ref)
        else:
            self.append_child(new_thead)
        return new_thead  # type: ignore[return-value]

    def delete_t_head(self) -> None:
        """Remove the first ``<thead>`` direct child. No-op if none.

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> doc = Document()
        >>> table = doc.create_element("table")
        >>> table.delete_t_head()
        >>> table.t_head is None
        True
        """
        existing = self.t_head
        if existing is not None:
            self.remove_child(existing)

    def create_t_foot(self) -> "HTMLTableSectionElement":
        """Return or create the ``<tfoot>`` direct child.

        If a ``<tfoot>`` already exists as a direct child, returns it.
        Otherwise creates a new ``<tfoot>`` element, appends it as the
        last child, and returns it.

        Examples
        --------
        >>> from aspose_html.dom import Document, HTMLTableSectionElement
        >>> doc = Document()
        >>> table = doc.create_element("table")
        >>> tfoot = table.create_t_foot()
        >>> isinstance(tfoot, HTMLTableSectionElement)
        True
        >>> table.create_t_foot() is tfoot
        True
        """
        existing = self.t_foot
        if existing is not None:
            return existing  # type: ignore[return-value]
        new_tfoot = self.owner_document.create_element("tfoot")
        self.append_child(new_tfoot)
        return new_tfoot  # type: ignore[return-value]

    def delete_t_foot(self) -> None:
        """Remove the first ``<tfoot>`` direct child. No-op if none.

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> doc = Document()
        >>> table = doc.create_element("table")
        >>> table.delete_t_foot()
        >>> table.t_foot is None
        True
        """
        existing = self.t_foot
        if existing is not None:
            self.remove_child(existing)

    def create_t_body(self) -> "HTMLTableSectionElement":
        """Return the first ``<tbody>`` child, creating one if absent.

        Per WHATWG HTML §4.9.9.3. If a ``<tbody>`` element already exists as a
        direct child of this table it is returned unchanged. If none exists, a new
        ``<tbody>`` element is created, appended to the table, and returned.

        Returns
        -------
        HTMLTableSectionElement
            The first (or newly created) ``<tbody>`` element.

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> doc = Document()
        >>> table = doc.create_element("table")
        >>> _ = doc.append_child(table)
        >>> tbody = table.create_t_body()
        >>> tbody.tag_name
        'TBODY'
        >>> table.create_t_body() is tbody
        True
        """
        for child in self._children:
            if getattr(child, "_tag_name", None) == "TBODY":
                return child  # type: ignore[return-value]
        new_tbody = self.owner_document.create_element("tbody")
        self.append_child(new_tbody)
        return new_tbody  # type: ignore[return-value]

    @property
    def thead(self):
        """Alias for :attr:`t_head` — IDL camelCase name (WHATWG HTML §4.9.1).

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> doc = Document()
        >>> table = doc.create_element("table")
        >>> table.thead is None
        True
        """
        return self.t_head

    @property
    def tfoot(self):
        """Alias for :attr:`t_foot` — IDL camelCase name (WHATWG HTML §4.9.1).

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> doc = Document()
        >>> table = doc.create_element("table")
        >>> table.tfoot is None
        True
        """
        return self.t_foot

    @property
    def align(self) -> str:
        """Reflects obsolete ``align`` content attribute (WHATWG HTML §4.9.1).

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> doc = Document()
        >>> el = doc.create_element("table")
        >>> el.align
        ''
        >>> el.set_attribute("align", "center")
        >>> el.align
        'center'
        """
        return self.get_attribute("align") or ""

    @align.setter
    def align(self, value: str) -> None:
        self.set_attribute("align", value)


class HTMLTableSectionElement(HTMLElement):
    """HTML ``<thead>``, ``<tbody>``, or ``<tfoot>`` element.

    Examples
    --------
    >>> from aspose_html.dom import Document, HTMLTableSectionElement
    >>> doc = Document()
    >>> tbody = doc.create_element("tbody")
    >>> isinstance(tbody, HTMLTableSectionElement)
    True
    """

    __slots__ = ()

    @property
    def rows(self) -> object:
        """Live collection of ``<tr>`` direct children."""
        from aspose_html.dom._collections import _SubtreeHTMLCollection  # noqa: PLC0415
        self_ref = self
        return _SubtreeHTMLCollection(
            self,
            lambda el: getattr(el, "_tag_name", None) == "TR"
            and el._parent is self_ref,
        )

    def insert_row(self, index: int = -1) -> "HTMLTableRowElement":
        """Insert a new ``<tr>`` at *index* in this section's rows.

        Returns the inserted :class:`HTMLTableRowElement`.
        ``index=-1`` or ``index==len(rows)`` appends.

        Raises :exc:`IndexSizeError` when ``index < -1`` or
        ``index > len(rows)``.

        Examples
        --------
        >>> from aspose_html.dom import Document, HTMLTableRowElement
        >>> doc = Document()
        >>> tbody = doc.create_element("tbody")
        >>> tr = tbody.insert_row()
        >>> isinstance(tr, HTMLTableRowElement)
        True
        >>> len(list(tbody.rows))
        1
        """
        from aspose_html.dom._exceptions import IndexSizeError  # noqa: PLC0415

        row_list = list(self.rows)
        n = len(row_list)
        if index < -1 or index > n:
            raise IndexSizeError("Index out of range")

        new_tr = self.owner_document.create_element("tr")

        if index == -1 or index == n:
            self.append_child(new_tr)
        else:
            self.insert_before(new_tr, row_list[index])

        return new_tr  # type: ignore[return-value]

    def delete_row(self, index: int) -> None:
        """Remove the ``<tr>`` at *index* from this section's rows.

        Raises :exc:`IndexSizeError` when ``index < 0`` or
        ``index >= len(rows)``.

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> doc = Document()
        >>> tbody = doc.create_element("tbody")
        >>> _ = tbody.insert_row()
        >>> tbody.delete_row(0)
        >>> len(list(tbody.rows))
        0
        """
        from aspose_html.dom._exceptions import IndexSizeError  # noqa: PLC0415

        row_list = list(self.rows)
        if index < 0 or index >= len(row_list):
            raise IndexSizeError("Index out of range")
        row = row_list[index]
        self.remove_child(row)

    @property
    def align(self) -> str:
        """Reflects obsolete ``align`` content attribute (WHATWG HTML §4.9.5).

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> doc = Document()
        >>> el = doc.create_element("tbody")
        >>> el.align
        ''
        """
        return self.get_attribute("align") or ""

    @align.setter
    def align(self, value: str) -> None:
        self.set_attribute("align", value)

    @property
    def ch(self) -> str:
        """Reflects obsolete ``char`` content attribute (WHATWG HTML §4.9.5).

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> doc = Document()
        >>> el = doc.create_element("tbody")
        >>> el.ch
        ''
        """
        return self.get_attribute("char") or ""

    @ch.setter
    def ch(self, value: str) -> None:
        self.set_attribute("char", value)

    @property
    def ch_off(self) -> str:
        """Reflects obsolete ``charoff`` content attribute (WHATWG HTML §4.9.5).

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> doc = Document()
        >>> el = doc.create_element("tbody")
        >>> el.ch_off
        ''
        """
        return self.get_attribute("charoff") or ""

    @ch_off.setter
    def ch_off(self, value: str) -> None:
        self.set_attribute("charoff", value)

    @property
    def v_align(self) -> str:
        """Reflects obsolete ``valign`` content attribute (WHATWG HTML §4.9.5).

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> doc = Document()
        >>> el = doc.create_element("tbody")
        >>> el.v_align
        ''
        """
        return self.get_attribute("valign") or ""

    @v_align.setter
    def v_align(self, value: str) -> None:
        self.set_attribute("valign", value)


class HTMLTableRowElement(HTMLElement):
    """HTML ``<tr>`` element.

    Examples
    --------
    >>> from aspose_html.dom import Document, HTMLTableRowElement
    >>> doc = Document()
    >>> tr = doc.create_element("tr")
    >>> isinstance(tr, HTMLTableRowElement)
    True
    """

    __slots__ = ()

    @property
    def cells(self) -> object:
        """Live collection of ``<td>`` and ``<th>`` direct children."""
        from aspose_html.dom._collections import _SubtreeHTMLCollection  # noqa: PLC0415
        self_ref = self
        return _SubtreeHTMLCollection(
            self,
            lambda el: getattr(el, "_tag_name", None) in ("TD", "TH")
            and el._parent is self_ref,
        )

    def insert_cell(self, index: int = -1) -> "HTMLTableCellElement":
        """Insert a new ``<td>`` at *index* in this row's cells.

        Returns the inserted :class:`HTMLTableCellElement`.
        ``index=-1`` or ``index==len(cells)`` appends.

        Raises :exc:`IndexSizeError` when ``index < -1`` or
        ``index > len(cells)``.

        Examples
        --------
        >>> from aspose_html.dom import Document, HTMLTableCellElement
        >>> doc = Document()
        >>> tr = doc.create_element("tr")
        >>> td = tr.insert_cell()
        >>> isinstance(td, HTMLTableCellElement)
        True
        >>> len(list(tr.cells))
        1
        """
        from aspose_html.dom._exceptions import IndexSizeError  # noqa: PLC0415

        cell_list = list(self.cells)
        n = len(cell_list)
        if index < -1 or index > n:
            raise IndexSizeError("Index out of range")

        new_td = self.owner_document.create_element("td")

        if index == -1 or index == n:
            self.append_child(new_td)
        else:
            self.insert_before(new_td, cell_list[index])

        return new_td  # type: ignore[return-value]

    def delete_cell(self, index: int) -> None:
        """Remove the cell at *index*. :exc:`IndexSizeError` for invalid index.

        Raises :exc:`IndexSizeError` when ``index < 0`` or
        ``index >= len(cells)``.

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> doc = Document()
        >>> tr = doc.create_element("tr")
        >>> _ = tr.insert_cell()
        >>> tr.delete_cell(0)
        >>> len(list(tr.cells))
        0
        """
        from aspose_html.dom._exceptions import IndexSizeError  # noqa: PLC0415

        cell_list = list(self.cells)
        if index < 0 or index >= len(cell_list):
            raise IndexSizeError("Index out of range")
        cell = cell_list[index]
        self.remove_child(cell)

    @property
    def row_index(self) -> int:
        """Index of this row in the containing table, or ``-1`` if not in a table."""
        node = self._parent
        while node is not None:
            if getattr(node, "_tag_name", None) == "TABLE":
                for i, row in enumerate(node.rows):  # type: ignore[attr-defined]
                    if row is self:
                        return i
                return -1
            node = node._parent
        return -1

    @property
    def section_row_index(self) -> int:
        """Index of this row within its section, or ``-1`` if not in a section."""
        parent = self._parent
        if parent is None or getattr(parent, "_tag_name", None) not in (
            "THEAD", "TBODY", "TFOOT"
        ):
            return -1
        for i, row in enumerate(parent.rows):  # type: ignore[attr-defined]
            if row is self:
                return i
        return -1

    @property
    def align(self) -> str:
        """Reflects obsolete ``align`` content attribute (WHATWG HTML §4.9.8).

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> doc = Document()
        >>> el = doc.create_element("tr")
        >>> el.align
        ''
        >>> el.set_attribute("align", "center")
        >>> el.align
        'center'
        """
        return self.get_attribute("align") or ""

    @align.setter
    def align(self, value: str) -> None:
        self.set_attribute("align", value)

    @property
    def bg_color(self) -> str:
        """Reflects obsolete ``bgcolor`` content attribute (WHATWG HTML §4.9.8).

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> doc = Document()
        >>> el = doc.create_element("tr")
        >>> el.bg_color
        ''
        >>> el.set_attribute("bgcolor", "#fff")
        >>> el.bg_color
        '#fff'
        """
        return self.get_attribute("bgcolor") or ""

    @bg_color.setter
    def bg_color(self, value: str) -> None:
        self.set_attribute("bgcolor", value)

    @property
    def ch(self) -> str:
        """Reflects obsolete ``char`` content attribute (WHATWG HTML §4.9.8).

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> doc = Document()
        >>> el = doc.create_element("tr")
        >>> el.ch
        ''
        """
        return self.get_attribute("char") or ""

    @ch.setter
    def ch(self, value: str) -> None:
        self.set_attribute("char", value)

    @property
    def ch_off(self) -> str:
        """Reflects obsolete ``charoff`` content attribute (WHATWG HTML §4.9.8).

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> doc = Document()
        >>> el = doc.create_element("tr")
        >>> el.ch_off
        ''
        """
        return self.get_attribute("charoff") or ""

    @ch_off.setter
    def ch_off(self, value: str) -> None:
        self.set_attribute("charoff", value)

    @property
    def v_align(self) -> str:
        """Reflects obsolete ``valign`` content attribute (WHATWG HTML §4.9.8).

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> doc = Document()
        >>> el = doc.create_element("tr")
        >>> el.v_align
        ''
        """
        return self.get_attribute("valign") or ""

    @v_align.setter
    def v_align(self, value: str) -> None:
        self.set_attribute("valign", value)


class HTMLTableCellElement(HTMLElement):
    """HTML ``<td>`` or ``<th>`` element.

    Examples
    --------
    >>> from aspose_html.dom import Document, HTMLTableCellElement
    >>> doc = Document()
    >>> td = doc.create_element("td")
    >>> isinstance(td, HTMLTableCellElement)
    True
    >>> td.col_span
    1
    """

    __slots__ = ()

    @property
    def col_span(self) -> int:
        """Integer IDL attribute reflecting ``'colspan'``. Default ``1``."""
        try:
            return int(self.get_attribute("colspan") or 1)
        except ValueError:
            return 1

    @col_span.setter
    def col_span(self, value: int) -> None:
        self.set_attribute("colspan", str(value))

    @property
    def row_span(self) -> int:
        """Integer IDL attribute reflecting ``'rowspan'``. Default ``1``."""
        try:
            return int(self.get_attribute("rowspan") or 1)
        except ValueError:
            return 1

    @row_span.setter
    def row_span(self, value: int) -> None:
        self.set_attribute("rowspan", str(value))

    @property
    def headers(self) -> str:
        """String IDL attribute reflecting ``'headers'``. Default ``""``."""
        return self.get_attribute("headers") or ""

    @headers.setter
    def headers(self, value: str) -> None:
        self.set_attribute("headers", value)

    @property
    def scope(self) -> str:
        """String IDL attribute reflecting ``'scope'``. Default ``""``.

        WHATWG HTML §4.9.11 — valid values are ``"row"``, ``"col"``,
        ``"rowgroup"``, ``"colgroup"``, or ``""`` (absent).
        Getter normalises absent attribute to ``""``.

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> doc = Document()
        >>> th = doc.create_element("th")
        >>> th.scope
        ''
        >>> th.scope = "col"
        >>> th.scope
        'col'
        """
        return self.get_attribute("scope") or ""

    @scope.setter
    def scope(self, value: str) -> None:
        self.set_attribute("scope", value)

    @property
    def cell_index(self) -> int:
        """0-based index in the parent ``<tr>``, or ``-1`` if not in a row (WHATWG HTML §4.9.11).

        Examples
        --------
        >>> from aspose_html import HTMLDocument
        >>> doc = HTMLDocument.parse('<table><tr><td>A</td><td>B</td></tr></table>')
        >>> cells = list(doc.query_selector_all('td'))
        >>> cells[0].cell_index
        0
        >>> cells[1].cell_index
        1
        """
        parent = self.parent_node
        if parent is None:
            return -1
        cells = [c for c in parent.child_nodes
                 if isinstance(c, HTMLTableCellElement)]
        try:
            return cells.index(self)
        except ValueError:
            return -1

    @property
    def abbr(self) -> str:
        """Reflect the ``abbr`` content attribute; empty string when absent (WHATWG HTML §4.9.11).

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> doc = Document()
        >>> el = doc.create_element('td')
        >>> el.abbr
        ''
        >>> el.set_attribute('abbr', 'name')
        >>> el.abbr
        'name'
        """
        return self.get_attribute("abbr") or ""

    @abbr.setter
    def abbr(self, value: str) -> None:
        self.set_attribute("abbr", value)

    @property
    def align(self) -> str:
        """Reflect the ``align`` content attribute (WHATWG HTML §4.9.11).

        Examples
        --------
        >>> from aspose_html.dom._document import Document
        >>> doc = Document(); el = doc.create_element('td')
        >>> el.align
        ''
        """
        return self.get_attribute("align") or ""

    @align.setter
    def align(self, value: str) -> None:
        self.set_attribute("align", value)

    @property
    def bg_color(self) -> str:
        """Reflect the ``bgcolor`` content attribute (WHATWG HTML §4.9.11).

        Examples
        --------
        >>> from aspose_html.dom._document import Document
        >>> doc = Document(); el = doc.create_element('td')
        >>> el.bg_color
        ''
        """
        return self.get_attribute("bgcolor") or ""

    @bg_color.setter
    def bg_color(self, value: str) -> None:
        self.set_attribute("bgcolor", value)

    @property
    def no_wrap(self) -> bool:
        """Reflect the ``nowrap`` boolean attribute (WHATWG HTML §4.9.11).

        Examples
        --------
        >>> from aspose_html.dom._document import Document
        >>> doc = Document(); el = doc.create_element('td')
        >>> el.no_wrap
        False
        >>> el.set_attribute('nowrap', ''); el.no_wrap
        True
        """
        return self.has_attribute("nowrap")

    @no_wrap.setter
    def no_wrap(self, value: bool) -> None:
        if value:
            self.set_attribute("nowrap", "")
        else:
            self.remove_attribute("nowrap")

    @property
    def width(self) -> str:
        """Reflect the ``width`` content attribute (WHATWG HTML §4.9.11).

        Examples
        --------
        >>> from aspose_html.dom._document import Document
        >>> doc = Document(); el = doc.create_element('td')
        >>> el.width
        ''
        """
        return self.get_attribute("width") or ""

    @width.setter
    def width(self, value: str) -> None:
        self.set_attribute("width", value)

    @property
    def height(self) -> str:
        """Reflect the ``height`` content attribute (WHATWG HTML §4.9.11).

        Examples
        --------
        >>> from aspose_html.dom._document import Document
        >>> doc = Document(); el = doc.create_element('td')
        >>> el.height
        ''
        """
        return self.get_attribute("height") or ""

    @height.setter
    def height(self, value: str) -> None:
        self.set_attribute("height", value)

    @property
    def axis(self) -> str:
        """Reflects obsolete ``axis`` content attribute (WHATWG HTML §4.9.11).

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> doc = Document()
        >>> el = doc.create_element("td")
        >>> el.axis
        ''
        >>> el.set_attribute("axis", "category")
        >>> el.axis
        'category'
        """
        return self.get_attribute("axis") or ""

    @axis.setter
    def axis(self, value: str) -> None:
        self.set_attribute("axis", value)

    @property
    def v_align(self) -> str:
        """Reflects obsolete ``valign`` content attribute (WHATWG HTML §4.9.11).

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> doc = Document()
        >>> el = doc.create_element("td")
        >>> el.v_align
        ''
        """
        return self.get_attribute("valign") or ""

    @v_align.setter
    def v_align(self, value: str) -> None:
        self.set_attribute("valign", value)

    @property
    def ch(self) -> str:
        """Reflects obsolete ``char`` content attribute (WHATWG HTML §4.9.11).

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> doc = Document()
        >>> el = doc.create_element("td")
        >>> el.ch
        ''
        """
        return self.get_attribute("char") or ""

    @ch.setter
    def ch(self, value: str) -> None:
        self.set_attribute("char", value)

    @property
    def ch_off(self) -> str:
        """Reflects obsolete ``charoff`` content attribute (WHATWG HTML §4.9.11).

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> doc = Document()
        >>> el = doc.create_element("td")
        >>> el.ch_off
        ''
        """
        return self.get_attribute("charoff") or ""

    @ch_off.setter
    def ch_off(self, value: str) -> None:
        self.set_attribute("charoff", value)


class HTMLTableCaptionElement(HTMLElement):
    """HTML ``<caption>`` element.

    Examples
    --------
    >>> from aspose_html.dom import Document, HTMLTableCaptionElement
    >>> doc = Document()
    >>> cap = doc.create_element("caption")
    >>> isinstance(cap, HTMLTableCaptionElement)
    True
    """

    __slots__ = ()



class HTMLTableColElement(HTMLElement):
    """HTML ``<col>`` or ``<colgroup>`` element.

    Examples
    --------
    >>> from aspose_html.dom import Document, HTMLTableColElement
    >>> doc = Document()
    >>> col = doc.create_element("col")
    >>> isinstance(col, HTMLTableColElement)
    True
    >>> col.span
    1
    """

    __slots__ = ()

    @property
    def span(self) -> int:
        """Integer IDL attribute reflecting ``'span'``. Default ``1``."""
        try:
            return int(self.get_attribute("span") or 1)
        except ValueError:
            return 1

    @span.setter
    def span(self, value: int) -> None:
        self.set_attribute("span", str(value))

    @property
    def width(self) -> str:
        """Reflect the ``width`` content attribute (WHATWG HTML §4.9.12).

        Examples
        --------
        >>> from aspose_html.dom._document import Document
        >>> doc = Document(); el = doc.create_element('col')
        >>> el.width
        ''
        """
        return self.get_attribute("width") or ""

    @width.setter
    def width(self, value: str) -> None:
        self.set_attribute("width", value)

    @property
    def align(self) -> str:
        """Reflect the ``align`` content attribute (WHATWG HTML §4.9.12).

        Examples
        --------
        >>> from aspose_html.dom._document import Document
        >>> doc = Document(); el = doc.create_element('col')
        >>> el.align
        ''
        """
        return self.get_attribute("align") or ""

    @align.setter
    def align(self, value: str) -> None:
        self.set_attribute("align", value)

    @property
    def v_align(self) -> str:
        """Reflect the ``valign`` content attribute (WHATWG HTML §4.9.12).

        Examples
        --------
        >>> from aspose_html.dom._document import Document
        >>> doc = Document(); el = doc.create_element('col')
        >>> el.v_align
        ''
        """
        return self.get_attribute("valign") or ""

    @v_align.setter
    def v_align(self, value: str) -> None:
        self.set_attribute("valign", value)

    @property
    def ch(self) -> str:
        """Reflects obsolete ``char`` content attribute (WHATWG HTML §4.9.12).

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> doc = Document()
        >>> el = doc.create_element("col")
        >>> el.ch
        ''
        """
        return self.get_attribute("char") or ""

    @ch.setter
    def ch(self, value: str) -> None:
        self.set_attribute("char", value)

    @property
    def ch_off(self) -> str:
        """Reflects obsolete ``charoff`` content attribute (WHATWG HTML §4.9.12).

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> doc = Document()
        >>> el = doc.create_element("col")
        >>> el.ch_off
        ''
        """
        return self.get_attribute("charoff") or ""

    @ch_off.setter
    def ch_off(self, value: str) -> None:
        self.set_attribute("charoff", value)


# ---------------------------------------------------------------------------
# HTML list subclasses  (BACK-36 / ADR-032)
# ---------------------------------------------------------------------------



"""Form control element classes.

Contains all 14 form-control classes: ``HTMLFormElement``,
``HTMLInputElement``, ``HTMLButtonElement``, ``HTMLSelectElement``,
``HTMLTextAreaElement``, ``HTMLFieldSetElement``, ``HTMLOptionElement``,
``HTMLOptGroupElement``, ``HTMLOutputElement``, ``HTMLDataListElement``,
``HTMLProgressElement``, ``HTMLMeterElement``, ``HTMLLabelElement``,
``HTMLLegendElement``, and the helper ``_get_form_owner``.

See ADR-304 for the split rationale.
"""
from __future__ import annotations

import re

from aspose_html.dom._html_element import HTMLElement
from aspose_html.dom._node_type import NodeType
from aspose_html.dom._validation import ValidityState, _ConstraintValidationMixin


def _get_form_owner(element: "HTMLElement") -> "HTMLElement | None":
    """Return the nearest ancestor ``<form>`` element, or ``None``.

    Implements the simplified headless form-owner algorithm: walk up
    the ``_parent_node`` chain and return the first node whose
    ``_tag_name`` is ``"FORM"``. The full WHATWG form-owner algorithm
    (§4.10.18.3) also allows a ``form`` content attribute pointing to a
    form by ID; this simpler tree-walk covers the overwhelmingly common
    case in headless document processing.

    >>> from aspose_html.html_document import HTMLDocument
    >>> doc = HTMLDocument.parse('<form id="f"><input id="i"></form>')
    >>> inp = doc.get_element_by_id("i")
    >>> form = doc.get_element_by_id("f")
    >>> _get_form_owner(inp) is form
    True
    >>> _get_form_owner(doc.create_element("input")) is None
    True
    """
    node = element.parent_node
    while node is not None:
        if getattr(node, "_tag_name", None) == "FORM":
            return node
        node = node.parent_node
    return None

# ---------------------------------------------------------------------------
# HTMLInputElement
# ---------------------------------------------------------------------------

class HTMLInputElement(_ConstraintValidationMixin, HTMLElement):
    """HTML ``<input>`` form control element.

    Reflects ``type`` (default ``"text"``), ``value``, ``name``, ``checked``,
    and ``disabled`` IDL attributes.

    Examples
    --------
    >>> from aspose_html.dom import Document
    >>> doc = Document()
    >>> inp = doc.create_element("input")
    >>> isinstance(inp, HTMLInputElement)
    True
    >>> inp.type
    'text'
    >>> inp.checked
    False
    """

    __slots__ = ("_custom_validity_message", "_indeterminate")

    @property
    def type(self) -> str:
        """The ``type`` attribute value; returns ``'text'`` when absent (WHATWG default).

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> doc = Document()
        >>> inp = doc.create_element("input")
        >>> inp.type
        'text'
        >>> inp.type = "checkbox"
        >>> inp.type
        'checkbox'
        """
        return self.get_attribute("type") or "text"

    @type.setter
    def type(self, value: str) -> None:
        self.set_attribute("type", value)

    @property
    def value(self) -> str:
        """The ``value`` attribute value, or ``''`` when absent.

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> doc = Document()
        >>> inp = doc.create_element("input")
        >>> inp.value
        ''
        >>> inp.value = "hello"
        >>> inp.value
        'hello'
        """
        return self.get_attribute("value") or ""

    @value.setter
    def value(self, value: str) -> None:
        self.set_attribute("value", value)

    @property
    def default_value(self) -> str:
        """The default value from the ``value`` content attribute.

        Per WHATWG HTML §4.10.5.1: reflects the ``value`` content attribute.
        Distinct from :attr:`value`, which is the live form-control value.

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> doc = Document()
        >>> inp = doc.create_element("input")
        >>> inp.set_attribute("value", "Alice")
        >>> inp.default_value
        'Alice'
        >>> inp.default_value = "Bob"
        >>> inp.default_value
        'Bob'
        >>> doc.create_element("input").default_value
        ''
        """
        return self.get_attribute("value") or ""

    @default_value.setter
    def default_value(self, value: str) -> None:
        self.set_attribute("value", value)

    @property
    def name(self) -> str:
        """The ``name`` attribute value, or ``''`` when absent.

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> doc = Document()
        >>> inp = doc.create_element("input")
        >>> inp.name
        ''
        >>> inp.name = "username"
        >>> inp.name
        'username'
        """
        return self.get_attribute("name") or ""

    @name.setter
    def name(self, value: str) -> None:
        self.set_attribute("name", value)

    @property
    def checked(self) -> bool:
        """Boolean presence attribute ``checked``.

        ``True`` if the attribute exists (any value); ``False`` when absent.
        Setting to ``True`` creates the attribute with an empty string value
        (WHATWG boolean attribute rule); setting to ``False`` removes it.

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> doc = Document()
        >>> inp = doc.create_element("input")
        >>> inp.checked
        False
        >>> inp.checked = True
        >>> inp.checked
        True
        >>> inp.checked = False
        >>> inp.checked
        False
        """
        return self.has_attribute("checked")

    @checked.setter
    def checked(self, value: bool) -> None:
        if value:
            self.set_attribute("checked", "")
        else:
            self.remove_attribute("checked")

    @property
    def disabled(self) -> bool:
        """Boolean presence attribute ``disabled``.

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> doc = Document()
        >>> inp = doc.create_element("input")
        >>> inp.disabled
        False
        >>> inp.disabled = True
        >>> inp.disabled
        True
        """
        return self.has_attribute("disabled")

    @disabled.setter
    def disabled(self, value: bool) -> None:
        if value:
            self.set_attribute("disabled", "")
        else:
            self.remove_attribute("disabled")

    @property
    def required(self) -> bool:
        """Boolean presence attribute ``required``."""
        return self.has_attribute("required")

    @required.setter
    def required(self, value: bool) -> None:
        if value:
            self.set_attribute("required", "")
        else:
            self.remove_attribute("required")

    @property
    def pattern(self) -> str:
        """The ``pattern`` attribute value, or ``''`` when absent."""
        return self.get_attribute("pattern") or ""

    @pattern.setter
    def pattern(self, value: str) -> None:
        self.set_attribute("pattern", value)

    @property
    def max_length(self) -> int:
        """The ``maxlength`` attribute as an integer (default ``-1``)."""
        raw = self.get_attribute("maxlength")
        if raw is None:
            return -1
        try:
            return int(raw)
        except ValueError:
            return -1

    @max_length.setter
    def max_length(self, value: int) -> None:
        self.set_attribute("maxlength", str(value))

    @property
    def min_length(self) -> int:
        """The ``minlength`` attribute as an integer (default ``-1``)."""
        raw = self.get_attribute("minlength")
        if raw is None:
            return -1
        try:
            return int(raw)
        except ValueError:
            return -1

    @min_length.setter
    def min_length(self, value: int) -> None:
        self.set_attribute("minlength", str(value))

    @property
    def placeholder(self) -> str:
        """The ``placeholder`` attribute value, or ``''`` when absent.

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> doc = Document()
        >>> inp = doc.create_element("input")
        >>> inp.placeholder
        ''
        >>> inp.placeholder = "Enter name"
        >>> inp.placeholder
        'Enter name'
        """
        return self.get_attribute("placeholder") or ""

    @placeholder.setter
    def placeholder(self, value: str) -> None:
        self.set_attribute("placeholder", value)

    @property
    def read_only(self) -> bool:
        """Boolean presence attribute reflecting the HTML ``readonly`` attribute.

        Named ``read_only`` per INV-001 (WHATWG IDL ``readOnly`` → snake_case).
        Presence means ``True``; absence means ``False``.
        Setting ``True`` writes an empty-string attribute value; setting
        ``False`` removes the attribute entirely.

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> doc = Document()
        >>> inp = doc.create_element("input")
        >>> inp.read_only
        False
        >>> inp.read_only = True
        >>> inp.read_only
        True
        >>> inp.read_only = False
        >>> inp.read_only
        False
        """
        return self.has_attribute("readonly")

    @read_only.setter
    def read_only(self, value: bool) -> None:
        if value:
            self.set_attribute("readonly", "")
        else:
            self.remove_attribute("readonly")

    @property
    def autocomplete(self) -> str:
        """The ``autocomplete`` attribute value, or ``''`` when absent.

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> doc = Document()
        >>> inp = doc.create_element("input")
        >>> inp.autocomplete
        ''
        >>> inp.autocomplete = "email"
        >>> inp.autocomplete
        'email'
        """
        return self.get_attribute("autocomplete") or ""

    @autocomplete.setter
    def autocomplete(self, value: str) -> None:
        self.set_attribute("autocomplete", value)

    @property
    def autofocus(self) -> bool:
        """Boolean presence attribute reflecting the HTML ``autofocus`` attribute.

        Presence means ``True``; absence means ``False``.
        Setting ``True`` writes an empty-string attribute value; setting
        ``False`` removes the attribute entirely.

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> doc = Document()
        >>> inp = doc.create_element("input")
        >>> inp.autofocus
        False
        >>> inp.autofocus = True
        >>> inp.autofocus
        True
        >>> inp.autofocus = False
        >>> inp.autofocus
        False
        """
        return self.has_attribute("autofocus")

    @autofocus.setter
    def autofocus(self, value: bool) -> None:
        if value:
            self.set_attribute("autofocus", "")
        else:
            self.remove_attribute("autofocus")

    # ------------------------------------------------------------------
    # Form-submission override attributes (WHATWG HTML §4.10.18.3)
    # ------------------------------------------------------------------

    @property
    def form_action(self) -> str:
        """Reflects the ``formaction`` attribute, or ``''`` when absent.

        Per WHATWG HTML §4.10.18.3.

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> doc = Document()
        >>> inp = doc.create_element("input")
        >>> inp.form_action
        ''
        >>> inp.form_action = "/submit"
        >>> inp.form_action
        '/submit'
        """
        return self.get_attribute("formaction") or ""

    @form_action.setter
    def form_action(self, value: str) -> None:
        self.set_attribute("formaction", value)

    @property
    def form_enctype(self) -> str:
        """Reflects the ``formenctype`` attribute, or ``''`` when absent.

        Per WHATWG HTML §4.10.18.3.

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> doc = Document()
        >>> inp = doc.create_element("input")
        >>> inp.form_enctype
        ''
        >>> inp.form_enctype = "multipart/form-data"
        >>> inp.form_enctype
        'multipart/form-data'
        """
        return self.get_attribute("formenctype") or ""

    @form_enctype.setter
    def form_enctype(self, value: str) -> None:
        self.set_attribute("formenctype", value)

    @property
    def form_method(self) -> str:
        """Reflects the ``formmethod`` attribute, or ``''`` when absent.

        Per WHATWG HTML §4.10.18.3.

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> doc = Document()
        >>> inp = doc.create_element("input")
        >>> inp.form_method
        ''
        >>> inp.form_method = "post"
        >>> inp.form_method
        'post'
        """
        return self.get_attribute("formmethod") or ""

    @form_method.setter
    def form_method(self, value: str) -> None:
        self.set_attribute("formmethod", value)

    @property
    def form_no_validate(self) -> bool:
        """Boolean presence attribute reflecting ``formnovalidate``.

        Per WHATWG HTML §4.10.18.3.

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> doc = Document()
        >>> inp = doc.create_element("input")
        >>> inp.form_no_validate
        False
        >>> inp.form_no_validate = True
        >>> inp.form_no_validate
        True
        >>> inp.form_no_validate = False
        >>> inp.form_no_validate
        False
        """
        return self.has_attribute("formnovalidate")

    @form_no_validate.setter
    def form_no_validate(self, value: bool) -> None:
        if value:
            self.set_attribute("formnovalidate", "")
        else:
            self.remove_attribute("formnovalidate")

    @property
    def form_target(self) -> str:
        """Reflects the ``formtarget`` attribute, or ``''`` when absent.

        Per WHATWG HTML §4.10.18.3.

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> doc = Document()
        >>> inp = doc.create_element("input")
        >>> inp.form_target
        ''
        >>> inp.form_target = "_blank"
        >>> inp.form_target
        '_blank'
        """
        return self.get_attribute("formtarget") or ""

    @form_target.setter
    def form_target(self, value: str) -> None:
        self.set_attribute("formtarget", value)

    @property
    def dirname(self) -> str:
        """Reflects the ``dirname`` attribute, or ``''`` when absent.

        Per WHATWG HTML §4.10.18.3.

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> doc = Document()
        >>> inp = doc.create_element("input")
        >>> inp.dirname
        ''
        >>> inp.dirname = "dir"
        >>> inp.dirname
        'dir'
        """
        return self.get_attribute("dirname") or ""

    @dirname.setter
    def dirname(self, value: str) -> None:
        self.set_attribute("dirname", value)

    @property
    def accept(self) -> str:
        """The ``accept`` attribute value, or ``''`` when absent.

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> doc = Document()
        >>> inp = doc.create_element("input")
        >>> inp.accept
        ''
        >>> inp.accept = "image/*"
        >>> inp.accept
        'image/*'
        """
        return self.get_attribute("accept") or ""

    @accept.setter
    def accept(self, value: str) -> None:
        self.set_attribute("accept", value)

    @property
    def size(self) -> int:
        """The ``size`` attribute as an integer (WHATWG default: ``20``).

        Returns ``20`` when the attribute is absent or not a valid integer.

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> doc = Document()
        >>> inp = doc.create_element("input")
        >>> inp.size
        20
        >>> inp.size = 30
        >>> inp.size
        30
        """
        raw = self.get_attribute("size")
        if raw is None:
            return 20
        try:
            return int(raw)
        except ValueError:
            return 20

    @size.setter
    def size(self, value: int) -> None:
        self.set_attribute("size", str(int(value)))

    # ------------------------------------------------------------------
    # Numeric / range constraint attributes (WHATWG §4.10.18)
    # ------------------------------------------------------------------

    @property
    def step(self) -> str:
        """The ``step`` content attribute value, or ``""`` when absent.

        Reflects the WHATWG HTML §4.10.18 ``step`` IDL attribute.

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> doc = Document()
        >>> inp = doc.create_element("input")
        >>> inp.step
        ''
        >>> inp.step = "0.5"
        >>> inp.step
        '0.5'
        """
        return self.get_attribute("step") or ""

    @step.setter
    def step(self, value: str) -> None:
        self.set_attribute("step", value)

    @property
    def min(self) -> str:
        """The ``min`` content attribute value, or ``""`` when absent.

        Reflects the WHATWG HTML §4.10.18 ``min`` IDL attribute.

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> doc = Document()
        >>> inp = doc.create_element("input")
        >>> inp.min
        ''
        >>> inp.min = "0"
        >>> inp.min
        '0'
        """
        return self.get_attribute("min") or ""

    @min.setter
    def min(self, value: str) -> None:
        self.set_attribute("min", value)

    @property
    def max(self) -> str:
        """The ``max`` content attribute value, or ``""`` when absent.

        Reflects the WHATWG HTML §4.10.18 ``max`` IDL attribute.

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> doc = Document()
        >>> inp = doc.create_element("input")
        >>> inp.max
        ''
        >>> inp.max = "100"
        >>> inp.max
        '100'
        """
        return self.get_attribute("max") or ""

    @max.setter
    def max(self, value: str) -> None:
        self.set_attribute("max", value)

    # ------------------------------------------------------------------
    # Boolean presence attribute
    # ------------------------------------------------------------------

    @property
    def multiple(self) -> bool:
        """Boolean ``multiple`` presence attribute.

        When ``True``, the input accepts multiple values (e.g. for
        ``type="email"`` or ``type="file"``).

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> doc = Document()
        >>> inp = doc.create_element("input")
        >>> inp.multiple
        False
        >>> inp.multiple = True
        >>> inp.multiple
        True
        >>> inp.multiple = False
        >>> inp.multiple
        False
        """
        return self.has_attribute("multiple")

    @multiple.setter
    def multiple(self, value: bool) -> None:
        if value:
            self.set_attribute("multiple", "")
        else:
            self.remove_attribute("multiple")

    # ------------------------------------------------------------------
    # value_as_number (WHATWG §4.10.18.6)
    # ------------------------------------------------------------------

    @property
    def value_as_number(self) -> float:
        """The element's current value as a floating-point number (WHATWG §4.10.18.6).

        Returns the ``value`` attribute parsed via :func:`float`. Returns
        ``float('nan')`` when the string is not a valid floating-point number.

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> doc = Document()
        >>> inp = doc.create_element("input")
        >>> inp.value = "3.14"
        >>> inp.value_as_number
        3.14
        >>> inp.value = "not-a-number"
        >>> import math
        >>> math.isnan(inp.value_as_number)
        True
        """
        try:
            return float(self.value)
        except (ValueError, TypeError):
            return float("nan")

    @value_as_number.setter
    def value_as_number(self, value: float) -> None:
        """Set the element value as a float.

        Raises :class:`~aspose_html.dom._exceptions.InvalidStateError` when
        ``type`` does not support numeric values (``text``, ``search``,
        ``password``, ``url``, ``tel``, ``email``, ``hidden``, ``button``,
        ``submit``, ``reset``, ``image``).
        """
        from aspose_html.dom._exceptions import InvalidStateError  # noqa: PLC0415
        _NON_NUMERIC_TYPES = frozenset({
            "text", "search", "password", "url", "tel",
            "email", "hidden", "button", "submit", "reset", "image",
        })
        if self.type in _NON_NUMERIC_TYPES:
            raise InvalidStateError(
                f"value_as_number is not applicable for input type='{self.type}'"
            )
        self.value = str(value)

    # ------------------------------------------------------------------
    # Stub properties (headless context)
    # ------------------------------------------------------------------

    @property
    def files(self) -> None:
        """The ``FileList`` for file-picker inputs — always ``None`` in headless mode.

        WHATWG HTML §4.10.18 defines ``files`` as ``FileList | null``. Since
        headless document processing does not support file selection, this stub
        always returns ``None``.

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> doc = Document()
        >>> inp = doc.create_element("input")
        >>> inp.files is None
        True
        """
        return None

    @property
    def list(self) -> None:
        """The associated ``<datalist>`` element — always ``None`` in this stub.

        WHATWG HTML §4.10.18 defines ``list`` as ``HTMLDataListElement | null``.
        Live DOM lookup for the referenced ``<datalist>`` is not implemented;
        this stub always returns ``None``.

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> doc = Document()
        >>> inp = doc.create_element("input")
        >>> inp.list is None
        True
        """
        return None

    # ------------------------------------------------------------------
    # WHATWG HTML §4.10.19.5 — text-selection API (headless stubs)
    # ------------------------------------------------------------------

    @property
    def selection_start(self) -> int:
        """Index of the start of the selected text (always ``0`` in headless mode).

        Per WHATWG HTML §4.10.19.5.

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> doc = Document()
        >>> inp = doc.create_element("input")
        >>> inp.selection_start
        0
        """
        return 0

    @property
    def selection_end(self) -> int:
        """Index of the end of the selected text (always ``0`` in headless mode).

        Per WHATWG HTML §4.10.19.5.

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> doc = Document()
        >>> inp = doc.create_element("input")
        >>> inp.selection_end
        0
        """
        return 0

    @property
    def selection_direction(self) -> str:
        """Direction of the selection (always ``"none"`` in headless mode).

        Per WHATWG HTML §4.10.19.5. Valid values are ``"forward"``,
        ``"backward"``, and ``"none"``.

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> doc = Document()
        >>> inp = doc.create_element("input")
        >>> inp.selection_direction
        'none'
        """
        return "none"

    def set_selection_range(
        self,
        start: int,
        end: int,
        direction: str = "none",
    ) -> None:
        """Set the selection boundaries (no-op in headless mode).

        Per WHATWG HTML §4.10.19.5.

        Parameters
        ----------
        start : int
            Start offset of the selection.
        end : int
            End offset of the selection.
        direction : str
            One of ``"forward"``, ``"backward"``, ``"none"``.

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> doc = Document()
        >>> inp = doc.create_element("input")
        >>> inp.set_selection_range(0, 5)  # no-op in headless mode
        """

    def select(self) -> None:
        """Select all text content (no-op in headless mode).

        Per WHATWG HTML §4.10.19.5.

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> doc = Document()
        >>> inp = doc.create_element("input")
        >>> inp.select()  # no-op in headless mode
        """

    @property
    def indeterminate(self) -> bool:
        """Runtime indeterminate checkbox flag (WHATWG §4.10.18.6.1).

        Not backed by a content attribute. Default ``False``.

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> doc = Document()
        >>> inp = doc.create_element("input")
        >>> inp.indeterminate
        False
        >>> inp.indeterminate = True
        >>> inp.indeterminate
        True
        """
        return getattr(self, "_indeterminate", False)

    @indeterminate.setter
    def indeterminate(self, value: bool) -> None:
        self._indeterminate = bool(value)

    @property
    def width(self) -> int:
        """Integer IDL attribute reflecting the ``width`` content attribute.

        Returns ``0`` when absent or non-numeric.

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> doc = Document()
        >>> inp = doc.create_element("input")
        >>> inp.width
        0
        >>> inp.width = 100
        >>> inp.width
        100
        """
        try:
            return int(self.get_attribute("width") or 0)
        except ValueError:
            return 0

    @width.setter
    def width(self, value: int) -> None:
        self.set_attribute("width", str(value))

    @property
    def height(self) -> int:
        """Integer IDL attribute reflecting the ``height`` content attribute.

        Returns ``0`` when absent or non-numeric.

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> doc = Document()
        >>> inp = doc.create_element("input")
        >>> inp.height
        0
        >>> inp.height = 64
        >>> inp.height
        64
        """
        try:
            return int(self.get_attribute("height") or 0)
        except ValueError:
            return 0

    @height.setter
    def height(self, value: int) -> None:
        self.set_attribute("height", str(value))

    @property
    def will_validate(self) -> bool:
        return not self.disabled and self.type != "hidden"

    def _compute_validity_state(self) -> ValidityState:
        if not self.will_validate:
            return ValidityState()

        value = self.value
        max_length = self.max_length
        min_length = self.min_length

        value_missing = self.required and value == ""
        too_long = max_length >= 0 and len(value) > max_length
        too_short = min_length >= 0 and value != "" and len(value) < min_length

        type_mismatch = False
        if value != "" and self.type == "email":
            type_mismatch = "@" not in value
        elif value != "" and self.type == "url":
            type_mismatch = re.match(r"^[a-zA-Z][a-zA-Z0-9+.-]*:", value) is None

        pattern_mismatch = False
        pattern = self.pattern
        if pattern != "" and value != "":
            try:
                pattern_mismatch = re.fullmatch(pattern, value) is None
            except re.error:
                pattern_mismatch = False

        range_underflow = False
        range_overflow = False
        if self.type in {"number", "range"} and value != "":
            try:
                num_value = float(value)
                min_attr = self.get_attribute("min")
                max_attr = self.get_attribute("max")
                if min_attr not in (None, ""):
                    range_underflow = num_value < float(min_attr)
                if max_attr not in (None, ""):
                    range_overflow = num_value > float(max_attr)
            except ValueError:
                range_underflow = False
                range_overflow = False

        return ValidityState(
            value_missing=value_missing,
            type_mismatch=type_mismatch,
            pattern_mismatch=pattern_mismatch,
            too_long=too_long,
            too_short=too_short,
            range_underflow=range_underflow,
            range_overflow=range_overflow,
            step_mismatch=False,
            bad_input=False,
        )

    @property
    def form(self) -> "HTMLElement | None":
        """Nearest ancestor ``<form>`` element, or ``None``.

        Returns the form owner per the simplified WHATWG form-association
        algorithm (ancestor walk). Returns ``None`` for detached elements
        or elements not nested inside a ``<form>``.

        Examples
        --------
        >>> from aspose_html.html_document import HTMLDocument
        >>> doc = HTMLDocument.parse('<form id="f"><input id="i"></form>')
        >>> doc.get_element_by_id("i").form is doc.get_element_by_id("f")
        True
        """
        return _get_form_owner(self)

    # -- IDL tail properties (ADR-294) ----------------------------------------

    @property
    def default_checked(self) -> bool:
        """Reflects the ``checked`` content attribute (markup default).

        Per WHATWG HTML §4.10.5.1. This is the content attribute (markup
        default); :attr:`checked` reflects current mutable state. In headless
        mode both reflect the content attribute.

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> doc = Document()
        >>> inp = doc.create_element("input")
        >>> inp.default_checked
        False
        >>> inp.default_checked = True
        >>> inp.default_checked
        True
        >>> inp.default_checked = False
        >>> inp.default_checked
        False
        """
        return self.has_attribute("checked")

    @default_checked.setter
    def default_checked(self, value: bool) -> None:
        if value:
            self.set_attribute("checked", "")
        else:
            self.remove_attribute("checked")

    @property
    def capture(self) -> str:
        """The ``capture`` attribute value, or ``''`` when absent.

        Per WHATWG HTML §4.10.5.1.

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> doc = Document()
        >>> inp = doc.create_element("input")
        >>> inp.capture
        ''
        >>> inp.capture = "environment"
        >>> inp.capture
        'environment'
        """
        return self.get_attribute("capture") or ""

    @capture.setter
    def capture(self, value: str) -> None:
        self.set_attribute("capture", value)

    @property
    def src(self) -> str:
        """Reflects the ``src`` content attribute (WHATWG HTML §4.10.5.1.3).

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> doc = Document()
        >>> inp = doc.create_element("input")
        >>> inp.src
        ''
        >>> inp.set_attribute("src", "foo.png")
        >>> inp.src
        'foo.png'
        """
        return self.get_attribute("src") or ""

    @src.setter
    def src(self, value: str) -> None:
        self.set_attribute("src", value)

    @property
    def alt(self) -> str:
        """Reflects the ``alt`` content attribute (WHATWG HTML §4.10.5.1.3).

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> doc = Document()
        >>> inp = doc.create_element("input")
        >>> inp.alt
        ''
        >>> inp.set_attribute("alt", "Submit")
        >>> inp.alt
        'Submit'
        """
        return self.get_attribute("alt") or ""

    @alt.setter
    def alt(self, value: str) -> None:
        self.set_attribute("alt", value)

    @property
    def labels(self) -> "_StaticNodeList":
        """Associated ``<label>`` elements (headless stub: always empty).

        Per WHATWG HTML §4.10.18.5. In headless mode, label association
        requires rendering-context semantics that are out of scope.

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> doc = Document()
        >>> inp = doc.create_element("input")
        >>> len(inp.labels)
        0
        >>> list(inp.labels)
        []
        """
        from aspose_html.dom._collections import _StaticNodeList  # noqa: PLC0415
        return _StaticNodeList([])

    def step_up(self, n: int = 1) -> None:
        """No-op stub — step mutation requires a layout engine (WHATWG HTML §4.10.5.1).

        In headless mode this method always returns ``None`` without mutating ``value``.

        Examples
        --------
        >>> from aspose_html.dom._document import Document
        >>> doc = Document(); el = doc.create_element('input')
        >>> el.set_attribute('type', 'number'); el.set_attribute('value', '5')
        >>> el.step_up() is None
        True
        >>> el.get_attribute('value')
        '5'
        """

    def step_down(self, n: int = 1) -> None:
        """No-op stub — step mutation requires a layout engine (WHATWG HTML §4.10.5.1).

        In headless mode this method always returns ``None`` without mutating ``value``.

        Examples
        --------
        >>> from aspose_html.dom._document import Document
        >>> doc = Document(); el = doc.create_element('input')
        >>> el.set_attribute('type', 'number'); el.set_attribute('value', '5')
        >>> el.step_down() is None
        True
        """

    # ------------------------------------------------------------------
    # Track 111, ADR-310 — set_range_text / list_ / value_as_date
    # ------------------------------------------------------------------

    @property
    def list_(self) -> None:
        """Reflects the ``list`` attribute; always ``None`` in headless mode.

        WHATWG HTML §4.10.18.6: in a rendering environment this returns the
        ``HTMLDataListElement`` referenced by the ``list`` content attribute.
        Headless mode does not support datalist lookup.

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> doc = Document()
        >>> inp = doc.create_element("input")
        >>> inp.list_ is None
        True
        """
        return None

    @property
    def value_as_date(self) -> None:
        """Returns ``None`` in headless mode (no date parsing).

        WHATWG HTML §4.10.18.7: the getter returns a ``Date`` object when
        the ``type`` state supports it; in headless mode no date parsing
        is performed.

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> doc = Document()
        >>> inp = doc.create_element("input")
        >>> inp.value_as_date is None
        True
        """
        return None

    @value_as_date.setter
    def value_as_date(self, value: object) -> None:
        """No-op setter — date values are not supported in headless mode.

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> doc = Document()
        >>> inp = doc.create_element("input")
        >>> inp.value_as_date = object()  # must not raise
        """

    # -- Track 113, ADR-312 — WebKit extension attributes ----------------------

    @property
    def autocorrect(self) -> str:
        """Reflects the ``autocorrect`` content attribute.

        Returns ``"on"`` when absent or set to any value other than ``"off"``;
        returns ``"off"`` when the attribute is explicitly ``"off"``.
        WebKit extension; WHATWG HTML §4.10.5.

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> doc = Document()
        >>> inp = doc.create_element("input")
        >>> inp.autocorrect
        'on'
        >>> inp.set_attribute("autocorrect", "off")
        >>> inp.autocorrect
        'off'
        >>> inp.set_attribute("autocorrect", "on")
        >>> inp.autocorrect
        'on'
        """
        val = self.get_attribute("autocorrect")
        if val is None or val.lower() != "off":
            return "on"
        return "off"

    @property
    def incremental(self) -> bool:
        """Reflects the ``incremental`` boolean content attribute.

        Returns ``True`` when the attribute is present (any value).
        WebKit extension for search inputs.

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> doc = Document()
        >>> inp = doc.create_element("input")
        >>> inp.incremental
        False
        >>> inp.set_attribute("incremental", "")
        >>> inp.incremental
        True
        """
        return self.has_attribute("incremental")

    @property
    def webkitdirectory(self) -> bool:
        """Reflects the ``webkitdirectory`` boolean content attribute.

        Returns ``True`` when the attribute is present.
        Used by directory-upload pickers.

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> doc = Document()
        >>> inp = doc.create_element("input")
        >>> inp.webkitdirectory
        False
        >>> inp.set_attribute("webkitdirectory", "")
        >>> inp.webkitdirectory
        True
        """
        return self.has_attribute("webkitdirectory")

    def set_range_text(
        self,
        replacement: str,
        start: "int | None" = None,
        end: "int | None" = None,
        select_mode: str = "preserve",
    ) -> None:
        """Raise ``NotSupportedError`` — text-range selection is unavailable in headless mode.

        WHATWG HTML §4.10.18.5: in a rendering environment this replaces
        the substring ``[start, end)`` with *replacement*. Headless mode
        has no selection pipeline.

        Raises
        ------
        NotSupportedError
            Always — headless mode does not support text-range selection.

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> from aspose_html.dom._exceptions import NotSupportedError
        >>> doc = Document()
        >>> inp = doc.create_element("input")
        >>> inp.set_range_text("x")
        Traceback (most recent call last):
            ...
        aspose_html.dom._exceptions.NotSupportedError: ...
        """
        from aspose_html.dom._exceptions import NotSupportedError  # noqa: PLC0415
        raise NotSupportedError(
            "setRangeText is not supported in headless mode (WHATWG HTML §4.10.18.5)"
        )


    # ------------------------------------------------------------------
    # Track 114 — dir_name alias + show_picker stub (BACK-335 / ADR-313)
    # ------------------------------------------------------------------

    @property
    def dir_name(self) -> str:
        """IDL snake_case alias for ``dirname`` (IDL attribute ``dirName``).

        WHATWG HTML §4.10.5 — the submission-direction attribute.
        Delegates to the ``dirname`` property which reflects the ``dirname``
        HTML content attribute.

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> inp = Document().create_element("input")
        >>> inp.dir_name
        ''
        >>> inp.dir_name = "ltr"
        >>> inp.dirname
        'ltr'
        """
        return self.dirname

    @dir_name.setter
    def dir_name(self, value: str) -> None:
        self.dirname = value

    def show_picker(self) -> None:
        """Raise ``NotSupportedError`` — no UI in headless mode.

        WHATWG HTML §4.10.5 — opens the browser-native picker widget for the
        input element. No rendering context exists in headless operation.

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> from aspose_html.dom._exceptions import NotSupportedError
        >>> inp = Document().create_element("input")
        >>> try:
        ...     inp.show_picker()
        ... except NotSupportedError:
        ...     print("raised")
        raised
        """
        from aspose_html.dom._exceptions import NotSupportedError  # noqa: PLC0415
        raise NotSupportedError(
            "showPicker() is not supported in headless mode"
        )


# ---------------------------------------------------------------------------
# HTMLFormElement
# ---------------------------------------------------------------------------

class HTMLFormElement(HTMLElement):
    """HTML ``<form>`` element.

    Reflects ``action``, ``method`` (default ``"get"``), ``name``,
    ``enctype`` (default ``"application/x-www-form-urlencoded"``),
    ``encoding`` (IDL alias for ``enctype``), ``novalidate``,
    ``target``, and ``autocomplete`` (default ``"on"``) IDL attributes.

    Examples
    --------
    >>> from aspose_html.dom import Document
    >>> doc = Document()
    >>> form = doc.create_element("form")
    >>> isinstance(form, HTMLFormElement)
    True
    >>> form.method
    'get'
    """

    __slots__ = ("_rel_list_cache",)

    _VALID_ENCTYPE_TOKENS = {
        "application/x-www-form-urlencoded",
        "multipart/form-data",
        "text/plain",
    }
    _DEFAULT_ENCTYPE = "application/x-www-form-urlencoded"

    @property
    def action(self) -> str:
        """The ``action`` attribute value, or ``''`` when absent.

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> doc = Document()
        >>> form = doc.create_element("form")
        >>> form.action
        ''
        >>> form.action = "/submit"
        >>> form.action
        '/submit'
        """
        return self.get_attribute("action") or ""

    @action.setter
    def action(self, value: str) -> None:
        self.set_attribute("action", value)

    @property
    def method(self) -> str:
        """The ``method`` attribute value; returns ``'get'`` when absent (WHATWG default).

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> doc = Document()
        >>> form = doc.create_element("form")
        >>> form.method
        'get'
        >>> form.method = "post"
        >>> form.method
        'post'
        """
        return self.get_attribute("method") or "get"

    @method.setter
    def method(self, value: str) -> None:
        self.set_attribute("method", value)

    @property
    def name(self) -> str:
        """The ``name`` attribute value, or ``''`` when absent.

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> doc = Document()
        >>> form = doc.create_element("form")
        >>> form.name
        ''
        >>> form.name = "login"
        >>> form.name
        'login'
        """
        return self.get_attribute("name") or ""

    @name.setter
    def name(self, value: str) -> None:
        self.set_attribute("name", value)

    @property
    def enctype(self) -> str:
        """The ``enctype`` attribute (encoding type); default
        ``"application/x-www-form-urlencoded"`` when absent (WHATWG §4.10.3).

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> doc = Document()
        >>> form = doc.create_element("form")
        >>> form.enctype
        'application/x-www-form-urlencoded'
        >>> form.enctype = "multipart/form-data"
        >>> form.enctype
        'multipart/form-data'
        """
        raw = self.get_attribute("enctype")
        if raw is None:
            return self._DEFAULT_ENCTYPE
        normalized = str(raw).strip().lower()
        if normalized in self._VALID_ENCTYPE_TOKENS:
            return normalized
        return self._DEFAULT_ENCTYPE

    @enctype.setter
    def enctype(self, value: str) -> None:
        normalized = str(value).strip().lower()
        if normalized not in self._VALID_ENCTYPE_TOKENS:
            normalized = self._DEFAULT_ENCTYPE
        self.set_attribute("enctype", normalized)

    @property
    def rel(self) -> str:
        """The ``rel`` attribute value, or ``''`` when absent.

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> doc = Document()
        >>> form = doc.create_element("form")
        >>> form.rel
        ''
        >>> form.rel = "noopener"
        >>> form.rel
        'noopener'
        """
        return self.get_attribute("rel") or ""

    @rel.setter
    def rel(self, value: str) -> None:
        self.set_attribute("rel", value)

    @property
    def encoding(self) -> str:
        """IDL alias for :attr:`enctype` per WHATWG §4.10.3.

        Reading this property returns the same value as :attr:`enctype`;
        writing it sets :attr:`enctype`.

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> doc = Document()
        >>> form = doc.create_element("form")
        >>> form.encoding
        'application/x-www-form-urlencoded'
        >>> form.enctype = "multipart/form-data"
        >>> form.encoding
        'multipart/form-data'
        >>> form.encoding = "text/plain"
        >>> form.enctype
        'text/plain'
        """
        return self.enctype

    @encoding.setter
    def encoding(self, value: str) -> None:
        self.enctype = value

    @property
    def novalidate(self) -> bool:
        """Boolean presence attribute reflecting the HTML ``novalidate`` attribute.

        Presence means ``True``; absence means ``False``.
        Setting ``True`` writes an empty-string attribute value; setting
        ``False`` removes the attribute entirely.

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> doc = Document()
        >>> form = doc.create_element("form")
        >>> form.novalidate
        False
        >>> form.novalidate = True
        >>> form.novalidate
        True
        >>> form.novalidate = False
        >>> form.novalidate
        False
        """
        return self.has_attribute("novalidate")

    @novalidate.setter
    def novalidate(self, value: bool) -> None:
        if value:
            self.set_attribute("novalidate", "")
        else:
            self.remove_attribute("novalidate")

    @property
    def target(self) -> str:
        """The ``target`` attribute value, or ``''`` when absent.

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> doc = Document()
        >>> form = doc.create_element("form")
        >>> form.target
        ''
        >>> form.target = "_blank"
        >>> form.target
        '_blank'
        """
        return self.get_attribute("target") or ""

    @target.setter
    def target(self, value: str) -> None:
        self.set_attribute("target", value)

    @property
    def autocomplete(self) -> str:
        """The ``autocomplete`` attribute value; default ``"on"`` when absent (WHATWG §4.10.3).

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> doc = Document()
        >>> form = doc.create_element("form")
        >>> form.autocomplete
        'on'
        >>> form.autocomplete = "off"
        >>> form.autocomplete
        'off'
        """
        return self.get_attribute("autocomplete") or "on"

    @autocomplete.setter
    def autocomplete(self, value: str) -> None:
        self.set_attribute("autocomplete", value)

    @property
    def elements(self) -> "_SubtreeHTMLCollection":
        """Live collection of all form-associated controls in tree order.

        Returns a live :class:`~aspose_html.dom._collections._SubtreeHTMLCollection`
        containing every descendant ``<input>``, ``<button>``, ``<select>``,
        ``<textarea>``, and ``<fieldset>`` element.  The collection re-scans
        the subtree on each iteration, so it reflects mutations immediately.

        Examples
        --------
        >>> from aspose_html.html_document import HTMLDocument
        >>> doc = HTMLDocument.parse("<form><input name='q'><button>Go</button></form>")
        >>> form = doc.query_selector("form")
        >>> len(form.elements)
        2
        >>> [el.tag_name for el in form.elements]
        ['INPUT', 'BUTTON']
        """
        from aspose_html.dom._collections import _SubtreeHTMLCollection  # noqa: PLC0415

        _FORM_CONTROLS = {"INPUT", "BUTTON", "SELECT", "TEXTAREA", "FIELDSET"}
        return _SubtreeHTMLCollection(
            self,
            lambda el: getattr(el, "_tag_name", None) in _FORM_CONTROLS,
        )

    def submit(self) -> None:
        """Submit the form (not supported in headless mode).

        Raises:
            NotSupportedError: always — form submission requires a browser.

        Examples
        --------
        >>> from aspose_html.dom import Document, NotSupportedError
        >>> doc = Document()
        >>> form = doc.create_element("form")
        >>> try:
        ...     form.submit()
        ... except NotSupportedError:
        ...     print("not supported")
        not supported
        """
        from aspose_html.dom._exceptions import NotSupportedError  # noqa: PLC0415
        raise NotSupportedError(
            "Form submission is not supported in headless mode."
        )

    def reset(self) -> None:
        """Reset the form (not supported in headless mode).

        Raises:
            NotSupportedError: always — form reset requires a browser.

        Examples
        --------
        >>> from aspose_html.dom import Document, NotSupportedError
        >>> doc = Document()
        >>> form = doc.create_element("form")
        >>> try:
        ...     form.reset()
        ... except NotSupportedError:
        ...     print("not supported")
        not supported
        """
        from aspose_html.dom._exceptions import NotSupportedError  # noqa: PLC0415
        raise NotSupportedError(
            "Form reset is not supported in headless mode."
        )

    def request_submit(self, submitter: object = None) -> None:
        """Request form submission (not supported in headless mode).

        Args:
            submitter: ignored — not applicable in headless mode.

        Raises:
            NotSupportedError: always — form submission requires a browser.

        Examples
        --------
        >>> from aspose_html.dom import Document, NotSupportedError
        >>> doc = Document()
        >>> form = doc.create_element("form")
        >>> try:
        ...     form.request_submit()
        ... except NotSupportedError:
        ...     print("not supported")
        not supported
        """
        from aspose_html.dom._exceptions import NotSupportedError  # noqa: PLC0415
        raise NotSupportedError(
            "Form submission is not supported in headless mode."
        )

    @property
    def length(self) -> int:
        """Number of listed form-control elements (WHATWG HTML §4.10.3).

        Equivalent to ``len(list(self.elements))``.  Returns the count of
        ``<input>``, ``<button>``, ``<select>``, ``<textarea>``, and
        ``<fieldset>`` descendants in tree order.

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> doc = Document()
        >>> form = doc.create_element("form")
        >>> form.length
        0
        >>> inp = doc.create_element("input")
        >>> _ = form.append_child(inp)
        >>> form.length
        1
        """
        return len(list(self.elements))

    def check_validity(self) -> bool:
        """Return ``True`` if all listed and validatable form controls are valid.

        Iterates :attr:`elements` and checks each control's validity per
        WHATWG HTML §4.10.22.2.  Only controls where ``will_validate`` is
        ``True`` participate.  A control with ``check_validity() == False``
        causes this method to return ``False`` immediately.  Empty forms and
        forms where no control has ``will_validate == True`` return ``True``.

        .NET parity: ``HTMLFormElement.CheckValidity()``.

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> doc = Document()
        >>> form = doc.create_element("form")
        >>> form.check_validity()
        True
        """
        for control in self.elements:
            if getattr(control, "will_validate", False) and not control.check_validity():
                return False
        return True

    def report_validity(self) -> bool:
        """Return ``True`` if all listed form controls are valid (headless mode).

        Identical semantics to :meth:`check_validity` in a headless
        environment: no browser UI is available to show validation messages.
        WHATWG HTML §4.10.22.2 permits this behaviour in non-rendering
        environments.

        .NET parity: ``HTMLFormElement.ReportValidity()``.

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> doc = Document()
        >>> form = doc.create_element("form")
        >>> form.report_validity()
        True
        """
        return self.check_validity()

    # -- IDL tail properties (ADR-294) ----------------------------------------

    @property
    def no_validate(self) -> bool:
        """Boolean presence attribute reflecting the HTML ``novalidate`` attribute.

        IDL name ``noValidate`` → snake_case ``no_validate`` per INV-001.
        Alias for the existing :attr:`novalidate` property.

        Per WHATWG HTML §4.10.3.

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> doc = Document()
        >>> form = doc.create_element("form")
        >>> form.no_validate
        False
        >>> form.no_validate = True
        >>> form.no_validate
        True
        >>> form.no_validate = False
        >>> form.no_validate
        False
        """
        return self.has_attribute("novalidate")

    @no_validate.setter
    def no_validate(self, value: bool) -> None:
        if value:
            self.set_attribute("novalidate", "")
        else:
            self.remove_attribute("novalidate")

    @property
    def accept_charset(self) -> str:
        """The ``accept-charset`` attribute value, or ``''`` when absent.

        IDL name ``acceptCharset`` → snake_case ``accept_charset`` per INV-001.
        The HTML attribute name uses a hyphen: ``accept-charset``.

        Per WHATWG HTML §4.10.3.

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> doc = Document()
        >>> form = doc.create_element("form")
        >>> form.accept_charset
        ''
        >>> form.accept_charset = "UTF-8"
        >>> form.accept_charset
        'UTF-8'
        """
        return self.get_attribute("accept-charset") or ""

    @accept_charset.setter
    def accept_charset(self, value: str) -> None:
        self.set_attribute("accept-charset", value)

    @property
    def auto_complete(self) -> str:
        """The ``autocomplete`` attribute value, or ``''`` when absent.

        IDL name ``autoComplete`` → snake_case ``auto_complete`` per INV-001.
        Reflects the ``autocomplete`` HTML attribute (no hyphen).

        Per WHATWG HTML §4.10.3. Note: the existing :attr:`autocomplete`
        property returns ``"on"`` as default; this property returns ``''``
        when absent, per strict IDL reflection.

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> doc = Document()
        >>> form = doc.create_element("form")
        >>> form.auto_complete
        ''
        >>> form.auto_complete = "off"
        >>> form.auto_complete
        'off'
        """
        return self.get_attribute("autocomplete") or ""

    @auto_complete.setter
    def auto_complete(self, value: str) -> None:
        self.set_attribute("autocomplete", value)

    def item(self, index: int) -> object:
        """Return the listed form-control element at *index*, or ``None``.

        WHATWG HTML §4.10.3 — ``form.item(index)``.

        >>> from aspose_html.dom import Document
        >>> form = Document().create_element("form")
        >>> form.item(0) is None
        True
        """
        elems = list(self.elements)
        if 0 <= index < len(elems):
            return elems[index]
        return None

    def named_item(self, name: str) -> object:
        """Return the first listed form-control element with ``id`` or ``name``
        equal to *name*, or ``None`` if none found.

        WHATWG HTML §4.10.3 — ``form[name]`` named access.

        >>> from aspose_html.dom import Document
        >>> form = Document().create_element("form")
        >>> form.named_item("x") is None
        True
        """
        for el in self.elements:
            if el.get_attribute("id") == name or el.get_attribute("name") == name:
                return el
        return None

    @property
    def rel_list(self) -> "DOMTokenList":
        """``DOMTokenList`` backed by the ``rel`` attribute (WHATWG HTML §4.10.3).

        The same instance is returned on every access.

        Examples
        --------
        >>> from aspose_html.dom import Document, DOMTokenList
        >>> doc = Document()
        >>> form = doc.create_element("form")
        >>> isinstance(form.rel_list, DOMTokenList)
        True
        >>> form.rel_list is form.rel_list
        True
        >>> form.rel_list.add("noopener")
        >>> form.rel
        'noopener'
        """
        cached = getattr(self, "_rel_list_cache", None)
        if cached is None:
            from aspose_html.dom._token_list import DOMTokenList  # noqa: PLC0415
            cached = DOMTokenList(self, "rel")
            object.__setattr__(self, "_rel_list_cache", cached)
        return cached


# ---------------------------------------------------------------------------
# HTMLButtonElement
# ---------------------------------------------------------------------------

class HTMLButtonElement(_ConstraintValidationMixin, HTMLElement):
    """HTML ``<button>`` element.

    Reflects ``type`` (default ``"submit"``), ``value``, and ``disabled``
    IDL attributes.

    Examples
    --------
    >>> from aspose_html.dom import Document
    >>> doc = Document()
    >>> btn = doc.create_element("button")
    >>> isinstance(btn, HTMLButtonElement)
    True
    >>> btn.type
    'submit'
    """

    __slots__ = ("_custom_validity_message",)

    @property
    def type(self) -> str:
        """The ``type`` attribute value; returns ``'submit'`` when absent (WHATWG default).

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> doc = Document()
        >>> btn = doc.create_element("button")
        >>> btn.type
        'submit'
        >>> btn.type = "reset"
        >>> btn.type
        'reset'
        """
        return self.get_attribute("type") or "submit"

    @type.setter
    def type(self, value: str) -> None:
        self.set_attribute("type", value)

    @property
    def value(self) -> str:
        """The ``value`` attribute value, or ``''`` when absent.

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> doc = Document()
        >>> btn = doc.create_element("button")
        >>> btn.value
        ''
        >>> btn.value = "Click me"
        >>> btn.value
        'Click me'
        """
        return self.get_attribute("value") or ""

    @value.setter
    def value(self, value: str) -> None:
        self.set_attribute("value", value)

    @property
    def disabled(self) -> bool:
        """Boolean presence attribute ``disabled``.

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> doc = Document()
        >>> btn = doc.create_element("button")
        >>> btn.disabled
        False
        >>> btn.disabled = True
        >>> btn.disabled
        True
        """
        return self.has_attribute("disabled")

    @disabled.setter
    def disabled(self, value: bool) -> None:
        if value:
            self.set_attribute("disabled", "")
        else:
            self.remove_attribute("disabled")

    @property
    def will_validate(self) -> bool:
        return False

    def _compute_validity_state(self) -> ValidityState:
        return ValidityState()

    @property
    def form(self) -> "HTMLElement | None":
        """Nearest ancestor ``<form>`` element, or ``None``.

        Returns the form owner per the simplified WHATWG form-association
        algorithm (ancestor walk). Returns ``None`` for detached elements
        or elements not nested inside a ``<form>``.

        Examples
        --------
        >>> from aspose_html.html_document import HTMLDocument
        >>> doc = HTMLDocument.parse('<form id="f"><button id="b"></button></form>')
        >>> doc.get_element_by_id("b").form is doc.get_element_by_id("f")
        True
        """
        return _get_form_owner(self)

    # ------------------------------------------------------------------
    # Form-submission override attributes (WHATWG HTML §4.10.18.3)
    # ------------------------------------------------------------------

    @property
    def form_action(self) -> str:
        """Reflects the ``formaction`` attribute, or ``''`` when absent.

        Per WHATWG HTML §4.10.18.3.

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> doc = Document()
        >>> btn = doc.create_element("button")
        >>> btn.form_action
        ''
        >>> btn.form_action = "/submit"
        >>> btn.form_action
        '/submit'
        """
        return self.get_attribute("formaction") or ""

    @form_action.setter
    def form_action(self, value: str) -> None:
        self.set_attribute("formaction", value)

    @property
    def form_enctype(self) -> str:
        """Reflects the ``formenctype`` attribute, or ``''`` when absent.

        Per WHATWG HTML §4.10.18.3.

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> doc = Document()
        >>> btn = doc.create_element("button")
        >>> btn.form_enctype
        ''
        >>> btn.form_enctype = "multipart/form-data"
        >>> btn.form_enctype
        'multipart/form-data'
        """
        return self.get_attribute("formenctype") or ""

    @form_enctype.setter
    def form_enctype(self, value: str) -> None:
        self.set_attribute("formenctype", value)

    @property
    def form_enc_type(self) -> str:
        """Alias for :attr:`form_enctype` — IDL snake_case name (WHATWG HTML §4.10.19.6).

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> doc = Document()
        >>> btn = doc.create_element("button")
        >>> btn.form_enc_type
        ''
        >>> btn.set_attribute("formenctype", "multipart/form-data")
        >>> btn.form_enc_type
        'multipart/form-data'
        """
        return self.get_attribute("formenctype") or ""

    @form_enc_type.setter
    def form_enc_type(self, value: str) -> None:
        self.set_attribute("formenctype", value)

    @property
    def form_method(self) -> str:
        """Reflects the ``formmethod`` attribute, or ``''`` when absent.

        Per WHATWG HTML §4.10.18.3.

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> doc = Document()
        >>> btn = doc.create_element("button")
        >>> btn.form_method
        ''
        >>> btn.form_method = "post"
        >>> btn.form_method
        'post'
        """
        return self.get_attribute("formmethod") or ""

    @form_method.setter
    def form_method(self, value: str) -> None:
        self.set_attribute("formmethod", value)

    @property
    def form_no_validate(self) -> bool:
        """Boolean presence attribute reflecting ``formnovalidate``.

        Per WHATWG HTML §4.10.18.3.

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> doc = Document()
        >>> btn = doc.create_element("button")
        >>> btn.form_no_validate
        False
        >>> btn.form_no_validate = True
        >>> btn.form_no_validate
        True
        >>> btn.form_no_validate = False
        >>> btn.form_no_validate
        False
        """
        return self.has_attribute("formnovalidate")

    @form_no_validate.setter
    def form_no_validate(self, value: bool) -> None:
        if value:
            self.set_attribute("formnovalidate", "")
        else:
            self.remove_attribute("formnovalidate")

    @property
    def form_target(self) -> str:
        """Reflects the ``formtarget`` attribute, or ``''`` when absent.

        Per WHATWG HTML §4.10.18.3.

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> doc = Document()
        >>> btn = doc.create_element("button")
        >>> btn.form_target
        ''
        >>> btn.form_target = "_blank"
        >>> btn.form_target
        '_blank'
        """
        return self.get_attribute("formtarget") or ""

    @form_target.setter
    def form_target(self, value: str) -> None:
        self.set_attribute("formtarget", value)

    @property
    def autofocus(self) -> bool:
        """Boolean presence attribute reflecting the HTML ``autofocus`` attribute.

        Presence means ``True``; absence means ``False``.
        Setting ``True`` writes an empty-string attribute value; setting
        ``False`` removes the attribute entirely.

        Per WHATWG HTML §4.10.6.1.

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> doc = Document()
        >>> btn = doc.create_element("button")
        >>> btn.autofocus
        False
        >>> btn.autofocus = True
        >>> btn.autofocus
        True
        >>> btn.autofocus = False
        >>> btn.autofocus
        False
        """
        return self.has_attribute("autofocus")

    @autofocus.setter
    def autofocus(self, value: bool) -> None:
        if value:
            self.set_attribute("autofocus", "")
        else:
            self.remove_attribute("autofocus")

    # -- IDL tail properties (ADR-294) ----------------------------------------

    @property
    def name(self) -> str:
        """The ``name`` attribute value, or ``''`` when absent.

        Per WHATWG HTML §4.10.6.1.

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> doc = Document()
        >>> btn = doc.create_element("button")
        >>> btn.name
        ''
        >>> btn.name = "submit-btn"
        >>> btn.name
        'submit-btn'
        """
        return self.get_attribute("name") or ""

    @name.setter
    def name(self, value: str) -> None:
        self.set_attribute("name", value)

    @property
    def labels(self) -> "_StaticNodeList":
        """Associated ``<label>`` elements (headless stub: always empty).

        Per WHATWG HTML §4.10.18.5. In headless mode, label association
        requires rendering-context semantics that are out of scope.

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> doc = Document()
        >>> btn = doc.create_element("button")
        >>> len(btn.labels)
        0
        >>> list(btn.labels)
        []
        """
        from aspose_html.dom._collections import _StaticNodeList  # noqa: PLC0415
        return _StaticNodeList([])


# ---------------------------------------------------------------------------
# HTMLSelectElement
# ---------------------------------------------------------------------------

class HTMLSelectElement(_ConstraintValidationMixin, HTMLElement):
    """HTML ``<select>`` element.

    Reflects ``value``, ``name``, ``multiple``, and ``disabled`` IDL
    attributes.

    Examples
    --------
    >>> from aspose_html.dom import Document
    >>> doc = Document()
    >>> sel = doc.create_element("select")
    >>> isinstance(sel, HTMLSelectElement)
    True
    >>> sel.multiple
    False
    """

    __slots__ = ("_custom_validity_message",)

    @property
    def value(self) -> str:
        """The value of the currently selected option, or ``''`` if none selected.

        Per WHATWG HTML §4.10.7.6.6: returns the ``value`` attribute of the
        first option element with its selectedness flag set to true.  If no
        option is selected, returns ``''``.

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> doc = Document()
        >>> sel = doc.create_element("select")
        >>> opt_a = doc.create_element("option")
        >>> opt_a.set_attribute("value", "a")
        >>> opt_b = doc.create_element("option")
        >>> opt_b.set_attribute("value", "b")
        >>> opt_b.set_attribute("selected", "")
        >>> _ = sel.append_child(opt_a)
        >>> _ = sel.append_child(opt_b)
        >>> sel.value
        'b'
        >>> sel.value = "a"
        >>> sel.value
        'a'
        >>> sel.value = "nonexistent"
        >>> sel.value
        ''
        """
        for option in self.options:
            if option.selected:
                return option.value
        return ""

    @value.setter
    def value(self, value: str) -> None:
        """Select the first option whose value equals *value*.

        Per WHATWG HTML §4.10.7.6.6: finds the first option with a matching
        value attribute, sets its selectedness, and clears all others.  If no
        option matches, all options are deselected.
        """
        for option in self.options:
            option.selected = (option.value == value)

    @property
    def name(self) -> str:
        """The ``name`` attribute value, or ``''`` when absent.

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> doc = Document()
        >>> sel = doc.create_element("select")
        >>> sel.name
        ''
        >>> sel.name = "country"
        >>> sel.name
        'country'
        """
        return self.get_attribute("name") or ""

    @name.setter
    def name(self, value: str) -> None:
        self.set_attribute("name", value)

    @property
    def multiple(self) -> bool:
        """Boolean presence attribute ``multiple``.

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> doc = Document()
        >>> sel = doc.create_element("select")
        >>> sel.multiple
        False
        >>> sel.multiple = True
        >>> sel.multiple
        True
        """
        return self.has_attribute("multiple")

    @multiple.setter
    def multiple(self, value: bool) -> None:
        if value:
            self.set_attribute("multiple", "")
        else:
            self.remove_attribute("multiple")

    @property
    def disabled(self) -> bool:
        """Boolean presence attribute ``disabled``.

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> doc = Document()
        >>> sel = doc.create_element("select")
        >>> sel.disabled
        False
        >>> sel.disabled = True
        >>> sel.disabled
        True
        """
        return self.has_attribute("disabled")

    @disabled.setter
    def disabled(self, value: bool) -> None:
        if value:
            self.set_attribute("disabled", "")
        else:
            self.remove_attribute("disabled")

    @property
    def required(self) -> bool:
        """Boolean presence attribute ``required``."""
        return self.has_attribute("required")

    @required.setter
    def required(self, value: bool) -> None:
        if value:
            self.set_attribute("required", "")
        else:
            self.remove_attribute("required")

    @property
    def options(self) -> "HTMLOptionsCollection":
        """Live options collection for this ``<select>`` element.

        Returns
        -------
        HTMLOptionsCollection
            Live collection of descendant ``<option>`` elements in tree order.

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> doc = Document()
        >>> sel = doc.create_element("select")
        >>> opt = doc.create_element("option")
        >>> sel.append_child(opt)
        <Element 'OPTION'>
        >>> sel.options.length
        1
        >>> sel.options[0] is opt
        True
        """
        from aspose_html.dom._collections import HTMLOptionsCollection  # noqa: PLC0415

        return HTMLOptionsCollection(self)

    @property
    def selected_options(self) -> "_SubtreeHTMLCollection":
        """Live collection of selected descendant ``<option>`` elements.

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> doc = Document()
        >>> sel = doc.create_element("select")
        >>> a = doc.create_element("option")
        >>> b = doc.create_element("option")
        >>> b.set_attribute("selected", "")
        >>> _ = sel.append_child(a)
        >>> _ = sel.append_child(b)
        >>> len(sel.selected_options)
        1
        """
        from aspose_html.dom._collections import _SubtreeHTMLCollection  # noqa: PLC0415

        return _SubtreeHTMLCollection(
            self,
            lambda el: el._local_name == "option" and el.has_attribute("selected"),
        )

    @property
    def selected_index(self) -> int:
        """Index of the first selected ``<option>``, or ``-1`` if none is selected.

        Reflects WHATWG HTML §4.10.7 ``selectedIndex`` IDL attribute.

        The getter iterates direct ``<option>`` children in tree order and
        returns the 0-based index of the first one that carries the ``selected``
        attribute, or ``-1`` when no option is selected.

        The setter selects the option at the given index. When ``multiple``
        is absent (single-select), ``selected`` is removed from all other
        options first. Setting to ``-1`` or to an index outside
        ``[0, length)`` removes ``selected`` from all options.

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> doc = Document()
        >>> sel = doc.create_element("select")
        >>> sel.selected_index
        -1
        >>> a = doc.create_element("option")
        >>> b = doc.create_element("option")
        >>> b.set_attribute("selected", "")
        >>> _ = sel.append_child(a)
        >>> _ = sel.append_child(b)
        >>> sel.selected_index
        1
        >>> sel.selected_index = 0
        >>> sel.selected_index
        0
        >>> b.has_attribute("selected")
        False
        """
        # INV-005: return -1 (WHATWG sentinel) when no option carries selected.
        options = [
            child
            for child in self._children
            if child._node_type == NodeType.ELEMENT_NODE
            and child._local_name.lower() == "option"
        ]
        for idx, opt in enumerate(options):
            if opt.has_attribute("selected"):
                return idx
        return -1

    @selected_index.setter
    def selected_index(self, value: int) -> None:
        options = [
            child
            for child in self._children
            if child._node_type == NodeType.ELEMENT_NODE
            and child._local_name.lower() == "option"
        ]
        # INV-005: single-select constraint — remove selected from all options
        # first when multiple is absent, or when value is out of range / -1.
        is_single_select = not self.has_attribute("multiple")
        if is_single_select or value < 0 or value >= len(options):
            for opt in options:
                opt.remove_attribute("selected")
        if 0 <= value < len(options):
            options[value].set_attribute("selected", "")

    @property
    def size(self) -> int:
        """The ``size`` content attribute reflected as an unsigned integer.

        Returns ``0`` when the attribute is absent or contains a non-integer
        value. Reflects WHATWG HTML §4.10.7 ``size`` IDL attribute.

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> doc = Document()
        >>> sel = doc.create_element("select")
        >>> sel.size
        0
        >>> sel.size = 3
        >>> sel.size
        3
        """
        try:
            return int(self.get_attribute("size") or 0)
        except ValueError:
            return 0

    @size.setter
    def size(self, value: int) -> None:
        self.set_attribute("size", str(value))

    @property
    def length(self) -> int:
        """Number of ``<option>`` elements that are direct children of this ``<select>``.

        Equivalent to ``len(self.options)`` but avoids constructing the
        ``HTMLOptionsCollection`` object. Reflects WHATWG HTML §4.10.7
        ``length`` IDL attribute.

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> doc = Document()
        >>> sel = doc.create_element("select")
        >>> sel.length
        0
        >>> _ = sel.append_child(doc.create_element("option"))
        >>> _ = sel.append_child(doc.create_element("option"))
        >>> sel.length
        2
        """
        return sum(
            1
            for child in self._children
            if child._node_type == NodeType.ELEMENT_NODE
            and child._local_name.lower() == "option"
        )

    def item(self, index: int) -> "HTMLOptionElement | None":
        """Return the option at ``index``, or ``None`` if out of range.

        WHATWG HTML §4.10.7 — element[index] indexed access.

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> doc = Document()
        >>> sel = doc.create_element("select")
        >>> opt = doc.create_element("option")
        >>> _ = sel.append_child(opt)
        >>> sel.item(0) is opt
        True
        >>> sel.item(99) is None
        True
        """
        try:
            return self.options[index]
        except IndexError:
            return None

    def named_item(self, name: str) -> "HTMLOptionElement | None":
        """Return the first option whose ``id`` or ``name`` equals ``name``.

        WHATWG HTML §4.10.7 — element[name] named access.

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> doc = Document()
        >>> sel = doc.create_element("select")
        >>> opt = doc.create_element("option")
        >>> opt.set_attribute("id", "first")
        >>> _ = sel.append_child(opt)
        >>> sel.named_item("first") is opt
        True
        >>> sel.named_item("missing") is None
        True
        """
        for opt in self.options:
            id_val = opt.get_attribute("id")
            name_val = opt.get_attribute("name")
            if id_val == name or name_val == name:
                return opt
        return None

    def add(
        self,
        element: "HTMLOptionElement | HTMLOptGroupElement",
        before: "HTMLOptionElement | int | None" = None,
    ) -> None:
        """Insert ``element`` into the select's option list.

        WHATWG HTML §4.10.7 — element.add(element, before).

        Args:
            element: the ``<option>`` or ``<optgroup>`` to insert.
            before: insertion point — an ``<option>`` element, an integer
                index into ``options``, or ``None`` to append at the end.

        Raises:
            HierarchyRequestError: if ``element`` is an ancestor of
                this ``<select>``.

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> doc = Document()
        >>> sel = doc.create_element("select")
        >>> opt = doc.create_element("option")
        >>> sel.add(opt)
        >>> sel.length
        1
        >>> opt2 = doc.create_element("option")
        >>> sel.add(opt2, 0)
        >>> sel.item(0) is opt2
        True
        """
        # Ancestor check — element must not be an ancestor of this <select>
        node = self.parent_node
        while node is not None:
            if node is element:
                from aspose_html.dom._exceptions import HierarchyRequestError  # noqa: PLC0415
                raise HierarchyRequestError(
                    "The new element is an ancestor of the select element."
                )
            node = node.parent_node

        # Resolve the ``before`` reference node
        ref = None
        if isinstance(before, int):
            ref = self.item(before)  # None if out of range → append
        elif before is not None:
            ref = before

        if ref is not None:
            self.insert_before(element, ref)
        else:
            self.append_child(element)

    def remove(self, index: int) -> None:
        """Remove the option at ``index``.  No-op if out of range.

        WHATWG HTML §4.10.7 — element.remove(index).

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> doc = Document()
        >>> sel = doc.create_element("select")
        >>> opt = doc.create_element("option")
        >>> _ = sel.append_child(opt)
        >>> sel.remove(0)
        >>> sel.length
        0
        >>> sel.remove(99)  # no-op, no exception
        """
        target = self.item(index)
        if target is not None:
            self.remove_child(target)

    @property
    def will_validate(self) -> bool:
        return not self.disabled

    @property
    def autocomplete(self) -> str:
        """Reflect the ``autocomplete`` attribute; default ``''``.

        WHATWG HTML §4.10.7.

        >>> from aspose_html.dom import Document
        >>> sel = Document().create_element("select")
        >>> sel.autocomplete
        ''
        >>> sel.autocomplete = "on"
        >>> sel.autocomplete
        'on'
        """
        return self.get_attribute("autocomplete") or ""

    @autocomplete.setter
    def autocomplete(self, value: str) -> None:
        self.set_attribute("autocomplete", value)

    @property
    def type(self) -> str:
        """The select type: ``'select-multiple'`` or ``'select-one'``.

        Returns ``'select-multiple'`` when the ``multiple`` attribute is
        present, otherwise ``'select-one'``.  WHATWG HTML §4.10.7.1.

        >>> from aspose_html.dom import Document
        >>> sel = Document().create_element("select")
        >>> sel.type
        'select-one'
        >>> sel.multiple = True
        >>> sel.type
        'select-multiple'
        """
        return "select-multiple" if self.has_attribute("multiple") else "select-one"

    def _compute_validity_state(self) -> ValidityState:
        if not self.will_validate:
            return ValidityState()

        selected_value = self.value
        if selected_value == "":
            for child in self._children:
                if child._node_type == NodeType.ELEMENT_NODE and child._local_name.lower() == "option":
                    if child.has_attribute("selected"):
                        selected_value = child.get_attribute("value") or ""
                        break

        return ValidityState(value_missing=self.required and selected_value == "")

    @property
    def form(self) -> "HTMLElement | None":
        """Nearest ancestor ``<form>`` element, or ``None``.

        Returns the form owner per the simplified WHATWG form-association
        algorithm (ancestor walk). Returns ``None`` for detached elements
        or elements not nested inside a ``<form>``.

        Examples
        --------
        >>> from aspose_html.html_document import HTMLDocument
        >>> doc = HTMLDocument.parse('<form id="f"><select id="s"></select></form>')
        >>> doc.get_element_by_id("s").form is doc.get_element_by_id("f")
        True
        """
        return _get_form_owner(self)

    @property
    def autofocus(self) -> bool:
        """Boolean presence attribute reflecting the HTML ``autofocus`` attribute.

        Presence means ``True``; absence means ``False``.
        Setting ``True`` writes an empty-string attribute value; setting
        ``False`` removes the attribute entirely.

        Per WHATWG HTML §4.10.7.1.

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> doc = Document()
        >>> sel = doc.create_element("select")
        >>> sel.autofocus
        False
        >>> sel.autofocus = True
        >>> sel.autofocus
        True
        >>> sel.autofocus = False
        >>> sel.autofocus
        False
        """
        return self.has_attribute("autofocus")

    @autofocus.setter
    def autofocus(self, value: bool) -> None:
        if value:
            self.set_attribute("autofocus", "")
        else:
            self.remove_attribute("autofocus")

    @property
    def labels(self):
        """Return empty static NodeList — no label association in headless mode.

        Per WHATWG HTML §4.10.18.5.

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> doc = Document()
        >>> sel = doc.create_element("select")
        >>> len(sel.labels)
        0
        >>> list(sel.labels)
        []
        """
        from aspose_html.dom._collections import _StaticNodeList  # noqa: PLC0415
        return _StaticNodeList([])


# ---------------------------------------------------------------------------
# HTMLTextAreaElement  (BACK-43 / ADR-037)
# ---------------------------------------------------------------------------

class HTMLTextAreaElement(_ConstraintValidationMixin, HTMLElement):
    """HTML ``<textarea>`` multi-line text input element.

    Reflects IDL attributes: name, placeholder, rows, cols, max_length,
    min_length, disabled, read_only, required. The value property reads the
    first Text child node.

    Examples
    --------
    >>> from aspose_html.dom import Document
    >>> doc = Document()
    >>> ta = doc.create_element("textarea")
    >>> isinstance(ta, HTMLTextAreaElement)
    True
    >>> ta.rows
    0
    >>> ta.placeholder
    ''
    """

    __slots__ = ("_custom_validity_message",)

    @property
    def name(self) -> str:
        """The ``name`` attribute value, or ``''`` when absent.

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> doc = Document()
        >>> ta = doc.create_element("textarea")
        >>> ta.name
        ''
        >>> ta.name = "bio"
        >>> ta.name
        'bio'
        """
        return self.get_attribute("name") or ""

    @name.setter
    def name(self, value: str) -> None:
        self.set_attribute("name", value)

    @property
    def placeholder(self) -> str:
        """The ``placeholder`` attribute value, or ``''`` when absent.

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> doc = Document()
        >>> ta = doc.create_element("textarea")
        >>> ta.placeholder
        ''
        >>> ta.placeholder = "Enter text here"
        >>> ta.placeholder
        'Enter text here'
        """
        return self.get_attribute("placeholder") or ""

    @placeholder.setter
    def placeholder(self, value: str) -> None:
        self.set_attribute("placeholder", value)

    @property
    def rows(self) -> int:
        """The ``rows`` attribute as an integer (default ``0``).

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> doc = Document()
        >>> ta = doc.create_element("textarea")
        >>> ta.rows
        0
        >>> ta.rows = 5
        >>> ta.rows
        5
        """
        try:
            return int(self.get_attribute("rows") or 0)
        except ValueError:
            return 0

    @rows.setter
    def rows(self, value: int) -> None:
        self.set_attribute("rows", str(value))

    @property
    def cols(self) -> int:
        """The ``cols`` attribute as an integer (default ``0``).

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> doc = Document()
        >>> ta = doc.create_element("textarea")
        >>> ta.cols
        0
        >>> ta.cols = 40
        >>> ta.cols
        40
        """
        try:
            return int(self.get_attribute("cols") or 0)
        except ValueError:
            return 0

    @cols.setter
    def cols(self, value: int) -> None:
        self.set_attribute("cols", str(value))

    @property
    def max_length(self) -> int:
        """The ``maxlength`` attribute as an integer (default ``0``).

        Maps to the HTML ``maxlength`` attribute per WHATWG IDL (INV-001).

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> doc = Document()
        >>> ta = doc.create_element("textarea")
        >>> ta.max_length
        0
        >>> ta.max_length = 200
        >>> ta.max_length
        200
        """
        try:
            return int(self.get_attribute("maxlength") or 0)
        except ValueError:
            return 0

    @max_length.setter
    def max_length(self, value: int) -> None:
        self.set_attribute("maxlength", str(value))

    @property
    def min_length(self) -> int:
        """The ``minlength`` attribute as an integer (default ``0``).

        Maps to the HTML ``minlength`` attribute per WHATWG IDL (INV-001).

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> doc = Document()
        >>> ta = doc.create_element("textarea")
        >>> ta.min_length
        0
        >>> ta.min_length = 10
        >>> ta.min_length
        10
        """
        try:
            return int(self.get_attribute("minlength") or 0)
        except ValueError:
            return 0

    @min_length.setter
    def min_length(self, value: int) -> None:
        self.set_attribute("minlength", str(value))

    @property
    def disabled(self) -> bool:
        """Boolean presence attribute ``disabled``.

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> doc = Document()
        >>> ta = doc.create_element("textarea")
        >>> ta.disabled
        False
        >>> ta.disabled = True
        >>> ta.disabled
        True
        """
        return self.has_attribute("disabled")

    @disabled.setter
    def disabled(self, value: bool) -> None:
        if value:
            self.set_attribute("disabled", "")
        else:
            self.remove_attribute("disabled")

    @property
    def read_only(self) -> bool:
        """Boolean presence attribute reflecting the HTML ``readonly`` attribute.

        Named ``read_only`` per INV-001 (WHATWG IDL ``readOnly`` -> snake_case).

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> doc = Document()
        >>> ta = doc.create_element("textarea")
        >>> ta.read_only
        False
        >>> ta.read_only = True
        >>> ta.read_only
        True
        """
        return self.has_attribute("readonly")

    @read_only.setter
    def read_only(self, value: bool) -> None:
        if value:
            self.set_attribute("readonly", "")
        else:
            self.remove_attribute("readonly")

    @property
    def required(self) -> bool:
        """Boolean presence attribute ``required``.

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> doc = Document()
        >>> ta = doc.create_element("textarea")
        >>> ta.required
        False
        >>> ta.required = True
        >>> ta.required
        True
        """
        return self.has_attribute("required")

    @required.setter
    def required(self, value: bool) -> None:
        if value:
            self.set_attribute("required", "")
        else:
            self.remove_attribute("required")

    # ------------------------------------------------------------------
    # Additional IDL attributes (WHATWG HTML §4.10.11.1)
    # ------------------------------------------------------------------

    @property
    def wrap(self) -> str:
        """Reflects the ``wrap`` attribute, or ``''`` when absent.

        Per WHATWG HTML §4.10.11.1.

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> doc = Document()
        >>> ta = doc.create_element("textarea")
        >>> ta.wrap
        ''
        >>> ta.wrap = "soft"
        >>> ta.wrap
        'soft'
        """
        return self.get_attribute("wrap") or ""

    @wrap.setter
    def wrap(self, value: str) -> None:
        self.set_attribute("wrap", value)

    @property
    def autocomplete(self) -> str:
        """Reflects the ``autocomplete`` attribute, or ``''`` when absent.

        Per WHATWG HTML §4.10.11.1.

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> doc = Document()
        >>> ta = doc.create_element("textarea")
        >>> ta.autocomplete
        ''
        >>> ta.autocomplete = "on"
        >>> ta.autocomplete
        'on'
        """
        return self.get_attribute("autocomplete") or ""

    @autocomplete.setter
    def autocomplete(self, value: str) -> None:
        self.set_attribute("autocomplete", value)

    @property
    def autofocus(self) -> bool:
        """Boolean presence attribute reflecting the HTML ``autofocus`` attribute.

        Presence means ``True``; absence means ``False``.
        Setting ``True`` writes an empty-string attribute value; setting
        ``False`` removes the attribute entirely.

        Per WHATWG HTML §4.10.11.1.

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> doc = Document()
        >>> ta = doc.create_element("textarea")
        >>> ta.autofocus
        False
        >>> ta.autofocus = True
        >>> ta.autofocus
        True
        >>> ta.autofocus = False
        >>> ta.autofocus
        False
        """
        return self.has_attribute("autofocus")

    @autofocus.setter
    def autofocus(self, value: bool) -> None:
        if value:
            self.set_attribute("autofocus", "")
        else:
            self.remove_attribute("autofocus")

    @property
    def dirname(self) -> str:
        """Reflects the ``dirname`` attribute, or ``''`` when absent.

        Per WHATWG HTML §4.10.11.1.

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> doc = Document()
        >>> ta = doc.create_element("textarea")
        >>> ta.dirname
        ''
        >>> ta.dirname = "ltr"
        >>> ta.dirname
        'ltr'
        """
        return self.get_attribute("dirname") or ""

    @dirname.setter
    def dirname(self, value: str) -> None:
        self.set_attribute("dirname", value)

    # ------------------------------------------------------------------
    # WHATWG HTML §4.10.19.5 — text-selection API (headless stubs)
    # ------------------------------------------------------------------

    @property
    def selection_start(self) -> int:
        """Index of the start of the selected text (always ``0`` in headless mode).

        Per WHATWG HTML §4.10.19.5.

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> doc = Document()
        >>> ta = doc.create_element("textarea")
        >>> ta.selection_start
        0
        """
        return 0

    @property
    def selection_end(self) -> int:
        """Index of the end of the selected text (always ``0`` in headless mode).

        Per WHATWG HTML §4.10.19.5.

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> doc = Document()
        >>> ta = doc.create_element("textarea")
        >>> ta.selection_end
        0
        """
        return 0

    @property
    def selection_direction(self) -> str:
        """Direction of the selection (always ``"none"`` in headless mode).

        Per WHATWG HTML §4.10.19.5. Valid values are ``"forward"``,
        ``"backward"``, and ``"none"``.

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> doc = Document()
        >>> ta = doc.create_element("textarea")
        >>> ta.selection_direction
        'none'
        """
        return "none"

    def set_selection_range(
        self,
        start: int,
        end: int,
        direction: str = "none",
    ) -> None:
        """Set the selection boundaries (no-op in headless mode).

        Per WHATWG HTML §4.10.19.5.

        Parameters
        ----------
        start : int
            Start offset of the selection.
        end : int
            End offset of the selection.
        direction : str
            One of ``"forward"``, ``"backward"``, ``"none"``.

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> doc = Document()
        >>> ta = doc.create_element("textarea")
        >>> ta.set_selection_range(0, 5)  # no-op in headless mode
        """

    def select(self) -> None:
        """Select all text content (no-op in headless mode).

        Per WHATWG HTML §4.10.19.5.

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> doc = Document()
        >>> ta = doc.create_element("textarea")
        >>> ta.select()  # no-op in headless mode
        """

    @property
    def value(self) -> str:
        """Read the element's text content (first Text child data).

        This is a getter-only property for static parsing — it does not
        implement the full WHATWG value/dirty-value flag semantics.

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> doc = Document()
        >>> ta = doc.create_element("textarea")
        >>> doc.append_child(ta)
        <Element 'TEXTAREA'>
        >>> ta.value
        ''
        >>> _ = ta.append_child(doc.create_text_node("hello"))
        >>> ta.value
        'hello'
        """
        from aspose_html.dom._node_type import NodeType  # noqa: PLC0415
        child = self.first_child
        if child is not None and child._node_type == NodeType.TEXT_NODE:
            return child.data  # type: ignore[attr-defined]
        return ""

    @property
    def will_validate(self) -> bool:
        return not self.disabled

    def _compute_validity_state(self) -> ValidityState:
        if not self.will_validate:
            return ValidityState()

        value = self.value
        max_length = self.max_length
        min_length = self.min_length
        return ValidityState(
            value_missing=self.required and value == "",
            too_long=max_length >= 0 and len(value) > max_length,
            too_short=min_length >= 0 and value != "" and len(value) < min_length,
        )

    @property
    def form(self) -> "HTMLElement | None":
        """Nearest ancestor ``<form>`` element, or ``None``.

        Returns the form owner per the simplified WHATWG form-association
        algorithm (ancestor walk). Returns ``None`` for detached elements
        or elements not nested inside a ``<form>``.

        Examples
        --------
        >>> from aspose_html.html_document import HTMLDocument
        >>> doc = HTMLDocument.parse('<form id="f"><textarea id="t"></textarea></form>')
        >>> doc.get_element_by_id("t").form is doc.get_element_by_id("f")
        True
        """
        return _get_form_owner(self)

    # -- IDL tail properties (ADR-294) ----------------------------------------

    @property
    def default_value(self) -> str:
        """The raw text content of the textarea (markup default).

        Per WHATWG HTML §4.10.11.2. The getter returns the element's
        ``text_content`` (or ``''``). The setter replaces text content.

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> doc = Document()
        >>> ta = doc.create_element("textarea")
        >>> ta.default_value
        ''
        >>> ta.default_value = "hello"
        >>> ta.default_value
        'hello'
        """
        return self.text_content or ""

    @default_value.setter
    def default_value(self, value: str) -> None:
        self.text_content = value

    @property
    def text_length(self) -> int:
        """Length of the current textarea value in UTF-16 code units.

        Per WHATWG HTML §4.10.11.1. Equivalent to ``len(self.value)``.

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> doc = Document()
        >>> ta = doc.create_element("textarea")
        >>> ta.text_length
        0
        >>> ta.default_value = "abc"
        >>> ta.text_length
        3
        """
        return len(self.value)

    @property
    def dir_name(self) -> str:
        """The ``dirname`` attribute value, or ``''`` when absent.

        IDL name ``dirName`` → snake_case ``dir_name`` per INV-001.
        Reflects the HTML ``dirname`` attribute.

        Per WHATWG HTML §4.10.11.1.

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> doc = Document()
        >>> ta = doc.create_element("textarea")
        >>> ta.dir_name
        ''
        >>> ta.dir_name = "ltr"
        >>> ta.dir_name
        'ltr'
        """
        return self.get_attribute("dirname") or ""

    @dir_name.setter
    def dir_name(self, value: str) -> None:
        self.set_attribute("dirname", value)

    @property
    def labels(self) -> "_StaticNodeList":
        """Associated ``<label>`` elements (headless stub: always empty).

        Per WHATWG HTML §4.10.18.5. In headless mode, label association
        requires rendering-context semantics that are out of scope.

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> doc = Document()
        >>> ta = doc.create_element("textarea")
        >>> len(ta.labels)
        0
        >>> list(ta.labels)
        []
        """
        from aspose_html.dom._collections import _StaticNodeList  # noqa: PLC0415
        return _StaticNodeList([])

    @property
    def type(self) -> str:
        """Read-only IDL attribute; always ``'textarea'`` (WHATWG HTML §4.10.11.1).

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> doc = Document()
        >>> ta = doc.create_element("textarea")
        >>> ta.type
        'textarea'
        """
        return "textarea"

    def set_range_text(self, replacement: str, *args, **kwargs) -> None:
        """Raise ``NotSupportedError`` — text-range selection unavailable headless.

        WHATWG HTML §4.10.11.1: in a rendering environment this replaces a
        substring. Headless mode has no selection pipeline.

        Raises
        ------
        NotSupportedError
            Always — headless mode does not support text-range selection.

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> from aspose_html.dom._exceptions import NotSupportedError
        >>> doc = Document()
        >>> ta = doc.create_element("textarea")
        >>> try:
        ...     ta.set_range_text("x")
        ... except NotSupportedError:
        ...     print("ok")
        ok
        """
        from aspose_html.dom._exceptions import NotSupportedError  # noqa: PLC0415
        raise NotSupportedError(
            "setRangeText is not supported in headless mode"
        )


# ---------------------------------------------------------------------------
# HTMLFieldSetElement  (BACK-43 / ADR-037)
# ---------------------------------------------------------------------------

class HTMLFieldSetElement(_ConstraintValidationMixin, HTMLElement):
    """HTML ``<fieldset>`` element for grouping form controls.

    Reflects IDL attributes: name, disabled.
    Participates in constraint validation via ``_ConstraintValidationMixin``
    (WHATWG HTML §4.10.21.2).

    Examples
    --------
    >>> from aspose_html.dom import Document
    >>> doc = Document()
    >>> fs = doc.create_element("fieldset")
    >>> isinstance(fs, HTMLFieldSetElement)
    True
    >>> fs.name
    ''
    >>> fs.disabled
    False
    >>> fs.check_validity()
    True
    """

    __slots__ = ("_custom_validity_message",)

    @property
    def name(self) -> str:
        """The ``name`` attribute value, or ``''`` when absent.

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> doc = Document()
        >>> fs = doc.create_element("fieldset")
        >>> fs.name
        ''
        >>> fs.name = "personal"
        >>> fs.name
        'personal'
        """
        return self.get_attribute("name") or ""

    @name.setter
    def name(self, value: str) -> None:
        self.set_attribute("name", value)

    @property
    def disabled(self) -> bool:
        """Boolean presence attribute ``disabled``.

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> doc = Document()
        >>> fs = doc.create_element("fieldset")
        >>> fs.disabled
        False
        >>> fs.disabled = True
        >>> fs.disabled
        True
        """
        return self.has_attribute("disabled")

    @disabled.setter
    def disabled(self, value: bool) -> None:
        if value:
            self.set_attribute("disabled", "")
        else:
            self.remove_attribute("disabled")

    @property
    def type(self) -> str:
        """Always returns ``"fieldset"`` (read-only IDL constant).

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> doc = Document()
        >>> doc.create_element("fieldset").type
        'fieldset'
        """
        return "fieldset"

    def _compute_validity_state(self) -> "ValidityState":
        """Return default validity state (no intrinsic validity constraint).

        ``HTMLFieldSetElement`` does not itself fail any validity check;
        only its descendant controls do. A fresh fieldset is always valid
        per WHATWG HTML §4.10.21.2.
        """
        return ValidityState()

    @property
    def elements(self) -> "HTMLCollection":
        """Live collection of listed form controls within this fieldset.

        Listed elements: button, fieldset, input, object, output, select,
        textarea. Scans the subtree on every access (live per INV-005).

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> doc = Document()
        >>> fs = doc.create_element("fieldset")
        >>> len(fs.elements)
        0
        >>> _ = fs.append_child(doc.create_element("input"))
        >>> len(fs.elements)
        1
        """
        from aspose_html.dom._collections import _SubtreeHTMLCollection
        _LISTED = frozenset(
            {"BUTTON", "FIELDSET", "INPUT", "OBJECT", "OUTPUT", "SELECT", "TEXTAREA"}
        )
        return _SubtreeHTMLCollection(
            self, lambda el: el._tag_name in _LISTED
        )

    @property
    def form(self) -> "HTMLFormElement | None":
        """Nearest ancestor ``HTMLFormElement``, or ``None`` if not associated (WHATWG HTML §4.10.17).

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> doc = Document()
        >>> el = doc.create_element('fieldset')
        >>> el.form is None
        True
        """
        node = self.parent_node
        while node is not None:
            if isinstance(node, HTMLFormElement):
                return node
            node = node.parent_node
        return None


# ---------------------------------------------------------------------------
# HTMLOptionElement  (BACK-43 / ADR-037)
# ---------------------------------------------------------------------------

class HTMLOptionElement(HTMLElement):
    """HTML ``<option>`` element representing a choice in a select list.

    Reflects IDL attributes: value, label, disabled, selected,
    default_selected. The text property reads the first Text child.

    Examples
    --------
    >>> from aspose_html.dom import Document
    >>> doc = Document()
    >>> opt = doc.create_element("option")
    >>> isinstance(opt, HTMLOptionElement)
    True
    >>> opt.value
    ''
    >>> opt.selected
    False
    """

    __slots__ = ()

    @property
    def value(self) -> str:
        """The ``value`` attribute value, or ``''`` when absent.

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> doc = Document()
        >>> opt = doc.create_element("option")
        >>> opt.value
        ''
        >>> opt.value = "fr"
        >>> opt.value
        'fr'
        """
        return self.get_attribute("value") or ""

    @value.setter
    def value(self, value: str) -> None:
        self.set_attribute("value", value)

    @property
    def label(self) -> str:
        """The ``label`` attribute value, or ``''`` when absent.

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> doc = Document()
        >>> opt = doc.create_element("option")
        >>> opt.label
        ''
        >>> opt.label = "France"
        >>> opt.label
        'France'
        """
        return self.get_attribute("label") or ""

    @label.setter
    def label(self, value: str) -> None:
        self.set_attribute("label", value)

    @property
    def disabled(self) -> bool:
        """Boolean presence attribute ``disabled``.

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> doc = Document()
        >>> opt = doc.create_element("option")
        >>> opt.disabled
        False
        >>> opt.disabled = True
        >>> opt.disabled
        True
        """
        return self.has_attribute("disabled")

    @disabled.setter
    def disabled(self, value: bool) -> None:
        if value:
            self.set_attribute("disabled", "")
        else:
            self.remove_attribute("disabled")

    @property
    def selected(self) -> bool:
        """Boolean presence attribute ``selected`` (runtime selection state).

        For static parsing this reflects the ``selected`` attribute directly.

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> doc = Document()
        >>> opt = doc.create_element("option")
        >>> opt.selected
        False
        >>> opt.selected = True
        >>> opt.selected
        True
        """
        return self.has_attribute("selected")

    @selected.setter
    def selected(self, value: bool) -> None:
        if value:
            self.set_attribute("selected", "")
        else:
            self.remove_attribute("selected")

    @property
    def default_selected(self) -> bool:
        """Whether the ``selected`` attribute was present in the markup.

        Reflects the presence of the HTML ``selected`` attribute. For static
        parsing this is identical to ``selected`` — both check the attribute.

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> doc = Document()
        >>> opt = doc.create_element("option")
        >>> opt.default_selected
        False
        >>> opt.default_selected = True
        >>> opt.default_selected
        True
        """
        return self.has_attribute("selected")

    @default_selected.setter
    def default_selected(self, value: bool) -> None:
        if value:
            self.set_attribute("selected", "")
        else:
            self.remove_attribute("selected")

    @property
    def text(self) -> str:
        """The text content of the option element (first Text child data).

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> doc = Document()
        >>> opt = doc.create_element("option")
        >>> doc.append_child(opt)
        <Element 'OPTION'>
        >>> opt.text
        ''
        >>> _ = opt.append_child(doc.create_text_node("France"))
        >>> opt.text
        'France'
        """
        from aspose_html.dom._node_type import NodeType  # noqa: PLC0415
        child = self.first_child
        if child is not None and child._node_type == NodeType.TEXT_NODE:
            return child.data  # type: ignore[attr-defined]
        return ""

    @property
    def index(self) -> int:
        """0-based index of this option in its parent select's options list.

        Returns ``0`` when this option is detached or not under a ``<select>``.

        Examples
        --------
        >>> from aspose_html.html_document import HTMLDocument
        >>> doc = HTMLDocument.parse('<select><option>a</option><option id="b">b</option></select>')
        >>> sel = doc.query_selector("select")
        >>> sel.options[0].index
        0
        >>> sel.options[1].index
        1
        >>> from aspose_html.dom import Document
        >>> detached = Document().create_element("option")
        >>> detached.index
        0
        """
        parent = self.parent_node
        if getattr(parent, "_tag_name", None) == "OPTGROUP":
            parent = parent.parent_node
        if not isinstance(parent, HTMLSelectElement):
            return 0

        for idx, option in enumerate(parent.options):
            if option is self:
                return idx
        return 0

    @property
    def form(self) -> "HTMLElement | None":
        """Form owner via this option's parent select, or ``None``.

        Examples
        --------
        >>> from aspose_html.html_document import HTMLDocument
        >>> doc = HTMLDocument.parse('<form id="f"><select><option id="o">x</option></select></form>')
        >>> opt = doc.get_element_by_id("o")
        >>> opt.form is doc.get_element_by_id("f")
        True
        >>> from aspose_html.dom import Document
        >>> detached = Document().create_element("option")
        >>> detached.form is None
        True
        """
        parent = self.parent_node
        if getattr(parent, "_tag_name", None) == "OPTGROUP":
            parent = parent.parent_node
        if isinstance(parent, HTMLSelectElement):
            return parent.form
        return None


# ---------------------------------------------------------------------------
# HTMLOptGroupElement  (BACK-43 / ADR-037)
# ---------------------------------------------------------------------------

class HTMLOptGroupElement(HTMLElement):
    """HTML ``<optgroup>`` element for grouping options in a select list.

    Reflects IDL attributes: label, disabled.

    Examples
    --------
    >>> from aspose_html.dom import Document
    >>> doc = Document()
    >>> og = doc.create_element("optgroup")
    >>> isinstance(og, HTMLOptGroupElement)
    True
    >>> og.label
    ''
    >>> og.disabled
    False
    """

    __slots__ = ()

    @property
    def label(self) -> str:
        """The ``label`` attribute value, or ``''`` when absent.

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> doc = Document()
        >>> og = doc.create_element("optgroup")
        >>> og.label
        ''
        >>> og.label = "Europe"
        >>> og.label
        'Europe'
        """
        return self.get_attribute("label") or ""

    @label.setter
    def label(self, value: str) -> None:
        self.set_attribute("label", value)

    @property
    def disabled(self) -> bool:
        """Boolean presence attribute ``disabled``.

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> doc = Document()
        >>> og = doc.create_element("optgroup")
        >>> og.disabled
        False
        >>> og.disabled = True
        >>> og.disabled
        True
        """
        return self.has_attribute("disabled")

    @disabled.setter
    def disabled(self, value: bool) -> None:
        if value:
            self.set_attribute("disabled", "")
        else:
            self.remove_attribute("disabled")


# ---------------------------------------------------------------------------
# HTMLOutputElement  (BACK-43 / ADR-037)
# ---------------------------------------------------------------------------

class HTMLOutputElement(_ConstraintValidationMixin, HTMLElement):
    """HTML ``<output>`` element for displaying calculation results.

    Reflects IDL attributes: ``name``, ``default_value``, ``type``,
    ``value``, and ``html_for`` (WHATWG §4.10.12).

    Examples
    --------
    >>> from aspose_html.dom import Document
    >>> doc = Document()
    >>> out = doc.create_element("output")
    >>> isinstance(out, HTMLOutputElement)
    True
    >>> out.name
    ''
    >>> out.default_value
    ''
    """

    __slots__ = ("_custom_validity_message", "_html_for")

    @property
    def name(self) -> str:
        """The ``name`` attribute value, or ``''`` when absent.

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> doc = Document()
        >>> out = doc.create_element("output")
        >>> out.name
        ''
        >>> out.name = "result"
        >>> out.name
        'result'
        """
        return self.get_attribute("name") or ""

    @name.setter
    def name(self, value: str) -> None:
        self.set_attribute("name", value)

    @property
    def default_value(self) -> str:
        """The HTML ``defaultvalue`` attribute value, or ``''`` when absent.

        Maps to the HTML ``defaultvalue`` attribute (all lowercase) per WHATWG
        IDL. Python property name uses snake_case per INV-001.

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> doc = Document()
        >>> out = doc.create_element("output")
        >>> out.default_value
        ''
        >>> out.default_value = "42"
        >>> out.default_value
        '42'
        """
        return self.get_attribute("defaultvalue") or ""

    @default_value.setter
    def default_value(self, value: str) -> None:
        self.set_attribute("defaultvalue", value)

    @property
    def type(self) -> str:
        """Always returns ``"output"`` (read-only IDL constant, WHATWG §4.10.12).

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> doc = Document()
        >>> doc.create_element("output").type
        'output'
        """
        return "output"

    @property
    def type_(self) -> str:
        """Always returns ``"output"`` per WHATWG HTML §4.10.19.4.

        IDL snake_case alias for :attr:`type` following the ``type_``
        convention used across embedded/source/input elements to avoid
        shadowing the Python built-in ``type``.

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> doc = Document()
        >>> doc.create_element("output").type_
        'output'
        """
        return "output"

    @property
    def value(self) -> str:
        """Current output value.

        Returns the ``data`` of the first ``Text`` child node when one exists;
        otherwise returns :attr:`default_value`. Setting ``value`` replaces
        the element's text content.

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> doc = Document()
        >>> out = doc.create_element("output")
        >>> out.value
        ''
        >>> doc.append_child(out)
        <Element 'OUTPUT'>
        >>> out.value = "42"
        >>> out.value
        '42'
        """
        from aspose_html.dom._node_type import NodeType  # noqa: PLC0415
        child = self.first_child
        if child is not None and child._node_type == NodeType.TEXT_NODE:
            return child.data  # type: ignore[attr-defined]
        return self.default_value

    @value.setter
    def value(self, v: str) -> None:
        from aspose_html.dom._node_type import NodeType  # noqa: PLC0415
        # Remove existing text children
        for child in list(self._children):
            if child._node_type == NodeType.TEXT_NODE:
                self.remove_child(child)
        if v:
            doc = self._owner_document
            if doc is not None:
                self.append_child(doc.create_text_node(v))

    @property
    def html_for(self) -> "DOMTokenList":
        """``DOMTokenList`` backed by the ``for`` attribute (WHATWG §4.10.12).

        The same instance is returned on every access (live view per INV-005).

        Examples
        --------
        >>> from aspose_html.dom import Document, DOMTokenList
        >>> doc = Document()
        >>> out = doc.create_element("output")
        >>> isinstance(out.html_for, DOMTokenList)
        True
        >>> out.html_for is out.html_for
        True
        >>> out.html_for.add("field1")
        >>> out.get_attribute("for")
        'field1'
        """
        cached = getattr(self, "_html_for", None)
        if cached is None:
            from aspose_html.dom._token_list import DOMTokenList  # noqa: PLC0415
            cached = DOMTokenList(self, "for")
            object.__setattr__(self, "_html_for", cached)
        return cached

    @property
    def will_validate(self) -> bool:
        return False

    def _compute_validity_state(self) -> ValidityState:
        return ValidityState()

    @property
    def form(self) -> "HTMLElement | None":
        """Nearest ancestor ``<form>`` element, or ``None``.

        Returns the form owner per the simplified WHATWG form-association
        algorithm (ancestor walk). Returns ``None`` for detached elements
        or elements not nested inside a ``<form>``.

        Examples
        --------
        >>> from aspose_html.html_document import HTMLDocument
        >>> doc = HTMLDocument.parse('<form id="f"><output id="o"></output></form>')
        >>> doc.get_element_by_id("o").form is doc.get_element_by_id("f")
        True
        """
        return _get_form_owner(self)

    @property
    def labels(self) -> "_StaticNodeList":
        """Return an empty node list stub (WHATWG HTML §4.10.12).

        In headless mode label association is not tracked; returns an empty
        ``_StaticNodeList`` to satisfy API shape without raising.

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> out = Document().create_element('output')
        >>> len(out.labels)
        0
        >>> list(out.labels)
        []
        """
        from aspose_html.dom._collections import _StaticNodeList  # noqa: PLC0415
        return _StaticNodeList([])


# ---------------------------------------------------------------------------
# HTMLDataListElement  (BACK-43 / ADR-037)
# ---------------------------------------------------------------------------

class HTMLDataListElement(HTMLElement):
    """HTML ``<datalist>`` element providing autocomplete suggestions.

    Implements the ``options`` IDL attribute (WHATWG HTML §4.10.20) returning
    a live collection of ``<option>`` child elements.

    Examples
    --------
    >>> from aspose_html.dom import Document
    >>> doc = Document()
    >>> dl = doc.create_element("datalist")
    >>> isinstance(dl, HTMLDataListElement)
    True
    """

    __slots__ = ()

    @property
    def options(self):
        """Live HTMLCollection of ``<option>`` child elements.

        WHATWG HTML §4.10.20. Uses the existing ``_SubtreeHTMLCollection``
        helper with a tag filter for ``"option"``.

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> doc = Document()
        >>> dl = doc.create_element("datalist")
        >>> opt1 = doc.create_element("option")
        >>> opt2 = doc.create_element("option")
        >>> span = doc.create_element("span")
        >>> _ = dl.append_child(opt1)
        >>> _ = dl.append_child(opt2)
        >>> _ = dl.append_child(span)
        >>> len(dl.options)
        2
        """
        from aspose_html.dom._collections import _SubtreeHTMLCollection  # noqa: PLC0415
        return _SubtreeHTMLCollection(self, lambda el: el._local_name == "option")


# ---------------------------------------------------------------------------
# HTMLProgressElement  (BACK-43 / ADR-037)
# ---------------------------------------------------------------------------

class HTMLProgressElement(HTMLElement):
    """HTML ``<progress>`` element showing task completion.

    Reflects IDL attributes: value (float, default 0.0), max (float, default 1.0).

    Examples
    --------
    >>> from aspose_html.dom import Document
    >>> doc = Document()
    >>> prog = doc.create_element("progress")
    >>> isinstance(prog, HTMLProgressElement)
    True
    >>> prog.value
    0.0
    >>> prog.max
    1.0
    """

    __slots__ = ()

    @property
    def value(self) -> float:
        """Float IDL attribute reflecting ``'value'``. Default ``0.0``.

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> doc = Document()
        >>> prog = doc.create_element("progress")
        >>> prog.value
        0.0
        >>> prog.value = 0.5
        >>> prog.value
        0.5
        """
        try:
            return float(self.get_attribute("value") or 0.0)
        except ValueError:
            return 0.0

    @value.setter
    def value(self, v: float) -> None:
        self.set_attribute("value", str(v))

    @property
    def max(self) -> float:
        """Float IDL attribute reflecting ``'max'``. Default ``1.0``.

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> doc = Document()
        >>> prog = doc.create_element("progress")
        >>> prog.max
        1.0
        >>> prog.max = 2.0
        >>> prog.max
        2.0
        """
        try:
            return float(self.get_attribute("max") or 1.0)
        except ValueError:
            return 1.0

    @max.setter
    def max(self, v: float) -> None:
        self.set_attribute("max", str(v))

    @property
    def position(self) -> float:
        """Ratio ``value / max``, or ``-1.0`` when indeterminate (WHATWG HTML §4.10.15).

        Returns ``-1.0`` when the ``value`` attribute is absent (indeterminate
        state).  Otherwise returns ``value / max`` clamped to ``[0.0, 1.0]``.
        Falls back to ``-1.0`` on malformed attribute values.

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> doc = Document()
        >>> el = doc.create_element('progress')
        >>> el.position
        -1.0
        >>> el.set_attribute('value', '5')
        >>> el.set_attribute('max', '10')
        >>> el.position
        0.5
        """
        val_attr = self.get_attribute("value")
        if val_attr is None:
            return -1.0
        try:
            v = float(val_attr)
            max_attr = self.get_attribute("max")
            m = float(max_attr) if max_attr is not None else 1.0
            if m <= 0:
                return -1.0
            return max(0.0, min(1.0, v / m))
        except (ValueError, ZeroDivisionError):
            return -1.0

    @property
    def labels(self) -> "_StaticNodeList":
        """Headless empty label association list (WHATWG HTML §4.10.18.5).

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> doc = Document()
        >>> el = doc.create_element('progress')
        >>> len(el.labels)
        0
        """
        from aspose_html.dom._collections import _StaticNodeList  # noqa: PLC0415
        return _StaticNodeList([])


# ---------------------------------------------------------------------------
# HTMLMeterElement  (BACK-43 / ADR-037)
# ---------------------------------------------------------------------------

class HTMLMeterElement(HTMLElement):
    """HTML ``<meter>`` element for displaying a scalar value in a range.

    Reflects IDL attributes: value, min, max, low, high, optimum (all float).

    Examples
    --------
    >>> from aspose_html.dom import Document
    >>> doc = Document()
    >>> meter = doc.create_element("meter")
    >>> isinstance(meter, HTMLMeterElement)
    True
    >>> meter.value
    0.0
    >>> meter.min
    0.0
    >>> meter.max
    1.0
    """

    __slots__ = ()

    @property
    def value(self) -> float:
        """Float IDL attribute reflecting ``'value'``. Default ``0.0``.

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> doc = Document()
        >>> meter = doc.create_element("meter")
        >>> meter.value
        0.0
        >>> meter.value = 0.7
        >>> meter.value
        0.7
        """
        try:
            return float(self.get_attribute("value") or 0.0)
        except ValueError:
            return 0.0

    @value.setter
    def value(self, v: float) -> None:
        self.set_attribute("value", str(v))

    @property
    def min(self) -> float:
        """Float IDL attribute reflecting ``'min'``. Default ``0.0``.

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> doc = Document()
        >>> meter = doc.create_element("meter")
        >>> meter.min
        0.0
        >>> meter.min = 0.5
        >>> meter.min
        0.5
        """
        try:
            return float(self.get_attribute("min") or 0.0)
        except ValueError:
            return 0.0

    @min.setter
    def min(self, v: float) -> None:
        self.set_attribute("min", str(v))

    @property
    def max(self) -> float:
        """Float IDL attribute reflecting ``'max'``. Default ``1.0``.

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> doc = Document()
        >>> meter = doc.create_element("meter")
        >>> meter.max
        1.0
        >>> meter.max = 5.0
        >>> meter.max
        5.0
        """
        try:
            return float(self.get_attribute("max") or 1.0)
        except ValueError:
            return 1.0

    @max.setter
    def max(self, v: float) -> None:
        self.set_attribute("max", str(v))

    @property
    def low(self) -> float:
        """Float IDL attribute reflecting ``'low'``. Default ``0.0``.

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> doc = Document()
        >>> meter = doc.create_element("meter")
        >>> meter.low
        0.0
        >>> meter.low = 0.25
        >>> meter.low
        0.25
        """
        try:
            return float(self.get_attribute("low") or 0.0)
        except ValueError:
            return 0.0

    @low.setter
    def low(self, v: float) -> None:
        self.set_attribute("low", str(v))

    @property
    def high(self) -> float:
        """Float IDL attribute reflecting ``'high'``. Default ``0.0``.

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> doc = Document()
        >>> meter = doc.create_element("meter")
        >>> meter.high
        0.0
        >>> meter.high = 0.75
        >>> meter.high
        0.75
        """
        try:
            return float(self.get_attribute("high") or 0.0)
        except ValueError:
            return 0.0

    @high.setter
    def high(self, v: float) -> None:
        self.set_attribute("high", str(v))

    @property
    def optimum(self) -> float:
        """Float IDL attribute reflecting ``'optimum'``. Default ``0.0``.

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> doc = Document()
        >>> meter = doc.create_element("meter")
        >>> meter.optimum
        0.0
        >>> meter.optimum = 0.6
        >>> meter.optimum
        0.6
        """
        try:
            return float(self.get_attribute("optimum") or 0.0)
        except ValueError:
            return 0.0

    @optimum.setter
    def optimum(self, v: float) -> None:
        self.set_attribute("optimum", str(v))

    @property
    def labels(self) -> "_StaticNodeList":
        """Headless empty label association list (WHATWG HTML §4.10.16).

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> doc = Document()
        >>> el = doc.create_element('meter')
        >>> len(el.labels)
        0
        """
        from aspose_html.dom._collections import _StaticNodeList  # noqa: PLC0415
        return _StaticNodeList([])



class HTMLLabelElement(HTMLElement):
    """HTML ``<label>`` element.

    Reflects ``for`` attribute as ``html_for`` (Python-safe identifier).
    """

    __slots__ = ()

    @property
    def html_for(self) -> str:
        """The ``for`` attribute value, exposed as ``html_for``.

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> doc = Document()
        >>> label = doc.create_element("label")
        >>> label.html_for
        ''
        >>> label.html_for = "email"
        >>> label.get_attribute("for")
        'email'
        """
        return self.get_attribute("for") or ""

    @html_for.setter
    def html_for(self, value: str) -> None:
        self.set_attribute("for", value)

    @property
    def control(self) -> "Element | None":
        """The element whose ``id`` matches this label's ``html_for``, or ``None``.

        Examples
        --------
        >>> from aspose_html.html_document import HTMLDocument
        >>> doc = HTMLDocument.parse('<label for="i" id="l">Name</label><input id="i">')
        >>> label = doc.get_element_by_id("l")
        >>> label.control is doc.get_element_by_id("i")
        True
        >>> from aspose_html.dom import Document
        >>> detached = Document().create_element("label")
        >>> detached.control is None
        True
        """
        for_id = self.html_for
        if not for_id:
            return None
        doc = self._owner_document
        if doc is None:
            return None
        return doc.get_element_by_id(for_id)

    @property
    def form(self) -> "HTMLElement | None":
        """Form owner of this label's associated control, or ``None``.

        Examples
        --------
        >>> from aspose_html.html_document import HTMLDocument
        >>> doc = HTMLDocument.parse('<form id="f"><label for="i" id="l">N</label><input id="i"></form>')
        >>> label = doc.get_element_by_id("l")
        >>> label.form is doc.get_element_by_id("f")
        True
        >>> from aspose_html.dom import Document
        >>> detached = Document().create_element("label")
        >>> detached.form is None
        True
        """
        ctrl = self.control
        if ctrl is None:
            return None
        return getattr(ctrl, "form", None)



class HTMLLegendElement(HTMLElement):
    """HTML ``<legend>`` element (WHATWG §4.10.4).

    Reflects the ``form`` IDL attribute, which returns the owner form of
    the nearest ancestor ``<fieldset>``, or ``None``.

    Examples
    --------
    >>> from aspose_html.dom import Document
    >>> doc = Document()
    >>> isinstance(doc.create_element("legend"), HTMLLegendElement)
    True
    """

    __slots__ = ()

    @property
    def form(self) -> "HTMLElement | None":
        """Owner form of the nearest ancestor ``<fieldset>``, or ``None``.

        Walks up the parent chain to find the first ``<fieldset>`` ancestor,
        then walks from there to find the nearest ``<form>`` ancestor.
        Returns ``None`` if no ``<fieldset>`` ancestor exists or the fieldset
        has no ``<form>`` ancestor.

        Examples
        --------
        >>> from aspose_html.html_document import HTMLDocument
        >>> doc = HTMLDocument.parse(
        ...     '<form id="f"><fieldset><legend id="lg"></legend></fieldset></form>'
        ... )
        >>> legend = doc.get_element_by_id("lg")
        >>> form = doc.get_element_by_id("f")
        >>> legend.form is form
        True
        """
        # Walk to first <fieldset> ancestor
        node = self._parent
        fieldset = None
        while node is not None:
            if getattr(node, "_tag_name", None) == "FIELDSET":
                fieldset = node
                break
            node = node._parent
        if fieldset is None:
            return None
        # Walk to first <form> ancestor of fieldset
        node = fieldset._parent
        while node is not None:
            if getattr(node, "_tag_name", None) == "FORM":
                return node  # type: ignore[return-value]
            node = node._parent
        return None




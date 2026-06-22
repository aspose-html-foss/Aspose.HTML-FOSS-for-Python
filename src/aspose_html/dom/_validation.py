"""Constraint validation primitives for HTML form controls.
"""
from __future__ import annotations

class ValidityState:
    """Constraint-validation flags for a form control.

    Examples
    --------
    >>> state = ValidityState(value_missing=True)
    >>> state.value_missing
    True
    >>> state.valid
    False
    """

    __slots__ = (
        "_value_missing",
        "_type_mismatch",
        "_pattern_mismatch",
        "_too_long",
        "_too_short",
        "_range_underflow",
        "_range_overflow",
        "_step_mismatch",
        "_bad_input",
        "_custom_error",
    )

    def __init__(
        self,
        *,
        value_missing: bool = False,
        type_mismatch: bool = False,
        pattern_mismatch: bool = False,
        too_long: bool = False,
        too_short: bool = False,
        range_underflow: bool = False,
        range_overflow: bool = False,
        step_mismatch: bool = False,
        bad_input: bool = False,
        custom_error: bool = False,
    ) -> None:
        self._value_missing = value_missing
        self._type_mismatch = type_mismatch
        self._pattern_mismatch = pattern_mismatch
        self._too_long = too_long
        self._too_short = too_short
        self._range_underflow = range_underflow
        self._range_overflow = range_overflow
        self._step_mismatch = step_mismatch
        self._bad_input = bad_input
        self._custom_error = custom_error

    @property
    def value_missing(self) -> bool:
        return self._value_missing

    @property
    def type_mismatch(self) -> bool:
        return self._type_mismatch

    @property
    def pattern_mismatch(self) -> bool:
        return self._pattern_mismatch

    @property
    def too_long(self) -> bool:
        return self._too_long

    @property
    def too_short(self) -> bool:
        return self._too_short

    @property
    def range_underflow(self) -> bool:
        return self._range_underflow

    @property
    def range_overflow(self) -> bool:
        return self._range_overflow

    @property
    def step_mismatch(self) -> bool:
        return self._step_mismatch

    @property
    def bad_input(self) -> bool:
        return self._bad_input

    @property
    def custom_error(self) -> bool:
        return self._custom_error

    @property
    def valid(self) -> bool:
        """Whether all non-``valid`` flags are false.

        Examples
        --------
        >>> ValidityState().valid
        True
        >>> ValidityState(custom_error=True).valid
        False
        """
        return not any(
            (
                self.value_missing,
                self.type_mismatch,
                self.pattern_mismatch,
                self.too_long,
                self.too_short,
                self.range_underflow,
                self.range_overflow,
                self.step_mismatch,
                self.bad_input,
                self.custom_error,
            )
        )


class _ConstraintValidationMixin:
    """Shared Constraint Validation API surface.
    """

    __slots__ = ()

    @property
    def validity(self) -> ValidityState:
        """Return computed validity flags for the control.
        """
        state = self._compute_validity_state()
        if getattr(self, "_custom_validity_message", "") == "":
            return state
        return ValidityState(
            value_missing=state.value_missing,
            type_mismatch=state.type_mismatch,
            pattern_mismatch=state.pattern_mismatch,
            too_long=state.too_long,
            too_short=state.too_short,
            range_underflow=state.range_underflow,
            range_overflow=state.range_overflow,
            step_mismatch=state.step_mismatch,
            bad_input=state.bad_input,
            custom_error=True,
        )

    @property
    def validation_message(self) -> str:
        """Current custom validation message, or ``''``.
        """
        return getattr(self, "_custom_validity_message", "")

    @property
    def will_validate(self) -> bool:
        """Whether this control participates in validation.
        """
        return True

    def check_validity(self) -> bool:
        """Return ``True`` when :attr:`validity` has no failing flag.
        """
        return self.validity.valid

    def report_validity(self) -> bool:
        """Same as :meth:`check_validity` in this non-UI implementation.
        """
        return self.check_validity()

    def set_custom_validity(self, message: str) -> None:
        """Set a custom validation error message.

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> inp = Document().create_element("input")
        >>> inp.set_custom_validity("bad")
        >>> inp.validation_message
        'bad'
        >>> inp.validity.custom_error
        True
        """
        self._custom_validity_message = message

    def _compute_validity_state(self) -> ValidityState:
        raise NotImplementedError

"""Internal browsing-context ownership state for Window lifecycle orchestration."""
from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from aspose_html.dom._document import Document


class BrowsingContext:
    """Internal owner of navigation lifecycle/document state.

    This is an internal-only abstraction used by ``Window`` to keep ownership
    responsibilities explicit without changing the public surface.
    """

    __slots__ = (
        "_current_document",
        "_lifecycle_state",
        "_cleanup_marks",
        "_navigation_epoch",
        "_active_navigation_token",
        "_dynamic_markup_intents",
    )

    def __init__(self, document: "Document") -> None:
        self._current_document: Document = document
        self._lifecycle_state: str = "idle"
        self._cleanup_marks: list[str] = []
        self._navigation_epoch: int = 0
        self._active_navigation_token: int | None = None
        self._dynamic_markup_intents: list[str] = []

    @property
    def current_document(self) -> "Document":
        return self._current_document

    @property
    def lifecycle_state(self) -> str:
        return self._lifecycle_state

    @property
    def cleanup_marks(self) -> list[str]:
        return self._cleanup_marks

    @property
    def navigation_epoch(self) -> int:
        return self._navigation_epoch

    @property
    def active_navigation_token(self) -> int | None:
        return self._active_navigation_token

    @property
    def dynamic_markup_intents(self) -> tuple[str, ...]:
        """Recorded Document dynamic-markup intents routed via lifecycle owner.

        Internal  guardrail: Document.open/write/writeln/close entrypoints
        must route through browsing-context ownership boundaries even when their
        public behavior remains a deterministic NotSupportedError stub.
        """
        return tuple(self._dynamic_markup_intents)

    def record_dynamic_markup_intent(self, operation: str) -> None:
        """Record dynamic-markup intent without mutating lifecycle ownership.

        This helper deliberately does not touch lifecycle state, document
        replacement, or parser scheduling. It only records that a document-level
        entrypoint crossed the ownership boundary.
        """
        self._dynamic_markup_intents.append(operation)

    def iframe_content_document_for(self, iframe_element: object) -> object | None:
        """Resolve an iframe embedded document through browsing-context ownership.

         guardrail contract: iframe embedded context ownership belongs to
        ``BrowsingContext`` (not to ``HTMLIFrameElement`` internals). Current
        headless behavior returns ``None`` deterministically.
        """
        _ = iframe_element
        return None

    def iframe_content_window_for(self, iframe_element: object) -> object | None:
        """Resolve an iframe embedded window through browsing-context ownership.

         guardrail contract: iframe embedded context ownership belongs to
        ``BrowsingContext`` (not to ``HTMLIFrameElement`` internals). Current
        headless behavior returns ``None`` deterministically.
        """
        _ = iframe_element
        return None

    def begin_navigation(self) -> bool:
        if self._lifecycle_state not in {"idle", "cancelled", "completed"}:
            return False
        self._navigation_epoch += 1
        self._active_navigation_token = self._navigation_epoch
        self._cleanup_marks = []
        self._lifecycle_state = "navigating"
        return True

    def accept_response(self) -> None:
        if self._lifecycle_state != "navigating":
            raise RuntimeError("navigation response can be accepted only from navigating")
        self._lifecycle_state = "replacing_document"
        self._cleanup_marks.append("replace_started")

    def attach_document(self, document: "Document") -> None:
        if self._lifecycle_state != "replacing_document":
            raise RuntimeError("document attach requires replacing_document state")
        self._current_document = document
        self._cleanup_marks.append("document_attached")

    def mark_parsing(self) -> None:
        if self._lifecycle_state != "replacing_document":
            raise RuntimeError("parsing can begin only after replacing_document")
        self._lifecycle_state = "parsing"
        self._cleanup_marks.append("parser_started")

    def mark_complete(self) -> None:
        if self._lifecycle_state != "parsing":
            raise RuntimeError("navigation completion requires parsing state")
        self._lifecycle_state = "completed"
        self._cleanup_marks.append("completed")
        self._active_navigation_token = None

    def complete_non_html(self) -> None:
        self._lifecycle_state = "completed"
        self._cleanup_marks.append("completed_non_html")
        self._active_navigation_token = None

    def cancel_navigation(self) -> bool:
        if self._lifecycle_state not in {"navigating", "replacing_document", "parsing"}:
            return False
        self._cleanup_marks.append("cancel_requested")
        self._lifecycle_state = "cancelled"
        self._lifecycle_state = "idle"
        self._active_navigation_token = None
        return True

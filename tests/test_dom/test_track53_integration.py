"""Track 53 integration hardening tests (BACK-235 / SPEC-108 / ADR-218)."""

from __future__ import annotations

from aspose_html.dom import Document, IntersectionObserver, ResizeObserver


class TestTrack53Integration:
    """Cross-surface observer/idle/animation behavior matrix."""

    def test_window_observer_idle_and_animation_surfaces_are_coherent(self) -> None:
        doc = Document()
        win = doc.default_view
        el = doc.create_element("div")
        doc.append_child(el)

        assert win.IntersectionObserver is IntersectionObserver
        assert win.ResizeObserver is ResizeObserver

        io_seen = []
        ro_seen = []
        io = win.IntersectionObserver(lambda entries, obs: io_seen.append((entries, obs)))
        ro = win.ResizeObserver(lambda entries, obs: ro_seen.append((entries, obs)))

        io.observe(el)
        io.unobserve(el)
        io.disconnect()
        ro.observe(el)
        ro.unobserve(el)
        ro.disconnect()

        assert io.take_records() == []
        assert ro.take_records() == []
        assert io_seen == []
        assert ro_seen == []

        idle_seen = []
        idle_id = win.request_idle_callback(lambda deadline=None: idle_seen.append(deadline))
        assert isinstance(idle_id, int)
        assert idle_seen == []

        win.cancel_idle_callback(idle_id)
        win.cancel_idle_callback(idle_id)
        win.cancel_idle_callback(999_999)

        assert el.get_animations() == []
        assert doc.get_animations() == []

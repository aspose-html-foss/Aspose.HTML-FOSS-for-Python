"""Track 56 integration matrix tests (BACK-241)."""

from __future__ import annotations

from aspose_html.dom import Document


class TestTrack56Integration:
    """Navigation lifecycle completion/cancellation integration matrix."""

    def test_completion_path_clears_preexisting_scheduled_work(self) -> None:
        win = Document().default_view
        calls: list[str] = []

        # Pre-existing timer work must be neutralized when replacement starts.
        win.set_timeout(lambda: calls.append("stale-timeout"), 0)
        win.set_interval(lambda: calls.append("stale-interval"), 0)
        win.request_idle_callback(lambda *_: calls.append("stale-idle"))

        seen: list[str] = []

        def scheduler(job):
            seen.append(f"schedule:{win.document.ready_state}")
            job()

        result_doc = win._navigation_process_response(
            response_kind="html",
            html_source="<html><body><p>ok</p></body></html>",
            scheduler_hook=scheduler,
        )

        assert result_doc is win.document
        assert win.document.ready_state == "complete"
        assert seen == ["schedule:loading"]
        assert calls == []
        assert win._dispatch_timer_macrotasks(20) == 0
        assert calls == []

    def test_cancellation_then_reentry_starts_clean_and_no_stale_callbacks_fire(self) -> None:
        win = Document().default_view
        calls: list[str] = []

        win.set_timeout(lambda: calls.append("stale-timeout"), 0)
        win.set_interval(lambda: calls.append("stale-interval"), 0)
        win.request_idle_callback(lambda *_: calls.append("stale-idle"))

        assert win._navigation_begin() is True
        win._navigation_cancel()

        # Cancellation boundary: queues are clean and no old callbacks run.
        assert win._navigation_lifecycle_state == "idle"
        assert win._dispatch_timer_macrotasks(20) == 0
        assert calls == []

        reentry_events: list[str] = []

        def scheduler(job):
            reentry_events.append("scheduler")
            job()

        win._navigation_process_response(
            response_kind="html",
            html_source="<html><body><p>reentry</p></body></html>",
            scheduler_hook=scheduler,
        )

        assert win.document.ready_state == "complete"
        assert reentry_events == ["scheduler"]
        assert calls == []

    def test_media_like_branch_completes_without_parser_hook_call(self) -> None:
        win = Document().default_view
        parser_called = False

        def parser_hook(_html: str, _doc: Document) -> None:
            nonlocal parser_called
            parser_called = True

        win._navigation_process_response(
            response_kind="image",
            parser_hook=parser_hook,
        )

        assert parser_called is False
        assert win.document.ready_state == "complete"
        assert "media_like_branch" in win._navigation_cleanup_marks
        assert win._navigation_cleanup_marks[-1] == "completed_non_html"

    def test_track54_timer_semantics_remain_stable_after_track56_navigation(self) -> None:
        win = Document().default_view
        calls: list[str] = []

        win._navigation_process_response(
            response_kind="html",
            html_source="<html><body></body></html>",
            scheduler_hook=lambda job: job(),
        )

        t1 = win.set_timeout(lambda: calls.append("t1"), 0)
        i1 = win.set_interval(lambda: calls.append("i1"), 0)
        t2 = win.set_timeout(lambda: calls.append("t2"), 0)
        assert t1 > 0 and i1 > 0 and t2 > 0

        assert win._dispatch_timer_macrotasks(3) == 3
        assert calls == ["t1", "i1", "t2"]

        win.clear_interval(i1)
        assert win._dispatch_timer_macrotasks(10) == 0

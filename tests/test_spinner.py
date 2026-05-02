from unittest.mock import MagicMock, patch, call

import pytest

import dot_tools.spinner as spinner_mod
from dot_tools.spinner import filter_spin_log, pause_live, ProgressLogger, spinner
from dot_tools.constants import Status


# ---------------------------------------------------------------------------
# filter_spin_log
# ---------------------------------------------------------------------------

class TestFilterSpinLog:

    def test_filter_spin_log__allows_records_without_spin_flag(self):
        record = {"extra": {}}
        assert filter_spin_log(record) is True

    def test_filter_spin_log__allows_records_with_spin_false(self):
        record = {"extra": {"spin": False}}
        assert filter_spin_log(record) is True

    def test_filter_spin_log__blocks_records_with_spin_true(self):
        record = {"extra": {"spin": True}}
        assert filter_spin_log(record) is False

    def test_filter_spin_log__allows_records_with_no_extra_key(self):
        assert filter_spin_log({}) is True


# ---------------------------------------------------------------------------
# ProgressLogger.handler
# ---------------------------------------------------------------------------

class TestProgressLoggerHandler:

    def _make_message(self, text: str, status: Status | None = None) -> MagicMock:
        msg = MagicMock()
        msg.strip.return_value = text
        msg.record = {"extra": {"status": status} if status else {}}
        return msg

    def test_handler__appends_plain_message_when_no_status(self):
        pl = ProgressLogger()
        pl.handler(self._make_message("hello"))
        assert any("hello" in m for m in pl.messages)

    def test_handler__appends_colored_symbol_when_status_present(self):
        pl = ProgressLogger()
        pl.handler(self._make_message("done", status=Status.CONFIRM))
        last = pl.messages[-1]
        symbol, color = Status.CONFIRM.value
        assert symbol in last
        assert color in last
        assert "done" in last

    def test_handler__respects_maxlen_of_ten(self):
        pl = ProgressLogger()
        for i in range(15):
            pl.handler(self._make_message(f"line {i}"))
        assert len(pl.messages) == 10

    def test_get_renderables__yields_messages_after_progress_renderables(self):
        pl = ProgressLogger()
        pl.handler(self._make_message("msg1"))
        pl.handler(self._make_message("msg2"))
        renderables = list(pl.get_renderables())
        texts = [r for r in renderables if isinstance(r, str)]
        assert any("msg1" in t for t in texts)
        assert any("msg2" in t for t in texts)


# ---------------------------------------------------------------------------
# pause_live
# ---------------------------------------------------------------------------

class TestPauseLive:

    def test_pause_live__stops_and_restarts_active_live(self):
        mock_live = MagicMock()
        spinner_mod.active_live = mock_live
        try:
            with pause_live():
                mock_live.stop.assert_called_once()
            mock_live.start.assert_called_once()
        finally:
            spinner_mod.active_live = None

    def test_pause_live__is_no_op_when_no_active_live(self):
        spinner_mod.active_live = None
        # Should not raise
        with pause_live():
            pass

    def test_pause_live__restarts_live_even_if_body_raises(self):
        mock_live = MagicMock()
        spinner_mod.active_live = mock_live
        try:
            with pytest.raises(RuntimeError):
                with pause_live():
                    raise RuntimeError("boom")
            mock_live.start.assert_called_once()
        finally:
            spinner_mod.active_live = None


# ---------------------------------------------------------------------------
# spinner context manager
# ---------------------------------------------------------------------------

class TestSpinner:

    def _patch_spinner_deps(self):
        """Patch only the Rich Live display to avoid terminal rendering."""
        return patch("dot_tools.spinner.Live")

    def test_spinner__yields_and_completes_without_error(self):
        with self._patch_spinner_deps():
            with spinner("doing a thing"):
                pass  # no exception — should complete normally

    def test_spinner__reraises_exception_from_body(self):
        with self._patch_spinner_deps():
            with pytest.raises(ValueError, match="exploded"):
                with spinner("doing a thing"):
                    raise ValueError("exploded")

    def test_spinner__nested_spinners_use_branch_stack(self):
        with self._patch_spinner_deps():
            with spinner("outer"):
                assert len(spinner_mod.branch_stack) > 0
                with spinner("inner"):
                    assert len(spinner_mod.branch_stack) > 1
                assert len(spinner_mod.branch_stack) == 1
            assert len(spinner_mod.branch_stack) == 0

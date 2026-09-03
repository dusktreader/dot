from unittest.mock import MagicMock, patch

import pytest
from loguru import logger
from rich.text import Text

import dot_tools.spinner as spinner_mod
from dot_tools.spinner import filter_spin_log, pause_live, print_output, ProgressLogger, spinner
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

    def test_handler__keeps_installer_output_out_of_messages_but_logs_it(self):
        progress = ProgressLogger()
        live = MagicMock()
        logged_messages: list[str] = []
        progress_handler_id = logger.add(progress.handler, format="{message}")
        sink_id = logger.add(
            lambda message: logged_messages.append(message.record["message"]),
            format="{message}",
        )
        chunk = "installer [red]chunk[/red]\npartial"

        spinner_mod.progress_logger_stack.append(progress)
        spinner_mod.active_live = live
        try:
            print_output(chunk)
            logger.bind(installer_output=True).debug(chunk)
        finally:
            spinner_mod.progress_logger_stack.clear()
            spinner_mod.active_live = None
            logger.remove(sink_id)
            logger.remove(progress_handler_id)

        assert list(progress.messages) == []
        rendered_output = [renderable.plain for renderable in progress.get_renderables() if isinstance(renderable, Text)]
        assert rendered_output.count("installer [red]chunk[/red]") == 1
        assert rendered_output.count("partial") == 1
        assert logged_messages == [chunk]

    def test_get_renderables__yields_messages_after_progress_renderables(self):
        pl = ProgressLogger()
        pl.handler(self._make_message("msg1"))
        pl.handler(self._make_message("msg2"))
        renderables = list(pl.get_renderables())
        texts = [r for r in renderables if isinstance(r, str)]
        assert any("msg1" in t for t in texts)
        assert any("msg2" in t for t in texts)

    def test_add_output__retains_only_latest_twenty_complete_lines(self):
        pl = ProgressLogger()

        for i in range(25):
            pl.add_output(f"line {i}\n")

        assert list(pl.output_lines) == [f"line {i}" for i in range(5, 25)]

    def test_add_output__keeps_partial_output_visible_and_combines_later_chunks(self):
        pl = ProgressLogger()
        pl.add_output("prompt> ")

        assert pl.partial_output == "prompt> "
        assert any(str(renderable) == "prompt> " for renderable in pl.get_renderables())

        pl.add_output("continue\nnext")

        assert list(pl.output_lines) == ["prompt> continue"]
        assert pl.partial_output == "next"

    def test_get_renderables__renders_installer_markup_as_literal_text(self):
        pl = ProgressLogger()
        pl.add_output("[red]not markup[/red]\n")

        output = list(pl.get_renderables())[-1]

        assert isinstance(output, Text)
        assert output.plain == "[red]not markup[/red]"


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
# print_output
# ---------------------------------------------------------------------------

class TestPrintOutput:

    def test_print_output__flushes_partial_output_without_live_display(self, capsys):
        print_output("prompt> ")

        assert capsys.readouterr().out == "prompt> "

    def test_print_output__uses_active_live_console_without_markup_parsing(self):
        mock_live = MagicMock()
        spinner_mod.active_live = mock_live
        try:
            print_output("[not markup]")
        finally:
            spinner_mod.active_live = None

        mock_live.console.print.assert_called_once()
        printed_text = mock_live.console.print.call_args.args[0]
        assert str(printed_text) == "[not markup]"
        assert mock_live.console.print.call_args.kwargs["end"] == ""

    def test_print_output__routes_chunks_to_active_progress_and_refreshes_live(self):
        progress = ProgressLogger()
        mock_live = MagicMock()
        spinner_mod.progress_logger_stack.append(progress)
        spinner_mod.active_live = mock_live
        try:
            print_output("prompt> ")
        finally:
            spinner_mod.progress_logger_stack.clear()
            spinner_mod.active_live = None

        assert progress.partial_output == "prompt> "
        mock_live.refresh.assert_called_once()
        mock_live.console.print.assert_not_called()

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
                    print_output("nested output\n")
                    assert list(spinner_mod.progress_logger_stack[-1].output_lines) == ["nested output"]
                assert len(spinner_mod.branch_stack) == 1
                assert len(spinner_mod.progress_logger_stack) == 1
            assert len(spinner_mod.branch_stack) == 0

    def test_spinner__keeps_active_live_display_while_streaming_output(self):
        with self._patch_spinner_deps() as live_class:
            with spinner("outer"):
                live = spinner_mod.active_live
                assert live is live_class.return_value
                print_output("installer output")
                assert spinner_mod.active_live is live
                assert spinner_mod.progress_logger_stack

from collections import defaultdict
from dataclasses import dataclass
from datetime import date, datetime, timezone
from typing import Any, Iterable, cast

import plotille

from dot_tools.opencode_costs import SessionRecord, model_matches_provider


NO_DATA_MESSAGE = "No recorded OpenCode usage found for the selected period."
OTHER_LABEL = "other"
DEFAULT_MAX_MODELS = 6
MODEL_COLORS = (
    (230, 25, 75),
    (60, 180, 75),
    (0, 130, 200),
    (145, 30, 180),
    (0, 128, 128),
    (255, 225, 25),
    (245, 130, 48),
    (240, 50, 230),
    (70, 240, 240),
    (210, 245, 60),
    (170, 110, 40),
    (0, 0, 128),
    (128, 0, 0),
)
OTHER_COLOR = (128, 128, 128)
CHARS_PER_DATE = 12
BAR_COLUMNS_PER_DATE = 3
DATE_LABEL_WIDTH = 10
PLOT_Y_AXIS_PREFIX = 13


@dataclass(frozen=True)
class TrendSeries:
    """Store daily recorded costs grouped into chart series."""

    dates: tuple[date, ...]
    values: dict[str, tuple[float, ...]]
    colors: dict[str, tuple[int, int, int]]
    provider: str | None = None

    @property
    def series_names(self) -> tuple[str, ...]:
        """Return series names in their stacked and legend order."""
        return tuple(self.values)


def _session_date(session: SessionRecord) -> date:
    """Convert a session timestamp into the report's UTC calendar date."""
    return datetime.fromtimestamp(session.time_created / 1000, tz=timezone.utc).date()


def aggregate_daily_model_costs(
    sessions: Iterable[SessionRecord],
    since: date | None = None,
    max_models: int = DEFAULT_MAX_MODELS,
    provider: str | None = None,
) -> TrendSeries:
    """Aggregate recorded session costs by UTC date and model."""
    if max_models < 0:
        raise ValueError("max_models must be non-negative")
    daily: dict[date, dict[str, float]] = defaultdict(lambda: defaultdict(float))
    totals: dict[str, float] = defaultdict(float)
    available_models: set[str] = set()

    for session in sessions:
        if provider is not None and not model_matches_provider(session.model, provider):
            continue
        session_date = _session_date(session)
        if since is not None and session_date < since:
            continue
        if session.cost is None:
            continue

        model = session.model or OTHER_LABEL
        daily[session_date][model] += session.cost
        totals[model] += session.cost
        available_models.add(model)

    dates = tuple(sorted(daily))
    named_models = sorted(
        (model for model in available_models if model != OTHER_LABEL),
        key=lambda model: (-totals[model], model),
    )
    top_models = named_models[:max_models]
    other_needed = OTHER_LABEL in available_models or len(named_models) > len(top_models)
    series_names = top_models + ([OTHER_LABEL] if other_needed else [])
    colors = {model: MODEL_COLORS[index % len(MODEL_COLORS)] for index, model in enumerate(top_models)}
    if other_needed:
        colors[OTHER_LABEL] = OTHER_COLOR

    values: dict[str, tuple[float, ...]] = {}
    for model in series_names:
        values[model] = tuple(
            sum(
                value
                for name, value in daily[day].items()
                if name == model or (model == OTHER_LABEL and name not in top_models)
            )
            for day in dates
        )
    return TrendSeries(dates, values, colors, provider)


def render_trends(series: TrendSeries) -> str:
    """Render a recorded-cost trend as colored stacked terminal bars."""
    if not series.dates:
        return NO_DATA_MESSAGE

    x_values = list(range(len(series.dates)))
    totals = [sum(series.values[name][index] for name in series.series_names) for index in range(len(series.dates))]
    maximum = max(totals, default=0.0)

    figure = plotille.Figure()
    figure.color_mode = "rgb"
    figure.width = 80
    figure.height = 20
    figure.width = max(figure.width, (len(series.dates) + 1) * CHARS_PER_DATE)
    figure.y_label = "USD"
    figure.set_y_limits(0, max(1.0, maximum * 1.1))
    # Give each populated date a stable, sequential x coordinate. The limits make one
    # date occupy twelve terminal columns in plotille's character-cell coordinate system.
    figure.set_x_limits(-1, -1 + figure.width / CHARS_PER_DATE)
    figure.with_x_axis = False
    figure.origin = False

    def format_currency(value: float, chars: int, delta: float, left: bool = False) -> str:
        """Format y-axis values as dollar amounts."""
        label = f"${value:.2f}"
        return label.ljust(chars) if left else label.rjust(chars)

    figure.register_label_formatter(float, cast(Any, format_currency))

    for model_index, model in enumerate(series.series_names):
        color = series.colors[model]
        values = series.values[model]
        plot_x: list[float] = []
        plot_y: list[float] = []
        for index, value in enumerate(values):
            bottom = sum(series.values[name][index] for name in series.series_names[:model_index])
            top = bottom + value
            if top == bottom:
                continue
            samples = max(2, figure.height * 4)
            y_values = [bottom + (top - bottom) * offset / (samples - 1) for offset in range(samples)]
            date_x = x_values[index]
            # Plot three adjacent marker columns for each date. The shared slot geometry
            # keeps these markers and the custom date axis tied to the same coordinates.
            slot_offsets = tuple(
                (offset - BAR_COLUMNS_PER_DATE // 2) / CHARS_PER_DATE
                for offset in range(BAR_COLUMNS_PER_DATE)
            )
            plot_x.extend([date_x + offset for offset in slot_offsets for _ in range(samples)])
            plot_y.extend(y_values * BAR_COLUMNS_PER_DATE)
        if plot_x:
            figure.plot(plot_x, plot_y, lc=color, interp=None, label=model, marker="█")

    legend = ["Legend:", "-------"]
    legend.extend(
        plotille.color(
            f"⠤█⠤ {model} (${sum(series.values[model]):.2f})",
            fg=series.colors[model],
            mode=figure.color_mode,
        )
        for model in series.series_names
    )
    total = sum(value for model in series.series_names for value in series.values[model])
    legend.append("-------")
    legend.append(f"Total recorded cost: ${total:.2f}")
    rendered = figure.show()
    rendered_lines = rendered.splitlines()
    axis_line = _render_date_axis(series.dates, figure.width)
    rendered_lines.extend(axis_line.splitlines())
    rendered = "\n".join(rendered_lines)
    return (
        f"OpenCode recorded cost trends ($) [provider: {series.provider or 'all'}]\n\n"
        + rendered
        + "\n\n"
        + "\n".join(legend)
    )


def _render_date_axis(dates: tuple[date, ...], width: int) -> str:
    """Render date labels at the explicit plotille columns used for their bars."""
    bar_columns = _bar_columns(len(dates), width)
    label_width = max(width + PLOT_Y_AXIS_PREFIX, *(column + DATE_LABEL_WIDTH for column in bar_columns))
    labels = [" "] * label_width
    for value, column in zip(dates, bar_columns, strict=True):
        text = value.isoformat()
        label_start = column - DATE_LABEL_WIDTH // 2
        labels[label_start : label_start + len(text)] = text
    labels_text = "".join(labels).rstrip()
    ruler = " " * PLOT_Y_AXIS_PREFIX + "|" + "-" * max(0, label_width - PLOT_Y_AXIS_PREFIX - 1) + "-> (Date)"
    return f"{ruler}\n{labels_text}"


def _bar_columns(number_of_dates: int, width: int) -> tuple[int, ...]:
    """Return terminal columns for plotille's sequential date coordinates."""
    if number_of_dates == 0:
        return ()
    return tuple(PLOT_Y_AXIS_PREFIX + (index + 1) * CHARS_PER_DATE for index in range(number_of_dates))

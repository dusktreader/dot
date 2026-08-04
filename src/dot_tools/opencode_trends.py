from collections import defaultdict
from dataclasses import dataclass
from datetime import date, datetime, timezone
from typing import Any, Iterable, cast

import plotille

from dot_tools.opencode_costs import SessionRecord


NO_DATA_MESSAGE = "No recorded OpenCode usage found for the selected period."
OTHER_LABEL = "other"
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


@dataclass(frozen=True)
class TrendSeries:
    """Store daily recorded costs grouped into chart series."""

    dates: tuple[date, ...]
    values: dict[str, tuple[float, ...]]
    colors: dict[str, tuple[int, int, int]]

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
    max_models: int = 3,
) -> TrendSeries:
    """Aggregate recorded session costs by UTC date and model."""
    if max_models < 0:
        raise ValueError("max_models must be non-negative")
    daily: dict[date, dict[str, float]] = defaultdict(lambda: defaultdict(float))
    totals: dict[str, float] = defaultdict(float)
    available_models: set[str] = set()

    for session in sessions:
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
    other_needed = len(named_models) > len(top_models)
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
    return TrendSeries(dates, values, colors)


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
    columns_per_date = 11
    figure.width = max(figure.width, (len(series.dates) + 1) * columns_per_date)
    figure.x_label = "Date"
    figure.y_label = "USD"
    figure.set_y_limits(0, max(1.0, maximum * 1.1))
    # Plotille places x-axis ticks every ten columns. Use a separate label line so the
    # ten-character ISO labels can have a separating column without changing the bars.
    figure.set_x_limits(-1, -1 + figure.width / columns_per_date)

    def format_empty_tick(_value: float, _next_value: float) -> str:
        """Suppress plotille's fixed-width x-axis tick labels."""
        return ""

    def format_currency(value: float, chars: int, delta: float, left: bool = False) -> str:
        """Format y-axis values as dollar amounts."""
        label = f"${value:.2f}"
        return label.ljust(chars) if left else label.rjust(chars)

    figure.register_label_formatter(float, cast(Any, format_currency))
    figure.x_ticks_fkt = cast(Any, format_empty_tick)

    for model_index, model in enumerate(series.series_names):
        color = series.colors[model]
        values = series.values[model]
        plot_x: list[int] = []
        plot_y: list[float] = []
        for index, value in enumerate(values):
            bottom = sum(series.values[name][index] for name in series.series_names[:model_index])
            top = bottom + value
            if top == bottom:
                continue
            samples = max(2, figure.height * 4)
            y_values = [bottom + (top - bottom) * offset / (samples - 1) for offset in range(samples)]
            plot_x.extend([x_values[index]] * samples)
            plot_y.extend(y_values)
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
    rendered = figure.show()
    rendered_lines = rendered.splitlines()
    axis_line = rendered_lines[-1]
    nonzero_date_indices = [index for index, total in enumerate(totals) if total > 0]
    baseline_line = next((line for line in rendered_lines if "$0.00 |" in line), "")
    baseline_bar_positions = [index for index, character in enumerate(baseline_line) if character == "█"]
    if baseline_bar_positions:
        first_bar_start = baseline_bar_positions[0] - nonzero_date_indices[0] * columns_per_date
    else:
        # A zero-cost series has no plotted points, so use a temporary baseline plot to
        # obtain plotille's x geometry without displaying fabricated bars in the result.
        geometry_figure = plotille.Figure()
        geometry_figure.color_mode = figure.color_mode
        geometry_figure.width = figure.width
        geometry_figure.height = figure.height
        geometry_figure.y_label = "USD"
        geometry_figure.set_y_limits(0, max(1.0, maximum * 1.1))
        geometry_figure.set_x_limits(-1, -1 + figure.width / columns_per_date)
        geometry_figure.register_label_formatter(float, cast(Any, format_currency))
        geometry_figure.x_ticks_fkt = cast(Any, format_empty_tick)
        geometry_figure.plot(x_values, [0.0] * len(x_values), interp=None, marker="█")
        geometry_baseline = next(line for line in geometry_figure.show().splitlines() if "$0.00 |" in line)
        first_bar_start = geometry_baseline.index("█")
    label_line = list(axis_line.ljust(first_bar_start + len(series.dates) * columns_per_date))
    for index, value in enumerate(series.dates):
        label_start = first_bar_start + index * columns_per_date
        label_line[label_start : label_start + len(value.isoformat())] = value.isoformat()
    axis_line = "".join(label_line)
    rendered_lines[-1] = axis_line
    rendered = "\n".join(rendered_lines)
    return "OpenCode recorded cost trends ($)\n\n" + rendered + "\n\n" + "\n".join(legend)

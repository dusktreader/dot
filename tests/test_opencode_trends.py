from datetime import date, datetime, timezone
from typing import Any

from dot_tools.opencode_costs import SessionRecord
from dot_tools.opencode_trends import NO_DATA_MESSAGE, aggregate_daily_model_costs, render_trends


def record(**overrides: Any) -> SessionRecord:
    values = dict(
        session_id="one",
        parent_id=None,
        directory="/project",
        agent="executor",
        model="gpt-5.6-luna",
        time_created=1760000000000,
        cost=2.0,
        tokens={"input": 100, "output": 50, "reasoning": 10, "cache_read": 20, "cache_write": 5},
        metadata=None,
        root_id="one",
        ancestry_status="ok",
    )
    values.update(overrides)
    return SessionRecord(**values)


def test_aggregate_daily_model_costs_filters_and_groups_models() -> None:
    result = aggregate_daily_model_costs(
        [
            record(session_id="old", time_created=1759913600000, cost=10.0),
            record(session_id="same-day", time_created=1760001000000, cost=3.0),
            record(session_id="other", time_created=1760086400000, model="gpt-5.6-sol", cost=4.0),
            record(session_id="missing", time_created=1760086400000, model=None, cost=1.0),
            record(session_id="unknown-cost", time_created=1760086400000, cost=None),
        ],
        since=date(2025, 10, 9),
    )

    assert result.dates == (date(2025, 10, 9), date(2025, 10, 10))
    assert result.series_names == ("gpt-5.6-sol", "gpt-5.6-luna", "other")
    assert result.values["gpt-5.6-luna"] == (3.0, 0.0)
    assert result.values["gpt-5.6-sol"] == (0.0, 4.0)
    assert result.values["other"] == (0.0, 1.0)


def test_aggregate_daily_model_costs_filters_provider_and_personal_directory() -> None:
    result = aggregate_daily_model_costs(
        [
            record(model="github-copilot/gpt-5.6-luna", directory="/personal/repo", cost=2.0),
            record(session_id="other-provider", model="openai/gpt-5.6-luna", cost=3.0),
            record(session_id="unqualified", model="gpt-5.6-luna", cost=100.0),
        ],
        provider="github-copilot",
    )
    assert result.values["github-copilot/gpt-5.6-luna"] == (2.0,)
    assert result.provider == "github-copilot"
    assert "provider: github-copilot" in render_trends(result)


def test_default_max_models_includes_six_named_models_and_groups_the_seventh() -> None:
    sessions = [record(session_id=model, model=model, cost=8 - index) for index, model in enumerate(
        ("alpha", "bravo", "charlie", "delta", "echo", "foxtrot", "golf")
    )]

    result = aggregate_daily_model_costs(sessions)

    assert result.series_names == ("alpha", "bravo", "charlie", "delta", "echo", "foxtrot", "other")
    assert result.values["other"] == (2.0,)


def test_max_models_controls_other_grouping() -> None:
    result = aggregate_daily_model_costs(
        [
            record(model="alpha", cost=4.0),
            record(session_id="b", model="bravo", cost=3.0),
            record(session_id="c", model="charlie", cost=2.0),
        ],
        max_models=2,
    )

    assert result.series_names == ("alpha", "bravo", "other")
    assert result.values["other"] == (2.0,)


def test_max_models_zero_groups_all_named_models() -> None:
    result = aggregate_daily_model_costs([record(model="alpha", cost=1.0)], max_models=0)

    assert result.series_names == ("other",)
    assert result.values["other"] == (1.0,)


def test_max_models_larger_than_color_palette_does_not_fail() -> None:
    models = [f"model-{index}" for index in range(10)]
    result = aggregate_daily_model_costs(
        [record(session_id=model, model=model, cost=1.0) for model in models],
        max_models=10,
    )

    assert result.series_names == tuple(models)
    assert len(result.colors) == len(models)
    assert len(set(result.colors.values())) == len(models)


def test_max_models_at_least_named_model_count_omits_empty_other() -> None:
    result = aggregate_daily_model_costs(
        [record(model="alpha", cost=1.0), record(session_id="b", model="bravo", cost=1.0)],
        max_models=3,
    )

    assert result.series_names == ("alpha", "bravo")
    assert "other" not in result.colors


def test_top_three_model_colors_are_stable() -> None:
    result = aggregate_daily_model_costs(
        [
            record(model="alpha", cost=3.0),
            record(session_id="b", model="bravo", cost=2.0),
            record(session_id="c", model="charlie", cost=1.0),
            record(session_id="d", model="delta", cost=1.0),
        ]
    )

    assert len(set(result.colors.values())) == 4


def test_render_trends_handles_empty_and_single_day() -> None:
    empty = aggregate_daily_model_costs([])
    assert render_trends(empty) == NO_DATA_MESSAGE
    assert "Total recorded cost" not in render_trends(empty)

    rendered = render_trends(aggregate_daily_model_costs([record()]))
    assert "OpenCode recorded cost trends ($)" in rendered
    assert "[provider: all]" in rendered
    assert "Legend:" in rendered
    assert "gpt-5.6-luna" in rendered
    assert "Date" in rendered
    assert "$" in rendered
    assert "Label " not in rendered
    assert "Total recorded cost: $2.00" in rendered
    rendered_lines = rendered.splitlines()
    total_index = rendered_lines.index("Total recorded cost: $2.00")
    assert rendered_lines[total_index - 1] == "-------"


def test_render_trends_total_uses_all_selected_model_values() -> None:
    series = aggregate_daily_model_costs(
        [
            record(model="alpha", cost=1.25),
            record(session_id="alpha-two", model="alpha", time_created=1760086400000, cost=2.75),
            record(session_id="bravo", model="bravo", cost=3.0),
        ],
        since=date(2025, 10, 9),
        max_models=2,
    )

    rendered = render_trends(series)

    assert "Total recorded cost: $7.00" in rendered


def test_render_trends_total_uses_provider_filtered_values() -> None:
    series = aggregate_daily_model_costs(
        [
            record(model="github-copilot/gpt-5.6-luna", cost=2.0),
            record(session_id="other-provider", model="openai/gpt-5.6-luna", cost=3.0),
        ],
        provider="github-copilot",
    )

    rendered = render_trends(series)

    assert "Total recorded cost: $2.00" in rendered
    assert "Total recorded cost: $3.00" not in rendered


def test_render_trends_total_includes_grouped_other() -> None:
    series = aggregate_daily_model_costs(
        [
            record(model="alpha", cost=4.0),
            record(session_id="bravo", model="bravo", cost=3.0),
            record(session_id="charlie", model="charlie", cost=2.0),
        ],
        max_models=2,
    )

    rendered = render_trends(series)

    assert "other ($2.00)" in rendered
    assert "Total recorded cost: $9.00" in rendered


def test_render_trends_includes_only_unmodeled_sessions_in_other() -> None:
    rendered = render_trends(
        aggregate_daily_model_costs(
            [record(model=None, cost=2.50), record(session_id="two", model=None, cost=1.25)]
        )
    )

    assert "other ($3.75)" in rendered
    rendered_lines = rendered.splitlines()
    total_index = rendered_lines.index("Total recorded cost: $3.75")
    assert rendered_lines[total_index - 1] == "-------"
    assert rendered_lines[total_index - 2] != "-------"


def test_render_trends_omits_plotille_origin_lines_without_hiding_bars() -> None:
    rendered = render_trends(aggregate_daily_model_costs([record(cost=3.0)]))

    assert "⣀" not in rendered
    assert "⡇" not in rendered
    assert "███" in rendered
    assert "2025-10-09" in rendered
    assert "-> (Date)" in rendered


def test_render_trends_uses_hyphenated_labels_aligned_with_each_bar() -> None:
    series = aggregate_daily_model_costs(
        [
            record(session_id="day-one", time_created=1760001000000, cost=1.0),
            record(session_id="day-two", time_created=1760086400000, cost=10.0),
        ],
        since=date(2025, 10, 9),
    )

    rendered = render_trends(series)

    assert rendered.count("2025-10-09") == 1
    assert rendered.count("2025-10-10") == 1
    assert "20251009" not in rendered

    axis = next(line for line in rendered.splitlines() if "2025-10-09" in line)
    baseline = next(line for line in rendered.splitlines() if "$0.00 |" in line)
    first_bar = baseline.index("█")
    second_bar = baseline.index("█", first_bar + 3)
    assert axis.index("2025-10-09") + 4 == first_bar
    assert axis.index("2025-10-10") + 4 == second_bar
    assert "2025-10-092025-10-10" not in axis
    assert axis.index("2025-10-10") - axis.index("2025-10-09") == 12
    assert axis[axis.index("2025-10-09") + 10 : axis.index("2025-10-10")] == "  "
    assert baseline[first_bar : first_bar + 3] == "███"


def test_render_trends_omits_missing_dates_and_places_sparse_dates_adjacent() -> None:
    series = aggregate_daily_model_costs(
        [
            record(session_id="first", time_created=1760001000000),
            record(session_id="last", time_created=1760262400000),
        ],
        since=date(2025, 10, 9),
    )

    rendered = render_trends(series)
    axis = next(line for line in rendered.splitlines() if "2025-10-09" in line)
    bars = next(line for line in rendered.splitlines() if "█" in line)

    assert rendered.count("2025-10-09") == 1
    assert rendered.count("2025-10-12") == 1
    assert "2025-10-10" not in rendered
    assert "2025-10-11" not in rendered
    first_bar = bars.index("█")
    second_bar = bars.index("█", first_bar + 3)
    assert axis.index("2025-10-09") + 4 == first_bar
    assert axis.index("2025-10-12") + 4 == second_bar
    assert "2025-10-092025-10-12" not in axis
    assert axis.index("2025-10-12") - axis.index("2025-10-09") == 12


def test_render_trends_sizes_axis_for_many_populated_dates() -> None:
    series = aggregate_daily_model_costs(
        [record(session_id=f"day-{index}", time_created=1760001000000 + index * 86_400_000) for index in range(10)],
        since=date(2025, 10, 9),
    )

    rendered = render_trends(series)
    axis = next(line for line in rendered.splitlines() if "2025-10-09" in line)
    bars = next(line for line in rendered.splitlines() if "█" in line)

    assert len(axis) > 100
    assert axis.index("2025-10-18") - axis.index("2025-10-09") == 9 * 12
    assert axis.index("2025-10-18") + 6 == bars.rindex("█")


def test_render_trends_keeps_zero_cost_dates_and_labels() -> None:
    series = aggregate_daily_model_costs(
        [
            record(session_id="zero-one", time_created=1760001000000, cost=0.0),
            record(session_id="zero-two", time_created=1760086400000, cost=0.0),
        ],
        since=date(2025, 10, 9),
    )

    rendered = render_trends(series)

    assert series.dates == (date(2025, 10, 9), date(2025, 10, 10))
    assert rendered.count("2025-10-09") == 1
    assert rendered.count("2025-10-10") == 1
    axis = next(line for line in rendered.splitlines() if "2025-10-09" in line)
    assert axis.index("2025-10-10") - axis.index("2025-10-09") == 12


def test_render_trends_keeps_zero_cost_dates_in_explicit_bar_geometry() -> None:
    series = aggregate_daily_model_costs(
        [
            record(session_id="leading-zero", time_created=1760001000000, cost=0.0),
            record(session_id="populated", time_created=1760086400000, cost=4.0),
            record(session_id="trailing-zero", time_created=1760172800000, cost=0.0),
        ],
        since=date(2025, 10, 9),
    )

    rendered = render_trends(series)
    axis = next(line for line in rendered.splitlines() if "2025-10-09" in line)
    bars = next(line for line in rendered.splitlines() if "$0.00 |" in line)

    assert axis.index("2025-10-09") == 20
    assert axis.index("2025-10-10") == 32
    assert axis.index("2025-10-11") == 44
    assert bars.index("█") == axis.index("2025-10-10") + 4
    assert bars[bars.index("█") : bars.index("█") + 3] == "███"


def test_render_trends_aligns_unequal_stacked_bars_with_many_models() -> None:
    sessions = [
        record(session_id="short", model="short", cost=1.0),
        record(session_id="tall-a", model="tall-a", time_created=1760086400000, cost=8.0),
        record(session_id="tall-b", model="tall-b", time_created=1760086400000, cost=2.0),
    ]

    series = aggregate_daily_model_costs(sessions, max_models=10)
    rendered = render_trends(series)
    axis = next(line for line in rendered.splitlines() if "2025-10-09" in line)
    baseline = next(line for line in rendered.splitlines() if "$0.00 |" in line)
    bar_columns = [index for index, character in enumerate(baseline) if character == "█"]

    assert axis.index("2025-10-09") == bar_columns[0] - 4
    second_bar = next(column for column in bar_columns if column >= bar_columns[0] + 12)
    assert axis.index("2025-10-10") == second_bar - 4
    assert second_bar - bar_columns[0] == 12
    assert baseline[bar_columns[0] : bar_columns[0] + 3] == "███"


def test_render_trends_aligns_a_single_day_label_with_its_bar() -> None:
    rendered = render_trends(aggregate_daily_model_costs([record(cost=3.0)]))

    axis = next(line for line in rendered.splitlines() if "2025-10-09" in line)
    bars = next(line for line in rendered.splitlines() if "$0.00 |" in line)
    assert axis.index("2025-10-09") + 4 == bars.index("█")


def test_render_trends_uses_utc_dates_across_dst_boundary() -> None:
    sessions = [
        record(
            session_id="before-dst-transition",
            time_created=int(datetime(2025, 11, 1, 23, tzinfo=timezone.utc).timestamp() * 1000),
        ),
        record(
            session_id="after-dst-transition",
            time_created=int(datetime(2025, 11, 3, 1, tzinfo=timezone.utc).timestamp() * 1000),
        ),
    ]

    series = aggregate_daily_model_costs(sessions)

    assert series.dates == (date(2025, 11, 1), date(2025, 11, 3))
    rendered = render_trends(series)
    assert rendered.count("2025-11-01") == 1
    assert rendered.count("2025-11-03") == 1


def test_render_trends_includes_selected_totals_for_models_and_other() -> None:
    series = aggregate_daily_model_costs(
        [
            record(session_id="outside-range", time_created=1759913600000, model="alpha", cost=100.0),
            record(session_id="alpha-one", model="alpha", cost=1.25),
            record(session_id="alpha-two", time_created=1760086400000, model="alpha", cost=2.75),
            record(session_id="bravo", model="bravo", cost=3.0),
            record(session_id="charlie", model="charlie", cost=2.0),
            record(session_id="delta", model="delta", cost=1.0),
        ],
        since=date(2025, 10, 9),
        max_models=2,
    )

    rendered = render_trends(series)

    assert "alpha ($4.00)" in rendered
    assert "bravo ($3.00)" in rendered
    assert "other ($3.00)" in rendered
    assert "alpha ($104.00)" not in rendered

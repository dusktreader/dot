from datetime import date
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
    assert result.series_names == ("gpt-5.6-sol", "gpt-5.6-luna")
    assert result.values["gpt-5.6-luna"] == (3.0, 0.0)
    assert result.values["gpt-5.6-sol"] == (0.0, 4.0)


def test_top_three_models_use_spend_and_alphabetical_tie_break() -> None:
    sessions = [
        record(session_id="a", model="alpha", cost=3.0),
        record(session_id="b", model="bravo", cost=2.0),
        record(session_id="c", model="charlie", cost=1.0),
        record(session_id="d", model="delta", cost=1.0),
    ]

    result = aggregate_daily_model_costs(sessions)

    assert result.series_names == ("alpha", "bravo", "charlie", "other")


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

    rendered = render_trends(aggregate_daily_model_costs([record()]))
    assert "OpenCode recorded cost trends ($)" in rendered
    assert "Legend:" in rendered
    assert "gpt-5.6-luna" in rendered
    assert "Date" in rendered
    assert "$" in rendered
    assert "Label " not in rendered

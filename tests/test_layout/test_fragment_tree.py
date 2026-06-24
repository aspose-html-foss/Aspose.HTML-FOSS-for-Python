from __future__ import annotations

import pickle
from dataclasses import FrozenInstanceError

import pytest

from aspose_html.layout import (
    BlockFragment,
    EdgeSizes,
    FragmentRoot,
    InlineTextFragment,
    LineFragment,
    PageFragment,
    PageMarginBoxes,
    ShapedRun,
)


def test_fragment_records_are_frozen() -> None:
    frag = BlockFragment(
        source_node=None,
        children=(),
        x=0.0,
        y=0.0,
        width=100.0,
        height=20.0,
        margin=EdgeSizes(),
        padding=EdgeSizes(),
        border=EdgeSizes(),
        line_fragments=(),
        is_anonymous=False,
    )
    with pytest.raises(FrozenInstanceError):
        frag.width = 50.0  # type: ignore[misc]


def test_fragment_records_are_picklable() -> None:
    root = FragmentRoot(
        children=(
            BlockFragment(
                source_node=None,
                children=(),
                x=1.0,
                y=2.0,
                width=300.0,
                height=40.0,
                margin=EdgeSizes(),
                padding=EdgeSizes(),
                border=EdgeSizes(),
                line_fragments=(
                    LineFragment(
                        runs=(
                            InlineTextFragment(
                                run=ShapedRun(text="x", advance=1.0, ascent=0.0, descent=0.0),
                                x=0.0,
                                y=0.0,
                                width=1.0,
                                height=0.0,
                                baseline=0.0,
                            ),
                        ),
                        x=0.0,
                        y=0.0,
                        width=1.0,
                        height=0.0,
                        baseline=0.0,
                    ),
                ),
                is_anonymous=True,
            ),
        )
    )
    payload = pickle.dumps(root)
    loaded = pickle.loads(payload)
    assert loaded == root


def test_page_fragment_records_are_picklable() -> None:
    page = PageFragment(
        page_index=0,
        x=0.0,
        y=0.0,
        width=800.0,
        height=1000.0,
        children=(),
        margin_boxes=PageMarginBoxes(),
    )
    payload = pickle.dumps(page)
    loaded = pickle.loads(payload)
    assert loaded == page

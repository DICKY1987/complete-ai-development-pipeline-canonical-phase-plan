from __future__ import annotations

import os
import importlib

from src.pipeline import orchestrator
from src.pipeline import bundles


def test_lifecycle_comments_are_emitted(monkeypatch):
    # Enable sync and stub out the poster to capture events
    monkeypatch.setenv('ENABLE_GH_SYNC', 'true')

    events = []

    def fake_post(issue, ev):  # noqa: ARG001
        events.append((ev.step, ev.final_status))
        return True

    gh = importlib.import_module('src.integrations.github_sync')
    monkeypatch.setattr(gh, 'post_lifecycle_comment', fake_post)

    # Pick a known workstream id
    items = bundles.load_and_validate_bundles()
    ws_id = next(b.id for b in items if getattr(b, 'ccpm_issue', None) is not None)

    result = orchestrator.run_single_workstream_from_bundle(ws_id, context={"dry_run": True})
    assert result['final_status'] == 'done'
    # Expect start and end events
    assert ('workstream_start', None) in events
    assert ('workstream_end', 'done') in events


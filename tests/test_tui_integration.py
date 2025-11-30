"""Lightweight integration test for the TUI entrypoint."""

from gui.tui_app.config.layout_config import LogConfig, PanelRefreshConfig, ThemeConfig, TUIConfig
from gui.tui_app.main import PipelineTUI


def test_pipeline_tui_headless_smoke(tmp_path):
    """Ensure the TUI boots and exits cleanly in smoke-test mode."""
    log_file = tmp_path / "integration.log"
    log_file.write_text("test log line\n")

    config = TUIConfig(
        theme=ThemeConfig(),
        panels=PanelRefreshConfig(
            dashboard=0.1,
            pattern_activity=0.1,
            file_lifecycle=0.1,
            tool_health=0.1,
            log_stream=0.1,
        ),
        logs=LogConfig(path=log_file, max_lines=10),
    )

    app = PipelineTUI(smoke_test=True, use_mock_data=True, config=config)
    app.run(headless=True)

# DOC_LINK: DOC-TEST-TERMINAL-TEST-STATE-CAPTURE-315
from core.terminal import TerminalContext, capture_state


def test_capture_state_tails_and_sanitizes_env(monkeypatch):
    monkeypatch.setenv("VISIBLE_VAR", "ok")
    monkeypatch.setenv("SECRET_KEY", "hidden")

    stdout = "\n".join([f"line {i}" for i in range(120)])
    stderr = "error1\nerror2"

    state = capture_state(stdout=stdout, stderr=stderr, exit_code=1, tail_lines=5)

    assert state.exit_code == 1
    assert state.stdout_tail == [f"line {i}" for i in range(115, 120)]
    assert state.stderr_tail == ["error1", "error2"]
    assert "VISIBLE_VAR" in state.env
    assert "SECRET_KEY" not in state.env


def test_terminal_context_captures_output():
    with TerminalContext():
        print("hello stdout")
        import sys

        print("oops", file=sys.stderr)

    captured = TerminalContext.last_state
    assert captured is not None
    assert "hello stdout" in captured.stdout_tail
    assert "oops" in captured.stderr_tail

# DOC_LINK: DOC-SCRIPT-RUN-TUI-BACKGROUND-069
# Starts the AI Pipeline TUI in a minimized console window (background-friendly).

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$root = Resolve-Path "$scriptDir/.."
Set-Location $root

$python = "python"

$args = @("-m", "tui_app.main", "--layout", "dual", "--secondary-panel", "log_stream")

# Launch minimized
Start-Process -FilePath $python -ArgumentList $args -WindowStyle Minimized

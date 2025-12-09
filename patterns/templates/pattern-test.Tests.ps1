# Tests for {PATTERN_NAME}
Describe "{PATTERN_NAME}" {
    It "Executor exists" {
        Test-Path "$PSScriptRoot\..\executors\{PATTERN_NAME}_executor.ps1" | Should -Be $true
    }
}

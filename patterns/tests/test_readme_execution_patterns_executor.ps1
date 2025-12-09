# Test: PAT-EXEC-readme_execution_patterns-1021 Executor
# DOC_ID: DOC-PAT-EXEC-readme_execution_patterns-1021
# Generated: 2025-12-08

Describe "Readme Execution Patterns Executor Tests" {
    BeforeAll {
        $ExecutorPath = Join-Path $PSScriptRoot "..\executors\readme_execution_patterns_executor.ps1"
        $PatternID = "PAT-EXEC-readme_execution_patterns-1021"
        $DocID = "DOC-PAT-EXEC-readme_execution_patterns-1021"
    }

    Context "File Validation" {
        It "Executor file exists" {
            Test-Path $ExecutorPath | Should -Be $true
        }

        It "Executor is a valid PowerShell script" {
            { Get-Command $ExecutorPath -ErrorAction Stop } | Should -Not -Throw
        }

        It "Executor has valid syntax" {
            $errors = $null
            $content = Get-Content $ExecutorPath -Raw
            $null = [System.Management.Automation.PSParser]::Tokenize($content, [ref]$errors)
            $errors.Count | Should -Be 0
        }
    }

    Context "Pattern Execution" {
        It "Executes with required context parameter" {
            $result = & $ExecutorPath -Context "test_context"
            $result | Should -Not -BeNullOrEmpty
        }

        It "Returns success status" {
            $result = & $ExecutorPath -Context "test_execution"
            $result.status | Should -Be "success"
        }

        It "Returns correct pattern_id" {
            $result = & $ExecutorPath -Context "test_validation"
            $result.pattern_id | Should -Be $PatternID
        }

        It "Returns correct doc_id" {
            $result = & $ExecutorPath -Context "test_doc_id"
            $result.doc_id | Should -Be $DocID
        }

        It "Throws error when context is missing" {
            { & $ExecutorPath } | Should -Throw
        }
    }

    Context "Output Validation" {
        It "Returns all required fields" {
            $result = & $ExecutorPath -Context "test_fields"
            $result.Keys | Should -Contain "pattern_id"
            $result.Keys | Should -Contain "doc_id"
            $result.Keys | Should -Contain "status"
            $result.Keys | Should -Contain "context"
            $result.Keys | Should -Contain "timestamp"
        }

        It "Timestamp is in ISO 8601 format" {
            $result = & $ExecutorPath -Context "test_timestamp"
            { [datetime]::Parse($result.timestamp) } | Should -Not -Throw
        }

        It "Accepts optional parameters" {
            $params = @{ key1 = "value1"; key2 = "value2" }
            $result = & $ExecutorPath -Context "test_params" -Parameters $params
            $result.status | Should -Be "success"
        }

        It "Accepts optional inputs" {
            $inputs = @{ input1 = "data1"; input2 = "data2" }
            $result = & $ExecutorPath -Context "test_inputs" -Inputs $inputs
            $result.status | Should -Be "success"
        }
    }
}

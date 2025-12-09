# Test: EXEC-001 Executor
# DOC_ID: DOC-PAT-EXEC-001-890
# Generated: 2025-12-09

Describe "Type Safe Operations Executor Tests" {
    BeforeAll {
        $ExecutorPath = Join-Path $PSScriptRoot "..\executors\type_safe_operations_executor.ps1"
        $PatternID = "EXEC-001"
        $DocID = "DOC-PAT-EXEC-001-890"
    }

    Context "File Validation" {
        It "Executor file exists" {
            Test-Path $ExecutorPath | Should -Be $true
        }

        It "Executor has valid PowerShell syntax" {
            $errors = $null
            $content = Get-Content $ExecutorPath -Raw
            $null = [System.Management.Automation.PSParser]::Tokenize($content, [ref]$errors)
            $errors.Count | Should -Be 0
        }
    }

    Context "Validation Mode" {
        It "Executes in validate-only mode" {
            $operation = @{
                type = "test"
                target = "test_target"
            }

            $result = & $ExecutorPath -Context "test_validation" -Operation $operation -ValidateOnly
            $result | Should -Not -BeNullOrEmpty
            $result.status | Should -BeIn @("success", "skipped")
        }

        It "Returns validation results" {
            $operation = @{
                type = "test"
                target = "test_target"
            }

            $result = & $ExecutorPath -Context "test_validation" -Operation $operation -ValidateOnly
            $result.validation | Should -Not -BeNullOrEmpty
            $result.validation.passed | Should -BeOfType [bool]
        }
    }

    Context "Execution Mode" {
        It "Executes with valid operation" {
            $operation = @{
                type = "test"
                target = "test_target"
            }

            $result = & $ExecutorPath -Context "test_execution" -Operation $operation
            $result | Should -Not -BeNullOrEmpty
        }

        It "Returns correct pattern_id" {
            $operation = @{
                type = "test"
                target = "test_target"
            }

            $result = & $ExecutorPath -Context "test_pattern_id" -Operation $operation
            $result.pattern_id | Should -Be $PatternID
        }

        It "Returns success status for valid operation" {
            $operation = @{
                type = "test"
                target = "test_target"
            }

            $result = & $ExecutorPath -Context "test_success" -Operation $operation
            $result.status | Should -Be "success"
        }

        It "Throws error when context is missing" {
            $operation = @{
                type = "test"
                target = "test_target"
            }

            { & $ExecutorPath -Operation $operation } | Should -Throw
        }

        It "Throws error when operation is missing" {
            { & $ExecutorPath -Context "test" } | Should -Throw
        }
    }

    Context "Output Validation" {
        It "Returns all required fields" {
            $operation = @{
                type = "test"
                target = "test_target"
            }

            $result = & $ExecutorPath -Context "test_fields" -Operation $operation
            $result.Keys | Should -Contain "pattern_id"
            $result.Keys | Should -Contain "status"
            $result.Keys | Should -Contain "context"
            $result.Keys | Should -Contain "timestamp"
        }

        It "Timestamp is in ISO 8601 format" {
            $operation = @{
                type = "test"
                target = "test_target"
            }

            $result = & $ExecutorPath -Context "test_timestamp" -Operation $operation
            { [datetime]::Parse($result.timestamp) } | Should -Not -Throw
        }

        It "Includes validation results" {
            $operation = @{
                type = "test"
                target = "test_target"
            }

            $result = & $ExecutorPath -Context "test_validation_results" -Operation $operation
            $result.validation | Should -Not -BeNullOrEmpty
        }
    }
}

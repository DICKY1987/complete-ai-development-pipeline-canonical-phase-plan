# DOC_LINK: DOC-PAT-PREFLIGHT-VERIFY-INSTANCE-TEST-002
# Comprehensive tests for preflight_verify pattern executor

Describe "preflight_verify pattern executor" {

    BeforeAll {
        $ExecutorPath = "$PSScriptRoot\..\executors\preflight_verify_executor.ps1"
        $ExamplePath = "$PSScriptRoot\..\examples\preflight_verify\instance_minimal.json"
        $SchemaPath = "$PSScriptRoot\..\schemas\preflight_verify.schema.json"

        $TestRoot = "$TestDrive\preflight_verify_tests"
        New-Item -ItemType Directory -Path $TestRoot -Force | Out-Null
    }

    Context "Executor Validation" {
        It "Executor file should exist" {
            Test-Path $ExecutorPath | Should -Be $true
        }

        It "Example instance should exist" {
            Test-Path $ExamplePath | Should -Be $true
        }

        It "Schema file should exist" {
            Test-Path $SchemaPath | Should -Be $true
        }

        It "Executor should have DOC_LINK header" {
            $content = Get-Content $ExecutorPath -Raw
            $content | Should -Match "# DOC_LINK: DOC-PAT-PREFLIGHT-VERIFY-INSTANCE-TEST-002"
        }

        It "Should accept InstancePath parameter" {
            $params = (Get-Command $ExecutorPath).Parameters
            $params.Keys -contains 'InstancePath' | Should -Be $true
        }
    }

    Context "Instance Validation" {
        It "Should validate instance doc_id" {
            $testInstance = @{
                doc_id = "INVALID"
                pattern_id = "PAT-PREFLIGHT-VERIFY-001"
                inputs = @{ checks = @() }
            } | ConvertTo-Json

            $testPath = "$TestDrive\test_invalid.json"
            Set-Content $testPath $testInstance

            { & $ExecutorPath -InstancePath $testPath } | Should -Throw
        }

        It "Should validate instance pattern_id" {
            $testInstance = @{
                doc_id = "DOC-PAT-PREFLIGHT-VERIFY-INSTANCE-TEST-002"
                pattern_id = "INVALID"
                inputs = @{ checks = @() }
            } | ConvertTo-Json

            $testPath = "$TestDrive\test_invalid_pattern.json"
            Set-Content $testPath $testInstance

            { & $ExecutorPath -InstancePath $testPath } | Should -Throw
        }
    }

    Context "Core Functionality" {
        It "Should pass all checks when commands succeed" {
            $testInstance = @{
                doc_id = "DOC-PAT-PREFLIGHT-VERIFY-INSTANCE-TEST-002"
                pattern_id = "PAT-PREFLIGHT-VERIFY-001"
                inputs = @{
                    checks = @(
                        @{ name = "check1"; command = "exit 0" },
                        @{ name = "check2"; command = "exit 0" }
                    )
                    fail_fast = $false
                }
            } | ConvertTo-Json -Depth 10

            $testPath = "$TestDrive\test_success.json"
            Set-Content $testPath $testInstance

            $result = & $ExecutorPath -InstancePath $testPath | ConvertFrom-Json

            $result.success | Should -Be $true
            $result.data.checks_passed | Should -Be 2
            $result.data.checks_failed | Should -Be 0
            $result.data.can_proceed | Should -Be $true
        }

        It "Should fail when any check fails" {
            $testInstance = @{
                doc_id = "DOC-PAT-PREFLIGHT-VERIFY-INSTANCE-TEST-002"
                pattern_id = "PAT-PREFLIGHT-VERIFY-001"
                inputs = @{
                    checks = @(
                        @{ name = "check1"; command = "exit 0" },
                        @{ name = "check2"; command = "exit 1" }
                    )
                    fail_fast = $false
                }
            } | ConvertTo-Json -Depth 10

            $testPath = "$TestDrive\test_fail.json"
            Set-Content $testPath $testInstance

            $result = & $ExecutorPath -InstancePath $testPath | ConvertFrom-Json

            $result.success | Should -Be $false
            $result.data.checks_failed | Should -BeGreaterThan 0
            $result.data.can_proceed | Should -Be $false
        }

        It "Should support fail-fast mode" {
            $testInstance = @{
                doc_id = "DOC-PAT-PREFLIGHT-VERIFY-INSTANCE-TEST-002"
                pattern_id = "PAT-PREFLIGHT-VERIFY-001"
                inputs = @{
                    checks = @(
                        @{ name = "check1"; command = "exit 1" },
                        @{ name = "check2"; command = "exit 0" }
                    )
                    fail_fast = $true
                }
            } | ConvertTo-Json -Depth 10

            $testPath = "$TestDrive\test_failfast.json"
            Set-Content $testPath $testInstance

            $result = & $ExecutorPath -InstancePath $testPath | ConvertFrom-Json

            $result.success | Should -Be $false
            # Should not run second check
            $result.data.results.Count | Should -Be 1
        }
    }

    Context "Edge Cases" {
        It "Should handle empty checks array" {
            $testInstance = @{
                doc_id = "DOC-PAT-PREFLIGHT-VERIFY-INSTANCE-TEST-002"
                pattern_id = "PAT-PREFLIGHT-VERIFY-001"
                inputs = @{
                    checks = @()
                    fail_fast = $false
                }
            } | ConvertTo-Json -Depth 10

            $testPath = "$TestDrive\test_empty.json"
            Set-Content $testPath $testInstance

            $result = & $ExecutorPath -InstancePath $testPath | ConvertFrom-Json

            $result.success | Should -Be $true
            $result.data.checks_passed | Should -Be 0
        }
    }

    Context "Integration Tests" {
        It "Should execute with minimal example" {
            $result = & $ExecutorPath -InstancePath $ExamplePath | ConvertFrom-Json
            $result | Should -Not -BeNullOrEmpty
            $result.success | Should -BeIn @($true, $false)
        }
    }

    Context "Performance Tests" {
        It "Should complete within reasonable time" {
            $testInstance = @{
                doc_id = "DOC-PAT-PREFLIGHT-VERIFY-INSTANCE-TEST-002"
                pattern_id = "PAT-PREFLIGHT-VERIFY-001"
                inputs = @{
                    checks = @(
                        @{ name = "perf_check"; command = "exit 0" }
                    )
                }
            } | ConvertTo-Json -Depth 10

            $testPath = "$TestDrive\test_perf.json"
            Set-Content $testPath $testInstance

            $elapsed = Measure-Command {
                & $ExecutorPath -InstancePath $testPath | Out-Null
            }

            $elapsed.TotalSeconds | Should -BeLessThan 5
        }
    }

    AfterAll {
        if (Test-Path $TestRoot) {
            Remove-Item $TestRoot -Recurse -Force -ErrorAction SilentlyContinue
        }
    }
}

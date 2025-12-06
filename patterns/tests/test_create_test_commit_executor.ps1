# DOC_LINK: DOC-PAT-CREATE-TEST-COMMIT-INSTANCE-TEST-003
# Comprehensive tests for create_test_commit pattern executor

Describe "create_test_commit pattern executor" {

    BeforeAll {
        $ExecutorPath = "$PSScriptRoot\..\executors\create_test_commit_executor.ps1"
        $ExamplePath = "$PSScriptRoot\..\examples\create_test_commit\instance_minimal.json"

        $TestRoot = "$TestDrive\create_test_commit_tests"
        New-Item -ItemType Directory -Path $TestRoot -Force | Out-Null
    }

    Context "Executor Validation" {
        It "Executor file should exist" {
            Test-Path $ExecutorPath | Should -Be $true
        }

        It "Should have DOC_LINK header" {
            $content = Get-Content $ExecutorPath -Raw
            $content | Should -Match "# DOC_LINK: DOC-PAT-CREATE-TEST-COMMIT-INSTANCE-TEST-003"
        }
    }

    Context "Core Functionality" {
        It "Should create file when tests pass" {
            $testFile = Join-Path $TestRoot "success.txt"
            $testInstance = @{
                doc_id = "DOC-PAT-CREATE-TEST-COMMIT-INSTANCE-TEST-003"
                pattern_id = "PAT-CREATE-TEST-COMMIT-001"
                inputs = @{
                    file_path = $testFile
                    file_content = "Test content"
                    test_command = "exit 0"
                    commit_message = "test: add file"
                }
            } | ConvertTo-Json -Depth 10

            $instancePath = "$TestDrive\test_success.json"
            Set-Content $instancePath $testInstance

            $result = & $ExecutorPath -InstancePath $instancePath | ConvertFrom-Json

            $result.success | Should -Be $true
            Test-Path $testFile | Should -Be $true
        }

        It "Should rollback file when tests fail" {
            $testFile = Join-Path $TestRoot "fail.txt"
            $testInstance = @{
                doc_id = "DOC-PAT-CREATE-TEST-COMMIT-INSTANCE-TEST-003"
                pattern_id = "PAT-CREATE-TEST-COMMIT-001"
                inputs = @{
                    file_path = $testFile
                    file_content = "Test content"
                    test_command = "exit 1"
                    commit_message = "test: should fail"
                }
            } | ConvertTo-Json -Depth 10

            $instancePath = "$TestDrive\test_fail.json"
            Set-Content $instancePath $testInstance

            $result = & $ExecutorPath -InstancePath $instancePath | ConvertFrom-Json

            $result.success | Should -Be $false
            Test-Path $testFile | Should -Be $false
        }

        It "Should handle nested directory creation" {
            $testFile = Join-Path $TestRoot "deep\nested\test.txt"
            $testInstance = @{
                doc_id = "DOC-PAT-CREATE-TEST-COMMIT-INSTANCE-TEST-003"
                pattern_id = "PAT-CREATE-TEST-COMMIT-001"
                inputs = @{
                    file_path = $testFile
                    file_content = "Nested content"
                    test_command = "exit 0"
                    commit_message = "test: nested"
                }
            } | ConvertTo-Json -Depth 10

            $instancePath = "$TestDrive\test_nested.json"
            Set-Content $instancePath $testInstance

            $result = & $ExecutorPath -InstancePath $instancePath | ConvertFrom-Json

            $result.success | Should -Be $true
            Test-Path $testFile | Should -Be $true
        }
    }

    AfterAll {
        if (Test-Path $TestRoot) {
            Remove-Item $TestRoot -Recurse -Force -ErrorAction SilentlyContinue
        }
    }
}

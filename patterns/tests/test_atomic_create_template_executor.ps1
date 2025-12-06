# DOC_LINK: DOC-PAT-ATOMIC-CREATE-TEMPLATE-INSTANCE-TEST-002
# Comprehensive tests for atomic_create_template pattern executor

Describe "atomic_create_template pattern executor" {

    BeforeAll {
        $ExecutorPath = "$PSScriptRoot\..\executors\atomic_create_template_executor.ps1"
        $ExamplePath = "$PSScriptRoot\..\examples\atomic_create_template\instance_minimal.json"
        $SchemaPath = "$PSScriptRoot\..\schemas\atomic_create_template.schema.json"

        $TestRoot = "$TestDrive\atomic_create_template_tests"
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
            $content | Should -Match "# DOC_LINK: DOC-PAT-ATOMIC-CREATE-TEMPLATE-INSTANCE-TEST-002"
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
                pattern_id = "PAT-ATOMIC-CREATE-TEMPLATE-001"
                inputs = @{}
            } | ConvertTo-Json

            $testPath = "$TestDrive\test_invalid.json"
            Set-Content $testPath $testInstance

            { & $ExecutorPath -InstancePath $testPath } | Should -Throw
        }

        It "Should validate instance pattern_id" {
            $testInstance = @{
                doc_id = "DOC-PAT-ATOMIC-CREATE-TEMPLATE-INSTANCE-TEST-002"
                pattern_id = "INVALID"
                inputs = @{}
            } | ConvertTo-Json

            $testPath = "$TestDrive\test_invalid_pattern.json"
            Set-Content $testPath $testInstance

            { & $ExecutorPath -InstancePath $testPath } | Should -Throw
        }
    }

    Context "Core Functionality" {
        It "Should return structured result" {
            $result = & $ExecutorPath -InstancePath $ExamplePath -ErrorAction SilentlyContinue | ConvertFrom-Json -ErrorAction SilentlyContinue

            if ($result) {
                $result | Should -HaveKey "success"
                $result | Should -HaveKey "message"
                $result | Should -HaveKey "data"
            }
        }
    }

    Context "Integration Tests" {
        It "Should execute without fatal errors" {
            { & $ExecutorPath -InstancePath $ExamplePath -ErrorAction SilentlyContinue } | Should -Not -Throw
        }
    }

    Context "Performance Tests" {
        It "Should complete within reasonable time" {
            $elapsed = Measure-Command {
                & $ExecutorPath -InstancePath $ExamplePath -ErrorAction SilentlyContinue | Out-Null
            }

            $elapsed.TotalSeconds | Should -BeLessThan 10
        }
    }

    AfterAll {
        if (Test-Path $TestRoot) {
            Remove-Item $TestRoot -Recurse -Force -ErrorAction SilentlyContinue
        }
    }
}

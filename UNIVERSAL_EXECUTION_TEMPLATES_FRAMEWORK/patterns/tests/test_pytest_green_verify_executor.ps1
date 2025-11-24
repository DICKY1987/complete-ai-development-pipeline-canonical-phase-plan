# DOC_LINK: DOC-PAT-PYTEST-GREEN-VERIFY-002
# Comprehensive tests for pytest_green_verify pattern executor

Describe "pytest_green_verify pattern executor" {
    
    BeforeAll {
        $ExecutorPath = "$PSScriptRoot\..\executors\pytest_green_verify_executor.ps1"
        $ExamplePath = "$PSScriptRoot\..\examples\pytest_green_verify\instance_minimal.json"
        $SchemaPath = "$PSScriptRoot\..\schemas\pytest_green_verify.schema.json"
        
        $TestRoot = "$TestDrive\pytest_green_verify_tests"
        New-Item -ItemType Directory -Path $TestRoot -Force | Out-Null
    }
    
    Context "Executor Validation" {
        It "Executor file should exist" {
            Test-Path $ExecutorPath | Should -Be $true
        }
        
        It "Example instance should exist" {
            Test-Path $ExamplePath | Should -Be $true
        }
        
        It "Should have DOC_LINK header" {
            $content = Get-Content $ExecutorPath -Raw
            $content | Should -Match "# DOC_LINK: DOC-PAT-PYTEST-GREEN-VERIFY-002"
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
                pattern_id = "PAT-PYTEST-GREEN-VERIFY-002"
                inputs = @{ test_path = "tests/" }
            } | ConvertTo-Json
            
            $testPath = "$TestDrive\test_invalid.json"
            Set-Content $testPath $testInstance
            
            { & $ExecutorPath -InstancePath $testPath } | Should -Throw
        }
    }
    
    Context "Core Functionality" {
        It "Should return result structure" {
            $testInstance = @{
                doc_id = "DOC-PAT-PYTEST-GREEN-VERIFY-002"
                pattern_id = "PAT-PYTEST-GREEN-VERIFY-002"
                inputs = @{
                    test_path = "$TestRoot"
                    pytest_args = @("-v")
                }
            } | ConvertTo-Json -Depth 10
            
            $testPath = "$TestDrive\test_struct.json"
            Set-Content $testPath $testInstance
            
            $result = & $ExecutorPath -InstancePath $testPath | ConvertFrom-Json
            
            $result | Should -HaveKey "success"
            $result | Should -HaveKey "message"
            $result | Should -HaveKey "data"
        }
    }
    
    Context "Integration Tests" {
        It "Should execute with minimal example" {
            $result = & $ExecutorPath -InstancePath $ExamplePath | ConvertFrom-Json
            $result | Should -Not -BeNullOrEmpty
        }
    }
    
    AfterAll {
        if (Test-Path $TestRoot) {
            Remove-Item $TestRoot -Recurse -Force -ErrorAction SilentlyContinue
        }
    }
}

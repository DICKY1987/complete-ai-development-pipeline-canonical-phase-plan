# DOC_LINK: DOC-TEST-TEST-MODULE-CREATION-EXECUTOR-020
# DOC_LINK: DOC-MODULE-CREATION-001
# Tests for module_creation pattern executor

Describe "module_creation pattern executor" {
    
    BeforeAll {
        $ExecutorPath = "$PSScriptRoot\..\executors\module_creation_executor.ps1"
        $ExamplePath = "$PSScriptRoot\..\examples\module_creation\instance_minimal.json"
    }
    
    It "Executor file should exist" {
        Test-Path $ExecutorPath | Should -Be $true
    }
    
    It "Example instance should exist" {
        Test-Path $ExamplePath | Should -Be $true
    }
    
    It "Should accept InstancePath parameter" {
        $params = (Get-Command $ExecutorPath).Parameters
        $params.Keys -contains 'InstancePath' | Should -Be $true
    }
    
    It "Should validate instance schema" {
        # TODO: Add schema validation test
        $true | Should -Be $true
    }
}

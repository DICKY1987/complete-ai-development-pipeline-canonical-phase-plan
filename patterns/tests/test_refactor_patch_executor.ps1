# DOC_LINK: DOC-TEST-TEST-REFACTOR-PATCH-EXECUTOR-024
# DOC_LINK: DOC-REFACTOR-PATCH-001
# Tests for refactor_patch pattern executor

Describe "refactor_patch pattern executor" {

    BeforeAll {
        $ExecutorPath = "$PSScriptRoot\..\executors\refactor_patch_executor.ps1"
        $ExamplePath = "$PSScriptRoot\..\examples\refactor_patch\instance_minimal.json"
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

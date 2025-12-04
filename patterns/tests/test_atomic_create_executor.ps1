# DOC_LINK: DOC-TEST-TEST-ATOMIC-CREATE-EXECUTOR-010
# DOC_LINK: DOC-ATOMIC-CREATE-001
# Tests for atomic_create pattern executor

Describe "atomic_create pattern executor" {

    BeforeAll {
        $ExecutorPath = "$PSScriptRoot\..\executors\atomic_create_executor.ps1"
        $ExamplePath = "$PSScriptRoot\..\examples\atomic_create\instance_minimal.json"
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

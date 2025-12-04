# DOC_LINK: DOC-TEST-TEST-SELF-HEAL-EXECUTOR-026
# DOC_LINK: DOC-SELF-HEAL-001
# Tests for self_heal pattern executor

Describe "self_heal pattern executor" {

    BeforeAll {
        $ExecutorPath = "$PSScriptRoot\..\executors\self_heal_executor.ps1"
        $ExamplePath = "$PSScriptRoot\..\examples\self_heal\instance_minimal.json"
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

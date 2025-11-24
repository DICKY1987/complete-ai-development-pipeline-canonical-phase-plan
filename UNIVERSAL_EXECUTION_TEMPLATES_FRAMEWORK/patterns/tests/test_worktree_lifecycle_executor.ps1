# DOC_LINK: DOC-WORKTREE-LIFECYCLE-001
# Tests for worktree_lifecycle pattern executor

Describe "worktree_lifecycle pattern executor" {
    
    BeforeAll {
        $ExecutorPath = "$PSScriptRoot\..\executors\worktree_lifecycle_executor.ps1"
        $ExamplePath = "$PSScriptRoot\..\examples\worktree_lifecycle\instance_minimal.json"
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

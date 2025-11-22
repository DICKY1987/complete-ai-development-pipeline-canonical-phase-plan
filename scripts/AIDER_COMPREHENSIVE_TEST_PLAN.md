# Aider Comprehensive Test Plan

**Objective**: Definitively prove that aider + Ollama + DeepSeek-R1 is fully functional and can generate responses and modify code.

**Critical Context**: Aider has never worked fully in this environment. This test plan addresses every potential failure point.

---

## Test Strategy: 6-Layer Verification

Each layer must pass before proceeding to the next. This ensures we isolate exactly where any failure occurs.

### Layer 1: Foundation - Prerequisites Check
**Purpose**: Verify all required components are installed and accessible

**Tests**:
1. ✓ Ollama service is running
2. ✓ DeepSeek-R1 model is available
3. ✓ Aider executable exists and is in PATH
4. ✓ Git is available (aider requires git)
5. ✓ Python environment is accessible

**Success Criteria**: All 5 checks pass
**Failure Action**: Install missing components before proceeding

---

### Layer 2: Connectivity - Network Communication
**Purpose**: Verify Ollama API is responding and models are accessible

**Tests**:
1. ✓ Ollama API responds to health check (`/api/tags`)
2. ✓ DeepSeek-R1 model appears in available models list
3. ✓ Can send test generation request directly to Ollama API
4. ✓ Ollama returns valid JSON response

**Success Criteria**: Direct API communication works
**Failure Action**: Check Ollama service status, firewall, port conflicts

---

### Layer 3: Environment - Configuration Validation
**Purpose**: Verify environment variables and config files are correct

**Tests**:
1. ✓ `PYTHONIOENCODING=utf-8` is set
2. ✓ `PYTHONUTF8=1` is set
3. ✓ `OLLAMA_API_BASE=http://127.0.0.1:11434` is set
4. ✓ `AIDER_MODEL=ollama_chat/deepseek-r1:latest` is set
5. ✓ Config file `~/.aider.conf.yml` exists and specifies correct model
6. ✓ No conflicting environment variables

**Success Criteria**: All environment variables are correctly set
**Failure Action**: Source setup script or fix configuration

---

### Layer 4: Aider Startup - Basic Functionality
**Purpose**: Verify aider can start without crashing

**Tests**:
1. ✓ `aider --version` runs without error
2. ✓ `aider --help` displays help without Unicode encoding crash
3. ✓ Can display Unicode characters (│ ├ └) without error
4. ✓ Aider can initialize in a test directory

**Success Criteria**: Aider starts and displays output without crashing
**Failure Action**: Check encoding settings, try different terminal

---

### Layer 5: Response Generation - Model Communication
**Purpose**: Verify aider can communicate with DeepSeek-R1 and receive responses

**Tests**:
1. ✓ Aider can connect to Ollama backend
2. ✓ Aider sends prompt to model
3. ✓ Model generates response (any response)
4. ✓ Aider receives and displays response without crash
5. ✓ Response contains actual content (not timeout/error)

**Success Criteria**: Aider gets and displays model-generated text
**Failure Action**: Check model name format, timeout settings, API connectivity

---

### Layer 6: Code Modification - Full Workflow
**Purpose**: Verify aider can actually modify code as requested

**Tests**:
1. ✓ Create test Python file with simple function
2. ✓ Request specific modification via `--message` flag
3. ✓ Aider generates modification plan
4. ✓ Aider applies changes to file
5. ✓ Verify file contents changed correctly
6. ✓ Changes match the requested modification
7. ✓ Multiple sequential edits work

**Success Criteria**: Aider successfully modifies code as requested
**Failure Action**: Review model capabilities, prompt format, file permissions

---

## Test Implementation

### Automated Test Script: `test-aider-comprehensive.ps1`

Creates a complete test suite that:
- Runs all 6 layers sequentially
- Stops at first failure with diagnostic output
- Captures full logs for debugging
- Provides clear PASS/FAIL status for each layer
- Generates detailed report

### Test Artifacts Generated

1. **Test workspace**: Temporary directory with git repo
2. **Test files**: Python file with deliberate issues to fix
3. **Log files**: Complete output from each test layer
4. **Report**: Summary of all test results

---

## Success Metrics

### Minimum Viable Success
- Layers 1-5 pass: Aider can start and communicate
- Layer 6 basic test passes: Aider can modify one file

### Full Success
- All 6 layers pass completely
- Multiple sequential edits work
- Different file types can be edited
- Works across multiple terminal sessions

### Production Ready
- Full success + stress tests pass
- No encoding errors after 10+ edits
- Works with large files (>1000 lines)
- Handles multiple files in single session

---

## Diagnostic Checklist

If any layer fails, check:

**Layer 1 Failures**:
- [ ] Is Ollama actually running? (`ollama ps`)
- [ ] Is deepseek-r1 pulled? (`ollama list`)
- [ ] Is aider installed? (`pip list | grep aider`)

**Layer 2 Failures**:
- [ ] Can you curl Ollama? (`curl http://127.0.0.1:11434/api/tags`)
- [ ] Is port 11434 blocked?
- [ ] Is Ollama serving on different port?

**Layer 3 Failures**:
- [ ] Run `set-aider-env.ps1` to fix environment
- [ ] Check `$env:AIDER_MODEL` matches config file
- [ ] Check for typos in model name

**Layer 4 Failures**:
- [ ] Are you in PowerShell (not Git Bash)?
- [ ] Is `PYTHONIOENCODING=utf-8` actually set?
- [ ] Try `$env:PYTHONIOENCODING` to verify

**Layer 5 Failures**:
- [ ] Check model name format: `ollama_chat/` prefix required
- [ ] Try direct Ollama generation: `ollama run deepseek-r1 "hello"`
- [ ] Check timeout settings in config

**Layer 6 Failures**:
- [ ] Is file writable?
- [ ] Is git repo initialized?
- [ ] Check aider's verbose output for errors

---

## Expected Output

### Successful Run Example

```
=== AIDER COMPREHENSIVE TEST ===

Layer 1: Foundation Checks
  ✓ Ollama is running
  ✓ deepseek-r1:latest is available
  ✓ Aider executable found at C:\Users\richg\.local\bin\aider
  ✓ Git is available (version 2.x.x)
  ✓ Python is accessible (version 3.x.x)
LAYER 1: PASSED

Layer 2: Connectivity Tests
  ✓ Ollama API responds at http://127.0.0.1:11434
  ✓ deepseek-r1 found in model list
  ✓ Test generation request successful
  ✓ Received valid JSON response
LAYER 2: PASSED

Layer 3: Environment Validation
  ✓ PYTHONIOENCODING=utf-8
  ✓ PYTHONUTF8=1
  ✓ OLLAMA_API_BASE=http://127.0.0.1:11434
  ✓ AIDER_MODEL=ollama_chat/deepseek-r1:latest
  ✓ Config file exists: C:\Users\richg\.aider.conf.yml
  ✓ No conflicting variables detected
LAYER 3: PASSED

Layer 4: Aider Startup Tests
  ✓ aider --version: 0.86.1
  ✓ aider --help displayed without errors
  ✓ Unicode test: │├└ rendered correctly
  ✓ Initialized in test directory
LAYER 4: PASSED

Layer 5: Response Generation Tests
  ✓ Connected to Ollama backend
  ✓ Sent test prompt to model
  ✓ Received response from deepseek-r1
  ✓ Response displayed without crash
  ✓ Response contains actual content (127 chars)
LAYER 5: PASSED

Layer 6: Code Modification Tests
  ✓ Created test file: test_math.py
  ✓ Requested change: "Add docstring to add function"
  ✓ Aider generated modification
  ✓ Applied changes to file
  ✓ Verified: docstring present in function
  ✓ Requested change: "Add type hints"
  ✓ Sequential edit successful
LAYER 6: PASSED

=== ALL TESTS PASSED ===

Aider is FULLY FUNCTIONAL and ready for production use.
```

---

## Test Execution Commands

### Quick Test (Layers 1-5 only)
```powershell
.\scripts\test-aider-comprehensive.ps1 -Quick
```

### Full Test (All 6 layers)
```powershell
.\scripts\test-aider-comprehensive.ps1
```

### Verbose Test (With detailed logging)
```powershell
.\scripts\test-aider-comprehensive.ps1 -Verbose
```

### Stress Test (Multiple iterations)
```powershell
.\scripts\test-aider-comprehensive.ps1 -Iterations 10
```

---

## Post-Test Actions

### If All Tests Pass
1. Document successful configuration
2. Add environment to PowerShell profile (permanent)
3. Begin using aider for development tasks
4. Consider stress testing for production workloads

### If Tests Fail
1. Review failure layer diagnostic checklist
2. Capture full logs from failed layer
3. Fix identified issue
4. Re-run from failed layer
5. Document solution for future reference

---

## Test Maintenance

This test suite should be run:
- ✓ After any configuration changes
- ✓ After Ollama updates
- ✓ After aider updates
- ✓ After system reboots (to verify persistence)
- ✓ Before integrating with AIM pipeline

---

*Test Plan Version: 1.0*
*Created: 2025-11-22*
*Target: Aider + Ollama + DeepSeek-R1 on Windows*

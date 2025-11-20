#!/usr/bin/env python3
"""
Codex CLI Tool Adapter - PH-5B

Adapter for interfacing with GitHub Codex CLI for AI-assisted development.
"""

import json
import subprocess
import sys
import argparse
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass


@dataclass
class CodexConfig:
    """Codex CLI execution configuration."""
    write_mode: bool = False
    verbose: bool = False
    context_files: List[str] = None
    
    def __post_init__(self):
        if self.context_files is None:
            self.context_files = []


class CodexAdapter:
    """Adapter for GitHub Codex CLI."""
    
    def __init__(self, config: Optional[CodexConfig] = None):
        self.config = config or CodexConfig()
        self.codex_path = self._find_codex()
    
    def _find_codex(self) -> str:
        """Find Codex CLI executable."""
        try:
            result = subprocess.run(
                ["which", "codex"] if sys.platform != "win32" else ["where", "codex"],
                capture_output=True,
                text=True,
                check=True
            )
            return result.stdout.strip().split('\n')[0]
        except subprocess.CalledProcessError:
            return "codex"
    
    def build_command(
        self,
        prompt: str,
        write_mode: Optional[bool] = None,
        context_files: Optional[List[str]] = None,
        **kwargs
    ) -> List[str]:
        """
        Build Codex CLI command.
        
        Args:
            prompt: The prompt to send to Codex
            write_mode: Enable write/edit mode
            context_files: Additional context files
            **kwargs: Additional options
        
        Returns:
            Command as list of strings
        """
        cmd = [self.codex_path]
        
        # Write mode
        if write_mode is None:
            write_mode = self.config.write_mode
        
        if write_mode:
            # Codex uses different syntax for write mode
            cmd.append("--write")
        
        # Verbose mode
        if kwargs.get("verbose", self.config.verbose):
            cmd.append("--verbose")
        
        # Context files
        files = context_files or self.config.context_files
        if files:
            for file in files:
                cmd.extend(["--file", file])
        
        # Prompt (as final argument)
        cmd.append(prompt)
        
        return cmd
    
    def execute(
        self,
        prompt: str,
        write_mode: bool = False,
        context_files: Optional[List[str]] = None,
        capture_output: bool = True,
        dry_run: bool = False,
        **kwargs
    ) -> Dict:
        """
        Execute Codex CLI with the given prompt.
        
        Args:
            prompt: The prompt to send to Codex
            write_mode: Enable write/edit mode
            context_files: Additional context files
            capture_output: Whether to capture stdout/stderr
            dry_run: If True, only show command without executing
            **kwargs: Additional options
        
        Returns:
            Dictionary with execution results
        """
        cmd = self.build_command(prompt, write_mode, context_files, **kwargs)
        
        result = {
            "command": " ".join(cmd),
            "executed": not dry_run,
            "success": False,
            "stdout": "",
            "stderr": "",
            "exit_code": None
        }
        
        if dry_run:
            result["success"] = True
            result["dry_run"] = True
            return result
        
        try:
            process = subprocess.run(
                cmd,
                capture_output=capture_output,
                text=True,
                timeout=600  # 10 minute timeout for Codex
            )
            
            result["success"] = process.returncode == 0
            result["exit_code"] = process.returncode
            result["stdout"] = process.stdout if capture_output else ""
            result["stderr"] = process.stderr if capture_output else ""
            
        except subprocess.TimeoutExpired as e:
            result["success"] = False
            result["error"] = "Codex execution timed out (600s)"
            result["stdout"] = e.stdout.decode() if e.stdout else ""
            result["stderr"] = e.stderr.decode() if e.stderr else ""
        
        except Exception as e:
            result["success"] = False
            result["error"] = str(e)
        
        return result
    
    def execute_from_file(
        self,
        prompt_file: str,
        **kwargs
    ) -> Dict:
        """
        Execute Codex with prompt from file.
        
        Args:
            prompt_file: Path to file containing prompt
            **kwargs: Additional options
        
        Returns:
            Dictionary with execution results
        """
        prompt = Path(prompt_file).read_text()
        return self.execute(prompt, **kwargs)
    
    def validate_output(self, result: Dict) -> Tuple[bool, Optional[str]]:
        """
        Validate Codex execution output.
        
        Args:
            result: Execution result dictionary
        
        Returns:
            (is_valid, error_message)
        """
        if not result.get("success"):
            return False, result.get("error", "Codex execution failed")
        
        stderr = result.get("stderr", "")
        
        # Check for error patterns
        if "error" in stderr.lower() and "warning" not in stderr.lower():
            return False, "Codex reported errors in stderr"
        
        if result.get("exit_code", 0) != 0:
            return False, f"Codex exited with code {result['exit_code']}"
        
        return True, None


def main():
    """CLI entry point."""
    parser = argparse.ArgumentParser(description="Codex CLI adapter")
    parser.add_argument("--prompt", type=str, help="Prompt text or file path")
    parser.add_argument("--write-mode", action="store_true", help="Enable write mode")
    parser.add_argument("--context-files", type=str, nargs="*", help="Context files")
    parser.add_argument("--dry-run", action="store_true", help="Show command without executing")
    parser.add_argument("--execute", action="store_true", help="Execute Codex")
    parser.add_argument("--capture-output", action="store_true", help="Capture stdout/stderr")
    parser.add_argument("--verbose", action="store_true", help="Verbose output")
    
    args = parser.parse_args()
    
    if not args.prompt:
        parser.print_help()
        return 1
    
    try:
        adapter = CodexAdapter()
        
        # Load prompt from file if it's a path
        prompt = args.prompt
        if Path(args.prompt).exists():
            prompt = Path(args.prompt).read_text()
        
        # Execute or dry-run
        result = adapter.execute(
            prompt=prompt,
            write_mode=args.write_mode,
            context_files=args.context_files,
            dry_run=args.dry_run or not args.execute,
            capture_output=args.capture_output,
            verbose=args.verbose
        )
        
        # Output result
        if args.dry_run or not args.execute:
            print(result["command"])
        else:
            print(json.dumps(result, indent=2))
        
        return 0 if result["success"] else 1
    
    except Exception as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())

#!/usr/bin/env python3
"""
Aider Tool Adapter - PH-5A

Adapter for interfacing with Aider CLI tool for AI-assisted code editing.
"""

import json
import subprocess
import sys
import argparse
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass


@dataclass
class AiderConfig:
    """Aider execution configuration."""
    model: str = "gpt-4"
    auto_commits: bool = True
    yes_always: bool = False
    dry_run: bool = False
    edit_format: str = "whole"
    map_tokens: int = 1024
    cache_prompts: bool = True


class AiderAdapter:
    """Adapter for Aider CLI tool."""
    
    def __init__(self, config: Optional[AiderConfig] = None):
        self.config = config or AiderConfig()
        self.aider_path = self._find_aider()
    
    def _find_aider(self) -> str:
        """Find Aider executable."""
        # Try common locations
        try:
            result = subprocess.run(
                ["which", "aider"] if sys.platform != "win32" else ["where", "aider"],
                capture_output=True,
                text=True,
                check=True
            )
            return result.stdout.strip().split('\n')[0]
        except subprocess.CalledProcessError:
            # Fallback to just "aider" and hope it's in PATH
            return "aider"
    
    def build_command(
        self,
        prompt: str,
        files: Optional[List[str]] = None,
        read_only_files: Optional[List[str]] = None,
        **kwargs
    ) -> List[str]:
        """
        Build Aider command with arguments.
        
        Args:
            prompt: The prompt to send to Aider
            files: List of files to edit
            read_only_files: List of read-only files for context
            **kwargs: Additional Aider options
        
        Returns:
            Command as list of strings
        """
        cmd = [self.aider_path]
        
        # Model selection
        model = kwargs.get("model", self.config.model)
        cmd.extend(["--model", model])
        
        # Edit format
        edit_format = kwargs.get("edit_format", self.config.edit_format)
        cmd.extend(["--edit-format", edit_format])
        
        # Auto-commits
        if kwargs.get("auto_commits", self.config.auto_commits):
            cmd.append("--auto-commits")
        else:
            cmd.append("--no-auto-commits")
        
        # Yes always (non-interactive)
        if kwargs.get("yes_always", self.config.yes_always):
            cmd.append("--yes-always")
        
        # Dry run
        if kwargs.get("dry_run", self.config.dry_run):
            cmd.append("--dry-run")
        
        # Cache prompts
        if kwargs.get("cache_prompts", self.config.cache_prompts):
            cmd.append("--cache-prompts")
        
        # Map tokens
        map_tokens = kwargs.get("map_tokens", self.config.map_tokens)
        cmd.extend(["--map-tokens", str(map_tokens)])
        
        # Files to edit
        if files:
            for file in files:
                cmd.append(file)
        
        # Read-only files
        if read_only_files:
            for file in read_only_files:
                cmd.extend(["--read", file])
        
        # Message/prompt
        cmd.extend(["--message", prompt])
        
        return cmd
    
    def execute(
        self,
        prompt: str,
        files: Optional[List[str]] = None,
        read_only_files: Optional[List[str]] = None,
        capture_output: bool = True,
        dry_run: bool = False,
        **kwargs
    ) -> Dict:
        """
        Execute Aider with the given prompt.
        
        Args:
            prompt: The prompt to send to Aider
            files: List of files to edit
            read_only_files: List of read-only files
            capture_output: Whether to capture stdout/stderr
            dry_run: If True, only show command without executing
            **kwargs: Additional Aider options
        
        Returns:
            Dictionary with execution results
        """
        # Override dry_run if specified
        if dry_run:
            kwargs["dry_run"] = True
        
        cmd = self.build_command(prompt, files, read_only_files, **kwargs)
        
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
                timeout=300  # 5 minute timeout
            )
            
            result["success"] = process.returncode == 0
            result["exit_code"] = process.returncode
            result["stdout"] = process.stdout if capture_output else ""
            result["stderr"] = process.stderr if capture_output else ""
            
        except subprocess.TimeoutExpired as e:
            result["success"] = False
            result["error"] = "Aider execution timed out (300s)"
            result["stdout"] = e.stdout.decode() if e.stdout else ""
            result["stderr"] = e.stderr.decode() if e.stderr else ""
        
        except Exception as e:
            result["success"] = False
            result["error"] = str(e)
        
        return result
    
    def execute_from_file(
        self,
        prompt_file: str,
        files: Optional[List[str]] = None,
        **kwargs
    ) -> Dict:
        """
        Execute Aider with prompt from file.
        
        Args:
            prompt_file: Path to file containing prompt
            files: List of files to edit
            **kwargs: Additional Aider options
        
        Returns:
            Dictionary with execution results
        """
        prompt = Path(prompt_file).read_text()
        return self.execute(prompt, files, **kwargs)
    
    def validate_output(self, result: Dict) -> Tuple[bool, Optional[str]]:
        """
        Validate Aider execution output.
        
        Args:
            result: Execution result dictionary
        
        Returns:
            (is_valid, error_message)
        """
        if not result.get("success"):
            return False, result.get("error", "Aider execution failed")
        
        # Check for common Aider error patterns
        stderr = result.get("stderr", "")
        
        if "error" in stderr.lower() and "warning" not in stderr.lower():
            return False, "Aider reported errors in stderr"
        
        if result.get("exit_code", 0) != 0:
            return False, f"Aider exited with code {result['exit_code']}"
        
        return True, None


def main():
    """CLI entry point."""
    parser = argparse.ArgumentParser(description="Aider CLI adapter")
    parser.add_argument("--prompt", type=str, help="Prompt text or file path")
    parser.add_argument("--files", type=str, nargs="*", help="Files to edit")
    parser.add_argument("--read", type=str, nargs="*", help="Read-only files")
    parser.add_argument("--model", type=str, default="gpt-4", help="Model to use")
    parser.add_argument("--dry-run", action="store_true", help="Show command without executing")
    parser.add_argument("--execute", action="store_true", help="Execute Aider")
    parser.add_argument("--capture-output", action="store_true", help="Capture stdout/stderr")
    parser.add_argument("--yes-always", action="store_true", help="Non-interactive mode")
    
    args = parser.parse_args()
    
    if not args.prompt:
        parser.print_help()
        return 1
    
    try:
        adapter = AiderAdapter()
        
        # Load prompt from file if it's a path
        prompt = args.prompt
        if Path(args.prompt).exists():
            prompt = Path(args.prompt).read_text()
        
        # Execute or dry-run
        result = adapter.execute(
            prompt=prompt,
            files=args.files,
            read_only_files=args.read,
            model=args.model,
            dry_run=args.dry_run or not args.execute,
            capture_output=args.capture_output,
            yes_always=args.yes_always
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

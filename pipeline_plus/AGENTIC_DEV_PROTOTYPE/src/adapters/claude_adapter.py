#!/usr/bin/env python3
"""
Claude Code Tool Adapter - PH-5C

Adapter for interfacing with Claude Code CLI for AI-assisted development.
"""

import json
import subprocess
import sys
import argparse
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass


@dataclass
class ClaudeConfig:
    """Claude Code CLI configuration."""
    project_dir: Optional[str] = None
    model: str = "claude-3-5-sonnet-20241022"
    max_tokens: int = 8192
    temperature: float = 0.7


class ClaudeAdapter:
    """Adapter for Claude Code CLI."""
    
    def __init__(self, config: Optional[ClaudeConfig] = None):
        self.config = config or ClaudeConfig()
        self.claude_path = self._find_claude()
    
    def _find_claude(self) -> str:
        """Find Claude CLI executable."""
        try:
            result = subprocess.run(
                ["which", "claude"] if sys.platform != "win32" else ["where", "claude"],
                capture_output=True,
                text=True,
                check=True
            )
            return result.stdout.strip().split('\n')[0]
        except subprocess.CalledProcessError:
            return "claude"
    
    def build_command(
        self,
        prompt: str,
        project_dir: Optional[str] = None,
        model: Optional[str] = None,
        **kwargs
    ) -> List[str]:
        """
        Build Claude Code CLI command.
        
        Args:
            prompt: The prompt to send to Claude
            project_dir: Project directory for context
            model: Model to use
            **kwargs: Additional options
        
        Returns:
            Command as list of strings
        """
        cmd = [self.claude_path]
        
        # Model selection
        model = model or self.config.model
        cmd.extend(["--model", model])
        
        # Project directory
        proj_dir = project_dir or self.config.project_dir
        if proj_dir:
            cmd.extend(["--project-dir", str(proj_dir)])
        
        # Max tokens
        max_tokens = kwargs.get("max_tokens", self.config.max_tokens)
        cmd.extend(["--max-tokens", str(max_tokens)])
        
        # Temperature
        temperature = kwargs.get("temperature", self.config.temperature)
        cmd.extend(["--temperature", str(temperature)])
        
        # Additional context files
        context_files = kwargs.get("context_files", [])
        for file in context_files:
            cmd.extend(["--file", file])
        
        # Prompt (as final argument)
        cmd.append(prompt)
        
        return cmd
    
    def execute(
        self,
        prompt: str,
        project_dir: Optional[str] = None,
        model: Optional[str] = None,
        capture_output: bool = True,
        dry_run: bool = False,
        **kwargs
    ) -> Dict:
        """
        Execute Claude Code CLI with the given prompt.
        
        Args:
            prompt: The prompt to send to Claude
            project_dir: Project directory for context
            model: Model to use
            capture_output: Whether to capture stdout/stderr
            dry_run: If True, only show command without executing
            **kwargs: Additional options
        
        Returns:
            Dictionary with execution results
        """
        cmd = self.build_command(prompt, project_dir, model, **kwargs)
        
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
                timeout=600  # 10 minute timeout
            )
            
            result["success"] = process.returncode == 0
            result["exit_code"] = process.returncode
            result["stdout"] = process.stdout if capture_output else ""
            result["stderr"] = process.stderr if capture_output else ""
            
        except subprocess.TimeoutExpired as e:
            result["success"] = False
            result["error"] = "Claude execution timed out (600s)"
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
        Execute Claude with prompt from file.
        
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
        Validate Claude execution output.
        
        Args:
            result: Execution result dictionary
        
        Returns:
            (is_valid, error_message)
        """
        if not result.get("success"):
            return False, result.get("error", "Claude execution failed")
        
        stderr = result.get("stderr", "")
        
        # Check for error patterns
        if "error" in stderr.lower() and "warning" not in stderr.lower():
            return False, "Claude reported errors in stderr"
        
        if result.get("exit_code", 0) != 0:
            return False, f"Claude exited with code {result['exit_code']}"
        
        return True, None


def main():
    """CLI entry point."""
    parser = argparse.ArgumentParser(description="Claude Code CLI adapter")
    parser.add_argument("--prompt", type=str, help="Prompt text or file path")
    parser.add_argument("--project-dir", type=str, help="Project directory")
    parser.add_argument("--model", type=str, help="Model to use")
    parser.add_argument("--context-files", type=str, nargs="*", help="Context files")
    parser.add_argument("--dry-run", action="store_true", help="Show command without executing")
    parser.add_argument("--execute", action="store_true", help="Execute Claude")
    parser.add_argument("--capture-output", action="store_true", help="Capture stdout/stderr")
    parser.add_argument("--max-tokens", type=int, help="Max tokens")
    parser.add_argument("--temperature", type=float, help="Temperature")
    
    args = parser.parse_args()
    
    if not args.prompt:
        parser.print_help()
        return 1
    
    try:
        adapter = ClaudeAdapter()
        
        # Load prompt from file if it's a path
        prompt = args.prompt
        if Path(args.prompt).exists():
            prompt = Path(args.prompt).read_text()
        
        # Build kwargs
        kwargs = {}
        if args.context_files:
            kwargs["context_files"] = args.context_files
        if args.max_tokens:
            kwargs["max_tokens"] = args.max_tokens
        if args.temperature:
            kwargs["temperature"] = args.temperature
        
        # Execute or dry-run
        result = adapter.execute(
            prompt=prompt,
            project_dir=args.project_dir,
            model=args.model,
            dry_run=args.dry_run or not args.execute,
            capture_output=args.capture_output,
            **kwargs
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

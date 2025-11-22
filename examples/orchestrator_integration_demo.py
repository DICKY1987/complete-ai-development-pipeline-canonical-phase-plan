"""Orchestrator Integration Example

This shows how the engine orchestrator integrates with UI settings
to determine whether tools should run in headless or interactive mode.
"""

from typing import List, Dict, Any
from core.ui_settings import get_settings_manager


class EnhancedOrchestrator:
    """
    Example orchestrator that respects UI settings for tool execution modes.
    
    This demonstrates how to integrate UISettingsManager with the job orchestrator
    to ensure tools run in the appropriate mode (headless vs interactive).
    """
    
    def __init__(self):
        """Initialize orchestrator with UI settings support."""
        self.settings = get_settings_manager()
        self.tool_processes = {}
    
    def build_tool_command(self, tool_name: str, base_args: List[str]) -> List[str]:
        """
        Build command with appropriate flags based on execution mode.
        
        Args:
            tool_name: Name of the tool to run
            base_args: Base command arguments
            
        Returns:
            Complete command with mode-specific flags
        """
        command = [tool_name] + base_args
        
        # Check if tool should run in headless mode
        if self.settings.is_headless(tool_name):
            # Add headless flags based on tool type
            headless_flags = self._get_headless_flags(tool_name)
            command.extend(headless_flags)
        else:
            # Interactive mode - allow user input
            interactive_flags = self._get_interactive_flags(tool_name)
            command.extend(interactive_flags)
        
        return command
    
    def _get_headless_flags(self, tool_name: str) -> List[str]:
        """
        Get headless mode flags for a specific tool.
        
        Args:
            tool_name: Name of the tool
            
        Returns:
            List of flags to add for headless execution
        """
        # Tool-specific headless configurations
        headless_configs = {
            "aider": ["--yes", "--no-auto-commits"],
            "codex": ["--non-interactive", "--quiet"],
            "pytest": ["-q"],  # Quiet mode
            "aim": ["--json"],  # JSON output for parsing
        }
        
        return headless_configs.get(tool_name, [])
    
    def _get_interactive_flags(self, tool_name: str) -> List[str]:
        """
        Get interactive mode flags for a specific tool.
        
        Args:
            tool_name: Name of the tool
            
        Returns:
            List of flags to add for interactive execution
        """
        # Tool-specific interactive configurations
        interactive_configs = {
            "aider": ["--interactive"],
            "codex": ["--interactive"],
            "aim": [],  # Default interactive mode
        }
        
        return interactive_configs.get(tool_name, [])
    
    def launch_tool(self, tool_name: str, args: List[str]) -> Dict[str, Any]:
        """
        Launch a tool in the appropriate mode.
        
        Args:
            tool_name: Name of the tool
            args: Tool-specific arguments
            
        Returns:
            Dictionary with launch information
        """
        mode = self.settings.get_tool_mode(tool_name)
        command = self.build_tool_command(tool_name, args)
        
        launch_info = {
            "tool": tool_name,
            "mode": mode,
            "command": command,
            "is_headless": self.settings.is_headless(tool_name),
        }
        
        if mode == "interactive":
            # For interactive tools, launch in foreground with terminal
            print(f"Launching {tool_name} in INTERACTIVE mode")
            print(f"Command: {' '.join(command)}")
            print(f"Layout: {self.settings.get_interactive_layout()}")
            launch_info["layout"] = self.settings.get_interactive_layout()
        else:
            # For headless tools, launch in background
            print(f"Launching {tool_name} in HEADLESS mode (background)")
            print(f"Command: {' '.join(command)}")
            launch_info["background"] = True
        
        # In real implementation, would actually spawn the process here
        # For now, just return the info
        return launch_info
    
    def startup_tools(self):
        """
        Launch tools according to startup configuration.
        
        This would be called when the UI starts.
        """
        print("=" * 70)
        print("ORCHESTRATOR STARTUP")
        print("=" * 70)
        
        startup_config = self.settings.get_startup_config()
        
        # Launch interactive tool if configured
        if startup_config.get("auto_launch_interactive", True):
            interactive_tool = self.settings.get_interactive_tool()
            print(f"\nLaunching interactive tool: {interactive_tool}")
            info = self.launch_tool(interactive_tool, [])
            self.tool_processes[interactive_tool] = info
        
        # Launch headless tools
        headless_tools = startup_config.get("auto_launch_headless", [])
        if headless_tools:
            print(f"\nLaunching headless tools: {', '.join(headless_tools)}")
            for tool in headless_tools:
                info = self.launch_tool(tool, [])
                self.tool_processes[tool] = info
        
        print("\n" + "=" * 70)
        print(f"Active Tools: {len(self.tool_processes)}")
        print("=" * 70)
    
    def switch_interactive_tool(self, new_tool: str) -> bool:
        """
        Switch which tool is interactive.
        
        Args:
            new_tool: Name of new interactive tool
            
        Returns:
            True if successful
        """
        current_tool = self.settings.get_interactive_tool()
        
        if new_tool == current_tool:
            print(f"{new_tool} is already the interactive tool")
            return True
        
        print(f"\nSwitching interactive tool: {current_tool} → {new_tool}")
        
        # 1. Stop current interactive tool
        print(f"  1. Stopping {current_tool}...")
        if current_tool in self.tool_processes:
            del self.tool_processes[current_tool]
        
        # 2. Update configuration
        print(f"  2. Updating configuration...")
        success = self.settings.set_interactive_tool(new_tool)
        
        if not success:
            print(f"  ✗ Failed to update configuration")
            return False
        
        # 3. Relaunch old tool in headless mode if needed
        if current_tool in self.settings.get_auto_launch_headless_tools():
            print(f"  3. Relaunching {current_tool} in headless mode...")
            info = self.launch_tool(current_tool, [])
            self.tool_processes[current_tool] = info
        
        # 4. Launch new tool in interactive mode
        print(f"  4. Launching {new_tool} in interactive mode...")
        info = self.launch_tool(new_tool, [])
        self.tool_processes[new_tool] = info
        
        print(f"  ✓ Interactive tool switched successfully")
        return True


def demonstrate_orchestrator_integration():
    """Demonstrate orchestrator integration with UI settings."""
    
    print("\n" + "=" * 70)
    print(" ORCHESTRATOR INTEGRATION DEMONSTRATION")
    print("=" * 70)
    
    orchestrator = EnhancedOrchestrator()
    
    # Simulate UI startup
    print("\n[1] UI Startup - Auto-launching tools...")
    orchestrator.startup_tools()
    
    # Show active processes
    print("\nActive Tool Processes:")
    for tool, info in orchestrator.tool_processes.items():
        print(f"  {tool:<15} Mode: {info['mode'].upper():<12} Headless: {info['is_headless']}")
    
    # Simulate user switching interactive tool
    print("\n" + "=" * 70)
    print("[2] User switches interactive tool to 'aider'")
    print("=" * 70)
    orchestrator.switch_interactive_tool("aider")
    
    # Show updated processes
    print("\nUpdated Tool Processes:")
    for tool, info in orchestrator.tool_processes.items():
        print(f"  {tool:<15} Mode: {info['mode'].upper():<12} Headless: {info['is_headless']}")
    
    # Demonstrate building commands
    print("\n" + "=" * 70)
    print("[3] Building tool commands based on mode")
    print("=" * 70)
    
    tools_to_test = ["aider", "aim", "pytest"]
    for tool in tools_to_test:
        base_args = ["--config", "default"]
        command = orchestrator.build_tool_command(tool, base_args)
        mode = orchestrator.settings.get_tool_mode(tool)
        print(f"\n{tool} ({mode}):")
        print(f"  Command: {' '.join(command)}")


if __name__ == "__main__":
    demonstrate_orchestrator_integration()

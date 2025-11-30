"""
YAML Template Generator
Generates UET-style YAML templates from detected patterns
"""
DOC_ID: DOC-PAT-GENERATORS-YAML-TEMPLATE-GENERATOR-646

from typing import Dict, Any
from pathlib import Path
import yaml
from ..detectors.base_detector import DetectedPattern


class YAMLTemplateGenerator:
    """Generates execution pattern YAML templates"""
    
    def generate_template(self, pattern: DetectedPattern) -> Dict[str, Any]:
        """
        Generate a UET-style execution pattern template
        
        Format follows: templates/execution_patterns/*.pattern.yaml
        """
        template = {
            'pattern_id': f"{pattern.pattern_id}_v1",
            'category': self._map_category(pattern.pattern_type),
            'description': self._generate_description(pattern),
            'use_case': self._generate_use_case(pattern),
            'time_savings': self._format_time_savings(pattern),
            
            'structural_decisions': self._generate_structural_decisions(pattern),
            'execution_steps': self._generate_execution_steps(pattern),
            'ground_truth': self._generate_ground_truth(pattern),
            
            'meta': {
                'created_at': '2025-11-23',
                'version': '1.0.0',
                'based_on': 'CLI log pattern extraction',
                'proven_uses': pattern.frequency,
                'avg_duration_seconds': round(pattern.avg_duration_seconds, 2),
                'time_savings_percent': f"{pattern.time_savings_percent:.0f}%"
            }
        }
        
        # Add pattern-specific sections
        if pattern.pattern_type == 'parallel':
            template['parallelism'] = self._generate_parallelism_info(pattern)
        
        return template
    
    def _map_category(self, pattern_type: str) -> str:
        """Map pattern type to category"""
        mapping = {
            'parallel': 'file_creation',
            'sequential': 'file_modification',
            'template': 'template_application'
        }
        return mapping.get(pattern_type, 'unknown')
    
    def _generate_description(self, pattern: DetectedPattern) -> str:
        """Generate human-readable description"""
        tools = ', '.join(pattern.tool_sequence)
        
        if pattern.pattern_type == 'parallel':
            return f"Execute {tools} in parallel for {pattern.time_savings_percent:.0f}% time savings"
        elif pattern.pattern_type == 'sequential':
            return f"Sequential workflow: {tools}"
        else:
            return f"Template pattern using {tools}"
    
    def _generate_use_case(self, pattern: DetectedPattern) -> str:
        """Generate use case description"""
        if pattern.pattern_type == 'parallel':
            return f"Use when you need to {' and '.join(pattern.tool_sequence)} simultaneously"
        else:
            return f"Use for {' → '.join(pattern.tool_sequence)} workflows"
    
    def _format_time_savings(self, pattern: DetectedPattern) -> str:
        """Format time savings message"""
        if pattern.time_savings_percent:
            return f"{pattern.time_savings_percent:.0f}% (proven across {pattern.frequency} uses)"
        return "Time savings not measured"
    
    def _generate_structural_decisions(self, pattern: DetectedPattern) -> Dict[str, Any]:
        """Generate structural decisions section"""
        decisions = {
            'tool_sequence': pattern.tool_sequence,
            'proven_frequency': pattern.frequency,
            'no_placeholders': True,
            'include_error_handling': True
        }
        
        if pattern.pattern_type == 'parallel':
            decisions['execution_mode'] = 'parallel'
            decisions['max_concurrent'] = len(pattern.tool_sequence)
        
        return decisions
    
    def _generate_execution_steps(self, pattern: DetectedPattern) -> Dict[str, Any]:
        """Generate execution steps section"""
        steps = {}
        
        for idx, tool in enumerate(pattern.tool_sequence, 1):
            step_key = f"{idx}_{tool}"
            steps[step_key] = {
                'tool': tool,
                'on_fail': 'enter_fix_loop'
            }
        
        return steps
    
    def _generate_ground_truth(self, pattern: DetectedPattern) -> Dict[str, Any]:
        """Generate ground truth verification section"""
        return {
            'success_criteria': [
                f"All {len(pattern.tool_sequence)} operations complete successfully",
                "No errors in execution logs",
                "Expected artifacts created"
            ]
        }
    
    def _generate_parallelism_info(self, pattern: DetectedPattern) -> Dict[str, Any]:
        """Generate parallelism-specific information"""
        metadata = pattern.metadata or {}
        
        return {
            'parallel_eligible': True,
            'speedup_factor': round(metadata.get('speedup_factor', 1.0), 2),
            'avg_parallel_duration': round(metadata.get('avg_parallel_duration', 0), 2),
            'avg_sequential_duration': round(metadata.get('avg_sequential_duration', 0), 2)
        }
    
    def save_template(self, pattern: DetectedPattern, output_dir: Path) -> Path:
        """
        Generate and save YAML template to file
        
        Args:
            pattern: Detected pattern to convert to template
            output_dir: Directory to save template in
            
        Returns:
            Path to saved template file
        """
        template = self.generate_template(pattern)
        
        # Determine subdirectory based on pattern type
        subdir = output_dir / pattern.pattern_type
        subdir.mkdir(parents=True, exist_ok=True)
        
        # Create filename
        filename = f"{pattern.pattern_id}.pattern.yaml"
        filepath = subdir / filename
        
        # Save as YAML
        with open(filepath, 'w', encoding='utf-8') as f:
            yaml.dump(
                template, 
                f, 
                default_flow_style=False,
                sort_keys=False,
                allow_unicode=True
            )
        
        return filepath

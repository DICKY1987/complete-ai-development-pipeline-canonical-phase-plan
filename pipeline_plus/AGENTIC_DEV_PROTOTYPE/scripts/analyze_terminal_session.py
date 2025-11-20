#!/usr/bin/env python3
"""
Terminal Session Analyzer
Extracts insights from saved terminal session transcripts
Generated: 2025-11-20
"""

import re
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any
from collections import Counter


class TerminalSessionAnalyzer:
    """Analyzes terminal session transcripts for development insights"""
    
    def __init__(self, transcript_path: str):
        self.transcript_path = Path(transcript_path)
        self.transcript_text = ""
        self.metrics = {
            "file": str(self.transcript_path),
            "analyzed_at": datetime.now().isoformat(),
            "session_metrics": {},
            "ai_metrics": {},
            "error_metrics": {},
            "interaction_metrics": {}
        }
        
        if self.transcript_path.exists():
            with open(self.transcript_path, 'r', encoding='utf-8', errors='ignore') as f:
                self.transcript_text = f.read()
    
    def analyze_all(self):
        """Run all analysis methods"""
        print(f"🔍 Analyzing transcript: {self.transcript_path.name}")
        
        if not self.transcript_text:
            print("❌ Error: Transcript file is empty or not found!")
            return None
        
        self.analyze_session_structure()
        self.analyze_ai_interactions()
        self.analyze_errors()
        self.analyze_time_patterns()
        self.analyze_commands()
        
        return self.metrics
    
    def analyze_session_structure(self):
        """Analyze overall session structure"""
        print("📊 Analyzing session structure...")
        
        lines = self.transcript_text.split('\n')
        
        # Count key patterns
        proceed_commands = len(re.findall(r'\bproceed\b', self.transcript_text, re.IGNORECASE))
        phase_mentions = len(re.findall(r'Phase \d[A-F]', self.transcript_text))
        milestone_mentions = len(re.findall(r'Milestone M\d', self.transcript_text))
        
        self.metrics["session_metrics"] = {
            "total_lines": len(lines),
            "total_characters": len(self.transcript_text),
            "proceed_commands": proceed_commands,
            "phase_mentions": phase_mentions,
            "milestone_mentions": milestone_mentions,
            "estimated_turns": proceed_commands + 5  # Initial + proceeds
        }
    
    def analyze_ai_interactions(self):
        """Analyze AI behavior patterns"""
        print("🤖 Analyzing AI interactions...")
        
        # Tool calls
        tool_calls = re.findall(r'<invoke name="([^"]+)"', self.transcript_text)
        tool_counter = Counter(tool_calls)
        
        # Intent reports
        intents = re.findall(r'<parameter name="intent">([^<]+)
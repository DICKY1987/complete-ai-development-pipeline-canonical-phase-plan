"""Multi-AI Log Miner (AUTO-006)

Mines conversation logs from Claude Code, GitHub Copilot, and Codex CLI
to detect repetitive user requests and auto-generate patterns.

**Goal**: Capture end-to-end workflows, detect common phrases/tasks,
and fold them into patterns without user input.

**Data Sources**:
- Claude Code: ~/.claude/file-history
- GitHub Copilot: ~/.copilot/session-state/*.jsonl
- Codex CLI: ~/.codex/log/*.log

**Output**: Auto-generated patterns for common user requests
"""

import json
import re
import sqlite3
from collections import Counter, defaultdict
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
import hashlib


@dataclass
class UserRequest:
    """Captured user request from AI tool logs."""
    timestamp: datetime
    source: str  # 'claude', 'copilot', 'codex'
    session_id: str
    user_message: str
    ai_response: Optional[str]
    tools_used: List[str]
    files_touched: List[str]
    operation_kind: str
    success: bool
    duration_seconds: Optional[float]


class MultiAILogMiner:
    """Mine logs from multiple AI tools to detect common patterns."""
    
    def __init__(self, db_connection, user_home: Optional[Path] = None):
        self.db = db_connection
        self.user_home = user_home or Path.home()
        
        # Log locations
        self.claude_logs = self.user_home / ".claude" / "file-history"
        self.copilot_logs = self.user_home / ".copilot" / "session-state"
        self.codex_logs = self.user_home / ".codex" / "log"
        
        # Phrase detection thresholds
        self.min_phrase_occurrences = 3  # Need 3+ occurrences to auto-generate
        self.similarity_threshold = 0.80  # 80% similarity = same pattern
        self.lookback_days = 30
    
    def mine_all_logs(self) -> List[UserRequest]:
        """Mine logs from all AI tools."""
        requests = []
        
        # Mine each source
        requests.extend(self._mine_claude_logs())
        requests.extend(self._mine_copilot_logs())
        requests.extend(self._mine_codex_logs())
        
        # Sort by timestamp
        requests.sort(key=lambda r: r.timestamp)
        
        return requests
    
    def _mine_copilot_logs(self) -> List[UserRequest]:
        """Parse GitHub Copilot session state JSONL files."""
        requests = []
        
        if not self.copilot_logs.exists():
            return requests
        
        cutoff = datetime.now() - timedelta(days=self.lookback_days)
        
        for session_file in self.copilot_logs.glob("*.jsonl"):
            try:
                session_id = session_file.stem
                user_messages = []
                ai_responses = []
                tools_used = set()
                files_touched = set()
                session_start = None
                
                with session_file.open('r', encoding='utf-8') as f:
                    for line in f:
                        try:
                            event = json.loads(line.strip())
                            
                            # Parse timestamp with timezone awareness
                            timestamp_str = event.get('timestamp', '')
                            if not timestamp_str:
                                continue
                            
                            # Handle both offset-aware and offset-naive timestamps
                            try:
                                timestamp = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
                            except:
                                # Fallback for various formats
                                timestamp = datetime.now()
                            
                            # Make cutoff timezone-aware for comparison
                            if timestamp.tzinfo is not None and cutoff.tzinfo is None:
                                from datetime import timezone
                                cutoff = cutoff.replace(tzinfo=timezone.utc)
                            elif timestamp.tzinfo is None and cutoff.tzinfo is not None:
                                timestamp = timestamp.replace(tzinfo=cutoff.tzinfo)
                            
                            if timestamp < cutoff:
                                continue
                            
                            if event.get('type') == 'session.start':
                                session_start = timestamp
                            
                            # User input
                            elif event.get('type') == 'user.input':
                                user_message = event.get('data', {}).get('message', '')
                                if user_message:
                                    user_messages.append((timestamp, user_message))
                            
                            # AI response
                            elif event.get('type') == 'assistant.message':
                                ai_response = event.get('data', {}).get('message', '')
                                if ai_response:
                                    ai_responses.append((timestamp, ai_response))
                            
                            # Tool use
                            elif event.get('type') == 'tool.call':
                                tool_name = event.get('data', {}).get('toolName', '')
                                if tool_name:
                                    tools_used.add(tool_name)
                            
                            # File operations
                            elif event.get('type') in ('file.read', 'file.write', 'file.edit'):
                                file_path = event.get('data', {}).get('path', '')
                                if file_path:
                                    files_touched.add(file_path)
                        
                        except (json.JSONDecodeError, ValueError):
                            continue
                
                # Pair user messages with AI responses
                for i, (ts, user_msg) in enumerate(user_messages):
                    # Find next AI response after this message
                    ai_resp = None
                    for resp_ts, resp_msg in ai_responses:
                        if resp_ts > ts:
                            ai_resp = resp_msg
                            break
                    
                    # Infer operation kind from message
                    operation_kind = self._infer_operation_kind(user_msg, list(tools_used))
                    
                    requests.append(UserRequest(
                        timestamp=ts,
                        source='copilot',
                        session_id=session_id,
                        user_message=user_msg,
                        ai_response=ai_resp,
                        tools_used=list(tools_used),
                        files_touched=list(files_touched),
                        operation_kind=operation_kind,
                        success=True,  # Assume success if logged
                        duration_seconds=None
                    ))
            
            except Exception as e:
                print(f"[log-miner] Error parsing {session_file.name}: {e}")
                continue
        
        return requests
    
    def _mine_codex_logs(self) -> List[UserRequest]:
        """Parse Codex CLI log files."""
        requests = []
        
        if not self.codex_logs.exists():
            return requests
        
        cutoff = datetime.now() - timedelta(days=self.lookback_days)
        
        for log_file in self.codex_logs.glob("*.log"):
            try:
                current_request = None
                
                with log_file.open('r', encoding='utf-8', errors='ignore') as f:
                    for line in f:
                        # Parse timestamp
                        match = re.match(r'(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2})', line)
                        if not match:
                            continue
                        
                        timestamp = datetime.fromisoformat(match.group(1))
                        if timestamp < cutoff:
                            continue
                        
                        # Detect user input
                        if 'UserInput:' in line or 'user_message:' in line.lower():
                            msg_match = re.search(r'(?:UserInput:|user_message:)\s*(.+)', line)
                            if msg_match:
                                user_msg = msg_match.group(1).strip()
                                current_request = {
                                    'timestamp': timestamp,
                                    'user_message': user_msg,
                                    'tools_used': [],
                                    'files_touched': []
                                }
                        
                        # Detect tool calls
                        elif 'ToolCall:' in line and current_request:
                            tool_match = re.search(r'ToolCall:\s*(\w+)', line)
                            if tool_match:
                                current_request['tools_used'].append(tool_match.group(1))
                        
                        # Detect file operations
                        elif ('file:' in line.lower() or 'path:' in line.lower()) and current_request:
                            path_match = re.search(r'(?:file|path):\s*"?([^"\s]+)"?', line, re.I)
                            if path_match:
                                current_request['files_touched'].append(path_match.group(1))
                        
                        # Request completed
                        elif ('completed' in line.lower() or 'success' in line.lower()) and current_request:
                            operation_kind = self._infer_operation_kind(
                                current_request['user_message'],
                                current_request['tools_used']
                            )
                            
                            requests.append(UserRequest(
                                timestamp=current_request['timestamp'],
                                source='codex',
                                session_id=log_file.stem,
                                user_message=current_request['user_message'],
                                ai_response=None,
                                tools_used=current_request['tools_used'],
                                files_touched=current_request['files_touched'],
                                operation_kind=operation_kind,
                                success='success' in line.lower(),
                                duration_seconds=None
                            ))
                            current_request = None
            
            except Exception as e:
                print(f"[log-miner] Error parsing {log_file.name}: {e}")
                continue
        
        return requests
    
    def _mine_claude_logs(self) -> List[UserRequest]:
        """Parse Claude Code file history."""
        # Note: .claude/file-history structure depends on Claude's implementation
        # This is a placeholder - adjust based on actual file format
        requests = []
        
        if not self.claude_logs.exists():
            return requests
        
        # Add parsing logic when structure is known
        # Expected: JSON or JSONL with user messages and file operations
        
        return requests
    
    def _infer_operation_kind(self, user_message: str, tools_used: List[str]) -> str:
        """Infer operation type from message and tools."""
        msg_lower = user_message.lower()
        
        # Pattern matching
        if 'create' in msg_lower and 'test' in msg_lower:
            return 'test_creation'
        elif 'create' in msg_lower and 'file' in msg_lower:
            return 'file_creation'
        elif 'refactor' in msg_lower or 'rename' in msg_lower:
            return 'refactoring'
        elif 'fix' in msg_lower or 'debug' in msg_lower:
            return 'debugging'
        elif 'add' in msg_lower and ('function' in msg_lower or 'method' in msg_lower):
            return 'feature_addition'
        elif 'document' in msg_lower or 'docstring' in msg_lower:
            return 'documentation'
        elif 'migrate' in msg_lower or 'move' in msg_lower:
            return 'migration'
        elif 'validate' in msg_lower or 'check' in msg_lower:
            return 'validation'
        
        # Tool-based inference
        if 'grep' in tools_used and 'edit' in tools_used:
            return 'search_and_replace'
        elif 'create' in tools_used:
            return 'file_creation'
        elif 'git' in tools_used:
            return 'git_operation'
        
        return 'unknown'
    
    def detect_common_phrases(self, requests: List[UserRequest]) -> Dict[str, List[UserRequest]]:
        """Group requests by similar user messages."""
        phrase_groups = defaultdict(list)
        
        for request in requests:
            # Normalize message (remove case, extra spaces, file paths)
            normalized = self._normalize_message(request.user_message)
            signature = self._hash_message(normalized)
            
            phrase_groups[signature].append(request)
        
        # Filter to only common phrases (3+ occurrences)
        common = {sig: reqs for sig, reqs in phrase_groups.items() 
                  if len(reqs) >= self.min_phrase_occurrences}
        
        return common
    
    def _normalize_message(self, message: str) -> str:
        """Normalize user message for comparison."""
        # Lowercase
        normalized = message.lower()
        
        # Remove file paths
        normalized = re.sub(r'[a-z]:\\[^\s]+', '{file_path}', normalized)
        normalized = re.sub(r'/[^\s]+', '{file_path}', normalized)
        
        # Remove specific names/numbers
        normalized = re.sub(r'\b\d+\b', '{number}', normalized)
        normalized = re.sub(r'\b[a-z]+_\d+\b', '{identifier}', normalized)
        
        # Remove extra whitespace
        normalized = ' '.join(normalized.split())
        
        return normalized
    
    def _hash_message(self, message: str) -> str:
        """Create hash of normalized message."""
        return hashlib.md5(message.encode()).hexdigest()[:16]
    
    def auto_generate_patterns(self, common_phrases: Dict[str, List[UserRequest]]) -> List[Dict]:
        """Auto-generate patterns from common user requests."""
        patterns = []
        
        for phrase_sig, requests in common_phrases.items():
            if len(requests) < self.min_phrase_occurrences:
                continue
            
            # Analyze requests to extract pattern
            pattern = self._synthesize_pattern_from_requests(requests)
            
            if pattern:
                patterns.append(pattern)
                self._save_pattern_to_db(pattern, requests)
        
        return patterns
    
    def _synthesize_pattern_from_requests(self, requests: List[UserRequest]) -> Optional[Dict]:
        """Create pattern spec from group of similar requests."""
        if not requests:
            return None
        
        # Extract common elements
        operation_kind = Counter(r.operation_kind for r in requests).most_common(1)[0][0]
        tools_used = set()
        for r in requests:
            tools_used.update(r.tools_used)
        
        file_types = set()
        for r in requests:
            for f in r.files_touched:
                ext = Path(f).suffix.lstrip('.')
                if ext:
                    file_types.add(ext)
        
        # Calculate confidence (how similar are the requests?)
        confidence = self._calculate_similarity_confidence(requests)
        
        if confidence < self.similarity_threshold:
            return None  # Too varied to be a pattern
        
        # Generate pattern ID
        pattern_id = f"AUTO-{operation_kind.upper()}-{datetime.now().strftime('%Y%m%d')}"
        
        # Extract representative user message
        user_phrase = requests[0].user_message
        
        return {
            'pattern_id': pattern_id,
            'name': f"Auto: {operation_kind.replace('_', ' ').title()}",
            'description': f"Auto-generated from {len(requests)} similar user requests",
            'user_phrase_trigger': self._normalize_message(user_phrase),
            'operation_kind': operation_kind,
            'tools_used': sorted(tools_used),
            'file_types': sorted(file_types),
            'confidence': confidence,
            'occurrences': len(requests),
            'sources': list(set(r.source for r in requests)),
            'first_seen': min(r.timestamp for r in requests).isoformat(),
            'last_seen': max(r.timestamp for r in requests).isoformat(),
            'auto_approved': confidence >= 0.90  # High confidence = auto-approve
        }
    
    def _calculate_similarity_confidence(self, requests: List[UserRequest]) -> float:
        """Calculate how similar a group of requests are."""
        if len(requests) < 2:
            return 1.0
        
        # Compare normalized messages
        normalized = [self._normalize_message(r.user_message) for r in requests]
        
        # Count common words
        all_words = [set(msg.split()) for msg in normalized]
        common_words = set.intersection(*all_words) if all_words else set()
        total_words = set.union(*all_words) if all_words else set()
        
        if not total_words:
            return 0.0
        
        # Jaccard similarity
        return len(common_words) / len(total_words)
    
    def _save_pattern_to_db(self, pattern: Dict, requests: List[UserRequest]):
        """Save detected pattern to database."""
        self.db.execute(
            """
            INSERT INTO pattern_candidates
            (pattern_id, signature, example_executions, confidence, auto_generated_spec, status, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                pattern['pattern_id'],
                pattern['user_phrase_trigger'],
                json.dumps([
                    {
                        'timestamp': r.timestamp.isoformat(),
                        'source': r.source,
                        'user_message': r.user_message,
                        'tools_used': r.tools_used
                    }
                    for r in requests[:10]  # Limit to 10 examples
                ]),
                pattern['confidence'],
                json.dumps(pattern),
                'approved' if pattern['auto_approved'] else 'pending',
                datetime.now()
            )
        )
        self.db.commit()
    
    def run_daily_mining(self) -> Dict:
        """Run daily log mining and pattern generation."""
        print("[log-miner] Starting daily AI log mining...")
        
        # Step 1: Mine all logs
        requests = self.mine_all_logs()
        print(f"[log-miner] Mined {len(requests)} requests from all sources")
        
        # Step 2: Detect common phrases
        common_phrases = self.detect_common_phrases(requests)
        print(f"[log-miner] Found {len(common_phrases)} common phrase patterns")
        
        # Step 3: Auto-generate patterns
        patterns = self.auto_generate_patterns(common_phrases)
        print(f"[log-miner] Generated {len(patterns)} new patterns")
        
        # Step 4: Generate report
        auto_approved = [p for p in patterns if p['auto_approved']]
        pending_review = [p for p in patterns if not p['auto_approved']]
        
        report = {
            'total_requests_mined': len(requests),
            'common_phrases_detected': len(common_phrases),
            'patterns_generated': len(patterns),
            'auto_approved': len(auto_approved),
            'pending_review': len(pending_review),
            'patterns': patterns,
            'timestamp': datetime.now().isoformat()
        }
        
        print(f"[log-miner] ✓ {len(auto_approved)} patterns auto-approved")
        print(f"[log-miner] ⏳ {len(pending_review)} patterns pending review")
        
        return report


# Scheduled task integration
def run_nightly_log_mining(db_path: str, user_home: Optional[Path] = None):
    """Run as scheduled task every night to mine logs."""
    import sqlite3
    
    db = sqlite3.connect(db_path)
    miner = MultiAILogMiner(db, user_home)
    
    report = miner.run_daily_mining()
    
    # Save report
    report_dir = Path(__file__).parent.parent.parent / "reports" / "log_mining"
    report_dir.mkdir(parents=True, exist_ok=True)
    
    report_file = report_dir / f"mining_report_{datetime.now().strftime('%Y%m%d')}.json"
    report_file.write_text(json.dumps(report, indent=2), encoding='utf-8')
    
    print(f"[log-miner] Report saved to {report_file}")
    
    db.close()
    return report


if __name__ == '__main__':
    # Test run
    db_path = Path(__file__).parent.parent.parent / "metrics" / "pattern_automation.db"
    run_nightly_log_mining(str(db_path))

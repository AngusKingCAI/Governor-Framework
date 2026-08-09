"""
Audit Logging for Governor - Simplified hash-chained JSONL logging
"""

import os
import sys
import json
import hashlib
from datetime import datetime
from typing import Dict, Any

# Get Governor package root for relative paths
GOVERNOR_ROOT = os.path.dirname(os.path.abspath(__file__))


def log_execution(component: str, data: Dict[str, Any]):
    """Log execution to daily JSONL file."""
    try:
        log_dir = os.path.join(GOVERNOR_ROOT, "logs")
        os.makedirs(log_dir, exist_ok=True)
        
        today = datetime.utcnow().strftime("%m-%d-%Y")
        log_file = os.path.join(log_dir, f"Governor-Log-{today}.jsonl")
        
        entry = {
            "File": "audit_log.py",
            "hook": component,
            "Time": datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S'),
            "data": data
        }
        
        with open(log_file, 'a', encoding='utf-8') as f:
            f.write(json.dumps(entry) + "\n")
            f.flush()
            
    except Exception as e:
        sys.stderr.write(f"Logging error: {e}\n")
        sys.stderr.flush()


# Audit log file path
AUDIT_DIR = os.path.join(GOVERNOR_ROOT, "logs")
AUDIT_FILE = os.path.join(AUDIT_DIR, "audit.jsonl")


def _compute_hash(data: Dict[str, Any]) -> str:
    """Compute SHA-256 hash of event data."""
    canonical_json = json.dumps(data, sort_keys=True, separators=(',', ':'))
    return hashlib.sha256(canonical_json.encode()).hexdigest()


def _get_last_hash() -> str:
    """Get the hash of the last event in the audit log."""
    if not os.path.exists(AUDIT_FILE):
        return ""
    
    try:
        with open(AUDIT_FILE, 'r') as f:
            lines = f.readlines()
            if not lines:
                return ""
            
            last_line = lines[-1].strip()
            if not last_line:
                return ""
            
            event = json.loads(last_line)
            return event.get("current_hash", "")
    except (json.JSONDecodeError, IOError):
        return ""


def log_event(hook_name: str, payload: Dict[str, Any], response: Dict[str, Any], level: str = "info") -> None:
    """Log event with hash chaining and internal decision."""
    log_execution("AuditLog", {
        "action": "log_event",
        "hook_name": hook_name,
        "level": level
    })
    
    os.makedirs(AUDIT_DIR, exist_ok=True)
    prev_hash = _get_last_hash()
    
    # Extract internal decision from governor_internal field
    internal_decision = response.get("governor_internal", {}).get("decision", "unknown")
    
    # Build event data for hashing
    event_data = {
        "timestamp": datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S'),
        "hook_name": hook_name,
        "prev_hash": prev_hash,
        "decision": internal_decision,
        "level": level,
        "data": response
    }
    
    # Compute current hash
    current_hash = _compute_hash(event_data)
    event_data["current_hash"] = current_hash
    
    # Append to audit log
    with open(AUDIT_FILE, 'a', newline='\n') as f:
        f.write(json.dumps(event_data))
        f.write('\n')
        f.flush()
        os.fsync(f.fileno())


def get_audit_log() -> list:
    """Get all events from the audit log."""
    if not os.path.exists(AUDIT_FILE):
        return []
    
    events = []
    with open(AUDIT_FILE, 'r') as f:
        for line in f:
            line = line.strip()
            if line:
                try:
                    events.append(json.loads(line))
                except json.JSONDecodeError:
                    continue
    
    return events

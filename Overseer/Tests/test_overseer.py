"""
Comprehensive test suite for Overseer Framework - overseer.py

This test suite follows TDD principles and tests all components of overseer.py:
- Foundation classes (GovernanceDecision, CanonicalPayload, HookResult)
- Protocol layer
- Audit logger
- Config manager
- Hook registry
- Policy coordinator
- Emergency controls
- Overseer main class

Test Strategy:
- Unit tests for each component in isolation
- Integration tests for end-to-end governance pipeline
- Security tests for input validation, secret redaction, configuration tampering
- Performance tests for hook execution and policy evaluation

Zero external dependencies - uses Python stdlib unittest only.
"""

import json
import os
import shutil
import tempfile
import time
import unittest
from datetime import datetime
from hashlib import sha256
from pathlib import Path
from threading import Thread
from typing import Dict, Any

# Import overseer.py components
import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from Overseer.Core.overseer import (
    AuditLogger,
    BaseAdapter,
    CanonicalPayload,
    ConfigManager,
    EmergencyControls,
    GovernanceDecision,
    HookPhase,
    HookRegistry,
    HookResult,
    Overseer,
    PolicyCoordinator,
    ProtocolLayer,
)


# ============================================================================
# Unit Tests - Foundation Classes
# ============================================================================

class TestGovernanceDecision(unittest.TestCase):
    """Test GovernanceDecision dataclass."""
    
    def test_decision_creation(self):
        """Test creating a governance decision."""
        decision = GovernanceDecision(
            decision="allow",
            policy_id="test_policy",
            rationale="Test rationale",
            context={"test": "data"}
        )
        self.assertEqual(decision.decision, "allow")
        self.assertEqual(decision.policy_id, "test_policy")
        self.assertEqual(decision.rationale, "Test rationale")
        self.assertEqual(decision.context, {"test": "data"})
    
    def test_decision_with_timestamp(self):
        """Test decision creation with auto-generated timestamp."""
        decision = GovernanceDecision(
            decision="deny",
            policy_id="test_policy",
            rationale="Test rationale",
            context={}
        )
        self.assertIsNotNone(decision.timestamp)
        # Verify ISO format
        datetime.fromisoformat(decision.timestamp)
    
    def test_decision_with_evaluated_rules(self):
        """Test decision with evaluated rules."""
        decision = GovernanceDecision(
            decision="allow",
            policy_id="test_policy",
            rationale="Test rationale",
            context={},
            evaluated_rules=[
                {"policy_id": "policy1", "decision": "allow"},
                {"policy_id": "policy2", "decision": "deny"}
            ]
        )
        self.assertEqual(len(decision.evaluated_rules), 2)


class TestCanonicalPayload(unittest.TestCase):
    """Test CanonicalPayload dataclass."""
    
    def test_payload_creation(self):
        """Test creating a canonical payload."""
        payload = CanonicalPayload(
            action_type="read",
            agent_identity="agent-001",
            resource="/path/to/file",
            access_level="read",
            audit_context={"session_id": "test-session"}
        )
        self.assertEqual(payload.action_type, "read")
        self.assertEqual(payload.agent_identity, "agent-001")
        self.assertEqual(payload.resource, "/path/to/file")
        self.assertEqual(payload.access_level, "read")
        self.assertEqual(payload.audit_context, {"session_id": "test-session"})
    
    def test_payload_with_metadata(self):
        """Test payload with optional metadata."""
        payload = CanonicalPayload(
            action_type="write",
            agent_identity="agent-001",
            resource="/path/to/file",
            access_level="write",
            audit_context={},
            metadata={"timeout": 30}
        )
        self.assertEqual(payload.metadata, {"timeout": 30})
    
    def test_payload_without_metadata(self):
        """Test payload without metadata defaults to None."""
        payload = CanonicalPayload(
            action_type="read",
            agent_identity="agent-001",
            resource="/path/to/file",
            access_level="read",
            audit_context={}
        )
        self.assertIsNone(payload.metadata)


class TestHookResult(unittest.TestCase):
    """Test HookResult dataclass."""
    
    def test_allow_result(self):
        """Test allow hook result."""
        result = HookResult(decision="allow", reason="Test passed")
        self.assertEqual(result.decision, "allow")
        self.assertEqual(result.reason, "Test passed")
        self.assertIsNone(result.modified_context)
    
    def test_deny_result(self):
        """Test deny hook result."""
        result = HookResult(decision="deny", reason="Test failed")
        self.assertEqual(result.decision, "deny")
        self.assertEqual(result.reason, "Test failed")
    
    def test_modify_result(self):
        """Test modify hook result with modified context."""
        result = HookResult(
            decision="modify",
            reason="Modified parameters",
            modified_context={"timeout": 60}
        )
        self.assertEqual(result.decision, "modify")
        self.assertEqual(result.modified_context, {"timeout": 60})


# ============================================================================
# Unit Tests - Protocol Layer
# ============================================================================

class TestProtocolLayer(unittest.TestCase):
    """Test ProtocolLayer component."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.audit_logger = AuditLogger(self.temp_dir, "ProtocolTest")
        self.protocol_layer = ProtocolLayer(self.audit_logger.logger)
    
    def tearDown(self):
        """Clean up test fixtures."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_validate_valid_payload(self):
        """Test validation of valid payload."""
        payload = CanonicalPayload(
            action_type="read",
            agent_identity="agent-001",
            resource="/path/to/file",
            access_level="read",
            audit_context={}
        )
        result = self.protocol_layer.validate_payload(payload)
        self.assertTrue(result)
    
    def test_validate_missing_field(self):
        """Test validation fails with missing field."""
        # Create payload with missing agent_identity
        payload = CanonicalPayload(
            action_type="read",
            agent_identity="",  # Empty field
            resource="/path/to/file",
            access_level="read",
            audit_context={}
        )
        result = self.protocol_layer.validate_payload(payload)
        self.assertFalse(result)
    
    def test_validate_none_field(self):
        """Test validation fails with None field."""
        payload = CanonicalPayload(
            action_type="read",
            agent_identity="agent-001",
            resource="/path/to/file",
            access_level="read",
            audit_context=None  # None field
        )
        result = self.protocol_layer.validate_payload(payload)
        self.assertFalse(result)


# ============================================================================
# Unit Tests - Audit Logger
# ============================================================================

class TestAuditLogger(unittest.TestCase):
    """Test AuditLogger component."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.audit_logger = AuditLogger(self.temp_dir, "AuditTest")
    
    def tearDown(self):
        """Clean up test fixtures."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_log_decision(self):
        """Test logging a governance decision."""
        decision = GovernanceDecision(
            decision="allow",
            policy_id="test_policy",
            rationale="Test rationale",
            context={"test": "data"}
        )
        self.audit_logger.log_decision(decision)
        
        # Verify log file was created
        log_files = list(Path(self.temp_dir).glob("AuditTest-Log-*.jsonl"))
        self.assertEqual(len(log_files), 1)
    
    def test_secret_redaction(self):
        """Test secret redaction from logged data."""
        decision = GovernanceDecision(
            decision="allow",
            policy_id="test_policy",
            rationale="Test rationale",
            context={
                "api_key": "sk-1234567890abcdef",
                "password": "secret123",
                "normal_data": "public info"
            }
        )
        self.audit_logger.log_decision(decision)
        
        # Read log file and verify secrets are redacted
        log_file = list(Path(self.temp_dir).glob("AuditTest-Log-*.jsonl"))[0]
        with open(log_file, 'r') as f:
            log_content = f.read()
        
        self.assertNotIn("sk-1234567890abcdef", log_content)
        self.assertNotIn("secret123", log_content)
        self.assertIn("public info", log_content)
        self.assertIn("[REDACTED]", log_content)
    
    def test_hash_chain_integrity(self):
        """Test hash chain integrity for tamper evidence."""
        # Log multiple decisions
        for i in range(5):
            decision = GovernanceDecision(
                decision="allow",
                policy_id=f"policy_{i}",
                rationale=f"Rationale {i}",
                context={"index": i}
            )
            self.audit_logger.log_decision(decision)
        
        # Verify integrity
        self.assertTrue(self.audit_logger.verify_integrity())
    
    def test_tampering_detection(self):
        """Test tampering detection in audit log."""
        # Log a decision
        decision = GovernanceDecision(
            decision="allow",
            policy_id="test_policy",
            rationale="Test rationale",
            context={}
        )
        self.audit_logger.log_decision(decision)
        
        # Tamper with log file
        log_file = list(Path(self.temp_dir).glob("AuditTest-Log-*.jsonl"))[0]
        with open(log_file, 'r') as f:
            lines = f.readlines()
        
        lines[0] = json.dumps({"tampered": True}) + '\n'
        
        with open(log_file, 'w') as f:
            f.writelines(lines)
        
        # Verify tampering is detected
        self.assertFalse(self.audit_logger.verify_integrity())


# ============================================================================
# Unit Tests - Config Manager
# ============================================================================

class TestConfigManager(unittest.TestCase):
    """Test ConfigManager component."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.config_path = os.path.join(self.temp_dir, "config.json")
        self.audit_logger = AuditLogger(self.temp_dir, "ConfigTest")
        
        # Create test config
        test_config = {
            "adapters": {
                "test_adapter": {
                    "enabled": True,
                    "class": "TestAdapter"
                }
            },
            "governance": {
                "allowed_hooks": ["pre_tool_use", "post_tool_use"],
                "conflict_resolution": "deny_wins"
            }
        }
        with open(self.config_path, 'w') as f:
            json.dump(test_config, f)
    
    def tearDown(self):
        """Clean up test fixtures."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_load_config(self):
        """Test loading configuration."""
        config_manager = ConfigManager(self.config_path, self.audit_logger)
        self.assertIn("adapters", config_manager.config)
        self.assertIn("governance", config_manager.config)
    
    def test_get_adapter_config(self):
        """Test getting adapter-specific configuration."""
        config_manager = ConfigManager(self.config_path, self.audit_logger)
        adapter_config = config_manager.get_adapter_config("test_adapter")
        self.assertTrue(adapter_config.get("enabled"))
        self.assertEqual(adapter_config.get("class"), "TestAdapter")
    
    def test_get_governance_config(self):
        """Test getting governance configuration."""
        config_manager = ConfigManager(self.config_path, self.audit_logger)
        governance_config = config_manager.get_governance_config()
        self.assertIn("allowed_hooks", governance_config)
        self.assertEqual(governance_config.get("conflict_resolution"), "deny_wins")
    
    def test_config_integrity_verification(self):
        """Test configuration integrity verification."""
        config_manager = ConfigManager(self.config_path, self.audit_logger)
        original_hash = config_manager.config_hash
        
        # Tamper with config
        with open(self.config_path, 'a') as f:
            f.write('{"malicious": "config"}')
        
        # Should raise error on reload
        with self.assertRaises(ValueError):
            ConfigManager(self.config_path, self.audit_logger)
    
    def test_secret_redaction_in_config(self):
        """Test secret redaction from in-memory config."""
        test_config = {
            "api_key": "sk-secret-key",
            "password": "secret123",
            "normal_data": "public"
        }
        with open(self.config_path, 'w') as f:
            json.dump(test_config, f)
        
        config_manager = ConfigManager(self.config_path, self.audit_logger)
        
        # Secrets should be redacted in memory
        self.assertNotIn("sk-secret-key", str(config_manager.config))
        self.assertNotIn("secret123", str(config_manager.config))
        self.assertIn("[REDACTED]", str(config_manager.config))


# ============================================================================
# Unit Tests - Hook Registry
# ============================================================================

class TestHookRegistry(unittest.TestCase):
    """Test HookRegistry component."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.audit_logger = AuditLogger(self.temp_dir, "HookTest")
        self.config = {
            "governance": {
                "allowed_hooks": ["pre_tool_use", "post_tool_use"]
            }
        }
        self.hook_registry = HookRegistry(self.config, self.audit_logger)
    
    def tearDown(self):
        """Clean up test fixtures."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_register_hook(self):
        """Test registering a hook."""
        def test_hook(event):
            return HookResult(decision="allow", reason="Test passed")
        
        self.hook_registry.register_hook("pre_tool_use", test_hook, priority=100)
        self.assertIn("pre_tool_use", self.hook_registry.hooks)
        self.assertEqual(len(self.hook_registry.hooks["pre_tool_use"]), 1)
    
    def test_register_hook_not_allowed(self):
        """Test registering non-allowed hook type raises error."""
        def test_hook(event):
            return HookResult(decision="allow", reason="Test passed")
        
        with self.assertRaises(ValueError):
            self.hook_registry.register_hook("invalid_hook", test_hook)
    
    def test_execute_hook_allow(self):
        """Test executing hook that returns allow."""
        def test_hook(event):
            return HookResult(decision="allow", reason="Test passed")
        
        self.hook_registry.register_hook("pre_tool_use", test_hook)
        result = self.hook_registry.execute_hook("pre_tool_use", {"test": "data"})
        self.assertEqual(result.decision, "allow")
    
    def test_execute_hook_deny(self):
        """Test executing hook that returns deny."""
        def test_hook(event):
            return HookResult(decision="deny", reason="Test failed")
        
        self.hook_registry.register_hook("pre_tool_use", test_hook)
        result = self.hook_registry.execute_hook("pre_tool_use", {"test": "data"})
        self.assertEqual(result.decision, "deny")
    
    def test_execute_hook_error_fail_closed(self):
        """Test hook error results in deny (fail-closed)."""
        def error_hook(event):
            raise Exception("Hook error")
        
        self.hook_registry.register_hook("pre_tool_use", error_hook)
        result = self.hook_registry.execute_hook("pre_tool_use", {"test": "data"})
        self.assertEqual(result.decision, "deny")
    
    def test_hook_priority_ordering(self):
        """Test hooks execute in priority order."""
        execution_order = []
        
        def hook1(event):
            execution_order.append("hook1")
            return HookResult(decision="allow", reason="Hook1")
        
        def hook2(event):
            execution_order.append("hook2")
            return HookResult(decision="allow", reason="Hook2")
        
        self.hook_registry.register_hook("pre_tool_use", hook1, priority=200)
        self.hook_registry.register_hook("pre_tool_use", hook2, priority=100)
        
        self.hook_registry.execute_hook("pre_tool_use", {})
        
        # Lower priority should execute first
        self.assertEqual(execution_order, ["hook2", "hook1"])


# ============================================================================
# Unit Tests - Policy Coordinator
# ============================================================================

class TestPolicyCoordinator(unittest.TestCase):
    """Test PolicyCoordinator component."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.audit_logger = AuditLogger(self.temp_dir, "PolicyTest")
        self.config = {
            "governance": {
                "conflict_resolution": "deny_wins"
            }
        }
        self.policy_coordinator = PolicyCoordinator(self.config, self.audit_logger)
    
    def tearDown(self):
        """Clean up test fixtures."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_evaluate_default_deny(self):
        """Test default deny when no policies match."""
        decision = self.policy_coordinator.evaluate({"test": "data"})
        self.assertEqual(decision.decision, "deny")
        self.assertEqual(decision.policy_id, "default")
    
    def test_evaluate_deterministic(self):
        """Test evaluation is deterministic (same inputs → same outputs)."""
        context = {"test": "data"}
        decision1 = self.policy_coordinator.evaluate(context)
        decision2 = self.policy_coordinator.evaluate(context)
        
        # Should produce same decision
        self.assertEqual(decision1.decision, decision2.decision)
        self.assertEqual(decision1.policy_id, decision2.policy_id)


# ============================================================================
# Unit Tests - Emergency Controls
# ============================================================================

class TestEmergencyControls(unittest.TestCase):
    """Test EmergencyControls component."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.audit_logger = AuditLogger(self.temp_dir, "EmergencyTest")
        self.emergency_controls = EmergencyControls(self.audit_logger)
    
    def tearDown(self):
        """Clean up test fixtures."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_emergency_halt(self):
        """Test emergency halt activation."""
        self.assertFalse(self.emergency_controls.is_halted())
        
        self.emergency_controls.emergency_halt(scope="global", reason="Test halt")
        
        self.assertTrue(self.emergency_controls.is_halted())
        self.assertEqual(self.emergency_controls.halt_reason, "Test halt")
    
    def test_resume_after_halt(self):
        """Test resuming after emergency halt."""
        self.emergency_controls.emergency_halt(scope="global", reason="Test halt")
        self.assertTrue(self.emergency_controls.is_halted())
        
        self.emergency_controls.resume(authorized_by="admin", reason="Test resume")
        
        self.assertFalse(self.emergency_controls.is_halted())


# ============================================================================
# Unit Tests - Overseer Main Class
# ============================================================================

class TestOverseer(unittest.TestCase):
    """Test Overseer main class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.config_path = os.path.join(self.temp_dir, "config.json")
        
        # Create test config
        test_config = {
            "adapters": {},
            "governance": {
                "allowed_hooks": ["pre_tool_use", "post_tool_use"],
                "conflict_resolution": "deny_wins"
            }
        }
        with open(self.config_path, 'w') as f:
            json.dump(test_config, f)
        
        self.overseer = Overseer(self.config_path)
    
    def tearDown(self):
        """Clean up test fixtures."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_overseer_initialization(self):
        """Test overseer initialization."""
        self.assertIsNotNone(self.overseer.audit_logger)
        self.assertIsNotNone(self.overseer.config_manager)
        self.assertIsNotNone(self.overseer.protocol_layer)
        self.assertIsNotNone(self.overseer.hook_registry)
        self.assertIsNotNone(self.overseer.policy_coordinator)
        self.assertIsNotNone(self.overseer.emergency_controls)
    
    def test_evaluate_policies_valid_payload(self):
        """Test policy evaluation with valid payload."""
        payload = CanonicalPayload(
            action_type="read",
            agent_identity="agent-001",
            resource="/path/to/file",
            access_level="read",
            audit_context={}
        )
        decision = self.overseer.evaluate_policies(payload)
        self.assertIn(decision.decision, ["allow", "deny"])
    
    def test_evaluate_policies_invalid_payload(self):
        """Test policy evaluation with invalid payload."""
        payload = CanonicalPayload(
            action_type="read",
            agent_identity="",  # Invalid: empty
            resource="/path/to/file",
            access_level="read",
            audit_context={}
        )
        decision = self.overseer.evaluate_policies(payload)
        self.assertEqual(decision.decision, "deny")
        self.assertEqual(decision.policy_id, "validation")
    
    def test_evaluate_policies_emergency_halt(self):
        """Test policy evaluation blocked by emergency halt."""
        self.overseer.emergency_halt(scope="global", reason="Test halt")
        
        payload = CanonicalPayload(
            action_type="read",
            agent_identity="agent-001",
            resource="/path/to/file",
            access_level="read",
            audit_context={}
        )
        decision = self.overseer.evaluate_policies(payload)
        self.assertEqual(decision.decision, "deny")
        self.assertEqual(decision.policy_id, "emergency_halt")
    
    def test_register_hook(self):
        """Test registering hook with overseer."""
        def test_hook(event):
            return HookResult(decision="allow", reason="Test passed")
        
        self.overseer.register_hook("pre_tool_use", test_hook, priority=100)
        self.assertIn("pre_tool_use", self.overseer.hook_registry.hooks)
    
    def test_execute_hook_emergency_halt(self):
        """Test hook execution blocked by emergency halt."""
        self.overseer.emergency_halt(scope="global", reason="Test halt")
        
        result = self.overseer.execute_hook("pre_tool_use", {"test": "data"})
        self.assertEqual(result, "deny")


# ============================================================================
# Integration Tests
# ============================================================================

class TestOverseerIntegration(unittest.TestCase):
    """Integration tests for end-to-end governance pipeline."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.config_path = os.path.join(self.temp_dir, "config.json")
        
        # Create test config
        test_config = {
            "adapters": {},
            "governance": {
                "allowed_hooks": ["pre_tool_use", "post_tool_use"],
                "conflict_resolution": "deny_wins",
                "timeouts": {
                    "pre_tool_use": 10.0,
                    "post_tool_use": 10.0
                }
            }
        }
        with open(self.config_path, 'w') as f:
            json.dump(test_config, f)
        
        self.overseer = Overseer(self.config_path)
    
    def tearDown(self):
        """Clean up test fixtures."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_end_to_end_policy_enforcement(self):
        """Test complete policy enforcement pipeline."""
        # Register a hook
        def test_hook(event):
            return HookResult(decision="allow", reason="Hook passed")
        
        self.overseer.register_hook("pre_tool_use", test_hook)
        
        # Create payload
        payload = CanonicalPayload(
            action_type="read",
            agent_identity="agent-001",
            resource="/path/to/file",
            access_level="read",
            audit_context={}
        )
        
        # Evaluate policies
        decision = self.overseer.evaluate_policies(payload)
        
        # Verify decision structure
        self.assertIn(decision.decision, ["allow", "deny"])
        self.assertIsNotNone(decision.policy_id)
        self.assertIsNotNone(decision.rationale)
        self.assertIsNotNone(decision.timestamp)
    
    def test_hook_chain_execution(self):
        """Test hook chain execution with multiple hooks."""
        execution_order = []
        
        def hook1(event):
            execution_order.append("hook1")
            return HookResult(decision="allow", reason="Hook1")
        
        def hook2(event):
            execution_order.append("hook2")
            return HookResult(decision="allow", reason="Hook2")
        
        def hook3(event):
            execution_order.append("hook3")
            return HookResult(decision="deny", reason="Hook3")
        
        self.overseer.register_hook("pre_tool_use", hook1, priority=100)
        self.overseer.register_hook("pre_tool_use", hook2, priority=50)
        self.overseer.register_hook("pre_tool_use", hook3, priority=150)
        
        result = self.overseer.execute_hook("pre_tool_use", {})
        
        # Should execute in priority order
        self.assertEqual(execution_order, ["hook2", "hook1", "hook3"])


# ============================================================================
# Security Tests
# ============================================================================

class TestOverseerSecurity(unittest.TestCase):
    """Security tests for overseer.py."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.config_path = os.path.join(self.temp_dir, "config.json")
        
        # Create test config
        test_config = {
            "adapters": {},
            "governance": {
                "allowed_hooks": ["pre_tool_use"],
                "conflict_resolution": "deny_wins"
            }
        }
        with open(self.config_path, 'w') as f:
            json.dump(test_config, f)
        
        self.overseer = Overseer(self.config_path)
    
    def tearDown(self):
        """Clean up test fixtures."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_secret_redaction_in_logs(self):
        """Test secrets are redacted from logs."""
        payload = CanonicalPayload(
            action_type="read",
            agent_identity="agent-001",
            resource="/path/to/file",
            access_level="read",
            audit_context={
                "api_key": "sk-1234567890abcdef",
                "password": "secret123"
            }
        )
        
        decision = self.overseer.evaluate_policies(payload)
        
        # Verify secrets not in log file
        log_files = list(Path(self.temp_dir).glob("Overseer/Logs/Overseer-Log-*.jsonl"))
        if log_files:
            with open(log_files[0], 'r') as f:
                log_content = f.read()
            
            self.assertNotIn("sk-1234567890abcdef", log_content)
            self.assertNotIn("secret123", log_content)
    
    def test_input_validation(self):
        """Test input validation for malicious payloads."""
        # Test with empty required field
        payload = CanonicalPayload(
            action_type="read",
            agent_identity="",  # Invalid
            resource="/path/to/file",
            access_level="read",
            audit_context={}
        )
        
        decision = self.overseer.evaluate_policies(payload)
        self.assertEqual(decision.decision, "deny")
    
    def test_hook_registration_not_allowed(self):
        """Test non-allowed hook type cannot be registered."""
        def test_hook(event):
            return HookResult(decision="allow", reason="Test")
        
        with self.assertRaises(ValueError):
            self.overseer.register_hook("malicious_hook", test_hook)


# ============================================================================
# Performance Tests
# ============================================================================

class TestOverseerPerformance(unittest.TestCase):
    """Performance tests for overseer.py."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.config_path = os.path.join(self.temp_dir, "config.json")
        
        # Create test config
        test_config = {
            "adapters": {},
            "governance": {
                "allowed_hooks": ["pre_tool_use"],
                "conflict_resolution": "deny_wins",
                "timeouts": {
                    "pre_tool_use": 10.0
                }
            }
        }
        with open(self.config_path, 'w') as f:
            json.dump(test_config, f)
        
        self.overseer = Overseer(self.config_path)
    
    def tearDown(self):
        """Clean up test fixtures."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_hook_execution_latency(self):
        """Test hook execution latency (< 100ms target)."""
        def test_hook(event):
            return HookResult(decision="allow", reason="Test")
        
        self.overseer.register_hook("pre_tool_use", test_hook)
        
        start_time = time.time()
        for _ in range(100):
            self.overseer.execute_hook("pre_tool_use", {})
        elapsed_time = time.time() - start_time
        
        # Average should be < 100ms
        avg_time = (elapsed_time / 100) * 1000
        self.assertLess(avg_time, 100, f"Average hook execution time: {avg_time}ms")
    
    def test_policy_evaluation_latency(self):
        """Test policy evaluation latency (< 500ms target)."""
        payload = CanonicalPayload(
            action_type="read",
            agent_identity="agent-001",
            resource="/path/to/file",
            access_level="read",
            audit_context={}
        )
        
        start_time = time.time()
        for _ in range(100):
            self.overseer.evaluate_policies(payload)
        elapsed_time = time.time() - start_time
        
        # Average should be < 500ms
        avg_time = (elapsed_time / 100) * 1000
        self.assertLess(avg_time, 500, f"Average policy evaluation time: {avg_time}ms")


# ============================================================================
# Test Runner
# ============================================================================

if __name__ == "__main__":
    unittest.main(verbosity=2)

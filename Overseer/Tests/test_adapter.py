"""
Unit tests for Adapter Layer

Test coverage for BaseAdapter and Devin-Adapter following TDD principles.
"""

import unittest
import sys
from pathlib import Path
from tempfile import TemporaryDirectory
from json import loads

# Add paths for imports
sys.path.append(str(Path(__file__).parent.parent / "Adapter"))
sys.path.append(str(Path(__file__).parent.parent / "Core"))

from base import BaseAdapter, AdapterCapabilities
from devin_adapter import DevinAdapter
from overseer import CanonicalPayload, HookResult


class MockAdapter(BaseAdapter):
    """Mock adapter for testing BaseAdapter abstract methods."""
    
    def transform_event(self, event):
        return CanonicalPayload(
            action_type="test_action",
            agent_identity="test_agent",
            resource="test_resource",
            access_level="low",
            audit_context={"test": True}
        )
    
    def get_capabilities(self):
        return AdapterCapabilities(
            supported_hooks={"TestHook"},
            supported_events={"test_event"},
            input_schema={"required": ["hook_event_name"]},
            output_schema={"action_type": "string"}
        )
    
    def register_hooks(self, hook_registry):
        pass


class TestBaseAdapter(unittest.TestCase):
    """Test BaseAdapter class functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = TemporaryDirectory()
        self.config = {"test": "config"}
        self.adapter = MockAdapter(self.config, self.temp_dir.name)
    
    def tearDown(self):
        """Clean up test fixtures."""
        # Close logger handlers to release file locks
        for handler in self.adapter.logger.handlers[:]:
            handler.close()
            self.adapter.logger.removeHandler(handler)
        self.temp_dir.cleanup()
    
    def test_base_adapter_init(self):
        """Test BaseAdapter initializes with config."""
        self.assertEqual(self.adapter.config, self.config)
        self.assertIsNotNone(self.adapter.logger)
    
    def test_base_adapter_transform_event(self):
        """Test event transformation method signature."""
        event = {"hook_event_name": "TestHook"}
        payload = self.adapter.transform_event(event)
        self.assertIsInstance(payload, CanonicalPayload)
        self.assertEqual(payload.action_type, "test_action")
    
    def test_base_adapter_get_capabilities(self):
        """Test capability discovery returns expected structure."""
        capabilities = self.adapter.get_capabilities()
        self.assertIsInstance(capabilities, AdapterCapabilities)
        self.assertIn("TestHook", capabilities.supported_hooks)
        self.assertIn("test_event", capabilities.supported_events)
    
    def test_base_adapter_register_hooks(self):
        """Test hook registration method signature."""
        # Mock hook registry
        class MockRegistry:
            def __init__(self):
                self.registered = []
            
            def register_hook(self, hook_type, hook_func, priority):
                self.registered.append((hook_type, hook_func, priority))
        
        registry = MockRegistry()
        self.adapter.register_hooks(registry)
        # Mock adapter doesn't register anything, so this is just testing the method exists
        self.assertEqual(len(registry.registered), 0)
    
    def test_base_adapter_validate_event(self):
        """Test event validation."""
        # Valid event
        valid_event = {"hook_event_name": "TestHook"}
        self.assertTrue(self.adapter.validate_event(valid_event))
        
        # Invalid event (missing required field)
        invalid_event = {"other_field": "value"}
        self.assertFalse(self.adapter.validate_event(invalid_event))


class TestDevinAdapter(unittest.TestCase):
    """Test Devin-Adapter specific functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = TemporaryDirectory()
        self.config = {
            "adapter": "devin",
            "adapter_specific_settings": {
                "devin": {
                    "config": {"timeout": 10}
                }
            }
        }
        self.adapter = DevinAdapter(self.config, self.temp_dir.name)
    
    def tearDown(self):
        """Clean up test fixtures."""
        # Close logger handlers to release file locks
        for handler in self.adapter.logger.handlers[:]:
            handler.close()
            self.adapter.logger.removeHandler(handler)
        self.temp_dir.cleanup()
    
    def test_devin_adapter_init(self):
        """Test Devin-Adapter initializes with config."""
        # Check that adapter config was extracted correctly
        self.assertEqual(self.adapter.config, {"timeout": 10})
        self.assertEqual(self.adapter.adapter_name, "devin_adapter")
        self.assertEqual(self.adapter.full_config, self.config)
    
    def test_devin_adapter_transform_pretooluse(self):
        """Test PreToolUse event transforms to CanonicalPayload."""
        event = {
            "hook_event_name": "PreToolUse",
            "tool_name": "exec",
            "tool_input": {"command": "ls"},
            "session_id": "test-session",
            "prompt_id": "test-prompt"
        }
        payload = self.adapter.transform_event(event)
        self.assertIsInstance(payload, CanonicalPayload)
        self.assertEqual(payload.action_type, "tool_execution_pre")
        self.assertEqual(payload.resource, "exec")
        self.assertEqual(payload.agent_identity, "test-session")
        self.assertEqual(payload.access_level, "high")
    
    def test_devin_adapter_transform_posttooluse(self):
        """Test PostToolUse event transforms to CanonicalPayload."""
        event = {
            "hook_event_name": "PostToolUse",
            "tool_name": "edit",
            "tool_input": {"file": "test.py"},
            "tool_response": {"success": True, "output": "edited"},
            "session_id": "test-session"
        }
        payload = self.adapter.transform_event(event)
        self.assertEqual(payload.action_type, "tool_execution_post")
        self.assertEqual(payload.resource, "edit")
    
    def test_devin_adapter_transform_permissionrequest(self):
        """Test PermissionRequest event transforms."""
        event = {
            "hook_event_name": "PermissionRequest",
            "tool_name": "exec",
            "tool_input": {"command": "git status"},
            "session_id": "test-session"
        }
        payload = self.adapter.transform_event(event)
        self.assertEqual(payload.action_type, "permission_request")
    
    def test_devin_adapter_get_capabilities(self):
        """Test capabilities include PreToolUse, PostToolUse."""
        capabilities = self.adapter.get_capabilities()
        self.assertIn("PreToolUse", capabilities.supported_hooks)
        self.assertIn("PostToolUse", capabilities.supported_hooks)
        self.assertIn("PermissionRequest", capabilities.supported_hooks)
        self.assertIn("tool_execution", capabilities.supported_events)
    
    def test_devin_adapter_session_id_handling(self):
        """Test session_id and prompt_id are preserved."""
        event = {
            "hook_event_name": "PreToolUse",
            "tool_name": "exec",
            "tool_input": {"command": "ls"},
            "session_id": "session-123",
            "prompt_id": "prompt-456"
        }
        payload = self.adapter.transform_event(event)
        self.assertEqual(payload.metadata["session_id"], "session-123")
        self.assertEqual(payload.metadata["prompt_id"], "prompt-456")
    
    def test_devin_adapter_invalid_event(self):
        """Test invalid event raises ValueError."""
        event = {"tool_name": "exec"}  # Missing hook_event_name
        with self.assertRaises(ValueError):
            self.adapter.transform_event(event)
    
    def test_devin_adapter_access_level_determination(self):
        """Test access level determination based on tool type."""
        # High-risk tool
        event = {
            "hook_event_name": "PreToolUse",
            "tool_name": "exec",
            "tool_input": {"command": "rm -rf /"},
            "session_id": "test"
        }
        payload = self.adapter.transform_event(event)
        self.assertEqual(payload.access_level, "high")
        
        # MCP tool (medium risk)
        event["tool_name"] = "mcp__github__create_issue"
        payload = self.adapter.transform_event(event)
        self.assertEqual(payload.access_level, "medium")


class TestAdapterCapabilities(unittest.TestCase):
    """Test AdapterCapabilities dataclass."""
    
    def test_adapter_capabilities_creation(self):
        """Test AdapterCapabilities can be created."""
        capabilities = AdapterCapabilities(
            supported_hooks={"PreToolUse"},
            supported_events={"tool_execution"},
            input_schema={"required": ["field1"]},
            output_schema={"action_type": "string"}
        )
        self.assertEqual(capabilities.supported_hooks, {"PreToolUse"})
        self.assertEqual(capabilities.supported_events, {"tool_execution"})


if __name__ == "__main__":
    unittest.main()

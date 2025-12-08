"""
RoboKen Simulator - Comprehensive Test Suite
"""

import pytest
import asyncio
from roboken_complete_platform import (
    RoboKenSimulator, TaskType, TaskStatus, AutomationResult
)
from error_handling_validation import ErrorHandler, ErrorCategory, InputValidator
from n8n_integration import N8nWorkflowEngine


class TestRoboKenSimulator:
    """Test suite for RoboKen Simulator"""
    
    @pytest.fixture
    def simulator(self):
        """Create simulator instance for testing"""
        return RoboKenSimulator(db_path=":memory:")
    
    @pytest.mark.asyncio
    async def test_submit_task(self, simulator):
        """Test task submission"""
        task = await simulator.submit_task(
            description="Test task",
            task_type=TaskType.WEB_AUTOMATION
        )
        
        assert task.id is not None
        assert task.status == TaskStatus.PENDING
        assert task.description == "Test task"
    
    @pytest.mark.asyncio
    async def test_execute_web_automation(self, simulator):
        """Test web automation execution"""
        task = await simulator.submit_task(
            description="Open Chrome and search for AI",
            task_type=TaskType.WEB_AUTOMATION
        )
        
        result = await simulator.execute_next_task()
        
        assert result.success is True
        assert result.execution_time > 0
        assert result.output is not None
    
    @pytest.mark.asyncio
    async def test_execute_mobile_automation(self, simulator):
        """Test mobile automation execution"""
        task = await simulator.submit_task(
            description="Launch mobile app",
            task_type=TaskType.MOBILE_AUTOMATION
        )
        
        result = await simulator.execute_next_task()
        
        assert result.success is True
        assert 'mobile_interaction' in result.output['action']
    
    @pytest.mark.asyncio
    async def test_execute_workflow_automation(self, simulator):
        """Test workflow automation execution"""
        task = await simulator.submit_task(
            description="Send automated email",
            task_type=TaskType.WORKFLOW_AUTOMATION
        )
        
        result = await simulator.execute_next_task()
        
        assert result.success is True
        assert 'workflow_execution' in result.output['action']
    
    @pytest.mark.asyncio
    async def test_execute_all_tasks(self, simulator):
        """Test executing multiple tasks"""
        # Submit multiple tasks
        await simulator.submit_task("Task 1", TaskType.WEB_AUTOMATION)
        await simulator.submit_task("Task 2", TaskType.MOBILE_AUTOMATION)
        await simulator.submit_task("Task 3", TaskType.DESKTOP_AUTOMATION)
        
        results = await simulator.execute_all_tasks()
        
        assert len(results) == 3
        assert all(r.success for r in results)
    
    def test_get_statistics(self, simulator):
        """Test statistics retrieval"""
        stats = simulator.get_statistics()
        
        assert 'executor_stats' in stats
        assert 'queue_length' in stats
        assert 'timestamp' in stats


class TestErrorHandler:
    """Test suite for Error Handler"""
    
    @pytest.fixture
    def error_handler(self):
        """Create error handler instance"""
        return ErrorHandler()
    
    @pytest.mark.asyncio
    async def test_classify_network_error(self, error_handler):
        """Test network error classification"""
        error = ConnectionError("Network connection failed")
        context = await error_handler.handle_error(error)
        
        assert context.category == ErrorCategory.NETWORK
        assert context.error_id is not None
    
    @pytest.mark.asyncio
    async def test_classify_validation_error(self, error_handler):
        """Test validation error classification"""
        error = ValueError("Invalid input format")
        context = await error_handler.handle_error(error)
        
        assert context.category == ErrorCategory.VALIDATION
    
    def test_error_statistics(self, error_handler):
        """Test error statistics"""
        stats = error_handler.get_error_statistics()
        
        assert 'total_errors' in stats
        assert 'by_category' in stats
        assert 'by_severity' in stats


class TestInputValidator:
    """Test suite for Input Validator"""
    
    def test_validate_email_valid(self):
        """Test valid email validation"""
        assert InputValidator.validate_email("test@example.com") is True
    
    def test_validate_email_invalid(self):
        """Test invalid email validation"""
        assert InputValidator.validate_email("invalid-email") is False
    
    def test_validate_url_valid(self):
        """Test valid URL validation"""
        assert InputValidator.validate_url("https://example.com") is True
    
    def test_validate_url_invalid(self):
        """Test invalid URL validation"""
        assert InputValidator.validate_url("not-a-url") is False
    
    def test_validate_command_valid(self):
        """Test valid command validation"""
        valid, error = InputValidator.validate_command("Open Chrome")
        assert valid is True
        assert error is None
    
    def test_validate_command_empty(self):
        """Test empty command validation"""
        valid, error = InputValidator.validate_command("")
        assert valid is False
        assert error is not None


class TestN8nWorkflowEngine:
    """Test suite for n8n Workflow Engine"""
    
    @pytest.fixture
    def engine(self):
        """Create workflow engine instance"""
        return N8nWorkflowEngine()
    
    def test_create_workflow(self, engine):
        """Test workflow creation"""
        workflow = engine.create_workflow(
            name="Test Workflow",
            description="Test Description"
        )
        
        assert workflow.id is not None
        assert workflow.name == "Test Workflow"
        assert len(workflow.nodes) == 0
    
    def test_add_node(self, engine):
        """Test adding node to workflow"""
        workflow = engine.create_workflow("Test", "Test")
        
        node = engine.add_node(
            workflow.id,
            'gmail',
            'Send Email',
            {'to': 'test@example.com'}
        )
        
        assert node.id is not None
        assert node.type == 'gmail'
        assert len(workflow.nodes) == 1
    
    @pytest.mark.asyncio
    async def test_execute_workflow(self, engine):
        """Test workflow execution"""
        workflow = engine.create_workflow("Test", "Test")
        
        engine.add_node(
            workflow.id,
            'gmail',
            'Send Email',
            {'to': 'test@example.com', 'subject': 'Test'}
        )
        
        result = await engine.execute_workflow(workflow.id)
        
        assert result['status'] == 'completed'
        assert result['nodes_executed'] > 0
    
    def test_workflow_statistics(self, engine):
        """Test workflow statistics"""
        stats = engine.get_statistics()
        
        assert 'total_workflows' in stats
        assert 'available_integrations' in stats


# Run tests
if __name__ == "__main__":
    pytest.main([__file__, "-v", "--asyncio-mode=auto"])

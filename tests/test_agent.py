"""
Tests for the cAIdence agent module.
"""

import pytest
from unittest.mock import Mock, patch
from caidence.agent import CaidenceAgent, ExecutionPlan, PlanStep


class TestCaidenceAgent:
    """Test cases for the CaidenceAgent class."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.agent = CaidenceAgent()
    
    def test_agent_initialization(self):
        """Test that the agent initializes correctly."""
        assert self.agent is not None
        assert self.agent.config == {}
        assert self.agent.tools == {}
    
    def test_understand_query(self):
        """Test query understanding functionality."""
        query = "Find all surgical notes mentioning arterial graft"
        result = self.agent.understand_query(query)
        
        assert isinstance(result, dict)
        assert "intent" in result
        assert "entities" in result
        assert result["intent"] == "search_documents"
    
    def test_create_plan(self):
        """Test execution plan creation."""
        query = "Find surgical notes with arterial graft but no infection"
        plan = self.agent.create_plan(query)
        
        assert isinstance(plan, ExecutionPlan)
        assert plan.query == query
        assert len(plan.steps) > 0
        assert plan.confidence > 0
        assert plan.estimated_duration > 0
    
    def test_plan_includes_negation_step(self):
        """Test that plans include negation detection when needed."""
        query = "Find notes mentioning bypass but not infection"
        plan = self.agent.create_plan(query)
        
        # Check if negation step is included
        negation_steps = [
            step for step in plan.steps 
            if step["type"] == PlanStep.CHECK_NEGATION.value
        ]
        assert len(negation_steps) > 0
    
    def test_analyze_method(self):
        """Test the main analyze method."""
        query = "Find surgical notes"
        result = self.agent.analyze(query)
        
        assert result.query == query
        assert result.documents_processed >= 0
        assert isinstance(result.entities_found, list)
        assert isinstance(result.summary, str)
        assert result.execution_time >= 0
        assert 0 <= result.confidence <= 1
    
    @patch('caidence.agent.logger')
    def test_logging_during_analysis(self, mock_logger):
        """Test that appropriate logging occurs during analysis."""
        query = "Test query"
        self.agent.analyze(query)
        
        # Verify logging calls were made
        mock_logger.info.assert_called()


class TestExecutionPlan:
    """Test cases for the ExecutionPlan class."""
    
    def test_execution_plan_creation(self):
        """Test creating an execution plan."""
        plan = ExecutionPlan(
            query="test query",
            steps=[],
            estimated_duration=30,
            confidence=0.85
        )
        
        assert plan.query == "test query"
        assert plan.steps == []
        assert plan.estimated_duration == 30
        assert plan.confidence == 0.85
    
    def test_add_step(self):
        """Test adding steps to execution plan."""
        plan = ExecutionPlan(
            query="test",
            steps=[],
            estimated_duration=30,
            confidence=0.85
        )
        
        plan.add_step(
            PlanStep.EXTRACT_ENTITIES,
            "Extract medical entities",
            "ctakes_processor",
            {"entities": ["medication", "procedure"]}
        )
        
        assert len(plan.steps) == 1
        step = plan.steps[0]
        assert step["type"] == "extract_entities"
        assert step["description"] == "Extract medical entities"
        assert step["tool"] == "ctakes_processor"
        assert "entities" in step["parameters"]


class TestIntegration:
    """Integration tests for the agent system."""
    
    @pytest.mark.integration
    def test_full_analysis_workflow(self):
        """Test the complete analysis workflow."""
        agent = CaidenceAgent()
        query = "Find discharge summaries mentioning diabetes treatment"
        
        # This would require actual tools to be available
        # For now, just test that the workflow doesn't crash
        result = agent.analyze(query)
        
        assert result is not None
        assert isinstance(result.summary, str)
    
    @pytest.mark.slow
    def test_large_query_processing(self):
        """Test processing of complex queries."""
        agent = CaidenceAgent()
        complex_query = (
            "Find all cardiology consultation notes from the past 6 months "
            "that mention coronary artery disease, myocardial infarction, "
            "or cardiac catheterization, but exclude notes mentioning "
            "previous heart surgery or transplant"
        )
        
        plan = agent.create_plan(complex_query)
        
        # Verify complex query generates appropriate plan
        assert len(plan.steps) >= 4  # Should have multiple processing steps
        assert plan.estimated_duration > 10  # Complex queries take longer


if __name__ == "__main__":
    pytest.main([__file__])

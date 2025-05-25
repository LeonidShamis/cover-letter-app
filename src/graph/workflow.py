from langgraph.graph import StateGraph, END
from src.graph.state import GraphState, JobDetails, ResumeDetails, CompanyInfo, CoverLetterPlan, CoverLetterContent, QAFeedback
from src.agents.job_ad_analyser import JobAdAnalyser
from src.agents.resume_analyser import ResumeAnalyser
from src.agents.company_researcher import CompanyResearcher
from src.agents.planner import Planner
from src.agents.cover_letter_writer import CoverLetterWriter
from src.agents.qa_expert import QAExpert
from src.agents.supervisor import Supervisor
import asyncio

class CoverLetterWorkflow:
    def __init__(self):
        self.job_analyser = JobAdAnalyser()
        self.resume_analyser = ResumeAnalyser()
        self.company_researcher = CompanyResearcher()
        self.planner = Planner()
        self.cover_letter_writer = CoverLetterWriter()
        self.qa_expert = QAExpert()
        self.supervisor = Supervisor()
        
        self.workflow = self._build_workflow()
    
    def _build_workflow(self) -> StateGraph:
        """Build the LangGraph workflow"""
        workflow = StateGraph(GraphState)
        
        # Add nodes
        workflow.add_node("job_ad_analyser", self._job_ad_analyser_node)
        workflow.add_node("resume_analyser", self._resume_analyser_node)
        workflow.add_node("company_researcher", self._company_researcher_node)
        workflow.add_node("planner", self._planner_node)
        workflow.add_node("cover_letter_writer", self._cover_letter_writer_node)
        workflow.add_node("qa_expert", self._qa_expert_node)
        workflow.add_node("supervisor", self._supervisor_node)
        
        # Define the workflow flow
        workflow.set_entry_point("job_ad_analyser")
        
        # Add conditional edges based on supervisor decisions
        workflow.add_conditional_edges(
            "job_ad_analyser",
            lambda x: x["next_agent"],
            {
                "resume_analyser": "resume_analyser",
                "FINISH": END
            }
        )
        
        workflow.add_conditional_edges(
            "resume_analyser",
            lambda x: x["next_agent"],
            {
                "company_researcher": "company_researcher",
                "FINISH": END
            }
        )
        
        workflow.add_conditional_edges(
            "company_researcher",
            lambda x: x["next_agent"],
            {
                "planner": "planner",
                "FINISH": END
            }
        )
        
        workflow.add_conditional_edges(
            "planner",
            lambda x: x["next_agent"],
            {
                "cover_letter_writer": "cover_letter_writer",
                "FINISH": END
            }
        )
        
        workflow.add_conditional_edges(
            "cover_letter_writer",
            lambda x: x["next_agent"],
            {
                "qa_expert": "qa_expert",
                "FINISH": END
            }
        )
        
        workflow.add_conditional_edges(
            "qa_expert",
            lambda x: x["next_agent"],
            {
                "cover_letter_writer": "cover_letter_writer",
                "supervisor": "supervisor",
                "FINISH": END
            }
        )
        
        workflow.add_conditional_edges(
            "supervisor",
            lambda x: x["next_agent"],
            {
                "cover_letter_writer": "cover_letter_writer",
                "qa_expert": "qa_expert",
                "FINISH": END
            }
        )
        
        return workflow.compile()
    
    # Node wrapper functions
    def _job_ad_analyser_node(self, state: GraphState) -> GraphState:
        return asyncio.run(self.job_analyser.analyze_job_ad(state))
    
    def _resume_analyser_node(self, state: GraphState) -> GraphState:
        return self.resume_analyser.analyze_resume(state)
    
    def _company_researcher_node(self, state: GraphState) -> GraphState:
        return asyncio.run(self.company_researcher.research_company(state))
    
    def _planner_node(self, state: GraphState) -> GraphState:
        return self.planner.create_plan(state)
    
    def _cover_letter_writer_node(self, state: GraphState) -> GraphState:
        return self.cover_letter_writer.write_cover_letter(state)
    
    def _qa_expert_node(self, state: GraphState) -> GraphState:
        return self.qa_expert.assess_cover_letter(state)
    
    def _supervisor_node(self, state: GraphState) -> GraphState:
        next_agent = self.supervisor.route_next_agent(state)
        state["next_agent"] = next_agent
        return state
    
    def run(self, initial_state: GraphState) -> GraphState:
        """Run the complete workflow"""
        result = self.workflow.invoke(initial_state)
        return result

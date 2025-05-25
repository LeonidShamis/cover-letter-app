from langchain_openai import ChatOpenAI
from langchain.schema import HumanMessage
from src.graph.state import GraphState

class Supervisor:
    def __init__(self):
        self.llm = ChatOpenAI(model="gpt-4o-mini-2024-07-18", temperature=0)
    
    def route_next_agent(self, state: GraphState) -> str:
        """Determine which agent should run next"""
        
        # Check current progress and decide routing
        routing_prompt = f"""
        Based on the current state of the cover letter generation process, determine the next agent to run.
        
        Current iteration: {state["iteration_count"]}
        Last agent: {state.get("next_agent", "start")}
        QA approved: {state["qa_feedback"].approved if state["qa_feedback"] else False}
        QA score: {state["qa_feedback"].score if state["qa_feedback"] else 0}
        
        Available agents:
        - job_ad_analyser: Analyze job advertisement
        - resume_analyser: Analyze resume content
        - company_researcher: Research company information  
        - planner: Create cover letter plan
        - cover_letter_writer: Write the cover letter
        - qa_expert: Assess cover letter quality
        - FINISH: Complete the process
        
        Messages so far: {', '.join(state["messages"])}
        
        Return only the agent name to run next.
        """
        
        response = self.llm.invoke([HumanMessage(content=routing_prompt)])
        next_agent = response.content.strip()
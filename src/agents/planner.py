from langchain_openai import ChatOpenAI
from langchain.schema import HumanMessage
from src.graph.state import GraphState, CoverLetterPlan

class Planner:
    def __init__(self):
        self.llm = ChatOpenAI(model="gpt-4o-mini-2024-07-18", temperature=0)
    
    def create_plan(self, state: GraphState) -> GraphState:
        """Create a plan for the cover letter content"""
        
        planning_prompt = f"""
        Create a detailed plan for a cover letter based on the following information:
        
        JOB REQUIREMENTS:
        {', '.join(state["job_details"].key_requirements)}
        
        JOB SKILLS:
        {', '.join(state["job_details"].key_skills)}
        
        RESUME EXPERIENCES:
        {', '.join(state["resume_details"].key_experiences)}
        
        RESUME ACHIEVEMENTS:
        {', '.join(state["resume_details"].key_achievements)}
        
        RESUME SKILLS:
        {', '.join(state["resume_details"].key_skills)}
        
        COMPANY INFO:
        Profile: {state["company_info"].profile}
        Culture: {state["company_info"].culture}
        Values: {', '.join(state["company_info"].values)}
        
        Create a plan with:
        1. Cover letter structure (paragraphs and their purposes)
        2. Key points to emphasize
        3. Specific matching between resume experiences and job requirements
        
        Format as:
        STRUCTURE:
        - [paragraph 1 purpose]
        - [paragraph 2 purpose]
        
        KEY_POINTS:
        - [key point 1]
        - [key point 2]
        
        EXPERIENCE_MATCHES:
        [job requirement] -> [matching resume experience]
        """
        
        response = self.llm.invoke([HumanMessage(content=planning_prompt)])
        
        # Parse response
        content = response.content
        structure = []
        key_points = []
        matching_experiences = {}
        
        current_section = None
        for line in content.split('\n'):
            line = line.strip()
            if line.startswith('STRUCTURE:'):
                current_section = 'structure'
            elif line.startswith('KEY_POINTS:'):
                current_section = 'key_points'
            elif line.startswith('EXPERIENCE_MATCHES:'):
                current_section = 'matches'
            elif line.startswith('- '):
                item = line[2:]
                if current_section == 'structure':
                    structure.append(item)
                elif current_section == 'key_points':
                    key_points.append(item)
            elif ' -> ' in line and current_section == 'matches':
                req, exp = line.split(' -> ', 1)
                matching_experiences[req.strip()] = exp.strip()
        
        # Update state
        state["plan"] = CoverLetterPlan(
            structure=structure,
            key_points=key_points,
            matching_experiences=matching_experiences
        )
        
        state["messages"].append("Cover letter plan created")
        state["next_agent"] = "cover_letter_writer"
        
        return state

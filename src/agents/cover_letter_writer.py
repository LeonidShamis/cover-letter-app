from langchain_openai import ChatOpenAI
from langchain.schema import HumanMessage
from src.graph.state import GraphState, CoverLetterContent
import os

class CoverLetterWriter:
    def __init__(self):
        self.llm = ChatOpenAI(model="gpt-4o-mini-2024-07-18", temperature=0.3)
    
    def write_cover_letter(self, state: GraphState) -> GraphState:
        """Write the cover letter based on the plan"""
        
        # Load SEEK instructions
        instructions = self._load_seek_instructions()
        
        writing_prompt = f"""
        Write a compelling cover letter based on the following plan and information:
        
        COVER LETTER WRITING INSTRUCTIONS:
        {instructions}
        
        STYLE: {state["cover_letter"].style}
        
        STRUCTURE PLAN:
        {', '.join(state["plan"].structure)}
        
        KEY POINTS TO INCLUDE:
        {', '.join(state["plan"].key_points)}
        
        EXPERIENCE MATCHES:
        {self._format_experience_matches(state["plan"].matching_experiences)}
        
        JOB DETAILS:
        Company: {state["company_info"].name}
        Requirements: {', '.join(state["job_details"].key_requirements)}
        
        COMPANY INFO:
        Profile: {state["company_info"].profile}
        Culture: {state["company_info"].culture}
        
        Write a complete cover letter that:
        1. Follows the SEEK guidelines
        2. Matches the specified style
        3. Clearly connects resume experiences to job requirements
        4. Shows understanding of the company
        5. Is engaging and professional
        """
        
        response = self.llm.invoke([HumanMessage(content=writing_prompt)])
        
        # Update state
        state["cover_letter"] = CoverLetterContent(
            content=response.content,
            style=state["cover_letter"].style,
            instructions=instructions
        )
        
        state["messages"].append("Cover letter written")
        state["next_agent"] = "qa_expert"
        
        return state
    
    def _load_seek_instructions(self) -> str:
        """Load SEEK cover letter instructions"""
        try:
            with open("data/SEEK_cover_letter_instructions.md", "r") as f:
                return f.read()
        except FileNotFoundError:
            return """
            SEEK Cover Letter Guidelines:
            1. Keep it concise (1 page maximum)
            2. Address the hiring manager by name if possible
            3. Show enthusiasm for the role and company
            4. Highlight relevant experience and achievements
            5. Explain why you're the right fit
            6. Include a strong closing statement
            7. Proofread carefully
            """
    
    def _format_experience_matches(self, matches: dict) -> str:
        """Format experience matches for the prompt"""
        formatted = []
        for req, exp in matches.items():
            formatted.append(f"- {req}: {exp}")
        return '\n'.join(formatted)

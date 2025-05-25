from langchain_openai import ChatOpenAI
from langchain.schema import HumanMessage
from src.graph.state import GraphState, QAFeedback

class QAExpert:
    def __init__(self):
        self.llm = ChatOpenAI(model="gpt-4o-mini-2024-07-18", temperature=0)
    
    def assess_cover_letter(self, state: GraphState) -> GraphState:
        """Assess the quality of the cover letter"""
        
        assessment_prompt = f"""
        Assess the following cover letter based on how well it:
        1. Links resume experiences to job requirements
        2. Demonstrates understanding of the company
        3. Follows professional writing standards
        4. Shows enthusiasm and personality
        5. Addresses all key job requirements
        
        JOB REQUIREMENTS:
        {', '.join(state["job_details"].key_requirements)}
        
        RESUME EXPERIENCES:
        {', '.join(state["resume_details"].key_experiences)}
        
        COVER LETTER:
        {state["cover_letter"].content}
        
        Provide:
        1. A score out of 10
        2. Specific feedback on strengths and weaknesses
        3. Suggestions for improvement
        4. Whether to approve (score 8+) or request revision
        
        Format as:
        SCORE: [number]
        FEEDBACK: [detailed feedback]
        SUGGESTIONS:
        - [suggestion 1]
        - [suggestion 2]
        APPROVED: [YES/NO]
        """
        
        response = self.llm.invoke([HumanMessage(content=assessment_prompt)])
        
        # Parse response
        content = response.content
        score = 0
        feedback = ""
        suggestions = []
        approved = False
        
        current_section = None
        for line in content.split('\n'):
            line = line.strip()
            if line.startswith('SCORE:'):
                score = int(line.split(':')[1].strip())
            elif line.startswith('FEEDBACK:'):
                current_section = 'feedback'
                feedback = line.split(':', 1)[1].strip()
            elif line.startswith('SUGGESTIONS:'):
                current_section = 'suggestions'
            elif line.startswith('APPROVED:'):
                approved = 'YES' in line.upper()
            elif line.startswith('- ') and current_section == 'suggestions':
                suggestions.append(line[2:])
            elif current_section == 'feedback' and line:
                feedback += " " + line
        
        # Update state
        state["qa_feedback"] = QAFeedback(
            score=score,
            feedback=feedback.strip(),
            suggestions=suggestions,
            approved=approved
        )
        
        state["messages"].append(f"QA assessment completed - Score: {score}/10")
        
        if approved or state["iteration_count"] >= 3:
            state["next_agent"] = "FINISH"
        else:
            state["next_agent"] = "cover_letter_writer"
            state["iteration_count"] += 1
        
        return state

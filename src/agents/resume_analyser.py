from langchain_openai import ChatOpenAI
from langchain.schema import HumanMessage
from src.graph.state import GraphState, ResumeDetails
from src.utils.vector_store import VectorStore

class ResumeAnalyser:
    def __init__(self):
        self.llm = ChatOpenAI(model="gpt-4o-mini-2024-07-18", temperature=0)
        self.vector_store = VectorStore()
    
    def analyze_resume(self, state: GraphState) -> GraphState:
        """Analyze resume content and store in vector database"""
        resume_content = state["resume_details"].content
        
        # Store resume in vector database
        self.vector_store.add_documents(resume_content)
        
        # Get job requirements for targeted analysis
        job_requirements = state["job_details"].key_requirements
        job_skills = state["job_details"].key_skills
        
        # Search for relevant experiences
        relevant_experiences = []
        for req in job_requirements[:3]:  # Top 3 requirements
            similar_content = self.vector_store.similarity_search(req, k=2)
            relevant_experiences.extend(similar_content)
        
        # Analyze resume for key information
        analysis_prompt = f"""
        Analyze the following resume content and extract:
        1. Key experiences relevant to the job requirements
        2. Key achievements with quantifiable results
        3. Key skills that match the job requirements
        
        Job Requirements: {', '.join(job_requirements)}
        Job Skills Needed: {', '.join(job_skills)}
        
        Resume Content:
        {resume_content}
        
        Relevant Context from Vector Search:
        {' '.join(relevant_experiences)}
        
        Format your response as:
        EXPERIENCES:
        - [experience 1 with specific details]
        - [experience 2 with specific details]
        
        ACHIEVEMENTS:
        - [achievement 1 with metrics]
        - [achievement 2 with metrics]
        
        SKILLS:
        - [skill 1]
        - [skill 2]
        """
        
        response = self.llm.invoke([HumanMessage(content=analysis_prompt)])
        
        # Parse response
        content = response.content
        experiences = []
        achievements = []
        skills = []
        
        current_section = None
        for line in content.split('\n'):
            line = line.strip()
            if line.startswith('EXPERIENCES:'):
                current_section = 'experiences'
            elif line.startswith('ACHIEVEMENTS:'):
                current_section = 'achievements'
            elif line.startswith('SKILLS:'):
                current_section = 'skills'
            elif line.startswith('- '):
                item = line[2:]
                if current_section == 'experiences':
                    experiences.append(item)
                elif current_section == 'achievements':
                    achievements.append(item)
                elif current_section == 'skills':
                    skills.append(item)
        
        # Update state
        state["resume_details"] = ResumeDetails(
            content=resume_content,
            key_experiences=experiences,
            key_achievements=achievements,
            key_skills=skills
        )
        
        state["messages"].append("Resume analysed and stored in vector database")
        state["next_agent"] = "company_researcher"
        
        return state

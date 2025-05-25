from langchain_openai import ChatOpenAI
from langchain.schema import HumanMessage
from src.graph.state import GraphState, JobDetails
from src.utils.mcp_clients import FetchMCPClient
import asyncio

class JobAdAnalyser:
    def __init__(self):
        self.llm = ChatOpenAI(model="gpt-4o-mini-2024-07-18", temperature=0)
    
    async def analyze_job_ad(self, state: GraphState) -> GraphState:
        """Fetch and analyze job advertisement"""
        job_url = state["job_details"].url
        
        # Fetch job ad content using MCP
        # TEMPORARY - start - load a static file instead of getting job content markdown through MCP
        # async with FetchMCPClient() as client:
        #     job_content = await client.fetch_url_content(job_url)

        try:
            file_path = "data/job_ad.md"
            with open(file_path, 'r') as file:
                job_content = file.read()
        except FileNotFoundError:
            print(f"Error: File not found at {file_path}")
            job_content = ""
        except Exception as e:
            print(f"An error occurred: {e}")
            job_content = ""
        # TEMPORARY - end

        # Analyze the job ad
        analysis_prompt = f"""
        Analyze the following job advertisement and extract:
        1. Key job requirements (must-haves)
        2. Key skills expected
        3. Key competencies expected
        
        Job Advertisement:
        {job_content}
        
        Format your response as:
        REQUIREMENTS:
        - [requirement 1]
        - [requirement 2]
        
        SKILLS:
        - [skill 1]
        - [skill 2]
        
        COMPETENCIES:
        - [competency 1]
        - [competency 2]
        """
        
        response = self.llm.invoke([HumanMessage(content=analysis_prompt)])
        
        # Parse the response (simplified parsing)
        content = response.content
        requirements = []
        skills = []
        competencies = []
        
        current_section = None
        for line in content.split('\n'):
            line = line.strip()
            if line.startswith('REQUIREMENTS:'):
                current_section = 'requirements'
            elif line.startswith('SKILLS:'):
                current_section = 'skills'
            elif line.startswith('COMPETENCIES:'):
                current_section = 'competencies'
            elif line.startswith('- '):
                item = line[2:]
                if current_section == 'requirements':
                    requirements.append(item)
                elif current_section == 'skills':
                    skills.append(item)
                elif current_section == 'competencies':
                    competencies.append(item)
        
        # Update state
        state["job_details"] = JobDetails(
            url=job_url,
            content=job_content,
            key_requirements=requirements,
            key_skills=skills,
            key_competencies=competencies
        )
        
        state["messages"].append("Job ad analysed successfully")
        state["next_agent"] = "resume_analyser"
        
        return state

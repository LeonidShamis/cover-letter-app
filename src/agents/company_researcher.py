from langchain_openai import ChatOpenAI
from langchain.schema import HumanMessage
from src.graph.state import GraphState, CompanyInfo
from src.utils.mcp_clients import BraveSearchMCPClient
import asyncio
import re

class CompanyResearcher:
    def __init__(self):
        self.llm = ChatOpenAI(model="gpt-4o-mini-2024-07-18", temperature=0)
    
    async def research_company(self, state: GraphState) -> GraphState:
        """Research company information using Brave Search"""
        # Extract company name from job details
        job_content = state["job_details"].content
        company_name = self._extract_company_name(job_content)
        
        # Search for company information
        # TEMPORARY - start - load a static file instead of getting through MCP
        # async with BraveSearchMCPClient() as client:
        #     search_results = await client.search_company(company_name)

        # Process search results
        company_info_text = ""
        # if "error" not in search_results:
        #     for result in search_results.get("results", [])[:3]:
        #         company_info_text += f"{result.get('title', '')}\n{result.get('description', '')}\n\n"
        
        try:
            file_path = "data/pathfindr_company.md"
            with open(file_path, 'r') as file:
                company_info_text = file.read()
        except FileNotFoundError:
            print(f"Error: File not found at {file_path}")
            company_info_text = ""
        except Exception as e:
            print(f"An error occurred: {e}")
            company_info_text = ""
        # TEMPORARY - end

        # Analyze company information
        analysis_prompt = f"""
        Based on the following information about {company_name}, extract:
        1. Company profile (what they do, their mission)
        2. Company culture (work environment, values)
        3. Company values (core principles)
        
        Company Information:
        {company_info_text}
        
        Format your response as:
        PROFILE:
        [company profile description]
        
        CULTURE:
        [company culture description]
        
        VALUES:
        - [value 1]
        - [value 2]
        - [value 3]
        """
        
        response = self.llm.invoke([HumanMessage(content=analysis_prompt)])
        
        # Parse response
        content = response.content
        profile = ""
        culture = ""
        values = []
        
        current_section = None
        for line in content.split('\n'):
            line = line.strip()
            if line.startswith('PROFILE:'):
                current_section = 'profile'
            elif line.startswith('CULTURE:'):
                current_section = 'culture'
            elif line.startswith('VALUES:'):
                current_section = 'values'
            elif line.startswith('- '):
                if current_section == 'values':
                    values.append(line[2:])
            elif line and current_section:
                if current_section == 'profile':
                    profile += line + " "
                elif current_section == 'culture':
                    culture += line + " "
        
        # Update state
        state["company_info"] = CompanyInfo(
            name=company_name,
            profile=profile.strip(),
            culture=culture.strip(),
            values=values
        )
        
        state["messages"].append(f"Company research completed for {company_name}")
        state["next_agent"] = "planner"
        
        return state
    
    def _extract_company_name(self, job_content: str) -> str:
        """Extract company name from job content"""
        # Simple regex to find company name patterns
        patterns = [
            r"Company:\s*([^\n]+)",
            r"at\s+([A-Z][a-zA-Z\s&]+)(?:\s|$)",
            r"join\s+([A-Z][a-zA-Z\s&]+)(?:\s|$)"
        ]
        
        for pattern in patterns:
            match = re.search(pattern, job_content, re.IGNORECASE)
            if match:
                return match.group(1).strip()
        
        return "Unknown Company"

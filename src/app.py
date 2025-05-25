import streamlit as st
import os
from src.graph.workflow import CoverLetterWorkflow
from src.graph.state import GraphState, JobDetails, ResumeDetails, CompanyInfo, CoverLetterPlan, CoverLetterContent, QAFeedback
from src.config.settings import settings

# Page configuration
st.set_page_config(
    page_title="AI Cover Letter Generator",
    page_icon="📝",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .step-header {
        font-size: 1.5rem;
        color: #2e8b57;
        margin-top: 2rem;
        margin-bottom: 1rem;
    }
    .info-box {
        background-color: #f0f8ff;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #1f77b4;
        margin: 1rem 0;
    }
    .success-box {
        background-color: #f0fff0;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #32cd32;
        margin: 1rem 0;
    }
    .warning-box {
        background-color: #fffacd;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #ffa500;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

def main():
    st.markdown('<h1 class="main-header">🤖 AI Cover Letter Generator</h1>', unsafe_allow_html=True)
    
    # Check API keys
    # if not settings.OPENAI_API_KEY:
    #     st.error("⚠️ OpenAI API key not found. Please set OPENAI_API_KEY in your .env file.")
    #     st.stop()
    
    # Sidebar for configuration
    with st.sidebar:
        st.header("⚙️ Configuration")
        
        # Cover letter style selection
        cover_letter_style = st.selectbox(
            "Cover Letter Style",
            ["Professional", "Creative", "Technical", "Executive", "Casual"],
            index=0
        )
        
        st.markdown("---")
        st.header("📋 Process Steps")
        st.markdown("""
        1. **Job Analysis** - Fetch and analyze job ad
        2. **Resume Analysis** - Process resume content
        3. **Company Research** - Gather company info
        4. **Planning** - Create cover letter structure
        5. **Writing** - Generate cover letter
        6. **Quality Check** - Review and refine
        """)
    
    # Main content area
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown('<div class="step-header">📄 Job Advertisement</div>', unsafe_allow_html=True)
        
        job_url = st.text_input(
            "Job Advertisement URL",
            placeholder="https://www.seek.com.au/job/...",
            help="Enter the URL of the job advertisement you're applying for"
        )
        
        if job_url:
            st.markdown('<div class="info-box">✅ Job URL provided</div>', unsafe_allow_html=True)
        
        st.markdown('<div class="step-header">📋 Resume Upload</div>', unsafe_allow_html=True)
        
        uploaded_file = st.file_uploader(
            "Upload your resume (Markdown format)",
            type=['md'],
            help="Upload your resume in Markdown format for analysis"
        )
        
        resume_content = ""
        if uploaded_file is not None:
            resume_content = str(uploaded_file.read(), "utf-8")
            st.markdown('<div class="success-box">✅ Resume uploaded successfully</div>', unsafe_allow_html=True)
            
            with st.expander("📖 Preview Resume Content"):
                st.markdown(resume_content[:1000] + "..." if len(resume_content) > 1000 else resume_content)
    
    with col2:
        st.markdown('<div class="step-header">🚀 Generate Cover Letter</div>', unsafe_allow_html=True)
        
        if st.button("🎯 Generate Cover Letter", type="primary", use_container_width=True):
            if not job_url:
                st.error("❌ Please provide a job advertisement URL")
                return
            
            if not resume_content:
                st.error("❌ Please upload your resume")
                return
            
            # Initialize progress tracking
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            try:
                # Initialize workflow
                workflow = CoverLetterWorkflow()
                
                # Create initial state
                initial_state = GraphState(
                    job_details=JobDetails(url=job_url),
                    resume_details=ResumeDetails(content=resume_content),
                    company_info=CompanyInfo(),
                    plan=CoverLetterPlan(),
                    cover_letter=CoverLetterContent(style=cover_letter_style.lower()),
                    qa_feedback=QAFeedback(),
                    iteration_count=0,
                    next_agent="job_ad_analyser",
                    messages=[]
                )
                
                # Run workflow with progress updates
                with st.spinner("🔄 Processing your request..."):
                    status_text.text("🔍 Analysing job advertisement...")
                    progress_bar.progress(20)
                    
                    # Run the workflow
                    result = workflow.run(initial_state)
                    
                    progress_bar.progress(100)
                    status_text.text("✅ Cover letter generation completed!")
                
                # Display results
                st.success("🎉 Cover letter generated successfully!")
                
                # Show the cover letter
                st.markdown('<div class="step-header">📝 Your Cover Letter</div>', unsafe_allow_html=True)
                
                if result["cover_letter"].content:
                    st.markdown("### Final Cover Letter")
                    st.markdown(result["cover_letter"].content)
                    
                    # Download button
                    st.download_button(
                        label="📥 Download Cover Letter",
                        data=result["cover_letter"].content,
                        file_name="cover_letter.txt",
                        mime="text/plain"
                    )
                    
                    # QA Feedback
                    if result["qa_feedback"].score > 0:
                        st.markdown("### 📊 Quality Assessment")
                        
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            st.metric("Score", f"{result['qa_feedback'].score}/10")
                        with col2:
                            st.metric("Status", "✅ Approved" if result['qa_feedback'].approved else "⚠️ Needs Work")
                        with col3:
                            st.metric("Iterations", result["iteration_count"])
                        
                        if result["qa_feedback"].feedback:
                            st.markdown("**Feedback:**")
                            st.info(result["qa_feedback"].feedback)
                        
                        if result["qa_feedback"].suggestions:
                            st.markdown("**Suggestions for Improvement:**")
                            for suggestion in result["qa_feedback"].suggestions:
                                st.markdown(f"• {suggestion}")
                
            except Exception as e:
                st.error(f"❌ An error occurred: {str(e)}")
                st.exception(e)
    
    # Process Summary Section
    if st.session_state.get('show_process_details', False):
        st.markdown("---")
        st.markdown('<div class="step-header">🔍 Process Details</div>', unsafe_allow_html=True)
        
        tab1, tab2, tab3, tab4 = st.tabs(["Job Analysis", "Resume Analysis", "Company Research", "Planning"])
        
        with tab1:
            st.markdown("### Job Advertisement Analysis")
            st.info("This section will show job requirements, skills, and competencies extracted from the job ad.")
        
        with tab2:
            st.markdown("### Resume Analysis")
            st.info("This section will show key experiences, achievements, and skills extracted from your resume.")
        
        with tab3:
            st.markdown("### Company Research")
            st.info("This section will show company profile, culture, and values discovered through research.")
        
        with tab4:
            st.markdown("### Cover Letter Planning")
            st.info("This section will show the strategic plan for your cover letter structure and content.")
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style='text-align: center; color: #666; padding: 2rem;'>
        <p>🤖 Powered by LangGraph Multi-Agent Architecture</p>
        <p>Built with Streamlit • OpenAI GPT-4 • MCP Servers</p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()

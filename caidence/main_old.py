"""
Main entry point for cAIdence application.
"""

import streamlit as st
import os
from pathlib import Path

def main():
    """Main application entry point."""
    st.set_page_config(
        page_title="cAIdence - Clinical AI Assistant",
        page_icon="🏥",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    st.title("🏥 cAIdence")
    st.subheader("Democratizing Clinical NLP through Agentic AI")
    
    # Sidebar for navigation
    with st.sidebar:
        st.markdown("## Navigation")
        page = st.selectbox(
            "Choose a page:",
            ["Chat Interface", "Data Analysis", "Dashboard", "Settings"]
        )
    
    # Main content area
    if page == "Chat Interface":
        show_chat_interface()
    elif page == "Data Analysis":
        show_data_analysis()
    elif page == "Dashboard":
        show_dashboard()
    elif page == "Settings":
        show_settings()

def show_chat_interface():
    """Display the conversational interface."""
    st.markdown("### 💬 Ask cAIdence")
    st.markdown("Use natural language to query your clinical data.")
    
    # Chat interface placeholder
    user_input = st.text_area(
        "Your question:",
        placeholder="Find all surgical notes from the last year that mention 'arterial graft' but do not mention 'infection'.",
        height=100
    )
    
    if st.button("Ask cAIdence", type="primary"):
        if user_input:
            with st.spinner("cAIdence is analyzing your request..."):
                # TODO: Implement agent processing
                st.success("Analysis complete! (Feature coming soon)")
        else:
            st.warning("Please enter a question.")

def show_data_analysis():
    """Display data analysis tools."""
    st.markdown("### 📊 Data Analysis")
    st.markdown("Upload and analyze clinical documents.")
    
    uploaded_file = st.file_uploader(
        "Upload clinical documents",
        type=['txt', 'pdf', 'docx'],
        accept_multiple_files=True
    )
    
    if uploaded_file:
        st.success(f"Uploaded {len(uploaded_file)} file(s)")
        # TODO: Implement file processing

def show_dashboard():
    """Display interactive dashboard."""
    st.markdown("### 📈 Interactive Dashboard")
    st.markdown("Visualize your clinical data insights.")
    
    # Placeholder dashboard
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Documents Processed", "1,234", "12")
    
    with col2:
        st.metric("Entities Extracted", "45,678", "234")
    
    with col3:
        st.metric("Queries Completed", "89", "5")

def show_settings():
    """Display application settings."""
    st.markdown("### ⚙️ Settings")
    
    st.markdown("#### cTAKES Configuration")
    ctakes_path = st.text_input("cTAKES Installation Path", "/opt/ctakes")
    
    st.markdown("#### Security Settings")
    phi_protection = st.checkbox("Enable PHI Protection", value=True)
    local_llm = st.checkbox("Use Local LLM Only", value=True)
    
    st.markdown("#### Database Connection")
    db_type = st.selectbox("Database Type", ["PostgreSQL", "MongoDB", "SQLite"])
    
    if st.button("Save Settings"):
        st.success("Settings saved successfully!")

if __name__ == "__main__":
    main()

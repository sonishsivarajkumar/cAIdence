"""
Main entry point for cAIdence application.
Enhanced with v0.2.0 features including FHIR support, enhanced visualizations,
query history, and user authentication.
"""

import streamlit as st
import os
import json
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional

# Import v0.2.0 enhanced modules
from caidence.auth import AuthenticationManager, UserRole, create_default_admin
from caidence.tools.query_manager import (
    QueryHistoryManager, QueryRecord, SavedSearch, 
    generate_query_id, generate_search_id
)
from caidence.tools.fhir_processor import FHIRProcessor, load_fhir_bundle
from caidence.tools.enhanced_visualizer import EnhancedVisualizer, create_summary_dashboard


# Initialize managers
@st.cache_resource
def get_auth_manager():
    """Get or create authentication manager."""
    auth_mgr = AuthenticationManager()
    # Create default admin if needed
    create_default_admin(auth_mgr)
    return auth_mgr

@st.cache_resource
def get_query_manager():
    """Get or create query history manager."""
    return QueryHistoryManager()

@st.cache_resource
def get_fhir_processor():
    """Get or create FHIR processor."""
    return FHIRProcessor()

@st.cache_resource
def get_visualizer():
    """Get or create enhanced visualizer."""
    return EnhancedVisualizer()

# Session state management
def init_session_state():
    """Initialize session state variables."""
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
    if 'user' not in st.session_state:
        st.session_state.user = None
    if 'query_history' not in st.session_state:
        st.session_state.query_history = []
    if 'saved_searches' not in st.session_state:
        st.session_state.saved_searches = []
    if 'current_analysis' not in st.session_state:
        st.session_state.current_analysis = None

def main():
    """Main application entry point."""
    st.set_page_config(
        page_title="cAIdence v0.2.0 - Clinical AI Assistant",
        page_icon="🏥",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    init_session_state()
    
    # Check authentication
    if not st.session_state.authenticated:
        show_login_page()
        return
    
    # Main application interface
    show_main_interface()

def show_login_page():
    """Display login/registration page."""
    st.title("🏥 cAIdence v0.2.0")
    st.subheader("Democratizing Clinical NLP through Agentic AI")
    
    auth_manager = get_auth_manager()
    
    tab1, tab2 = st.tabs(["Login", "Register"])
    
    with tab1:
        st.markdown("### Login to cAIdence")
        
        with st.form("login_form"):
            username = st.text_input("Username or Email")
            password = st.text_input("Password", type="password")
            submitted = st.form_submit_button("Login")
            
            if submitted and username and password:
                result = auth_manager.authenticate_user(
                    username, password, 
                    ip_address=st.session_state.get('client_ip', ''),
                    user_agent=st.session_state.get('user_agent', '')
                )
                
                if result:
                    user, token = result
                    st.session_state.authenticated = True
                    st.session_state.user = user
                    st.session_state.session_token = token
                    st.success(f"Welcome back, {user.full_name}!")
                    st.rerun()
                else:
                    st.error("Invalid username or password")
    
    with tab2:
        st.markdown("### Register for cAIdence")
        
        with st.form("register_form"):
            new_username = st.text_input("Username")
            new_email = st.text_input("Email")
            new_full_name = st.text_input("Full Name")
            new_password = st.text_input("Password", type="password")
            confirm_password = st.text_input("Confirm Password", type="password")
            role = st.selectbox("Role", [
                "Viewer", "Analyst", "Clinician", "Researcher"
            ])
            
            submitted = st.form_submit_button("Register")
            
            if submitted:
                if new_password != confirm_password:
                    st.error("Passwords do not match")
                elif len(new_password) < 8:
                    st.error("Password must be at least 8 characters")
                else:
                    user_role = UserRole(role.lower())
                    user = auth_manager.create_user(
                        new_username, new_email, new_full_name, 
                        new_password, user_role
                    )
                    
                    if user:
                        st.success("Registration successful! Please login.")
                    else:
                        st.error("Registration failed. Username or email may already exist.")

def show_main_interface():
    """Display the main application interface."""
    st.title("🏥 cAIdence v0.2.0")
    st.subheader("Democratizing Clinical NLP through Agentic AI")
    
    # Display user info and logout
    user = st.session_state.user
    col1, col2, col3 = st.columns([2, 1, 1])
    
    with col1:
        st.markdown(f"**Welcome, {user.full_name}** ({user.role.value})")
    
    with col2:
        if st.button("🔄 Refresh"):
            load_user_data()
    
    with col3:
        if st.button("🚪 Logout"):
            logout_user()
    
    # Sidebar navigation
    with st.sidebar:
        st.markdown("## Navigation")
        page = st.selectbox(
            "Choose a page:",
            ["Chat Interface", "Query History", "Saved Searches", 
             "Data Analysis", "FHIR Explorer", "Dashboard", "Settings"]
        )
    
    # Load user data
    load_user_data()
    
    # Main content area
    if page == "Chat Interface":
        show_enhanced_chat_interface()
    elif page == "Query History":
        show_query_history()
    elif page == "Saved Searches":
        show_saved_searches()
    elif page == "Data Analysis":
        show_enhanced_data_analysis()
    elif page == "FHIR Explorer":
        show_fhir_explorer()
    elif page == "Dashboard":
        show_enhanced_dashboard()
    elif page == "Settings":
        show_enhanced_settings()

def load_user_data():
    """Load user-specific data."""
    query_manager = get_query_manager()
    user_id = st.session_state.user.id
    
    # Load query history
    st.session_state.query_history = query_manager.get_query_history(user_id, limit=20)
    
    # Load saved searches
    st.session_state.saved_searches = query_manager.get_saved_searches(user_id)

def logout_user():
    """Logout the current user."""
    auth_manager = get_auth_manager()
    if 'session_token' in st.session_state:
        auth_manager.logout_user(st.session_state.session_token)
    
    # Clear session state
    st.session_state.authenticated = False
    st.session_state.user = None
    st.session_state.clear()
    st.rerun()

def show_enhanced_chat_interface():
    """Display the enhanced conversational interface with query suggestions."""
    st.markdown("### 💬 Ask cAIdence")
    st.markdown("Use natural language to query your clinical data.")
    
    query_manager = get_query_manager()
    user_id = st.session_state.user.id
    
    # Query suggestions based on history
    st.markdown("#### Recent Queries")
    recent_queries = st.session_state.query_history[:5]
    
    if recent_queries:
        selected_query = st.selectbox(
            "Select from recent queries:",
            [""] + [q.query_text for q in recent_queries],
            key="recent_query_select"
        )
    else:
        selected_query = ""
    
    # Main query input
    user_input = st.text_area(
        "Your question:",
        value=selected_query,
        placeholder="Find all surgical notes from the last year that mention 'arterial graft' but do not mention 'infection'.",
        height=100,
        key="main_query_input"
    )
    
    col1, col2, col3 = st.columns([1, 1, 2])
    
    with col1:
        if st.button("🔍 Analyze", type="primary"):
            if user_input.strip():
                execute_query(user_input)
    
    with col2:
        if st.button("💾 Save Query"):
            if user_input.strip():
                save_current_query(user_input)
    
    # Display current analysis results
    if st.session_state.current_analysis:
        display_analysis_results(st.session_state.current_analysis)

def execute_query(query_text: str):
    """Execute a query and display results."""
    start_time = datetime.now()
    query_manager = get_query_manager()
    visualizer = get_visualizer()
    user_id = st.session_state.user.id
    
    try:
        # Simulate query execution (replace with actual implementation)
        with st.spinner("Analyzing your query..."):
            # TODO: Implement actual query processing
            import time
            time.sleep(2)  # Simulate processing
            
            # Mock results
            results = {
                "query": query_text,
                "entities": [
                    {"text": "arterial graft", "type": "procedure", "confidence": 0.95},
                    {"text": "surgical", "type": "procedure", "confidence": 0.88}
                ],
                "documents_found": 42,
                "execution_time": (datetime.now() - start_time).total_seconds() * 1000
            }
        
        # Record query
        query_record = QueryRecord(
            id=generate_query_id(user_id, query_text, datetime.now()),
            user_id=user_id,
            query_text=query_text,
            query_type="search",
            timestamp=datetime.now(),
            execution_time_ms=int(results["execution_time"]),
            result_count=results["documents_found"],
            success=True,
            results_summary=results
        )
        
        query_manager.add_query_record(query_record)
        st.session_state.current_analysis = results
        
        st.success(f"Found {results['documents_found']} documents in {results['execution_time']:.0f}ms")
        
    except Exception as e:
        # Record failed query
        query_record = QueryRecord(
            id=generate_query_id(user_id, query_text, datetime.now()),
            user_id=user_id,
            query_text=query_text,
            query_type="search",
            timestamp=datetime.now(),
            execution_time_ms=int((datetime.now() - start_time).total_seconds() * 1000),
            result_count=0,
            success=False,
            error_message=str(e)
        )
        
        query_manager.add_query_record(query_record)
        st.error(f"Query failed: {str(e)}")

def display_analysis_results(results: Dict[str, Any]):
    """Display analysis results with enhanced visualizations."""
    st.markdown("### 📊 Analysis Results")
    
    tab1, tab2, tab3 = st.tabs(["Summary", "Entities", "Visualizations"])
    
    with tab1:
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Documents Found", results.get("documents_found", 0))
        
        with col2:
            st.metric("Entities Extracted", len(results.get("entities", [])))
        
        with col3:
            st.metric("Execution Time", f"{results.get('execution_time', 0):.0f}ms")
    
    with tab2:
        entities = results.get("entities", [])
        if entities:
            for entity in entities:
                with st.expander(f"{entity['text']} ({entity['type']})"):
                    st.write(f"**Confidence:** {entity['confidence']:.2%}")
                    st.write(f"**Type:** {entity['type']}")
        else:
            st.info("No entities extracted")
    
    with tab3:
        # Create mock visualization
        visualizer = get_visualizer()
        
        if entities:
            # Add mock dates for visualization
            for entity in entities:
                entity['date'] = datetime.now() - timedelta(days=10)
            
            fig = visualizer.create_entity_timeline(entities)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No data to visualize")

def save_current_query(query_text: str):
    """Save the current query as a saved search."""
    user_id = st.session_state.user.id
    
    with st.form("save_query_form"):
        st.markdown("#### Save Query")
        name = st.text_input("Search Name", value=f"Search {datetime.now().strftime('%Y-%m-%d %H:%M')}")
        description = st.text_area("Description (optional)")
        is_favorite = st.checkbox("Mark as Favorite")
        
        if st.form_submit_button("Save"):
            query_manager = get_query_manager()
            
            saved_search = SavedSearch(
                id=generate_search_id(user_id, name),
                user_id=user_id,
                name=name,
                description=description,
                query_text=query_text,
                parameters={},
                created_at=datetime.now(),
                last_modified=datetime.now(),
                is_favorite=is_favorite
            )
            
            if query_manager.save_search(saved_search):
                st.success("Query saved successfully!")
                load_user_data()  # Refresh saved searches
            else:
                st.error("Failed to save query")

def show_query_history():
    """Display query history page."""
    st.markdown("### 📋 Query History")
    
    history = st.session_state.query_history
    
    if not history:
        st.info("No query history found")
        return
    
    # Filters
    col1, col2, col3 = st.columns(3)
    
    with col1:
        query_type_filter = st.selectbox(
            "Filter by Type:",
            ["All"] + list(set(q.query_type for q in history))
        )
    
    with col2:
        success_filter = st.selectbox(
            "Filter by Status:",
            ["All", "Successful", "Failed"]
        )
    
    with col3:
        days_back = st.selectbox(
            "Time Period:",
            [7, 30, 90, 365],
            index=1,
            format_func=lambda x: f"Last {x} days"
        )
    
    # Apply filters
    filtered_history = history
    if query_type_filter != "All":
        filtered_history = [q for q in filtered_history if q.query_type == query_type_filter]
    if success_filter == "Successful":
        filtered_history = [q for q in filtered_history if q.success]
    elif success_filter == "Failed":
        filtered_history = [q for q in filtered_history if not q.success]
    
    # Display history
    for query in filtered_history:
        with st.expander(f"{query.timestamp.strftime('%Y-%m-%d %H:%M')} - {query.query_text[:50]}..."):
            col1, col2 = st.columns(2)
            
            with col1:
                st.write(f"**Query:** {query.query_text}")
                st.write(f"**Type:** {query.query_type}")
                st.write(f"**Results:** {query.result_count}")
            
            with col2:
                st.write(f"**Status:** {'✅ Success' if query.success else '❌ Failed'}")
                st.write(f"**Execution Time:** {query.execution_time_ms}ms")
                if query.error_message:
                    st.write(f"**Error:** {query.error_message}")
            
            if st.button(f"Re-run Query", key=f"rerun_{query.id}"):
                execute_query(query.query_text)

def show_saved_searches():
    """Display saved searches page."""
    st.markdown("### 💾 Saved Searches")
    
    searches = st.session_state.saved_searches
    
    if not searches:
        st.info("No saved searches found")
        return
    
    # Sort by favorites first, then by last modified
    searches.sort(key=lambda x: (not x.is_favorite, x.last_modified), reverse=True)
    
    for search in searches:
        with st.expander(f"{'⭐ ' if search.is_favorite else ''}{search.name}"):
            col1, col2 = st.columns(2)
            
            with col1:
                st.write(f"**Query:** {search.query_text}")
                if search.description:
                    st.write(f"**Description:** {search.description}")
                st.write(f"**Created:** {search.created_at.strftime('%Y-%m-%d')}")
            
            with col2:
                st.write(f"**Executions:** {search.execution_count}")
                if search.last_executed:
                    st.write(f"**Last Run:** {search.last_executed.strftime('%Y-%m-%d %H:%M')}")
                
                if st.button(f"Run Search", key=f"run_{search.id}"):
                    query_manager = get_query_manager()
                    query_manager.update_search_execution(search.id)
                    execute_query(search.query_text)
                
                if st.button(f"Delete", key=f"delete_{search.id}"):
                    query_manager = get_query_manager()
                    if query_manager.delete_saved_search(search.id, st.session_state.user.id):
                        st.success("Search deleted")
                        load_user_data()
                        st.rerun()

def show_enhanced_data_analysis():
    """Display enhanced data analysis tools."""
    st.markdown("### 📊 Enhanced Data Analysis")
    st.markdown("Upload and analyze clinical documents with advanced processing.")
    
    tab1, tab2 = st.tabs(["Document Upload", "Batch Processing"])
    
    with tab1:
        uploaded_files = st.file_uploader(
            "Upload clinical documents",
            type=['txt', 'pdf', 'docx', 'json'],
            accept_multiple_files=True
        )
        
        if uploaded_files:
            st.success(f"Uploaded {len(uploaded_files)} file(s)")
            
            # Analysis options
            st.markdown("#### Analysis Options")
            extract_entities = st.checkbox("Extract Clinical Entities", value=True)
            sentiment_analysis = st.checkbox("Perform Sentiment Analysis", value=False)
            negation_detection = st.checkbox("Detect Negations", value=True)
            
            if st.button("Start Analysis"):
                with st.spinner("Processing documents..."):
                    # TODO: Implement actual document processing
                    st.success("Analysis completed!")
    
    with tab2:
        st.markdown("#### Batch Processing")
        st.info("Configure batch processing for large document sets")
        
        batch_size = st.slider("Batch Size", 10, 1000, 100)
        parallel_processing = st.checkbox("Enable Parallel Processing")
        
        if st.button("Start Batch Processing"):
            st.info("Batch processing functionality coming soon!")

def show_fhir_explorer():
    """Display FHIR resource explorer."""
    st.markdown("### 🔗 FHIR Resource Explorer")
    st.markdown("Explore and analyze FHIR resources.")
    
    fhir_processor = get_fhir_processor()
    
    tab1, tab2, tab3 = st.tabs(["Upload FHIR", "Resource Explorer", "Patient Timeline"])
    
    with tab1:
        st.markdown("#### Upload FHIR Bundle")
        
        fhir_file = st.file_uploader(
            "Upload FHIR Bundle (JSON)",
            type=['json'],
            help="Upload a FHIR Bundle containing multiple resources"
        )
        
        if fhir_file:
            try:
                # Save uploaded file temporarily
                with open(f"temp_fhir_{fhir_file.name}", "wb") as f:
                    f.write(fhir_file.getbuffer())
                
                # Load FHIR resources
                resources = load_fhir_bundle(f"temp_fhir_{fhir_file.name}")
                
                if resources:
                    st.success(f"Loaded {len(resources)} FHIR resources")
                    
                    # Store in session state
                    st.session_state.fhir_resources = resources
                    
                    # Show resource summary
                    resource_types = {}
                    for resource in resources:
                        resource_types[resource.resource_type] = resource_types.get(resource.resource_type, 0) + 1
                    
                    st.markdown("**Resource Summary:**")
                    for resource_type, count in resource_types.items():
                        st.write(f"- {resource_type}: {count}")
                
                # Clean up temp file
                os.remove(f"temp_fhir_{fhir_file.name}")
                
            except Exception as e:
                st.error(f"Error loading FHIR bundle: {str(e)}")
    
    with tab2:
        if 'fhir_resources' in st.session_state:
            resources = st.session_state.fhir_resources
            
            # Resource type filter
            resource_types = list(set(r.resource_type for r in resources))
            selected_type = st.selectbox("Select Resource Type:", resource_types)
            
            # Display resources of selected type
            filtered_resources = [r for r in resources if r.resource_type == selected_type]
            
            for resource in filtered_resources[:10]:  # Limit display
                with st.expander(f"{resource.resource_type} - {resource.id}"):
                    # Extract and display text content
                    texts = fhir_processor.extract_text_from_resource(resource)
                    if texts:
                        st.markdown("**Extracted Text:**")
                        for text in texts:
                            st.write(f"- {text}")
                    
                    # Show raw data (abbreviated)
                    st.markdown("**Resource Data:**")
                    st.json(resource.data)
        else:
            st.info("Upload a FHIR bundle to explore resources")
    
    with tab3:
        if 'fhir_resources' in st.session_state:
            resources = st.session_state.fhir_resources
            
            # Get patient IDs
            patient_resources = [r for r in resources if r.resource_type == "Patient"]
            if patient_resources:
                patient_ids = [r.id for r in patient_resources]
                selected_patient = st.selectbox("Select Patient:", patient_ids)
                
                if selected_patient:
                    # Create patient timeline
                    timeline = fhir_processor.create_patient_timeline(selected_patient, resources)
                    
                    if timeline:
                        st.markdown(f"**Timeline for Patient {selected_patient}**")
                        
                        for event in timeline:
                            with st.expander(f"{event['date'].strftime('%Y-%m-%d')} - {event['description']}"):
                                st.write(f"**Type:** {event['category']}")
                                st.write(f"**Resource:** {event['resource_type']}")
                                st.write(f"**ID:** {event['id']}")
                    else:
                        st.info("No timeline events found for this patient")
            else:
                st.info("No patient resources found in the uploaded bundle")
        else:
            st.info("Upload a FHIR bundle to view patient timelines")

def show_enhanced_dashboard():
    """Display enhanced interactive dashboard."""
    st.markdown("### 📈 Enhanced Dashboard")
    
    # Get analytics data
    query_manager = get_query_manager()
    analytics = query_manager.get_analytics_summary(days_back=30)
    
    if analytics:
        # Key metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Queries", analytics.get("total_queries", 0))
        
        with col2:
            st.metric("Success Rate", f"{analytics.get('success_rate', 0):.1%}")
        
        with col3:
            st.metric("Avg Response Time", f"{analytics.get('avg_execution_time_ms', 0):.0f}ms")
        
        with col4:
            st.metric("Active Users", analytics.get("unique_users", 0))
        
        # Charts
        tab1, tab2, tab3 = st.tabs(["Usage Trends", "Query Types", "Performance"])
        
        with tab1:
            daily_trend = analytics.get("daily_trend", [])
            if daily_trend:
                import pandas as pd
                df = pd.DataFrame(daily_trend)
                st.line_chart(df.set_index('date')['count'])
            else:
                st.info("No trend data available")
        
        with tab2:
            top_types = analytics.get("top_query_types", [])
            if top_types:
                import pandas as pd
                df = pd.DataFrame(top_types)
                st.bar_chart(df.set_index('type')['count'])
            else:
                st.info("No query type data available")
        
        with tab3:
            st.metric("Average Execution Time", f"{analytics.get('avg_execution_time_ms', 0):.0f}ms")
            st.progress(min(analytics.get('success_rate', 0), 1.0))
    else:
        st.info("No analytics data available")

def show_enhanced_settings():
    """Display enhanced application settings."""
    st.markdown("### ⚙️ Enhanced Settings")
    
    user = st.session_state.user
    
    tab1, tab2, tab3, tab4 = st.tabs(["Profile", "Preferences", "Security", "System"])
    
    with tab1:
        st.markdown("#### User Profile")
        
        with st.form("profile_form"):
            full_name = st.text_input("Full Name", value=user.full_name)
            email = st.text_input("Email", value=user.email)
            
            # Display role (read-only for non-admins)
            if user.role == UserRole.ADMIN:
                role = st.selectbox("Role", [r.value for r in UserRole], 
                                  index=list(UserRole).index(user.role))
            else:
                st.text_input("Role", value=user.role.value, disabled=True)
            
            if st.form_submit_button("Update Profile"):
                st.success("Profile updated successfully!")
    
    with tab2:
        st.markdown("#### User Preferences")
        
        # Load current preferences
        prefs = user.preferences or {}
        
        with st.form("preferences_form"):
            theme = st.selectbox("Theme", ["Light", "Dark"], 
                                index=0 if prefs.get("theme", "light") == "light" else 1)
            
            auto_save = st.checkbox("Auto-save queries", value=prefs.get("auto_save", True))
            
            notifications = st.checkbox("Enable notifications", value=prefs.get("notifications", True))
            
            default_view = st.selectbox("Default view", 
                                      ["Chat Interface", "Dashboard", "Data Analysis"],
                                      index=0)
            
            if st.form_submit_button("Save Preferences"):
                # TODO: Save preferences to database
                st.success("Preferences saved successfully!")
    
    with tab3:
        st.markdown("#### Security Settings")
        
        # Active sessions
        auth_manager = get_auth_manager()
        active_sessions = auth_manager.get_active_sessions(user.id)
        
        st.markdown("**Active Sessions:**")
        for session in active_sessions:
            with st.expander(f"Session from {session.ip_address}"):
                st.write(f"**Created:** {session.created_at.strftime('%Y-%m-%d %H:%M')}")
                st.write(f"**Last Activity:** {session.last_activity.strftime('%Y-%m-%d %H:%M')}")
                st.write(f"**Expires:** {session.expires_at.strftime('%Y-%m-%d %H:%M')}")
                
                if st.button(f"Terminate Session", key=f"terminate_{session.session_id}"):
                    # TODO: Implement session termination
                    st.success("Session terminated")
        
        # Change password
        st.markdown("**Change Password:**")
        with st.form("password_form"):
            current_password = st.text_input("Current Password", type="password")
            new_password = st.text_input("New Password", type="password")
            confirm_password = st.text_input("Confirm New Password", type="password")
            
            if st.form_submit_button("Change Password"):
                if new_password != confirm_password:
                    st.error("New passwords do not match")
                elif len(new_password) < 8:
                    st.error("Password must be at least 8 characters")
                else:
                    # TODO: Implement password change
                    st.success("Password changed successfully!")
    
    with tab4:
        st.markdown("#### System Configuration")
        
        if user.role == UserRole.ADMIN:
            st.markdown("**cTAKES Configuration**")
            ctakes_path = st.text_input("cTAKES Installation Path", "/opt/ctakes")
            
            st.markdown("**Security Settings**")
            phi_protection = st.checkbox("Enable PHI Protection", value=True)
            local_llm = st.checkbox("Use Local LLM Only", value=True)
            
            st.markdown("**Database Configuration**")
            db_type = st.selectbox("Database Type", ["PostgreSQL", "MongoDB", "SQLite"])
            
            # System statistics
            st.markdown("**System Statistics**")
            
            # Cleanup options
            if st.button("Cleanup Expired Sessions"):
                auth_manager = get_auth_manager()
                cleaned = auth_manager.cleanup_expired_sessions()
                st.success(f"Cleaned up {cleaned} expired sessions")
            
            if st.button("Save System Settings"):
                st.success("System settings saved successfully!")
        else:
            st.info("System configuration is only available to administrators.")

if __name__ == "__main__":
    main()

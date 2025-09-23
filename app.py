"""
Schedulyze - AI-powered personalized study scheduler
Created by: Aanish Nithin
Description: Optimizes study sessions, deadlines, and breaks for maximum productivity
"""

import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta, date
import plotly.express as px
import plotly.graph_objects as go
from typing import List, Dict, Tuple
import json

# Configure Streamlit page
st.set_page_config(
    page_title="Schedulyze - AI Study Scheduler",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)

class StudyScheduleOptimizer:
    """
    AI-powered study schedule optimizer that creates personalized study plans
    based on deadlines, difficulty levels, and user preferences.
    """
    
    def __init__(self):
        self.subjects = []
        self.schedule = []
    
    def calculate_priority_score(self, deadline: date, difficulty: int, importance: int) -> float:
        """
        Calculate priority score for a subject based on multiple factors.
        
        Args:
            deadline: Subject deadline
            difficulty: Difficulty level (1-5)
            importance: Importance level (1-5)
            
        Returns:
            Priority score (higher = more urgent/important)
        """
        # Calculate days until deadline
        days_until_deadline = (deadline - date.today()).days
        
        # Avoid division by zero
        if days_until_deadline <= 0:
            urgency_factor = 10.0
        else:
            urgency_factor = 1.0 / days_until_deadline
        
        # Weight factors: urgency (40%), difficulty (30%), importance (30%)
        priority_score = (
            urgency_factor * 0.4 +
            difficulty / 5.0 * 0.3 +
            importance / 5.0 * 0.3
        )
        
        return priority_score
    
    def distribute_study_hours(self, subjects: List[Dict], total_daily_hours: int) -> Dict:
        """
        Distribute daily study hours among subjects based on priority scores.
        
        Args:
            subjects: List of subject dictionaries
            total_daily_hours: Total available study hours per day
            
        Returns:
            Dictionary with subject-wise daily hour allocation
        """
        if not subjects:
            return {}
        
        # Calculate priority scores for all subjects
        for subject in subjects:
            subject['priority_score'] = self.calculate_priority_score(
                subject['deadline'],
                subject['difficulty'],
                subject['importance']
            )
        
        # Sort subjects by priority (highest first)
        sorted_subjects = sorted(subjects, key=lambda x: x['priority_score'], reverse=True)
        
        # Calculate total priority score
        total_priority = sum(subject['priority_score'] for subject in sorted_subjects)
        
        # Distribute hours proportionally
        hour_distribution = {}
        remaining_hours = total_daily_hours
        
        for i, subject in enumerate(sorted_subjects):
            if i == len(sorted_subjects) - 1:  # Last subject gets remaining hours
                hours = remaining_hours
            else:
                proportion = subject['priority_score'] / total_priority
                hours = round(proportion * total_daily_hours, 1)
                remaining_hours -= hours
            
            # Ensure minimum 0.5 hours per subject if hours available
            hours = max(0.5, min(hours, remaining_hours + 0.5)) if remaining_hours > 0 else 0
            hour_distribution[subject['name']] = hours
        
        return hour_distribution
    
    def generate_schedule(
        self, 
        subjects: List[Dict], 
        start_date: date, 
        daily_hours: int,
        session_length: int,
        break_length: int,
        start_time: str = "09:00"
    ) -> List[Dict]:
        """
        Generate optimized study schedule with breaks.
        
        Args:
            subjects: List of subject dictionaries
            start_date: Start date for schedule
            daily_hours: Total daily study hours
            session_length: Length of each study session (minutes)
            break_length: Length of breaks (minutes)
            start_time: Daily start time (HH:MM format)
            
        Returns:
            List of schedule entries
        """
        schedule = []
        hour_distribution = self.distribute_study_hours(subjects, daily_hours)
        
        # Generate schedule for next 30 days or until all deadlines are met
        current_date = start_date
        max_date = start_date + timedelta(days=30)
        
        while current_date <= max_date:
            # Skip weekends if specified (can be made configurable)
            if current_date.weekday() < 5:  # Monday = 0, Sunday = 6
                daily_schedule = self._create_daily_schedule(
                    current_date, 
                    hour_distribution, 
                    session_length, 
                    break_length,
                    start_time
                )
                schedule.extend(daily_schedule)
            
            current_date += timedelta(days=1)
        
        return schedule
    
    def _create_daily_schedule(
        self, 
        date: date, 
        hour_distribution: Dict, 
        session_length: int, 
        break_length: int,
        start_time: str
    ) -> List[Dict]:
        """
        Create schedule for a single day.
        
        Args:
            date: Date for the schedule
            hour_distribution: Hours allocated per subject
            session_length: Study session length in minutes
            break_length: Break length in minutes
            start_time: Start time in HH:MM format
            
        Returns:
            List of schedule entries for the day
        """
        daily_schedule = []
        
        # Parse start time
        start_hour, start_minute = map(int, start_time.split(':'))
        current_time = datetime.combine(date, datetime.min.time().replace(hour=start_hour, minute=start_minute))
        
        # Create sessions for each subject
        for subject, hours in hour_distribution.items():
            if hours > 0:
                # Convert hours to minutes
                total_minutes = int(hours * 60)
                
                # Create sessions
                while total_minutes > 0:
                    # Determine session duration (either full session or remaining time)
                    session_duration = min(session_length, total_minutes)
                    
                    # Add study session
                    daily_schedule.append({
                        'date': date,
                        'start_time': current_time.strftime('%H:%M'),
                        'end_time': (current_time + timedelta(minutes=session_duration)).strftime('%H:%M'),
                        'subject': subject,
                        'type': 'Study',
                        'duration': session_duration
                    })
                    
                    current_time += timedelta(minutes=session_duration)
                    total_minutes -= session_duration
                    
                    # Add break if there's more to study
                    if total_minutes > 0:
                        daily_schedule.append({
                            'date': date,
                            'start_time': current_time.strftime('%H:%M'),
                            'end_time': (current_time + timedelta(minutes=break_length)).strftime('%H:%M'),
                            'subject': 'Break',
                            'type': 'Break',
                            'duration': break_length
                        })
                        current_time += timedelta(minutes=break_length)
        
        return daily_schedule

def create_google_calendar_export(schedule: List[Dict]) -> str:
    """
    Create a Google Calendar compatible CSV export.
    
    Args:
        schedule: List of schedule entries
        
    Returns:
        CSV string for Google Calendar import
    """
    csv_lines = ["Subject,Start Date,Start Time,End Date,End Time,Description"]
    
    for entry in schedule:
        if entry['type'] == 'Study':
            csv_lines.append(
                f"{entry['subject']} - Study Session,"
                f"{entry['date'].strftime('%m/%d/%Y')},"
                f"{entry['start_time']},"
                f"{entry['date'].strftime('%m/%d/%Y')},"
                f"{entry['end_time']},"
                f"Study session for {entry['subject']} ({entry['duration']} minutes)"
            )
    
    return '\n'.join(csv_lines)

def main():
    """
    Main Streamlit application function.
    """
    # Initialize session state
    if 'subjects' not in st.session_state:
        st.session_state.subjects = []
    if 'schedule' not in st.session_state:
        st.session_state.schedule = []
    
    # Main title and description
    st.title("📚 Schedulyze - AI Study Scheduler")
    st.markdown("""
    **AI-powered personalized study scheduler** that optimizes your study sessions, deadlines, and breaks for maximum productivity.
    
    ✨ **Features:**
    - Smart prioritization based on deadlines and difficulty
    - Optimized break scheduling
    - Calendar view of your study plan
    - Google Calendar export
    """)
    
    # Sidebar for settings
    with st.sidebar:
        st.header("⚙️ Settings")
        
        # Session and break settings
        st.subheader("Study Sessions")
        session_length = st.slider(
            "Session Length (minutes)", 
            min_value=15, 
            max_value=120, 
            value=45,
            help="Length of each focused study session"
        )
        
        break_length = st.slider(
            "Break Length (minutes)", 
            min_value=5, 
            max_value=30, 
            value=15,
            help="Length of breaks between study sessions"
        )
        
        # Daily schedule settings
        st.subheader("Daily Schedule")
        daily_hours = st.slider(
            "Daily Study Hours", 
            min_value=1, 
            max_value=12, 
            value=6,
            help="Total hours you want to study per day"
        )
        
        start_time = st.time_input(
            "Start Time", 
            value=datetime.strptime("09:00", "%H:%M").time(),
            help="When to start studying each day"
        )
        
        start_date = st.date_input(
            "Start Date", 
            value=date.today(),
            help="When to begin the study schedule"
        )
        
        # Include weekends option
        include_weekends = st.checkbox(
            "Include Weekends", 
            value=False,
            help="Include Saturday and Sunday in study schedule"
        )
    
    # Main content area with tabs
    tab1, tab2, tab3 = st.tabs(["📝 Add Subjects", "📅 Schedule View", "📊 Analytics"])
    
    with tab1:
        st.header("Add Study Subjects")
        
        # Subject input form
        with st.form("subject_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                subject_name = st.text_input(
                    "Subject Name", 
                    placeholder="e.g., Calculus, Chemistry, History",
                    help="Enter the name of the subject you want to study"
                )
                
                deadline = st.date_input(
                    "Deadline", 
                    min_value=date.today(),
                    help="When is this subject's exam or assignment due?"
                )
            
            with col2:
                study_hours = st.number_input(
                    "Total Study Hours Needed", 
                    min_value=1, 
                    max_value=100, 
                    value=10,
                    help="How many total hours do you need to study this subject?"
                )
                
                col2a, col2b = st.columns(2)
                with col2a:
                    difficulty = st.selectbox(
                        "Difficulty Level", 
                        options=[1, 2, 3, 4, 5],
                        index=2,
                        help="1 = Very Easy, 5 = Very Hard"
                    )
                
                with col2b:
                    importance = st.selectbox(
                        "Importance Level", 
                        options=[1, 2, 3, 4, 5],
                        index=2,
                        help="1 = Low Priority, 5 = High Priority"
                    )
            
            submitted = st.form_submit_button("➕ Add Subject", type="primary")
            
            if submitted and subject_name:
                # Add subject to session state
                new_subject = {
                    'name': subject_name,
                    'deadline': deadline,
                    'study_hours': study_hours,
                    'difficulty': difficulty,
                    'importance': importance,
                    'added_date': datetime.now()
                }
                st.session_state.subjects.append(new_subject)
                st.success(f"✅ Added '{subject_name}' to your study list!")
                st.rerun()
        
        # Display current subjects
        if st.session_state.subjects:
            st.subheader("Your Subjects")
            
            # Create a DataFrame for better display
            subjects_df = pd.DataFrame(st.session_state.subjects)
            subjects_df['Days Until Deadline'] = (subjects_df['deadline'] - date.today()).dt.days
            
            # Style the dataframe
            styled_df = subjects_df[['name', 'deadline', 'study_hours', 'difficulty', 'importance', 'Days Until Deadline']].copy()
            styled_df.columns = ['Subject', 'Deadline', 'Study Hours', 'Difficulty', 'Importance', 'Days Left']
            
            st.dataframe(
                styled_df,
                use_container_width=True,
                hide_index=True
            )
            
            # Remove subject option
            col1, col2 = st.columns([3, 1])
            with col2:
                if st.button("🗑️ Clear All Subjects", type="secondary"):
                    st.session_state.subjects = []
                    st.session_state.schedule = []
                    st.rerun()
    
    with tab2:
        st.header("📅 Your Optimized Study Schedule")
        
        if not st.session_state.subjects:
            st.info("👆 Please add some subjects in the 'Add Subjects' tab to generate your schedule.")
        else:
            # Generate schedule button
            if st.button("🚀 Generate Optimized Schedule", type="primary"):
                optimizer = StudyScheduleOptimizer()
                
                # Generate the schedule
                with st.spinner("🧠 AI is optimizing your study schedule..."):
                    st.session_state.schedule = optimizer.generate_schedule(
                        subjects=st.session_state.subjects,
                        start_date=start_date,
                        daily_hours=daily_hours,
                        session_length=session_length,
                        break_length=break_length,
                        start_time=start_time.strftime("%H:%M")
                    )
                
                st.success("✅ Schedule generated successfully!")
            
            # Display schedule if available
            if st.session_state.schedule:
                # Convert schedule to DataFrame
                schedule_df = pd.DataFrame(st.session_state.schedule)
                
                # Filter study sessions only for main view
                study_sessions = schedule_df[schedule_df['type'] == 'Study'].copy()
                
                if not study_sessions.empty:
                    # Schedule summary
                    st.subheader("📊 Schedule Summary")
                    
                    col1, col2, col3, col4 = st.columns(4)
                    with col1:
                        total_sessions = len(study_sessions)
                        st.metric("Total Study Sessions", total_sessions)
                    
                    with col2:
                        total_hours = study_sessions['duration'].sum() / 60
                        st.metric("Total Study Hours", f"{total_hours:.1f}")
                    
                    with col3:
                        unique_days = study_sessions['date'].nunique()
                        st.metric("Study Days", unique_days)
                    
                    with col4:
                        avg_daily_hours = total_hours / max(unique_days, 1)
                        st.metric("Avg Daily Hours", f"{avg_daily_hours:.1f}")
                    
                    # Schedule view options
                    view_option = st.radio(
                        "Choose View:",
                        ["📋 Table View", "📅 Calendar View"],
                        horizontal=True
                    )
                    
                    if view_option == "📋 Table View":
                        # Table view
                        display_df = study_sessions[['date', 'start_time', 'end_time', 'subject', 'duration']].copy()
                        display_df.columns = ['Date', 'Start Time', 'End Time', 'Subject', 'Duration (min)']
                        display_df['Date'] = display_df['Date'].dt.strftime('%Y-%m-%d')
                        
                        st.dataframe(
                            display_df,
                            use_container_width=True,
                            hide_index=True
                        )
                    
                    else:
                        # Calendar view using Plotly
                        st.subheader("📅 Calendar View")
                        
                        # Prepare data for calendar view
                        study_sessions['datetime_start'] = pd.to_datetime(
                            study_sessions['date'].astype(str) + ' ' + study_sessions['start_time']
                        )
                        study_sessions['datetime_end'] = pd.to_datetime(
                            study_sessions['date'].astype(str) + ' ' + study_sessions['end_time']
                        )
                        
                        # Create Gantt chart
                        fig = px.timeline(
                            study_sessions,
                            x_start='datetime_start',
                            x_end='datetime_end',
                            y='date',
                            color='subject',
                            title="Study Schedule Calendar View",
                            labels={'subject': 'Subject'},
                            height=600
                        )
                        
                        fig.update_layout(
                            xaxis_title="Time",
                            yaxis_title="Date",
                            showlegend=True
                        )
                        
                        st.plotly_chart(fig, use_container_width=True)
                    
                    # Google Calendar Export
                    st.subheader("📤 Export to Google Calendar")
                    
                    if st.button("📅 Generate Calendar Export"):
                        csv_content = create_google_calendar_export(st.session_state.schedule)
                        
                        st.download_button(
                            label="⬇️ Download Calendar CSV",
                            data=csv_content,
                            file_name=f"schedulyze_study_plan_{date.today().strftime('%Y-%m-%d')}.csv",
                            mime="text/csv",
                            help="Download this file and import it into Google Calendar"
                        )
                        
                        st.info("""
                        📝 **How to import into Google Calendar:**
                        1. Download the CSV file above
                        2. Go to Google Calendar
                        3. Click the '+' next to 'Other calendars'
                        4. Select 'Import'
                        5. Choose the downloaded CSV file
                        6. Select which calendar to import to
                        7. Click 'Import'
                        """)
    
    with tab3:
        st.header("📊 Study Analytics")
        
        if not st.session_state.subjects:
            st.info("👆 Add subjects to view analytics.")
        else:
            # Subject priority analysis
            st.subheader("🎯 Subject Priority Analysis")
            
            optimizer = StudyScheduleOptimizer()
            subjects_with_priority = []
            
            for subject in st.session_state.subjects:
                priority = optimizer.calculate_priority_score(
                    subject['deadline'],
                    subject['difficulty'],
                    subject['importance']
                )
                subjects_with_priority.append({
                    'Subject': subject['name'],
                    'Priority Score': priority,
                    'Difficulty': subject['difficulty'],
                    'Importance': subject['importance'],
                    'Days Until Deadline': (subject['deadline'] - date.today()).days
                })
            
            priority_df = pd.DataFrame(subjects_with_priority)
            
            # Priority score chart
            fig_priority = px.bar(
                priority_df.sort_values('Priority Score', ascending=True),
                x='Priority Score',
                y='Subject',
                orientation='h',
                title="Subject Priority Scores",
                color='Priority Score',
                color_continuous_scale='Reds'
            )
            
            st.plotly_chart(fig_priority, use_container_width=True)
            
            # Study time distribution
            if st.session_state.schedule:
                st.subheader("⏰ Study Time Distribution")
                
                schedule_df = pd.DataFrame(st.session_state.schedule)
                study_sessions = schedule_df[schedule_df['type'] == 'Study']
                
                if not study_sessions.empty:
                    # Group by subject and sum duration
                    time_distribution = study_sessions.groupby('subject')['duration'].sum().reset_index()
                    time_distribution['hours'] = time_distribution['duration'] / 60
                    
                    # Pie chart for time distribution
                    fig_pie = px.pie(
                        time_distribution,
                        values='hours',
                        names='subject',
                        title="Study Time Distribution by Subject"
                    )
                    
                    st.plotly_chart(fig_pie, use_container_width=True)
                    
                    # Daily study hours chart
                    st.subheader("📈 Daily Study Hours")
                    
                    daily_hours = study_sessions.groupby('date')['duration'].sum().reset_index()
                    daily_hours['hours'] = daily_hours['duration'] / 60
                    
                    fig_daily = px.line(
                        daily_hours,
                        x='date',
                        y='hours',
                        title="Daily Study Hours Over Time",
                        markers=True
                    )
                    
                    st.plotly_chart(fig_daily, use_container_width=True)

if __name__ == "__main__":
    main()
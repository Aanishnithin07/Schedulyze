"""
Schedulyze - AI-Powered Study Scheduler
A Streamlit application that helps students create optimized study schedules
with intelligent prioritization and break management.
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta, time
import calendar
from icalendar import Calendar, Event
import io

# Set page configuration
st.set_page_config(
    page_title="Schedulyze - AI Study Scheduler",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .subject-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
    }
    .schedule-item {
        background-color: #e8f4fd;
        padding: 0.8rem;
        border-left: 4px solid #1f77b4;
        margin: 0.3rem 0;
        border-radius: 0.3rem;
    }
    .break-item {
        background-color: #f0e68c;
        padding: 0.5rem;
        border-left: 4px solid #ffd700;
        margin: 0.3rem 0;
        border-radius: 0.3rem;
    }
</style>
""", unsafe_allow_html=True)

class StudyScheduler:
    """
    AI-powered study scheduler that optimizes study sessions based on
    deadlines, difficulty, and available time.
    """
    
    def __init__(self):
        self.subjects = []
        self.schedule = []
    
    def calculate_priority_score(self, subject):
        """
        Calculate priority score based on deadline urgency and difficulty.
        Higher scores indicate higher priority.
        """
        # Days until deadline
        days_until_deadline = (subject['deadline'] - datetime.now().date()).days
        
        # Base urgency score (inversely proportional to days remaining)
        if days_until_deadline <= 0:
            urgency_score = 100  # Overdue
        elif days_until_deadline <= 1:
            urgency_score = 90   # Due tomorrow
        elif days_until_deadline <= 3:
            urgency_score = 70   # Due within 3 days
        elif days_until_deadline <= 7:
            urgency_score = 50   # Due within a week
        else:
            urgency_score = max(10, 50 - (days_until_deadline - 7) * 2)
        
        # Difficulty multiplier (1-10 scale)
        difficulty_multiplier = subject['difficulty'] / 10
        
        # Hours remaining factor
        hours_factor = min(subject['hours_needed'] / 10, 1)  # Cap at 1
        
        # Final priority score
        priority_score = urgency_score * (1 + difficulty_multiplier + hours_factor)
        
        return priority_score
    
    def generate_optimized_schedule(self, subjects, settings):
        """
        Generate an optimized study schedule using AI logic.
        Considers priority, session length, breaks, and study preferences.
        """
        schedule = []
        
        # Sort subjects by priority score (highest first)
        prioritized_subjects = sorted(
            subjects, 
            key=self.calculate_priority_score, 
            reverse=True
        )
        
        current_date = settings['start_date']
        current_time = settings['start_time']
        
        # Track remaining hours for each subject
        remaining_hours = {subject['name']: subject['hours_needed'] for subject in prioritized_subjects}
        
        # Generate schedule day by day
        for day_offset in range(14):  # Generate for 2 weeks
            study_date = current_date + timedelta(days=day_offset)
            
            # Skip weekends if user prefers
            if not settings['include_weekends'] and study_date.weekday() >= 5:
                continue
            
            daily_sessions = []
            session_start_time = current_time
            
            # Calculate total daily study time
            total_daily_minutes = settings['daily_hours'] * 60
            session_length_minutes = settings['session_length']
            break_length_minutes = settings['break_length']
            
            # Generate sessions for the day
            time_accumulated = 0
            
            for subject in prioritized_subjects:
                if remaining_hours[subject['name']] <= 0:
                    continue
                
                # Check if we have time left in the day
                if time_accumulated >= total_daily_minutes:
                    break
                
                # Calculate session duration
                session_duration = min(
                    session_length_minutes,
                    remaining_hours[subject['name']] * 60,
                    total_daily_minutes - time_accumulated
                )
                
                if session_duration < 15:  # Skip sessions shorter than 15 minutes
                    continue
                
                # Create session
                session_end_time = (
                    datetime.combine(study_date, session_start_time) + 
                    timedelta(minutes=session_duration)
                ).time()
                
                session = {
                    'date': study_date,
                    'start_time': session_start_time,
                    'end_time': session_end_time,
                    'subject': subject['name'],
                    'duration_minutes': session_duration,
                    'type': 'study',
                    'priority_score': self.calculate_priority_score(subject),
                    'difficulty': subject['difficulty']
                }
                
                daily_sessions.append(session)
                
                # Update remaining hours
                remaining_hours[subject['name']] -= session_duration / 60
                time_accumulated += session_duration
                
                # Add break if not the last session of the day
                if time_accumulated < total_daily_minutes - session_length_minutes:
                    break_start = session_end_time
                    break_end = (
                        datetime.combine(study_date, break_start) + 
                        timedelta(minutes=break_length_minutes)
                    ).time()
                    
                    break_session = {
                        'date': study_date,
                        'start_time': break_start,
                        'end_time': break_end,
                        'subject': 'Break',
                        'duration_minutes': break_length_minutes,
                        'type': 'break',
                        'priority_score': 0,
                        'difficulty': 0
                    }
                    
                    daily_sessions.append(break_session)
                    time_accumulated += break_length_minutes
                    
                    # Update start time for next session
                    session_start_time = break_end
                else:
                    # Update start time for next session (next day)
                    session_start_time = (
                        datetime.combine(study_date, session_end_time) + 
                        timedelta(minutes=break_length_minutes)
                    ).time()
            
            schedule.extend(daily_sessions)
        
        return schedule

def create_sidebar_settings():
    """Create sidebar with user settings and preferences."""
    st.sidebar.header("⚙️ Schedule Settings")
    
    # Study session settings
    st.sidebar.subheader("Session Configuration")
    session_length = st.sidebar.slider(
        "Study Session Length (minutes)",
        min_value=15,
        max_value=180,
        value=60,
        step=15,
        help="Length of each study session"
    )
    
    break_length = st.sidebar.slider(
        "Break Length (minutes)",
        min_value=5,
        max_value=60,
        value=15,
        step=5,
        help="Length of breaks between study sessions"
    )
    
    daily_hours = st.sidebar.slider(
        "Daily Study Hours",
        min_value=1.0,
        max_value=12.0,
        value=6.0,
        step=0.5,
        help="Total hours to study per day"
    )
    
    # Schedule timing
    st.sidebar.subheader("Schedule Timing")
    start_date = st.sidebar.date_input(
        "Start Date",
        value=datetime.now().date(),
        help="When to start the study schedule"
    )
    
    start_time = st.sidebar.time_input(
        "Daily Start Time",
        value=time(9, 0),
        help="What time to start studying each day"
    )
    
    include_weekends = st.sidebar.checkbox(
        "Include Weekends",
        value=False,
        help="Whether to schedule study sessions on weekends"
    )
    
    return {
        'session_length': session_length,
        'break_length': break_length,
        'daily_hours': daily_hours,
        'start_date': start_date,
        'start_time': start_time,
        'include_weekends': include_weekends
    }

def create_subject_input_form():
    """Create form for inputting subject information."""
    st.header("📚 Add Subjects")
    
    with st.form("subject_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            subject_name = st.text_input(
                "Subject Name",
                placeholder="e.g., Mathematics, History, Science",
                help="Enter the name of the subject"
            )
            
            deadline = st.date_input(
                "Deadline",
                value=datetime.now().date() + timedelta(days=7),
                help="When is this subject's exam or deadline?"
            )
        
        with col2:
            hours_needed = st.number_input(
                "Study Hours Needed",
                min_value=0.5,
                max_value=100.0,
                value=10.0,
                step=0.5,
                help="Total hours needed to study this subject"
            )
            
            difficulty = st.slider(
                "Difficulty Level",
                min_value=1,
                max_value=10,
                value=5,
                help="How difficult is this subject? (1=Easy, 10=Very Hard)"
            )
        
        submitted = st.form_submit_button("➕ Add Subject")
        
        if submitted and subject_name:
            return {
                'name': subject_name,
                'deadline': deadline,
                'hours_needed': hours_needed,
                'difficulty': difficulty
            }
    
    return None

def display_subjects_table(subjects):
    """Display subjects in a formatted table."""
    if not subjects:
        st.info("No subjects added yet. Use the form above to add subjects.")
        return
    
    st.header("📋 Your Subjects")
    
    # Create DataFrame for display
    df = pd.DataFrame(subjects)
    df['Days Until Deadline'] = df['deadline'].apply(
        lambda x: (x - datetime.now().date()).days
    )
    df['Priority Score'] = df.apply(
        lambda row: StudyScheduler().calculate_priority_score(row), axis=1
    )
    
    # Format the display
    display_df = df[['name', 'deadline', 'hours_needed', 'difficulty', 'Days Until Deadline', 'Priority Score']].copy()
    display_df.columns = ['Subject', 'Deadline', 'Hours Needed', 'Difficulty', 'Days Until Deadline', 'Priority Score']
    display_df['Priority Score'] = display_df['Priority Score'].round(1)
    
    # Color code by urgency
    def highlight_urgency(row):
        if row['Days Until Deadline'] <= 1:
            return ['background-color: #ffcccc'] * len(row)  # Red for urgent
        elif row['Days Until Deadline'] <= 3:
            return ['background-color: #ffe6cc'] * len(row)  # Orange for soon
        elif row['Days Until Deadline'] <= 7:
            return ['background-color: #ffffcc'] * len(row)  # Yellow for moderate
        else:
            return ['background-color: #ccffcc'] * len(row)  # Green for distant
    
    styled_df = display_df.style.apply(highlight_urgency, axis=1)
    st.dataframe(styled_df, width="stretch")

def display_schedule_table(schedule):
    """Display the generated schedule in a table format."""
    if not schedule:
        st.info("No schedule generated yet. Add subjects and click 'Generate Schedule'.")
        return
    
    st.header("📅 Your Optimized Study Schedule")
    
    # Create DataFrame
    df = pd.DataFrame(schedule)
    
    # Format time columns
    df['start_time_str'] = df['start_time'].apply(lambda x: x.strftime("%H:%M"))
    df['end_time_str'] = df['end_time'].apply(lambda x: x.strftime("%H:%M"))
    df['date_str'] = df['date'].apply(lambda x: x.strftime("%Y-%m-%d (%A)"))
    
    # Create display DataFrame
    display_df = df[[
        'date_str', 'start_time_str', 'end_time_str', 
        'subject', 'duration_minutes', 'type'
    ]].copy()
    
    display_df.columns = [
        'Date', 'Start Time', 'End Time', 
        'Subject', 'Duration (min)', 'Type'
    ]
    
    # Color code by type
    def highlight_type(row):
        if row['Type'] == 'break':
            return ['background-color: #fff2cc'] * len(row)  # Light yellow for breaks
        else:
            return ['background-color: #e1f5fe'] * len(row)  # Light blue for study
    
    styled_df = display_df.style.apply(highlight_type, axis=1)
    st.dataframe(styled_df, width="stretch")

def create_schedule_visualization(schedule):
    """Create interactive visualizations of the study schedule."""
    if not schedule:
        return
    
    df = pd.DataFrame(schedule)
    
    # Timeline visualization
    st.subheader("📊 Schedule Timeline")
    
    # Create Gantt chart
    fig = go.Figure()
    
    colors = {
        'study': '#1f77b4',
        'break': '#ff7f0e'
    }
    
    for _, session in df.iterrows():
        start_datetime = datetime.combine(session['date'], session['start_time'])
        end_datetime = datetime.combine(session['date'], session['end_time'])
        
        fig.add_trace(go.Scatter(
            x=[start_datetime, end_datetime, end_datetime, start_datetime, start_datetime],
            y=[session['subject'], session['subject'], session['subject'], session['subject'], session['subject']],
            fill='toself',
            fillcolor=colors.get(session['type'], '#1f77b4'),
            line=dict(color=colors.get(session['type'], '#1f77b4')),
            name=f"{session['subject']} ({session['type']})",
            hovertemplate=f"<b>{session['subject']}</b><br>" +
                         f"Date: {session['date']}<br>" +
                         f"Time: {session['start_time']} - {session['end_time']}<br>" +
                         f"Duration: {session['duration_minutes']} min<br>" +
                         f"Type: {session['type']}<extra></extra>",
            showlegend=False
        ))
    
    fig.update_layout(
        title="Study Schedule Timeline",
        xaxis_title="Date and Time",
        yaxis_title="Subject",
        height=600
    )
    
    st.plotly_chart(fig, width="stretch")
    
    # Daily study hours chart
    st.subheader("📈 Daily Study Hours")
    
    daily_study = df[df['type'] == 'study'].groupby('date')['duration_minutes'].sum() / 60
    
    fig2 = px.bar(
        x=daily_study.index,
        y=daily_study.values,
        title="Study Hours per Day",
        labels={'x': 'Date', 'y': 'Study Hours'}
    )
    
    fig2.update_layout(height=400)
    st.plotly_chart(fig2, width="stretch")

def export_to_google_calendar(schedule):
    """Generate an iCal file for Google Calendar export."""
    if not schedule:
        st.warning("No schedule to export.")
        return
    
    st.subheader("📤 Export to Google Calendar")
    
    if st.button("Generate Calendar File"):
        # Create calendar
        cal = Calendar()
        cal.add('prodid', '-//Schedulyze//Study Scheduler//EN')
        cal.add('version', '2.0')
        
        for session in schedule:
            event = Event()
            
            # Event details
            start_datetime = datetime.combine(session['date'], session['start_time'])
            end_datetime = datetime.combine(session['date'], session['end_time'])
            
            event.add('summary', f"Study: {session['subject']}" if session['type'] == 'study' else "Break")
            event.add('dtstart', start_datetime)
            event.add('dtend', end_datetime)
            
            if session['type'] == 'study':
                event.add('description', 
                         f"Subject: {session['subject']}\n"
                         f"Duration: {session['duration_minutes']} minutes\n"
                         f"Difficulty: {session['difficulty']}/10\n"
                         f"Priority Score: {session['priority_score']:.1f}")
            else:
                event.add('description', f"Break time - {session['duration_minutes']} minutes")
            
            cal.add_component(event)
        
        # Create download
        calendar_data = cal.to_ical().decode('utf-8')
        
        st.download_button(
            label="📥 Download Calendar File (.ics)",
            data=calendar_data,
            file_name="schedulyze_study_schedule.ics",
            mime="text/calendar",
            help="Download this file and import it into Google Calendar or any other calendar application"
        )
        
        st.success("Calendar file generated! Click the download button above.")

def main():
    """Main application function."""
    # Title and description
    st.markdown('<h1 class="main-header">📚 Schedulyze</h1>', unsafe_allow_html=True)
    st.markdown(
        "<p style='text-align: center; font-size: 1.2rem; color: #666;'>"
        "AI-Powered Study Scheduler for Optimal Learning"
        "</p>", 
        unsafe_allow_html=True
    )
    
    # Initialize session state for subjects
    if 'subjects' not in st.session_state:
        st.session_state.subjects = []
    if 'schedule' not in st.session_state:
        st.session_state.schedule = []
    
    # Sidebar settings
    settings = create_sidebar_settings()
    
    # Main content area
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Subject input form
        new_subject = create_subject_input_form()
        if new_subject:
            st.session_state.subjects.append(new_subject)
            st.success(f"Added subject: {new_subject['name']}")
            st.rerun()
        
        # Display subjects
        display_subjects_table(st.session_state.subjects)
    
    with col2:
        st.header("🎯 Quick Actions")
        
        # Clear all subjects
        if st.button("🗑️ Clear All Subjects", type="secondary"):
            st.session_state.subjects = []
            st.session_state.schedule = []
            st.success("All subjects cleared!")
            st.rerun()
        
        # Remove last subject
        if st.session_state.subjects and st.button("↩️ Remove Last Subject"):
            removed = st.session_state.subjects.pop()
            st.success(f"Removed: {removed['name']}")
            st.rerun()
        
        # Generate schedule button
        if st.session_state.subjects:
            if st.button("✨ Generate Optimized Schedule", type="primary"):
                scheduler = StudyScheduler()
                st.session_state.schedule = scheduler.generate_optimized_schedule(
                    st.session_state.subjects, 
                    settings
                )
                st.success("Schedule generated successfully!")
                st.rerun()
    
    # Display schedule if generated
    if st.session_state.schedule:
        st.divider()
        
        # Schedule table
        display_schedule_table(st.session_state.schedule)
        
        # Visualizations
        create_schedule_visualization(st.session_state.schedule)
        
        # Export options
        export_to_google_calendar(st.session_state.schedule)
    
    # Footer
    st.divider()
    st.markdown(
        "<p style='text-align: center; color: #999; font-size: 0.9rem;'>"
        "Made with ❤️ using Streamlit | Schedulyze v1.0"
        "</p>", 
        unsafe_allow_html=True
    )

if __name__ == "__main__":
    main()

"""
Schedulyze Demo Script
This script demonstrates the core functionality of the Schedulyze application
without the Streamlit interface for testing purposes.
"""

from datetime import datetime, timedelta, time
import json

class StudySchedulerDemo:
    """
    Demo version of the AI-powered study scheduler that can run without Streamlit.
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
        for day_offset in range(7):  # Generate for 1 week in demo
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
                    'date': study_date.strftime('%Y-%m-%d'),
                    'start_time': session_start_time.strftime('%H:%M'),
                    'end_time': session_end_time.strftime('%H:%M'),
                    'subject': subject['name'],
                    'duration_minutes': session_duration,
                    'type': 'study',
                    'priority_score': round(self.calculate_priority_score(subject), 1),
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
                        'date': study_date.strftime('%Y-%m-%d'),
                        'start_time': break_start.strftime('%H:%M'),
                        'end_time': break_end.strftime('%H:%M'),
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
            
            schedule.extend(daily_sessions)
        
        return schedule

def demo_schedulyze():
    """
    Demonstrate the Schedulyze functionality with sample data.
    """
    print("🎓 Schedulyze Demo - AI-Powered Study Scheduler")
    print("=" * 50)
    
    # Create scheduler instance
    scheduler = StudySchedulerDemo()
    
    # Sample subjects with different priorities
    sample_subjects = [
        {
            'name': 'Mathematics',
            'deadline': datetime.now().date() + timedelta(days=3),
            'hours_needed': 12.0,
            'difficulty': 8
        },
        {
            'name': 'History',
            'deadline': datetime.now().date() + timedelta(days=7),
            'hours_needed': 8.0,
            'difficulty': 5
        },
        {
            'name': 'Physics',
            'deadline': datetime.now().date() + timedelta(days=2),
            'hours_needed': 15.0,
            'difficulty': 9
        },
        {
            'name': 'Literature',
            'deadline': datetime.now().date() + timedelta(days=10),
            'hours_needed': 6.0,
            'difficulty': 4
        }
    ]
    
    # Sample settings
    settings = {
        'session_length': 90,  # 90 minutes
        'break_length': 20,    # 20 minutes
        'daily_hours': 6.0,    # 6 hours per day
        'start_date': datetime.now().date(),
        'start_time': time(9, 0),  # 9:00 AM
        'include_weekends': False
    }
    
    print("\n📚 Sample Subjects:")
    print("-" * 30)
    for subject in sample_subjects:
        priority = scheduler.calculate_priority_score(subject)
        print(f"• {subject['name']}")
        print(f"  Deadline: {subject['deadline']}")
        print(f"  Hours needed: {subject['hours_needed']}")
        print(f"  Difficulty: {subject['difficulty']}/10")
        print(f"  Priority Score: {priority:.1f}")
        print()
    
    print("\n⚙️ Settings:")
    print("-" * 30)
    print(f"• Session Length: {settings['session_length']} minutes")
    print(f"• Break Length: {settings['break_length']} minutes")
    print(f"• Daily Study Hours: {settings['daily_hours']} hours")
    print(f"• Start Date: {settings['start_date']}")
    print(f"• Start Time: {settings['start_time']}")
    print(f"• Include Weekends: {settings['include_weekends']}")
    
    # Generate optimized schedule
    print("\n✨ Generating Optimized Schedule...")
    schedule = scheduler.generate_optimized_schedule(sample_subjects, settings)
    
    print(f"\n📅 Your Optimized Study Schedule ({len(schedule)} sessions):")
    print("-" * 60)
    
    current_date = None
    for session in schedule:
        # Print date header for new days
        if session['date'] != current_date:
            current_date = session['date']
            day_name = datetime.strptime(session['date'], '%Y-%m-%d').strftime('%A')
            print(f"\n📆 {session['date']} ({day_name})")
            print("-" * 40)
        
        # Print session details
        if session['type'] == 'study':
            print(f"  📖 {session['start_time']} - {session['end_time']} | "
                  f"{session['subject']} ({session['duration_minutes']}min) "
                  f"[Priority: {session['priority_score']}, Difficulty: {session['difficulty']}/10]")
        else:
            print(f"  ☕ {session['start_time']} - {session['end_time']} | "
                  f"Break ({session['duration_minutes']}min)")
    
    # Calculate statistics
    study_sessions = [s for s in schedule if s['type'] == 'study']
    total_study_hours = sum(s['duration_minutes'] for s in study_sessions) / 60
    total_break_time = sum(s['duration_minutes'] for s in schedule if s['type'] == 'break') / 60
    
    print(f"\n📊 Schedule Statistics:")
    print("-" * 30)
    print(f"• Total Study Sessions: {len(study_sessions)}")
    print(f"• Total Study Hours: {total_study_hours:.1f} hours")
    print(f"• Total Break Time: {total_break_time:.1f} hours")
    print(f"• Average Session Length: {sum(s['duration_minutes'] for s in study_sessions) / len(study_sessions):.0f} minutes")
    
    # Subject breakdown
    print(f"\n📚 Study Time by Subject:")
    print("-" * 30)
    subject_time = {}
    for session in study_sessions:
        subject = session['subject']
        if subject not in subject_time:
            subject_time[subject] = 0
        subject_time[subject] += session['duration_minutes'] / 60
    
    for subject, hours in sorted(subject_time.items(), key=lambda x: x[1], reverse=True):
        print(f"• {subject}: {hours:.1f} hours")
    
    print(f"\n🎯 Priority-based scheduling ensures urgent and difficult subjects get adequate attention!")
    print("💡 The AI optimizes your study time based on deadlines, difficulty, and available hours.")
    
    return schedule

if __name__ == "__main__":
    demo_schedulyze()
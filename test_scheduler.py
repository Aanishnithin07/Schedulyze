"""
Schedulyze - Basic AI-powered study scheduler (Standalone Version)
This version uses minimal dependencies for initial testing.
"""

import json
from datetime import datetime, timedelta, date
from typing import List, Dict, Tuple

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
    Command line version for testing the core functionality.
    """
    print("📚 Schedulyze - AI Study Scheduler (Test Version)")
    print("=" * 50)
    
    # Sample data for testing
    sample_subjects = [
        {
            'name': 'Mathematics',
            'deadline': date.today() + timedelta(days=7),
            'study_hours': 10,
            'difficulty': 4,
            'importance': 5
        },
        {
            'name': 'Physics',
            'deadline': date.today() + timedelta(days=14),
            'study_hours': 8,
            'difficulty': 3,
            'importance': 4
        },
        {
            'name': 'Chemistry',
            'deadline': date.today() + timedelta(days=21),
            'study_hours': 6,
            'difficulty': 2,
            'importance': 3
        }
    ]
    
    # Initialize optimizer
    optimizer = StudyScheduleOptimizer()
    
    # Generate schedule
    schedule = optimizer.generate_schedule(
        subjects=sample_subjects,
        start_date=date.today(),
        daily_hours=6,
        session_length=45,
        break_length=15,
        start_time="09:00"
    )
    
    # Display results
    print("\n📊 Priority Analysis:")
    for subject in sample_subjects:
        priority = optimizer.calculate_priority_score(
            subject['deadline'],
            subject['difficulty'], 
            subject['importance']
        )
        print(f"  {subject['name']}: Priority Score = {priority:.3f}")
    
    print(f"\n📅 Generated {len([s for s in schedule if s['type'] == 'Study'])} study sessions")
    print(f"📅 Schedule covers {len(set(s['date'] for s in schedule))} days")
    
    # Show first few days
    print("\n📋 First 3 days schedule:")
    unique_dates = sorted(set(s['date'] for s in schedule))[:3]
    
    for day in unique_dates:
        print(f"\n{day.strftime('%A, %B %d, %Y')}:")
        day_schedule = [s for s in schedule if s['date'] == day]
        for session in day_schedule:
            print(f"  {session['start_time']}-{session['end_time']}: {session['subject']} ({session['type']})")
    
    # Create CSV export
    csv_export = create_google_calendar_export(schedule)
    print(f"\n📤 Google Calendar CSV generated ({len(csv_export.split('\n'))} lines)")
    
    return True

if __name__ == "__main__":
    main()
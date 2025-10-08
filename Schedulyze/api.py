from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import List, Optional
import pandas as pd
import numpy as np
from datetime import datetime, date, timedelta
import json
from icalendar import Calendar, Event
import io

app = FastAPI(title="Schedulyze API", description="AI-Powered Study Scheduler API")

# Pydantic models for API requests
class Subject(BaseModel):
    name: str
    deadline: date
    hours_needed: float
    difficulty: int
    description: Optional[str] = ""

class ScheduleSettings(BaseModel):
    session_length: int = 90
    break_length: int = 15
    daily_hours: int = 8
    start_time: str = "09:00"
    end_time: str = "17:00"
    include_weekends: bool = True

class StudyScheduler:
    """
    AI-powered study scheduler that optimizes study sessions based on
    deadlines, difficulty, and available time.
    """
    
    def __init__(self):
        self.subjects = []
        self.schedule = []
    
    def calculate_priority_score(self, subject):
        """Calculate priority score based on deadline urgency and difficulty."""
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
        """Generate an optimized study schedule using AI logic."""
        schedule = []
        
        # Convert subjects to dictionary format
        subjects_dict = []
        for subject in subjects:
            subject_data = subject.dict()
            subject_data['priority_score'] = self.calculate_priority_score(subject_data)
            subjects_dict.append(subject_data)
        
        # Sort by priority score (highest first)
        subjects_dict.sort(key=lambda x: x['priority_score'], reverse=True)
        
        current_date = datetime.now().date()
        
        for subject in subjects_dict:
            hours_remaining = subject['hours_needed']
            subject_name = subject['name']
            
            # Distribute hours across available days
            days_available = (subject['deadline'] - current_date).days + 1
            
            if days_available <= 0:
                continue  # Skip overdue subjects for now
            
            # Calculate sessions per day
            session_duration_hours = settings.session_length / 60
            max_sessions_per_day = settings.daily_hours // (settings.session_length / 60)
            
            for day_offset in range(days_available):
                study_date = current_date + timedelta(days=day_offset)
                
                # Skip weekends if not included
                if not settings.include_weekends and study_date.weekday() >= 5:
                    continue
                
                # Calculate how many hours to study this subject today
                remaining_days = days_available - day_offset
                hours_today = min(
                    hours_remaining / max(remaining_days, 1),
                    settings.daily_hours,
                    hours_remaining
                )
                
                if hours_today > 0:
                    # Create study sessions
                    sessions_today = int(np.ceil(hours_today / session_duration_hours))
                    
                    start_time = datetime.strptime(settings.start_time, "%H:%M").time()
                    current_time = datetime.combine(study_date, start_time)
                    
                    for session in range(sessions_today):
                        session_duration = min(
                            session_duration_hours,
                            hours_remaining
                        )
                        
                        if session_duration <= 0:
                            break
                        
                        end_time = current_time + timedelta(hours=session_duration)
                        
                        schedule.append({
                            'date': study_date.strftime('%Y-%m-%d'),
                            'start_time': current_time.strftime('%H:%M'),
                            'end_time': end_time.strftime('%H:%M'),
                            'subject': subject_name,
                            'duration_hours': session_duration,
                            'session_type': 'Study',
                            'priority_score': subject['priority_score'],
                            'difficulty': subject['difficulty']
                        })
                        
                        hours_remaining -= session_duration
                        current_time = end_time + timedelta(minutes=settings.break_length)
                        
                        # Add break if not the last session
                        if session < sessions_today - 1 and hours_remaining > 0:
                            break_end = current_time
                            schedule.append({
                                'date': study_date.strftime('%Y-%m-%d'),
                                'start_time': (current_time - timedelta(minutes=settings.break_length)).strftime('%H:%M'),
                                'end_time': break_end.strftime('%H:%M'),
                                'subject': 'Break',
                                'duration_hours': settings.break_length / 60,
                                'session_type': 'Break',
                                'priority_score': 0,
                                'difficulty': 0
                            })
                
                if hours_remaining <= 0:
                    break
        
        return sorted(schedule, key=lambda x: (x['date'], x['start_time']))

scheduler = StudyScheduler()

@app.get("/", response_class=HTMLResponse)
async def root():
    """Serve the main HTML page."""
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Schedulyze - AI Study Scheduler</title>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <style>
            body { font-family: Arial, sans-serif; max-width: 1200px; margin: 0 auto; padding: 20px; }
            .header { text-align: center; color: #1f77b4; margin-bottom: 30px; }
            .form-group { margin-bottom: 15px; }
            .form-group label { display: block; margin-bottom: 5px; font-weight: bold; }
            .form-group input, select { width: 100%; padding: 8px; border: 1px solid #ddd; border-radius: 4px; }
            .btn { background-color: #1f77b4; color: white; padding: 10px 20px; border: none; border-radius: 4px; cursor: pointer; }
            .btn:hover { background-color: #1565c0; }
            .schedule-item { background-color: #e8f4fd; padding: 10px; margin: 5px 0; border-left: 4px solid #1f77b4; border-radius: 4px; }
            .break-item { background-color: #fff3cd; border-left-color: #ffc107; }
            .subjects-container, .schedule-container { margin-top: 20px; }
            .subject-form { background-color: #f8f9fa; padding: 20px; border-radius: 8px; margin-bottom: 20px; }
        </style>
    </head>
    <body>
        <div class="header">
            <h1>📚 Schedulyze - AI Study Scheduler</h1>
            <p>AI-powered personalized study scheduler for maximum productivity</p>
        </div>

        <div class="subject-form">
            <h2>Add Subject</h2>
            <form id="subjectForm">
                <div class="form-group">
                    <label>Subject Name:</label>
                    <input type="text" id="subjectName" required>
                </div>
                <div class="form-group">
                    <label>Deadline:</label>
                    <input type="date" id="deadline" required>
                </div>
                <div class="form-group">
                    <label>Hours Needed:</label>
                    <input type="number" id="hoursNeeded" min="0.5" step="0.5" required>
                </div>
                <div class="form-group">
                    <label>Difficulty (1-10):</label>
                    <select id="difficulty" required>
                        <option value="1">1 - Very Easy</option>
                        <option value="2">2 - Easy</option>
                        <option value="3">3 - Quite Easy</option>
                        <option value="4">4 - Slightly Easy</option>
                        <option value="5" selected>5 - Medium</option>
                        <option value="6">6 - Slightly Hard</option>
                        <option value="7">7 - Hard</option>
                        <option value="8">8 - Quite Hard</option>
                        <option value="9">9 - Very Hard</option>
                        <option value="10">10 - Extremely Hard</option>
                    </select>
                </div>
                <button type="button" class="btn" onclick="addSubject()">Add Subject</button>
            </form>
        </div>

        <div class="subjects-container">
            <h2>Subjects</h2>
            <div id="subjectsList"></div>
        </div>

        <div class="schedule-container">
            <h2>Generated Schedule</h2>
            <button type="button" class="btn" onclick="generateSchedule()">Generate Schedule</button>
            <div id="scheduleList"></div>
        </div>

        <script>
            let subjects = [];

            function addSubject() {
                const name = document.getElementById('subjectName').value;
                const deadline = document.getElementById('deadline').value;
                const hoursNeeded = parseFloat(document.getElementById('hoursNeeded').value);
                const difficulty = parseInt(document.getElementById('difficulty').value);

                if (name && deadline && hoursNeeded && difficulty) {
                    subjects.push({ name, deadline, hours_needed: hoursNeeded, difficulty });
                    displaySubjects();
                    document.getElementById('subjectForm').reset();
                }
            }

            function displaySubjects() {
                const list = document.getElementById('subjectsList');
                list.innerHTML = subjects.map((subject, index) => 
                    `<div class="schedule-item">
                        <strong>${subject.name}</strong> - Due: ${subject.deadline}, Hours: ${subject.hours_needed}, Difficulty: ${subject.difficulty}
                        <button onclick="removeSubject(${index})" style="float: right; background: #dc3545; color: white; border: none; padding: 5px 10px; border-radius: 3px;">Remove</button>
                    </div>`
                ).join('');
            }

            function removeSubject(index) {
                subjects.splice(index, 1);
                displaySubjects();
            }

            async function generateSchedule() {
                if (subjects.length === 0) {
                    alert('Please add at least one subject');
                    return;
                }

                const settings = {
                    session_length: 90,
                    break_length: 15,
                    daily_hours: 8,
                    start_time: "09:00",
                    end_time: "17:00",
                    include_weekends: true
                };

                try {
                    const response = await fetch('/api/generate-schedule', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ subjects, settings })
                    });

                    const schedule = await response.json();
                    displaySchedule(schedule);
                } catch (error) {
                    console.error('Error generating schedule:', error);
                    alert('Error generating schedule. Please try again.');
                }
            }

            function displaySchedule(schedule) {
                const list = document.getElementById('scheduleList');
                list.innerHTML = schedule.map(item => 
                    `<div class="${item.session_type === 'Break' ? 'break-item' : 'schedule-item'}">
                        <strong>${item.subject}</strong><br>
                        📅 ${item.date} | ⏰ ${item.start_time} - ${item.end_time} | ⏱️ ${item.duration_hours.toFixed(1)}h
                        ${item.session_type === 'Study' ? `<br>📈 Priority: ${item.priority_score.toFixed(1)} | 🎯 Difficulty: ${item.difficulty}` : ''}
                    </div>`
                ).join('');
            }
        </script>
    </body>
    </html>
    """

@app.post("/api/generate-schedule")
async def generate_schedule_api(request: dict):
    """Generate optimized study schedule via API."""
    try:
        subjects_data = request.get('subjects', [])
        settings_data = request.get('settings', {})
        
        # Convert to Pydantic models
        subjects = [Subject(**subject) for subject in subjects_data]
        settings = ScheduleSettings(**settings_data)
        
        # Generate schedule
        schedule = scheduler.generate_optimized_schedule(subjects, settings)
        
        return schedule
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error generating schedule: {str(e)}")

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "message": "Schedulyze API is running"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
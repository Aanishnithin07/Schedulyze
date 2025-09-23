"""
Schedulyze Demo - A web interface simulator for demonstration
This creates an HTML version of the Schedulyze app to show functionality
when Streamlit is not available.
"""

import pandas as pd
from datetime import datetime, timedelta, date
import json
import webbrowser
import os

# Import our core scheduler
from app_pandas import StudyScheduleOptimizer, create_google_calendar_export

def create_html_demo():
    """
    Create an HTML demo of the Schedulyze application.
    """
    
    # Sample data for demonstration
    sample_subjects = [
        {
            'name': 'Advanced Calculus',
            'deadline': date.today() + timedelta(days=5),
            'study_hours': 15,
            'difficulty': 5,
            'importance': 5
        },
        {
            'name': 'Organic Chemistry',
            'deadline': date.today() + timedelta(days=10),
            'study_hours': 12,
            'difficulty': 4,
            'importance': 4
        },
        {
            'name': 'World History',
            'deadline': date.today() + timedelta(days=14),
            'study_hours': 8,
            'difficulty': 2,
            'importance': 3
        },
        {
            'name': 'Data Structures',
            'deadline': date.today() + timedelta(days=7),
            'study_hours': 10,
            'difficulty': 4,
            'importance': 5
        }
    ]
    
    # Generate schedule
    optimizer = StudyScheduleOptimizer()
    schedule = optimizer.generate_schedule(
        subjects=sample_subjects,
        start_date=date.today(),
        daily_hours=6,
        session_length=45,
        break_length=15,
        start_time="09:00",
        include_weekends=False
    )
    
    # Create priority analysis
    priority_data = []
    for subject in sample_subjects:
        priority = optimizer.calculate_priority_score(
            subject['deadline'],
            subject['difficulty'],
            subject['importance']
        )
        priority_data.append({
            'Subject': subject['name'],
            'Priority Score': f"{priority:.3f}",
            'Difficulty': subject['difficulty'],
            'Importance': subject['importance'],
            'Days Until Deadline': (subject['deadline'] - date.today()).days,
            'Deadline': subject['deadline'].strftime('%Y-%m-%d')
        })
    
    # Filter study sessions
    study_sessions = [s for s in schedule if s['type'] == 'Study']
    
    # Calculate statistics
    total_sessions = len(study_sessions)
    total_hours = sum(s['duration'] for s in study_sessions) / 60
    unique_days = len(set(s['date'] for s in study_sessions))
    avg_daily_hours = total_hours / max(unique_days, 1)
    
    # Generate daily schedule view (first 5 days)
    daily_schedule_html = ""
    dates = sorted(set(s['date'] for s in study_sessions))[:5]
    
    for current_date in dates:
        day_sessions = [s for s in study_sessions if s['date'] == current_date]
        daily_schedule_html += f"""
        <div class="day-schedule">
            <h4>{current_date.strftime('%A, %B %d, %Y')}</h4>
            <div class="sessions">
        """
        
        for session in day_sessions:
            daily_schedule_html += f"""
                <div class="session">
                    🕒 {session['start_time']}-{session['end_time']}: 
                    <strong>{session['subject']}</strong> 
                    ({session['duration']} min)
                </div>
            """
        
        daily_schedule_html += "</div></div>"
    
    # Create HTML content
    html_content = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Schedulyze - AI Study Scheduler Demo</title>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 0;
            padding: 20px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
        }}
        
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 15px;
            box-shadow: 0 20px 40px rgba(0,0,0,0.1);
            overflow: hidden;
        }}
        
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 40px;
            text-align: center;
        }}
        
        .header h1 {{
            margin: 0;
            font-size: 2.5em;
            margin-bottom: 10px;
        }}
        
        .header p {{
            margin: 0;
            font-size: 1.2em;
            opacity: 0.9;
        }}
        
        .content {{
            padding: 40px;
        }}
        
        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-bottom: 40px;
        }}
        
        .stat-card {{
            background: #f8f9fa;
            padding: 20px;
            border-radius: 10px;
            text-align: center;
            border-left: 4px solid #667eea;
        }}
        
        .stat-value {{
            font-size: 2em;
            font-weight: bold;
            color: #667eea;
            margin-bottom: 5px;
        }}
        
        .stat-label {{
            color: #666;
            font-size: 0.9em;
        }}
        
        .section {{
            margin-bottom: 40px;
        }}
        
        .section h2 {{
            color: #333;
            border-bottom: 2px solid #667eea;
            padding-bottom: 10px;
            margin-bottom: 20px;
        }}
        
        table {{
            width: 100%;
            border-collapse: collapse;
            margin-bottom: 20px;
            background: white;
            border-radius: 8px;
            overflow: hidden;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}
        
        th, td {{
            padding: 12px;
            text-align: left;
            border-bottom: 1px solid #eee;
        }}
        
        th {{
            background: #667eea;
            color: white;
            font-weight: 600;
        }}
        
        tr:hover {{
            background: #f8f9fa;
        }}
        
        .day-schedule {{
            background: #f8f9fa;
            margin-bottom: 20px;
            padding: 20px;
            border-radius: 8px;
            border-left: 4px solid #667eea;
        }}
        
        .day-schedule h4 {{
            margin: 0 0 15px 0;
            color: #333;
        }}
        
        .session {{
            padding: 8px 0;
            border-bottom: 1px solid #eee;
        }}
        
        .session:last-child {{
            border-bottom: none;
        }}
        
        .feature-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }}
        
        .feature-card {{
            background: #f8f9fa;
            padding: 25px;
            border-radius: 10px;
            text-align: center;
        }}
        
        .feature-icon {{
            font-size: 3em;
            margin-bottom: 15px;
        }}
        
        .download-btn {{
            background: #667eea;
            color: white;
            padding: 12px 24px;
            border: none;
            border-radius: 5px;
            cursor: pointer;
            font-size: 16px;
            margin: 10px;
            text-decoration: none;
            display: inline-block;
        }}
        
        .download-btn:hover {{
            background: #5a6fd8;
        }}
        
        .note {{
            background: #e8f4fd;
            padding: 20px;
            border-radius: 8px;
            border-left: 4px solid #17a2b8;
            margin: 20px 0;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>📚 Schedulyze - AI Study Scheduler</h1>
            <p>AI-powered personalized study scheduler that optimizes your study sessions, deadlines, and breaks for maximum productivity</p>
        </div>
        
        <div class="content">
            <div class="note">
                <strong>🚀 Demo Version:</strong> This is a demonstration of the Schedulyze AI study scheduler. 
                The actual Streamlit app provides interactive features for adding subjects, configuring settings, and real-time schedule generation.
            </div>
            
            <div class="feature-grid">
                <div class="feature-card">
                    <div class="feature-icon">🧠</div>
                    <h3>Smart AI Prioritization</h3>
                    <p>Automatically prioritizes subjects based on deadlines, difficulty, and importance</p>
                </div>
                <div class="feature-card">
                    <div class="feature-icon">⏰</div>
                    <h3>Optimized Sessions</h3>
                    <p>Creates focused study blocks with intelligent break scheduling</p>
                </div>
                <div class="feature-card">
                    <div class="feature-icon">📅</div>
                    <h3>Calendar Export</h3>
                    <p>Export your schedule to Google Calendar with one click</p>
                </div>
                <div class="feature-card">
                    <div class="feature-icon">⚙️</div>
                    <h3>Flexible Settings</h3>
                    <p>Customize session length, breaks, daily hours, and preferences</p>
                </div>
            </div>
            
            <div class="section">
                <h2>📊 Schedule Overview</h2>
                <div class="stats-grid">
                    <div class="stat-card">
                        <div class="stat-value">{total_sessions}</div>
                        <div class="stat-label">Total Study Sessions</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-value">{total_hours:.1f}</div>
                        <div class="stat-label">Total Study Hours</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-value">{unique_days}</div>
                        <div class="stat-label">Study Days</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-value">{avg_daily_hours:.1f}</div>
                        <div class="stat-label">Avg Daily Hours</div>
                    </div>
                </div>
            </div>
            
            <div class="section">
                <h2>🎯 AI Priority Analysis</h2>
                <table>
                    <thead>
                        <tr>
                            <th>Subject</th>
                            <th>Priority Score</th>
                            <th>Difficulty</th>
                            <th>Importance</th>
                            <th>Days Left</th>
                            <th>Deadline</th>
                        </tr>
                    </thead>
                    <tbody>
    """
    
    # Add priority data to table
    priority_data_sorted = sorted(priority_data, key=lambda x: float(x['Priority Score']), reverse=True)
    for row in priority_data_sorted:
        html_content += f"""
                        <tr>
                            <td><strong>{row['Subject']}</strong></td>
                            <td>{row['Priority Score']}</td>
                            <td>{row['Difficulty']}/5</td>
                            <td>{row['Importance']}/5</td>
                            <td>{row['Days Until Deadline']}</td>
                            <td>{row['Deadline']}</td>
                        </tr>
        """
    
    html_content += f"""
                    </tbody>
                </table>
            </div>
            
            <div class="section">
                <h2>📅 Sample Study Schedule (First 5 Days)</h2>
                {daily_schedule_html}
            </div>
            
            <div class="section">
                <h2>📤 Export Options</h2>
                <p>In the full Streamlit app, you can export your schedule to Google Calendar:</p>
                <button class="download-btn" onclick="downloadCSV()">📅 Download Sample Calendar CSV</button>
                
                <div class="note">
                    <strong>How to import into Google Calendar:</strong>
                    <ol>
                        <li>Download the CSV file</li>
                        <li>Go to Google Calendar</li>
                        <li>Click the '+' next to 'Other calendars'</li>
                        <li>Select 'Import'</li>
                        <li>Choose the downloaded CSV file</li>
                        <li>Select which calendar to import to</li>
                        <li>Click 'Import'</li>
                    </ol>
                </div>
            </div>
            
            <div class="section">
                <h2>🚀 Getting Started</h2>
                <p>To run the full interactive Schedulyze application:</p>
                <ol>
                    <li>Install Streamlit: <code>pip install streamlit</code></li>
                    <li>Run the app: <code>streamlit run app.py</code></li>
                    <li>Add your subjects with deadlines and preferences</li>
                    <li>Generate your optimized study schedule</li>
                    <li>Export to Google Calendar</li>
                </ol>
            </div>
        </div>
    </div>
    
    <script>
        function downloadCSV() {{
            const csvContent = `{create_google_calendar_export(schedule).replace('`', '\\`')}`;
            const blob = new Blob([csvContent], {{ type: 'text/csv' }});
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = 'schedulyze_demo_{date.today().strftime("%Y-%m-%d")}.csv';
            a.click();
            window.URL.revokeObjectURL(url);
        }}
    </script>
</body>
</html>
    """
    
    return html_content

def main():
    """
    Create and open the HTML demo.
    """
    print("📚 Creating Schedulyze HTML Demo...")
    
    # Create HTML content
    html_content = create_html_demo()
    
    # Save to file
    demo_file = "/home/runner/work/Schedulyze/Schedulyze/schedulyze_demo.html"
    with open(demo_file, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print(f"✅ Demo created: {demo_file}")
    print("🌐 The HTML demo showcases the Schedulyze AI study scheduler functionality")
    print("📋 Features demonstrated:")
    print("   - AI priority scoring algorithm")
    print("   - Optimized study schedule generation")
    print("   - Statistics and analytics")
    print("   - Google Calendar export format")
    print("   - Professional UI design")
    
    return demo_file

if __name__ == "__main__":
    main()
# 📚 Schedulyze - AI-Powered Study Scheduler

An intelligent Streamlit application that helps students create optimized study schedules using AI logic. Schedulyze prioritizes subjects based on deadlines, difficulty levels, and study hours needed, while incorporating breaks and personal preferences.

## ✨ Features

### 🎯 Core Functionality
- **Smart Subject Management**: Add subjects with deadlines, study hours needed, and difficulty levels
- **AI-Powered Scheduling**: Intelligent algorithm that prioritizes urgent and difficult subjects
- **Optimized Time Management**: Automatic break scheduling between study sessions
- **Visual Schedule Display**: Interactive tables and charts showing your study plan

### ⚙️ Customizable Settings
- **Session Length**: Configure study session duration (15-180 minutes)
- **Break Length**: Set break duration between sessions (5-60 minutes)
- **Daily Study Hours**: Define total daily study time (1-12 hours)
- **Schedule Timing**: Set start date and daily start time
- **Weekend Options**: Include or exclude weekend study sessions

### 📊 Visualizations
- **Schedule Timeline**: Interactive Gantt chart showing your study sessions
- **Daily Study Hours**: Bar chart tracking study hours per day
- **Priority-based Color Coding**: Visual indicators for urgency and importance

### 📅 Export Options
- **Google Calendar Integration**: Export schedule as .ics file
- **Easy Import**: Compatible with all major calendar applications

## 🚀 Getting Started

### Prerequisites
- Python 3.8 or higher
- pip package manager

### Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/Aanishnithin07/Schedulyze.git
   cd Schedulyze/Schedulyze
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application**:
   ```bash
   streamlit run app.py
   ```

4. **Open your browser** and navigate to `http://localhost:8501`

## 🎮 How to Use

### 1. Configure Settings (Sidebar)
- **Session Configuration**: Set your preferred study session and break lengths
- **Schedule Timing**: Choose when to start and how many hours to study daily
- **Weekend Preferences**: Decide whether to include weekend study sessions

### 2. Add Subjects
- **Subject Name**: Enter the name of your subject (e.g., "Mathematics", "History")
- **Deadline**: Set the exam or assignment deadline
- **Study Hours Needed**: Estimate total hours required to study this subject
- **Difficulty Level**: Rate difficulty from 1 (easy) to 10 (very hard)

### 3. Generate Your Schedule
- Click **"Generate Optimized Schedule"** after adding subjects
- The AI will create a prioritized study plan based on:
  - **Deadline urgency**: Subjects due sooner get higher priority
  - **Difficulty level**: Harder subjects receive more focused attention
  - **Study hours needed**: Subjects requiring more time are scheduled appropriately

### 4. View Your Schedule
- **Table View**: See all sessions with dates, times, and subjects
- **Timeline Visualization**: Interactive Gantt chart of your study plan
- **Daily Study Hours**: Track your daily study time commitment

### 5. Export to Calendar
- Click **"Generate Calendar File"** to create an .ics file
- Import the file into Google Calendar, Outlook, or any calendar app
- Get reminders and sync across all your devices

## 🧠 AI Scheduling Algorithm

Schedulyze uses an intelligent priority scoring system:

### Priority Score Calculation
```
Priority Score = Urgency Score × (1 + Difficulty Factor + Hours Factor)
```

Where:
- **Urgency Score**: Based on days until deadline (100 for overdue, 90 for due tomorrow, etc.)
- **Difficulty Factor**: Subject difficulty (1-10 scale) divided by 10
- **Hours Factor**: Normalized hours needed (capped at 1.0)

### Scheduling Logic
1. **Sort by Priority**: Subjects with higher scores are scheduled first
2. **Optimize Daily Time**: Distribute study hours across available days
3. **Smart Session Management**: Break long study periods into manageable sessions
4. **Automatic Breaks**: Insert breaks between study sessions for better retention
5. **Weekend Handling**: Respect user preferences for weekend studying

## 📁 Project Structure

```
Schedulyze/
├── app.py                 # Main Streamlit application
├── schedulyze_demo.py     # Demo script (no Streamlit required)
├── requirements.txt       # Python dependencies
├── README.md             # This file
└── test_scheduler.py     # Unit tests for scheduler logic
```

## 🛠️ Technical Details

### Dependencies
- **Streamlit**: Web application framework
- **Pandas**: Data manipulation and analysis
- **NumPy**: Numerical computing
- **Plotly**: Interactive visualizations
- **iCalendar**: Calendar file generation

### Key Classes
- **`StudyScheduler`**: Core AI scheduling logic
- **`create_sidebar_settings()`**: User preference management
- **`create_subject_input_form()`**: Subject data collection
- **`display_schedule_table()`**: Schedule visualization
- **`export_to_google_calendar()`**: Calendar export functionality

## 🎯 Example Usage

### Sample Subject Input
```
Subject: Mathematics
Deadline: 2024-01-15
Hours Needed: 12.0
Difficulty: 8/10
```

### Generated Schedule Output
```
📅 2024-01-10 (Monday)
  📖 09:00 - 10:30 | Mathematics (90min) [Priority: 156.4, Difficulty: 8/10]
  ☕ 10:30 - 10:50 | Break (20min)
  📖 10:50 - 12:20 | Physics (90min) [Priority: 189.2, Difficulty: 9/10]
```

## 🧪 Testing

Run the demo script to test the scheduling algorithm:

```bash
python schedulyze_demo.py
```

This will demonstrate the AI scheduling with sample data and show how the priority algorithm works.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 👨‍💻 Author

**Aanish Nithin**
- GitHub: [@Aanishnithin07](https://github.com/Aanishnithin07)

## 🙏 Acknowledgments

- Built with [Streamlit](https://streamlit.io/)
- Visualizations powered by [Plotly](https://plotly.com/)
- Calendar integration using [iCalendar](https://pypi.org/project/icalendar/)

---

**Made with ❤️ for students who want to optimize their study time!**

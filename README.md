# Schedulyze
AI-powered personalized study scheduler that optimizes your study sessions, deadlines, and breaks for maximum productivity.

## Features

✨ **Core Features:**
- **Smart AI Prioritization**: Automatically prioritizes subjects based on deadlines, difficulty levels, and importance
- **Optimized Study Sessions**: Creates focused study blocks with intelligent break scheduling
- **Multiple Views**: Table view and calendar view of your study schedule
- **Google Calendar Export**: Export your schedule to CSV format for Google Calendar import
- **Flexible Settings**: Customize session length, break duration, daily hours, and start times
- **Weekend Options**: Choose whether to include weekends in your study schedule

## Getting Started

### Prerequisites
- Python 3.7 or higher
- Required packages (install with pip):
  ```bash
  pip install -r requirements.txt
  ```

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/Aanishnithin07/Schedulyze.git
   cd Schedulyze
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Run the Streamlit app:
   ```bash
   streamlit run app.py
   ```

### Alternative: Run without Streamlit
If Streamlit is not available, you can test the core functionality:
```bash
python test_scheduler.py
```

## How to Use

1. **Add Subjects**: Enter your subjects with deadlines, study hours needed, difficulty, and importance levels
2. **Configure Settings**: Use the sidebar to set session length, break duration, daily study hours, and schedule preferences
3. **Generate Schedule**: Click "Generate Optimized Schedule" to create your personalized study plan
4. **View Schedule**: Switch between table view and calendar view to see your schedule
5. **Export**: Download your schedule as a CSV file for Google Calendar import

## AI Algorithm

The Schedulyze AI uses a sophisticated priority scoring system:

- **Urgency Factor (40%)**: Based on how close the deadline is
- **Difficulty Factor (30%)**: Accounts for subject difficulty (1-5 scale)
- **Importance Factor (30%)**: Considers your personal importance rating (1-5 scale)

The algorithm then distributes your daily study hours proportionally based on these priority scores, ensuring you spend more time on urgent and challenging subjects.

## File Structure

- `app.py` - Main Streamlit application (full featured)
- `app_pandas.py` - Pandas-only version (fallback)
- `test_scheduler.py` - Core functionality test script
- `requirements.txt` - Python dependencies
- `.gitignore` - Git ignore file

## Example Usage

The app automatically creates optimized study schedules like this:

```
Tuesday, September 23, 2025:
  09:00-09:45: Mathematics (Study)
  09:45-10:00: Break
  10:00-10:45: Mathematics (Study)
  10:45-11:00: Break
  11:00-11:45: Mathematics (Study)
  11:45-12:00: Break
  12:00-12:21: Mathematics (Study)
  12:21-13:06: Physics (Study)
  ...
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is open source and available under the MIT License.

## Support

If you encounter any issues or have questions, please open an issue on GitHub.

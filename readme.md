1. Basic Run (with CSV files)
powershell
.venv\Scripts\python.exe main.py --courses sample_courses.csv --students sample_students.csv

2. Run + Show Graph Window
powershell
.venv\Scripts\python.exe main.py --courses sample_courses.csv --students sample_students.csv --visualize

3. Custom Output File
powershell
.venv\Scripts\python.exe main.py --courses sample_courses.csv --students sample_students.csv --output my_timetable.csv --image_output my_graph.png

4.web run
node server.js  
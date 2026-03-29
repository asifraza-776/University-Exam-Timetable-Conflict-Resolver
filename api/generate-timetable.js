const formidable = require('formidable');
const fs = require('fs');

// Disable Vercel's default body parser so formidable can handle multipart
module.exports.config = {
  api: { bodyParser: false }
};

// ─── Welsh-Powell Graph Coloring (JavaScript port) ────────────────────────────
class Graph {
  constructor() {
    this.courses = {};   // courseId -> { courseId, name }
    this.adjList = {};   // courseId -> Set of conflicting courseIds
  }

  addCourse(courseId, name) {
    if (!this.courses[courseId]) {
      this.courses[courseId] = { courseId, name };
      this.adjList[courseId] = new Set();
    }
  }

  enrollStudent(studentId, courseIds) {
    for (let i = 0; i < courseIds.length; i++) {
      for (let j = i + 1; j < courseIds.length; j++) {
        const c1 = courseIds[i].trim();
        const c2 = courseIds[j].trim();
        if (this.courses[c1] && this.courses[c2]) {
          this.adjList[c1].add(c2);
          this.adjList[c2].add(c1);
        }
      }
    }
  }

  welshPowell() {
    const sorted = Object.keys(this.courses).sort(
      (a, b) => this.adjList[b].size - this.adjList[a].size
    );
    const colors = {};
    let currentColor = 0;
    const uncolored = [...sorted];

    while (uncolored.length > 0) {
      const first = uncolored[0];
      colors[first] = currentColor;
      const coloredThisRound = [first];

      for (let i = 1; i < uncolored.length; i++) {
        const candidate = uncolored[i];
        const hasConflict = coloredThisRound.some(c => this.adjList[candidate].has(c));
        if (!hasConflict) {
          colors[candidate] = currentColor;
          coloredThisRound.push(candidate);
        }
      }

      for (const c of coloredThisRound) {
        uncolored.splice(uncolored.indexOf(c), 1);
      }
      currentColor++;
    }
    return colors;
  }

  getGraphData(colors) {
    const nodes = Object.keys(this.courses).map(id => ({
      id,
      label: id,
      name: this.courses[id].name,
      slot: colors[id]
    }));

    const edges = [];
    const seen = new Set();
    for (const [from, neighbors] of Object.entries(this.adjList)) {
      for (const to of neighbors) {
        const key = [from, to].sort().join('||');
        if (!seen.has(key)) {
          edges.push({ from, to });
          seen.add(key);
        }
      }
    }
    return { nodes, edges };
  }
}

// ─── CSV Parser ────────────────────────────────────────────────────────────────
function parseCSV(content) {
  const lines = content.trim().split('\n').filter(l => l.trim());
  const headers = lines[0].split(',').map(h => h.trim());
  return lines.slice(1).map(line => {
    const values = line.split(',');
    const obj = {};
    headers.forEach((h, i) => { obj[h] = values[i] ? values[i].trim() : ''; });
    return obj;
  });
}

// ─── API Handler ───────────────────────────────────────────────────────────────
module.exports = async (req, res) => {
  res.setHeader('Access-Control-Allow-Origin', '*');
  if (req.method !== 'POST') {
    return res.status(405).json({ error: 'Method not allowed' });
  }

  const form = new formidable.IncomingForm({ keepExtensions: true });

  form.parse(req, (err, fields, files) => {
    if (err) return res.status(500).json({ error: 'File parse error: ' + err.message });

    try {
      const coursesFile = files.courses?.[0] || files.courses;
      const studentsFile = files.students?.[0] || files.students;

      if (!coursesFile || !studentsFile) {
        return res.status(400).json({ error: 'Both courses and students CSV files are required.' });
      }

      const coursesPath = coursesFile.filepath || coursesFile.path;
      const studentsPath = studentsFile.filepath || studentsFile.path;

      const coursesCSV = fs.readFileSync(coursesPath, 'utf-8');
      const studentsCSV = fs.readFileSync(studentsPath, 'utf-8');

      // Build the graph
      const graph = new Graph();
      parseCSV(coursesCSV).forEach(r => graph.addCourse(r.course_id, r.name));
      parseCSV(studentsCSV).forEach(r => {
        const courseIds = r.course_ids.split(';').map(c => c.trim());
        graph.enrollStudent(r.student_id, courseIds);
      });

      // Run algorithm
      const colors = graph.welshPowell();
      const graphData = graph.getGraphData(colors);

      // Build timetable rows
      const slots = {};
      for (const [courseId, slot] of Object.entries(colors)) {
        if (!slots[slot]) slots[slot] = [];
        slots[slot].push({ courseId, name: graph.courses[courseId].name });
      }

      const timetable = [];
      for (const slot of Object.keys(slots).sort((a, b) => a - b)) {
        for (const course of slots[slot]) {
          timetable.push({
            'Time Slot': `Slot ${parseInt(slot) + 1}`,
            'Course ID': course.courseId,
            'Course Name': course.name
          });
        }
      }

      return res.status(200).json({
        message: 'Timetable Optimized Successfully',
        timetable,
        graphData,
        totalSlots: Object.keys(slots).length
      });

    } catch (e) {
      return res.status(500).json({ error: e.message });
    }
  });
};

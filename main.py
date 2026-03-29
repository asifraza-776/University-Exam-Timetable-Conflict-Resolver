import csv
import argparse
import networkx as nx
import matplotlib.pyplot as plt

class Course:
    def __init__(self, course_id, name):
        self.course_id = course_id
        self.name = name
        self.enrolled_students = set()

    def add_student(self, student_id):
        self.enrolled_students.add(student_id)

    def __repr__(self):
        return f"{self.course_id} - {self.name}"

class Graph:
    def __init__(self):
        self.courses = {}  # course_id -> Course object
        self.adj_list = {} # course_id -> set of conflicting course_ids

    def add_course(self, course_id, name):
        if course_id not in self.courses:
            self.courses[course_id] = Course(course_id, name)
            self.adj_list[course_id] = set()

    def enroll_student(self, student_id, course_ids):
        """Enroll a student in multiple courses, creating conflicts between them."""
        for course_id in course_ids:
            if course_id in self.courses:
                self.courses[course_id].add_student(student_id)
        
        for i in range(len(course_ids)):
            for j in range(i + 1, len(course_ids)):
                c1, c2 = course_ids[i], course_ids[j]
                if c1 in self.courses and c2 in self.courses:
                    self.adj_list[c1].add(c2)
                    self.adj_list[c2].add(c1)

    def welsh_powell_coloring(self):
        """
        Implements the Welsh-Powell Graph Coloring Algorithm.
        """
        degrees = {course_id: len(self.adj_list[course_id]) for course_id in self.courses}
        sorted_courses = sorted(degrees.keys(), key=lambda c: degrees[c], reverse=True)
        colors = {}
        current_color = 0
        uncolored_courses = list(sorted_courses) 

        while uncolored_courses:
            main_course = uncolored_courses[0]
            colors[main_course] = current_color
            colored_in_this_round = [main_course]

            for other_course in uncolored_courses[1:]:
                has_conflict = False
                for already_colored in colored_in_this_round:
                    if already_colored in self.adj_list[other_course]:
                        has_conflict = True
                        break
                
                if not has_conflict:
                    colors[other_course] = current_color
                    colored_in_this_round.append(other_course)

            for colored_node in colored_in_this_round:
                uncolored_courses.remove(colored_node)

            current_color += 1

        return colors

    def display_timetable(self, colors):
        """Formats and prints the scheduled timetable."""
        time_slots = {}
        for course_id, time_slot in colors.items():
            if time_slot not in time_slots:
                time_slots[time_slot] = []
            time_slots[time_slot].append(self.courses[course_id])

        print("\n--- Optimized Exam Timetable ---")
        print(f"Total Time Slots Required: {len(time_slots)}")
        print("--------------------------------")
        
        for slot in sorted(time_slots.keys()):
            print(f"Time Slot {slot + 1}:")
            for course in time_slots[slot]:
                print(f"   -> {course}")
            print()

    def load_courses_from_csv(self, filepath):
        """Loads courses from a CSV file (course_id, name)."""
        with open(filepath, mode='r') as file:
            reader = csv.DictReader(file)
            for row in reader:
                self.add_course(row['course_id'], row['name'])
        print(f"Loaded {len(self.courses)} courses from {filepath}")

    def load_students_from_csv(self, filepath):
        """Loads students from a CSV file (student_id, course_ids separated by ;)."""
        student_count = 0
        with open(filepath, mode='r') as file:
            reader = csv.DictReader(file)
            for row in reader:
                student_id = row['student_id']
                course_ids = row['course_ids'].split(';')
                self.enroll_student(student_id, course_ids)
                student_count += 1
        print(f"Loaded {student_count} student enrollments from {filepath}")

    def export_timetable_to_csv(self, colors, filepath):
        """Exports the assigned timetable to a CSV file."""
        time_slots = {}
        for course_id, time_slot in colors.items():
            if time_slot not in time_slots:
                time_slots[time_slot] = []
            time_slots[time_slot].append(self.courses[course_id])

        with open(filepath, mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(["Time Slot", "Course ID", "Course Name"])
            for slot in sorted(time_slots.keys()):
                for course in time_slots[slot]:
                    writer.writerow([f"Slot {slot + 1}", course.course_id, course.name])
        print(f"\nTimetable exported successfully to {filepath}")

    def visualize_graph(self, colors, image_path="timetable_graph.png", show_gui=False):
        """Uses networkx and matplotlib to draw the conflict graph with colored time slots."""
        G = nx.Graph()
        
        # Add nodes
        for course_id in self.courses:
            G.add_node(course_id)
            
        # Add edges (conflicts)
        for course_id, conflicts in self.adj_list.items():
            for conflict_id in conflicts:
                G.add_edge(course_id, conflict_id)
                
        # Colors map for visualization
        color_map = ['#FF9999', '#66B2FF', '#99FF99', '#FFCC99', '#D9B3FF', '#FF99CC', '#FFFF99']
        node_colors = []
        for node in G.nodes():
            color_index = colors.get(node, 0)
            # Cycle colors if more slots than predefined colors
            node_colors.append(color_map[color_index % len(color_map)])
            
        # Draw the graph
        plt.figure(figsize=(10, 8))
        pos = nx.spring_layout(G, seed=42) # Fixed seed for reproducible layout
        nx.draw(G, pos, with_labels=True, node_color=node_colors, node_size=2000, 
                font_size=12, font_weight='bold', font_color='black', edge_color='gray')
        
        plt.title("Exam Timetable Conflict Graph\n(Nodes with same color are in the same time slot)", fontsize=16)
        
        plt.savefig(image_path)
        print(f"\nGraph visualized! Saved as '{image_path}'.")
        if show_gui:
            plt.show()
        else:
            plt.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="University Exam Timetable Conflict Resolver")
    parser.add_argument("--courses", type=str, help="Path to courses CSV file", default="sample_courses.csv")
    parser.add_argument("--students", type=str, help="Path to students CSV file", default="sample_students.csv")
    parser.add_argument("--output", type=str, help="Path to export the output timetable CSV", default="timetable_output.csv")
    parser.add_argument("--image_output", type=str, help="Path to export the output graph image", default="timetable_graph.png")
    parser.add_argument("--demo", action="store_true", help="Run the built-in hardcoded demo instead of loading CSVs")
    parser.add_argument("--visualize", action="store_true", help="Generate and show a visual representation of the graph")

    args = parser.parse_args()

    graph = Graph()

    if args.demo:
        print("Running Hardcoded Demo...")
        graph.add_course("CS101", "Intro to Programming")
        graph.add_course("MTH101", "Calculus I")
        graph.add_course("PHY101", "Physics I")
        graph.add_course("ENG101", "English Literature")
        graph.add_course("CHM101", "Chemistry I")
        graph.add_course("CS201", "Data Structures")
        graph.add_course("MTH201", "Linear Algebra")

        graph.enroll_student("S1", ["CS101", "MTH101", "PHY101"])
        graph.enroll_student("S2", ["CS101", "ENG101", "CS201"])
        graph.enroll_student("S3", ["MTH101", "PHY101", "CHM101"])
        graph.enroll_student("S4", ["ENG101", "CHM101", "MTH201"])
        graph.enroll_student("S5", ["CS201", "MTH201"])
        graph.enroll_student("S6", ["CS101", "CHM101"])
    else:
        print("Loading data from CSVs...")
        try:
            graph.load_courses_from_csv(args.courses)
            graph.load_students_from_csv(args.students)
        except FileNotFoundError as e:
            print(f"Error: {e}")
            print("Please ensure the CSV files exist, or run with --demo for the built-in example.")
            exit(1)

    print("\nRunning Welsh-Powell Graph Coloring Algorithm...")
    timetable = graph.welsh_powell_coloring()

    graph.display_timetable(timetable)
    graph.export_timetable_to_csv(timetable, args.output)
    
    # Always generate and save the PNG every run.
    # Show the interactive window only if --visualize is passed.
    graph.visualize_graph(timetable, image_path=args.image_output, show_gui=args.visualize)

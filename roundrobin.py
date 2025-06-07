import tkinter as tk
from tkinter import ttk, messagebox
from collections import deque

class RoundRobinApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Round Robin Scheduling Simulator")
        self.root.geometry("900x700")
        self.root.configure(bg="#f0f8ff")
        
        # Create a title label
        title_frame = ttk.Frame(self.root)
        title_frame.pack(fill=tk.X, pady=10)
        title_label = ttk.Label(title_frame, text="Round Robin Scheduler Simulator", 
                              font=('Segoe UI', 24, 'bold'))
        title_label.pack(expand=True)  # This centers the label
        
        self.style = ttk.Style()
        self.style.theme_use('clam')
        self.style.configure('.', background="#f0f8ff", foreground="#333333")
        self.style.configure('TFrame', background="#f0f8ff")
        self.style.configure('TLabel', background="#f0f8ff", foreground="#333333")
        self.style.configure('TButton', background="#0078d7", foreground="white", font=('Segoe UI', 10, 'bold'), borderwidth=1)
        self.style.map('TButton', background=[('active', "#5cb3ff")], foreground=[('active', "#333333")])
        self.style.configure('TEntry', fieldbackground="white")
        self.style.configure('TLabelFrame', background="#f0f8ff")
        self.style.configure('Treeview', background="white", fieldbackground="white", foreground="#333333")
        self.style.configure('Treeview.Heading', background="#0078d7", foreground="white")
        self.style.map('Treeview.Heading', background=[('active', "#5cb3ff")])
        
        self.processes = []
        self.time_quantum = tk.IntVar(value=2)
        self.execution_sequence = []
        
        self.create_widgets()
        
    def create_widgets(self):
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        input_frame = ttk.LabelFrame(main_frame, text="Process Input", padding="15")
        input_frame.pack(fill=tk.X, pady=5)
        
        self.tree = ttk.Treeview(input_frame, columns=('id', 'arrival', 'burst'), show='headings')
        self.tree.heading('id', text='Process ID')
        self.tree.heading('arrival', text='Arrival Time')
        self.tree.heading('burst', text='Burst Time')
        self.tree.pack(fill=tk.X)
        
        add_frame = ttk.Frame(input_frame)
        add_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(add_frame, text="Process ID:").pack(side=tk.LEFT)
        self.id_entry = ttk.Entry(add_frame, width=10)
        self.id_entry.pack(side=tk.LEFT, padx=5)
        
        ttk.Label(add_frame, text="Arrival Time:").pack(side=tk.LEFT)
        self.arrival_entry = ttk.Entry(add_frame, width=10)
        self.arrival_entry.pack(side=tk.LEFT, padx=5)
        
        ttk.Label(add_frame, text="Burst Time:").pack(side=tk.LEFT)
        self.burst_entry = ttk.Entry(add_frame, width=10)
        self.burst_entry.pack(side=tk.LEFT, padx=5)
        
        add_btn = ttk.Button(add_frame, text="Add Process", command=self.add_process)
        add_btn.pack(side=tk.LEFT, padx=5)
        
        remove_btn = ttk.Button(add_frame, text="Remove Selected", command=self.remove_process)
        remove_btn.pack(side=tk.LEFT)
        
        quantum_frame = ttk.Frame(input_frame)
        quantum_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(quantum_frame, text="Time Quantum:").pack(side=tk.LEFT)
        quantum_entry = ttk.Entry(quantum_frame, textvariable=self.time_quantum, width=5)
        quantum_entry.pack(side=tk.LEFT, padx=5)
        
        button_frame = ttk.Frame(input_frame)
        button_frame.pack(fill=tk.X, pady=5)
        
        run_btn = ttk.Button(button_frame, text="Run Simulation", command=self.run_simulation)
        run_btn.pack(side=tk.LEFT, padx=5)
        
        # Add Reset Button
        reset_btn = ttk.Button(button_frame, text="Reset All", command=self.reset_all)
        reset_btn.pack(side=tk.LEFT)
        
        results_frame = ttk.LabelFrame(main_frame, text="Simulation Results", padding="10")
        results_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        ttk.Label(results_frame, text="Execution Sequence:").pack(anchor=tk.W)
        self.sequence_text = tk.Text(results_frame, height=3, wrap=tk.WORD, bg="white", fg="#333333")
        self.sequence_text.pack(fill=tk.X, pady=5)
        
        ttk.Label(results_frame, text="Gantt Chart:").pack(anchor=tk.W)
        self.gantt_canvas = tk.Canvas(results_frame, height=120, bg='white', highlightthickness=0)
        self.gantt_canvas.pack(fill=tk.X, pady=5)
        
        metrics_frame = ttk.Frame(results_frame)
        metrics_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(metrics_frame, text="Average Waiting Time:").pack(side=tk.LEFT)
        self.avg_wait_label = ttk.Label(metrics_frame, text="0.00")
        self.avg_wait_label.pack(side=tk.LEFT, padx=5)
        
        ttk.Label(metrics_frame, text="Average Turnaround Time:").pack(side=tk.LEFT)
        self.avg_turnaround_label = ttk.Label(metrics_frame, text="0.00")
        self.avg_turnaround_label.pack(side=tk.LEFT, padx=5)
        
        ttk.Label(results_frame, text="Process Details:").pack(anchor=tk.W)
        self.details_tree = ttk.Treeview(results_frame, columns=('id', 'arrival', 'burst', 'wait', 'turnaround'), show='headings')
        self.details_tree.heading('id', text='Process ID')
        self.details_tree.heading('arrival', text='Arrival Time')
        self.details_tree.heading('burst', text='Burst Time')
        self.details_tree.heading('wait', text='Waiting Time')
        self.details_tree.heading('turnaround', text='Turnaround Time')
        self.details_tree.pack(fill=tk.BOTH, expand=True)
    
    def add_process(self):
        try:
            pid = self.id_entry.get()
            arrival = int(self.arrival_entry.get())
            burst = int(self.burst_entry.get())
            
            if not pid:
                messagebox.showerror("Error", "Process ID cannot be empty")
                return
                
            if arrival < 0 or burst <= 0:
                messagebox.showerror("Error", "Arrival time must be >= 0 and burst time must be > 0")
                return
                
            self.processes.append((pid, arrival, burst))
            self.tree.insert('', tk.END, values=(pid, arrival, burst))
            
            self.id_entry.delete(0, tk.END)
            self.arrival_entry.delete(0, tk.END)
            self.burst_entry.delete(0, tk.END)
            
        except ValueError:
            messagebox.showerror("Error", "Please enter valid numbers for arrival and burst time")
    
    def remove_process(self):
        selected = self.tree.selection()
        if not selected:
            return
            
        for item in selected:
            index = self.tree.index(item)
            del self.processes[index]
            self.tree.delete(item)
    
    def reset_all(self):
        """Reset all inputs and results"""
        self.processes = []
        self.time_quantum.set(2)
        self.execution_sequence = []
        
        # Clear all widgets
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        for item in self.details_tree.get_children():
            self.details_tree.delete(item)
            
        self.id_entry.delete(0, tk.END)
        self.arrival_entry.delete(0, tk.END)
        self.burst_entry.delete(0, tk.END)
        self.sequence_text.delete(1.0, tk.END)
        self.gantt_canvas.delete("all")
        self.avg_wait_label.config(text="0.00")
        self.avg_turnaround_label.config(text="0.00")
    
    def run_simulation(self):
        if not self.processes:
            messagebox.showerror("Error", "No processes to schedule")
            return
            
        try:
            time_quantum = self.time_quantum.get()
            if time_quantum <= 0:
                messagebox.showerror("Error", "Time quantum must be > 0")
                return
                
            avg_wait, avg_turnaround, sequence = self.round_robin(self.processes, time_quantum)
            self.display_results(avg_wait, avg_turnaround, sequence)
            
        except ValueError:
            messagebox.showerror("Error", "Invalid input values")
    
    def round_robin(self, processes, time_quantum):
        n = len(processes)
        remaining_time = [p[2] for p in processes]
        arrival_time = [p[1] for p in processes]
        waiting_time = [0] * n
        turnaround_time = [0] * n
        execution_sequence = []
        gantt_data = []
        
        current_time = 0
        queue = deque()
        completed = 0
        
        for i in range(n):
            if arrival_time[i] == 0:
                queue.append(i)
        
        while completed != n:
            if not queue:
                current_time += 1
                for i in range(n):
                    if arrival_time[i] == current_time and i not in queue and remaining_time[i] > 0:
                        queue.append(i)
                continue
            
            current_process = queue.popleft()
            start_time = current_time
            execution_time = min(time_quantum, remaining_time[current_process])
            remaining_time[current_process] -= execution_time
            current_time += execution_time
            end_time = current_time
            
            gantt_data.append({
                'process': processes[current_process][0],
                'start': start_time,
                'end': end_time
            })
            
            execution_sequence.append(processes[current_process][0])
            
            for i in range(n):
                if i != current_process and remaining_time[i] > 0 and arrival_time[i] < current_time:
                    waiting_time[i] += execution_time
            
            for i in range(n):
                if arrival_time[i] <= current_time and i not in queue and remaining_time[i] > 0 and i != current_process:
                    queue.append(i)
            
            if remaining_time[current_process] > 0:
                queue.append(current_process)
            else:
                completed += 1
                turnaround_time[current_process] = current_time - arrival_time[current_process]
        
        avg_waiting = sum(waiting_time) / n
        avg_turnaround = sum(turnaround_time) / n
        
        process_details = []
        for i in range(n):
            process_details.append((
                processes[i][0],
                processes[i][1],
                processes[i][2],
                waiting_time[i],
                turnaround_time[i]
            ))
        
        return (avg_waiting, avg_turnaround, {
            'sequence': execution_sequence,
            'gantt': gantt_data,
            'details': process_details
        })
    
    def display_results(self, avg_wait, avg_turnaround, results):
        self.sequence_text.delete(1.0, tk.END)
        self.gantt_canvas.delete("all")
        for item in self.details_tree.get_children():
            self.details_tree.delete(item)
        
        self.sequence_text.insert(tk.END, " → ".join(results['sequence']))
        self.draw_gantt_chart(results['gantt'])
        self.avg_wait_label.config(text=f"{avg_wait:.2f}")
        self.avg_turnaround_label.config(text=f"{avg_turnaround:.2f}")
        
        for detail in results['details']:
            self.details_tree.insert('', tk.END, values=detail)
    
    def draw_gantt_chart(self, gantt_data):
        if not gantt_data:
            return
            
        canvas = self.gantt_canvas
        canvas_width = canvas.winfo_width()
        canvas_height = canvas.winfo_height()
        
        max_time = max(entry['end'] for entry in gantt_data)
        if max_time == 0:
            return
            
        scale = (canvas_width - 40) / max_time
        bar_height = 30
        y = (canvas_height - bar_height) / 2 - 20
        
        # Draw timeline at bottom
        timeline_y = y + bar_height + 20
        canvas.create_line(20, timeline_y, canvas_width - 20, timeline_y, width=2)
        
        # Draw vertical lines for each time unit
        for t in range(0, max_time + 1):
            x = 20 + t * scale
            canvas.create_line(x, timeline_y, x, timeline_y + 5, width=1)
            canvas.create_text(x, timeline_y + 10, text=str(t), anchor=tk.N)
        
        colors = ['#5cb3ff', '#0078d7', '#003366', '#4d94ff', '#1a66b3']
        color_index = 0
        
        for i, entry in enumerate(gantt_data):
            x1 = 20 + entry['start'] * scale
            x2 = 20 + entry['end'] * scale
            width = x2 - x1
            
            color = colors[color_index % len(colors)]
            canvas.create_rectangle(x1, y, x2, y + bar_height, fill=color, outline='black')
            canvas.create_text((x1 + x2)/2, y + bar_height/2, text=entry['process'], fill="white")
            
            # Draw vertical divider lines
            if i < len(gantt_data) - 1:
                canvas.create_line(x2, y, x2, y + bar_height, fill='white')
            
            color_index += 1

if __name__ == "__main__":
    root = tk.Tk()
    app = RoundRobinApp(root)
    root.mainloop()
import threading
import time
import random
import imageio
import io
import numpy as np
import tempfile
import shutil
from datetime import datetime
from tkinter import Tk, StringVar, messagebox
from tkinter import ttk, Canvas, Text
from PIL import Image, ImageDraw
from hanoi_game import TowerOfHanoi
from hanoi_search import EnhancedHanoiSearch

class EnhancedTowerOfHanoiGUI:
    def __init__(self):
        self.root = None
        self.num_disks = random.randint(2, 7)
        self.game = TowerOfHanoi(self.num_disks)
        self.game.randomize()
        self.initial_state = self.game.get_state()
        self.search = None
        self.solution_path = []
        self.search_thread = None
        self.animation_thread = None
        self.search_running = False
        self.animation_running = False
        self.animation_paused = False
        self.gif_frames = []
        
        self.canvas = None
        self.algorithm_var = None
        self.algorithm_selector = None
        self.start_btn = None
        self.pause_btn = None
        self.reset_btn = None
        self.randomize_btn = None
        self.create_gif_btn = None
        self.status_var = None
        self.result_label = None
        self.stats_text = None

    def setup_gui(self):
        self.root = Tk()
        self.root.title("Tower of Hanoi Solver")
        self.root.geometry("800x600")
        
        style = ttk.Style()
        style.theme_use('clam')
        
        self.search = EnhancedHanoiSearch(self.game, on_state_change=self.on_state_change, on_search_complete=self.on_search_complete)
        
        main_frame = ttk.Frame(self.root, padding=10)
        main_frame.pack(fill="both", expand=True)
        
        title_label = ttk.Label(main_frame, text="Tower of Hanoi Solver", font=("Arial", 14, "bold"))
        title_label.pack(pady=5)
        
        towers_frame = ttk.Frame(main_frame)
        towers_frame.pack(fill="both", expand=True, pady=5)
        
        self.canvas = Canvas(towers_frame, bg="white")
        self.canvas.pack(fill="both", expand=True)
        
        controls_frame = ttk.Frame(main_frame)
        controls_frame.pack(fill="x", pady=5)
        
        ttk.Label(controls_frame, text="Algorithm:").grid(row=0, column=0, padx=5, pady=2, sticky="e")
        self.algorithm_var = StringVar(value="BFS")
        self.algorithm_selector = ttk.Combobox(controls_frame, values=["BFS", "DFS", "Bidirectional"], 
                                               textvariable=self.algorithm_var, width=12, state="readonly")
        self.algorithm_selector.grid(row=0, column=1, padx=5, pady=2, sticky="w")
        
        self.start_btn = ttk.Button(controls_frame, text="Start Search", command=self.start_search)
        self.start_btn.grid(row=0, column=2, padx=5, pady=2)
        
        self.pause_btn = ttk.Button(controls_frame, text="Pause", command=self.toggle_pause)
        self.pause_btn.grid(row=0, column=3, padx=5, pady=2)
        
        self.reset_btn = ttk.Button(controls_frame, text="Reset", command=self.reset)
        self.reset_btn.grid(row=0, column=4, padx=5, pady=2)
        
        self.randomize_btn = ttk.Button(controls_frame, text="Randomize", command=self.randomize)
        self.randomize_btn.grid(row=0, column=5, padx=5, pady=2)
        
        self.create_gif_btn = ttk.Button(controls_frame, text="Create GIF", command=self.create_solution_gif, state="disabled")
        self.create_gif_btn.grid(row=0, column=6, padx=5, pady=2)
        
        status_frame = ttk.Frame(main_frame)
        status_frame.pack(fill="x", pady=5)
        
        ttk.Label(status_frame, text="Status:").grid(row=0, column=0, sticky="w", padx=10)
        self.status_var = StringVar(value="Ready")
        ttk.Label(status_frame, textvariable=self.status_var).grid(row=0, column=1, sticky="w", padx=10)
        
        self.result_frame = ttk.Frame(main_frame)
        self.result_frame.pack(fill="x", pady=5)
        
        self.result_label = ttk.Label(self.result_frame, text="", font=("Arial", 12))
        self.result_label.pack(pady=5)
        
        self.stats_text = Text(main_frame, height=7, width=60, state='disabled')
        self.stats_text.pack(fill="x", pady=10)
        
        self.update_button_states()
        self.root.update()  # Ensure geometry is applied
        self.draw_towers()

    def draw_towers(self):
        self.canvas.delete("all")
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()
        
        if canvas_width <= 1 or canvas_height <= 1:
            canvas_width = 800
            canvas_height = 400
        
        tower_width = 10
        tower_height = canvas_height * 0.6
        base_width = canvas_width * 0.8
        base_height = 20
        
        tower_x = [canvas_width * 0.25, canvas_width * 0.5, canvas_width * 0.75]
        base_y = canvas_height * 0.7
        tower_y = base_y - tower_height
        
        self.canvas.create_rectangle((canvas_width - base_width) / 2, base_y, 
                                     (canvas_width + base_width) / 2, base_y + base_height, fill="brown")
        
        for x in tower_x:
            self.canvas.create_rectangle(x - tower_width/2, tower_y, x + tower_width/2, base_y, fill="black")
        
        disk_height = 20
        max_disk_width = base_width / 4
        min_disk_width = max_disk_width / 3
        
        for tower_idx, tower in enumerate(self.game.towers):
            for disk_idx, disk in enumerate(tower):
                disk_width = min_disk_width + (max_disk_width - min_disk_width) * (disk / self.num_disks)
                disk_x = tower_x[tower_idx]
                disk_y = base_y - (disk_idx + 1) * disk_height
                color_value = int(225 * disk / self.num_disks)
                color = f"#{color_value:02x}00{255-color_value:02x}"
                self.canvas.create_rectangle(
                    disk_x - disk_width/2, disk_y - disk_height,
                    disk_x + disk_width/2, disk_y,
                    fill=color, outline="black"
                )

    def create_solution_gif(self):
        """Create a GIF animation of the solution"""
        if not self.solution_path:
            messagebox.showinfo("Error", "No solution available to animate. Run the search first.")
            return
        
        self.status_var.set("Creating GIF animation...")
        
        # Create temporary directory for frames
        temp_dir = tempfile.mkdtemp()
        
        # Create game copy for animation
        game_copy = TowerOfHanoi(self.num_disks)
        game_copy.set_state(self.initial_state)
        
        # Save initial state
        self.save_game_state_image(game_copy, f"{temp_dir}/frame_0.png")
        
        # Apply each move and save frames
        for i, move in enumerate(self.solution_path):
            game_copy.move(move[0], move[1])
            self.save_game_state_image(game_copy, f"{temp_dir}/frame_{i+1}.png")
        
        # Create GIF
        frames = []
        for i in range(len(self.solution_path) + 1):
            frames.append(Image.open(f"{temp_dir}/frame_{i}.png"))
        
        # Save GIF
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        gif_path = f"tower_of_hanoi_solution_{timestamp}.gif"
        frames[0].save(
            gif_path,
            format='GIF',
            append_images=frames[1:],
            save_all=True,
            duration=500,  # 0.5 seconds per frame
            loop=0  # Loop forever
        )
        
        # Cleanup
        shutil.rmtree(temp_dir)
        
        self.status_var.set(f"GIF animation saved as {gif_path}")
        messagebox.showinfo("GIF Created", f"Solution animation saved as {gif_path}")

    def save_game_state_image(self, game, filename):
        """Save current game state as an image"""
        width, height = 800, 400
        image = Image.new("RGB", (width, height), "white")
        draw = ImageDraw.Draw(image)
        
        # Tower dimensions
        tower_width = 10
        tower_height = height * 0.6
        base_width = width * 0.8
        base_height = 20
        
        # Tower positions
        tower_x = [width * 0.25, width * 0.5, width * 0.75]
        base_y = height * 0.7
        tower_y = base_y - tower_height
        
        # Draw base
        base_x = (width - base_width) / 2
        draw.rectangle([base_x, base_y, base_x + base_width, base_y + base_height], fill="brown")
        
        # Draw towers
        for x in tower_x:
            draw.rectangle([x - tower_width/2, tower_y, x + tower_width/2, base_y], fill="black")
        
        # Disk dimensions
        disk_height = 20
        max_disk_width = base_width / 4
        min_disk_width = max_disk_width / 3
        
        # Draw disks on towers
        for tower_idx, tower in enumerate(game.towers):
            for disk_idx, disk in enumerate(tower):
                disk_width = min_disk_width + (max_disk_width - min_disk_width) * (disk / game.num_disks)
                disk_x = tower_x[tower_idx]
                disk_y = base_y - (disk_idx + 1) * disk_height
                
                # Colors based on disk size (simplified for PIL, matching canvas)
                color_value = int(225 * disk / game.num_disks)
                r, g, b = color_value, 0, 255 - color_value
                draw.rectangle([
                    disk_x - disk_width/2, disk_y - disk_height,
                    disk_x + disk_width/2, disk_y
                ], fill=(r, g, b), outline="black")
        
        image.save(filename)

    def update_button_states(self):
        if self.search_running or self.animation_running:
            self.start_btn.config(state="disabled")
            self.pause_btn.config(state="normal" if self.animation_running else "disabled", 
                                 text="Pause" if not self.animation_paused else "Resume")
            self.reset_btn.config(state="normal")
            self.randomize_btn.config(state="disabled")
            self.algorithm_selector.config(state="disabled")
            self.create_gif_btn.config(state="disabled")
        else:
            self.start_btn.config(state="normal")
            self.pause_btn.config(state="disabled", text="Pause")
            self.reset_btn.config(state="normal")
            self.randomize_btn.config(state="normal")
            self.algorithm_selector.config(state="readonly")
            self.create_gif_btn.config(state="normal" if self.solution_path else "disabled")

    def reset(self):
        self.stop_threads()
        self.game.set_state(self.initial_state)
        self.search = EnhancedHanoiSearch(self.game, on_state_change=self.on_state_change, on_search_complete=self.on_search_complete)
        self.search_running = False
        self.animation_running = False
        self.animation_paused = False
        self.solution_path = []
        self.gif_frames = []
        self.status_var.set("Reset to initial state")
        self.draw_towers()
        self.result_label.config(text="")
        self.stats_text.config(state='normal')
        self.stats_text.delete(1.0, "end")
        self.stats_text.config(state='disabled')
        self.update_button_states()
    
    def randomize(self):
        if self.search_running or self.animation_running:
            return
        self.num_disks = random.randint(2, 7)
        self.game = TowerOfHanoi(self.num_disks)
        self.game.randomize()
        self.initial_state = self.game.get_state()
        self.search = EnhancedHanoiSearch(self.game, on_state_change=self.on_state_change, on_search_complete=self.on_search_complete)
        self.draw_towers()
        self.status_var.set(f"Randomized with {self.num_disks} disks")
        self.result_label.config(text="")
        self.update_button_states()
    
    def start_search(self):
        if self.search_running or self.animation_running:
            return
        self.search_running = True
        self.update_button_states()
        self.result_label.config(text="")
        self.stats_text.config(state='normal')
        self.stats_text.delete(1.0, "end")
        self.stats_text.config(state='disabled')
        self.status_var.set("Searching for solution...")
        self.search_thread = threading.Thread(target=self.run_search, daemon=True)
        self.search_thread.start()
    
    def run_search(self):
        algorithm = self.algorithm_var.get()
        try:
            path = {"BFS": self.search.bfs, "DFS": self.search.dfs, "Bidirectional": self.search.bidirectional}[algorithm]()
            if path and path != [] and not self.search.pause_search:
                self.root.after(0, lambda: self.animate_solution(path))
            elif path == []:
                self.root.after(0, lambda: self.result_label.config(text="✗ No Solution Found", foreground="red"))
                self.search_running = False
                self.root.after(0, self.update_button_states)
        except Exception as e:
            self.root.after(0, lambda: self.status_var.set(f"Error: {str(e)}"))
            self.root.after(0, self.on_search_fail)
    
    def toggle_pause(self):
        if not self.animation_running:
            return
        self.animation_paused = not self.animation_paused
        self.update_button_states()
        self.status_var.set(f"Animation {'paused' if self.animation_paused else 'resumed'}")
    
    def animate_solution(self, path):
        self.search_running = False
        self.animation_running = True
        self.solution_path = path
        self.game.set_state(self.initial_state)
        self.draw_towers()
        self.update_button_states()
        self.animation_thread = threading.Thread(target=self.run_animation, daemon=True)
        self.animation_thread.start()
    
    def run_animation(self):
        if not self.solution_path:
            self.status_var.set("No solution path to animate.")
            self.animation_running = False
            self.update_button_states()
            return
        self.gif_frames = []
        total_moves = len(self.solution_path)
        for i, move in enumerate(self.solution_path):
            if not self.animation_running:
                return
            while self.animation_paused:
                time.sleep(0.1)
                if not self.animation_running:
                    return
            self.game.move(move[0], move[1])
            self.root.after(0, self.draw_towers)
            self.root.after(0, lambda i=i: self.status_var.set(f"Animating move {i+1}/{total_moves}"))
            time.sleep(0.5)
        self.animation_running = False
        self.root.after(0, lambda: self.status_var.set(
            "Solution successfully completed!" if self.game.is_goal_state() else "Animation completed but goal state not reached."
        ))
        self.root.after(0, self.update_button_states)
    
    def on_state_change(self, game_state, status, path):
        self.root.after(0, lambda: self.status_var.set(f"{status}: Exploring state {len(path)} steps from start"))
    
    def on_search_complete(self, success, path, stats):
        self.root.after(0, lambda: self.result_label.config(
            text="✓ Solution Found!" if success else "✗ No Solution Found",
            foreground="green" if success else "red"
        ))
        self.root.after(0, self.update_stats_display, stats)
        if not self.animation_running:
            self.search_running = False
            self.root.after(0, self.update_button_states)
    
    def on_search_fail(self):
        self.result_label.config(text="✗ Search Error", foreground="red")
        self.search_running = False
        self.animation_running = False
        self.update_button_states()
    
    def update_stats_display(self, stats):
        self.stats_text.config(state='normal')
        self.stats_text.delete(1.0, "end")
        stats_text = f"Search Results:\n- Success: {stats['success']}\n- Time: {stats['search_time']:.3f} seconds\n" \
                     f"- States explored: {stats['nodes_explored']}\n- Unique states: {stats['states_visited']}\n" \
                     f"- Solution length: {stats['path_length']} moves"
        self.stats_text.insert(1.0, stats_text)
        self.stats_text.config(state='disabled')
    
    def stop_threads(self):
        if self.search_thread and self.search_thread.is_alive():
            self.search.pause_search = True
            self.search_thread.join(timeout=0.1)
        if self.animation_thread and self.animation_thread.is_alive():
            self.animation_running = False
            self.animation_thread.join(timeout=0.1)
        self.search_thread = None
        self.animation_thread = None
    
    def run(self):
        self.setup_gui()
        
        def on_resize(event):
            if event.widget == self.root:
                self.draw_towers()
        
        self.root.bind("<Configure>", on_resize)
        
        def on_close():
            self.stop_threads()
            self.root.destroy()
        
        self.root.protocol("WM_DELETE_WINDOW", on_close)
        self.root.mainloop()

if __name__ == "__main__":
    gui = EnhancedTowerOfHanoiGUI()
    gui.run()
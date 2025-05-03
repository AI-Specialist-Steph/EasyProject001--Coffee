import tkinter as tk
from PIL import Image, ImageTk, ImageSequence
import threading
import time

SLEEP_GIF = "sleep-time-cute gif.gif"

class CoffeeAnimation(tk.Canvas):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.steam_lines = []
        self.pour_stream = None
        self.running = False
        self.status_text_machine = None
        self.screen_display = None

        # Cup coordinates (shared between functions)
        self.cup_left_x = 175
        self.cup_right_x = self.cup_left_x + 50
        self.cup_top_y = 200  # = 240 - 40 (base_y - height)
        self.cup_bottom_y = 240

    def start_animation(self):
        self.running = True
        self.delete("all")
        self.draw_machine()
        self.draw_cup()
        self.screen_display = self.create_text(200, 60, text="Starting...", font=("Arial", 10), fill="black")
        threading.Thread(target=self.animate_pour).start()

    def draw_machine(self):
        # Main body - soft pink tones
        self.create_rectangle(80, 20, 320, 80, fill="#f9d5e5", outline="#d48eb3", width=2)
        self.create_rectangle(100, 80, 300, 240, fill="#f7a8b8", outline="#d48eb3")

        # Screen and buttons
        self.create_rectangle(170, 30, 230, 70, fill="lightblue", outline="darkblue", width=2) # Screen
        self.create_oval(110, 35, 125, 50, fill="#e75480", outline="black")  # Buttons
        self.create_oval(135, 35, 150, 50, fill="#e75480", outline="black")
        self.create_rectangle(270, 35, 275, 45, fill="#c71585")  # Slim buttons
        self.create_rectangle(280, 35, 285, 45, fill="#c71585")
        self.create_rectangle(290, 35, 295, 45, fill="#c71585")

        # Nozzle and handle
        self.create_rectangle(185, 80, 215, 120, fill="#5c4b51")  # Dark nozzle
        self.create_rectangle(215, 95, 260, 105, fill="#d48eb3")  # Handle

        # Stream dimensions
        self.stream_x1 = 198
        self.stream_x2 = 202
        self.stream_y_top = 123
        self.stream_y_bottom = 200  # Stop at top of cup

        # Machine base
        self.create_rectangle(110, 120, 290, 230, fill="#f4c2c2", outline="#d48eb3")
        self.create_rectangle(100, 230, 300, 240, fill="#e68fac", outline="black")
        self.create_rectangle(90, 240, 310, 250, fill="#d36c99")  # Base stand

    def draw_cup(self):
        # Cup body (rectangle and bottom)
        self.create_rectangle(self.cup_left_x, self.cup_top_y + 10, self.cup_right_x, self.cup_bottom_y - 5,
                              fill="white", outline="black", width=2)
        self.create_oval(self.cup_left_x, self.cup_bottom_y - 5, self.cup_right_x, self.cup_bottom_y,
                         fill="white", outline="black", width=2)

        # Handle (white outer, coffee-machine-colored inner)
        handle_x1 = self.cup_right_x - 2
        handle_x2 = handle_x1 + 20
        handle_y1 = self.cup_top_y + 12
        handle_y2 = self.cup_bottom_y - 12
        self.create_oval(handle_x1, handle_y1, handle_x2, handle_y2, fill="white", outline="black", width=2)
        self.create_oval(handle_x1 + 4, handle_y1 + 4, handle_x2 - 4, handle_y2 - 4, fill="#f4c2c2", outline="black", width=2)

        # Pour stream
        self.pour_stream = self.create_rectangle(self.stream_x1, self.stream_y_top, self.stream_x2, self.stream_y_top,
                                                 fill="#7b3f00", outline="#7b3f00")

        # Top rim (drawn last to hide the stream entering the cup)
        self.create_oval(self.cup_left_x, self.cup_top_y, self.cup_right_x, self.cup_top_y + 10,
                         fill="white", outline="black", width=2)

    def animate_pour(self):
        for h in range(self.stream_y_top, self.stream_y_bottom, 3):
            if not self.running:
                return
            self.coords(self.pour_stream, self.stream_x1, self.stream_y_top, self.stream_x2, h)
            self.itemconfig(self.screen_display, text="Pouring...")
            self.update()
            time.sleep(0.03)

        self.itemconfig(self.screen_display, text=" Ready! ☕")
        self.delete(self.pour_stream)

        # Draw coffee surface after pouring completes
        self.create_oval(self.cup_left_x + 5, self.cup_top_y + 3,
                         self.cup_right_x - 5, self.cup_top_y + 8,
                         fill="#7b3f00", outline="#7b3f00", width=1)

        self.animate_steam()

    def animate_steam(self):
        def steam():
            for _ in range(10):
                if not self.running:
                    return
                steam1 = self.create_line(190, 190, 190, 175, fill="gray", smooth=True)
                steam2 = self.create_line(210, 190, 210, 175, fill="gray", smooth=True)
                self.steam_lines.extend([steam1, steam2])
                self.update()
                time.sleep(0.2)
                for line in self.steam_lines:
                    self.delete(line)
                self.steam_lines.clear()
        threading.Thread(target=steam).start()

    def stop(self):
        self.running = False
        self.delete("all")

class App:
    def __init__(self, root):
        self.root = root
        self.root.title("Coffee or Sleep?")
        self.root.geometry("400x400")

        self.canvas = CoffeeAnimation(root, width=400, height=350, bg="#f3e9dc")
        self.canvas.pack()

        self.btn_frame = tk.Frame(root)
        self.btn_frame.pack()

        self.make_btn = tk.Button(self.btn_frame, text="Make Coffee", command=self.make_coffee,
                                  bg="#6c4c3a", fg="white", width=15)
        self.make_btn.grid(row=0, column=0, padx=10)

        self.sleep_btn = tk.Button(self.btn_frame, text="Don't Make Coffee", command=self.sleep_instead,
                                   bg="#6c4c3a", fg="white", width=15)
        self.sleep_btn.grid(row=0, column=1, padx=10)

        self.sleep_label = None
        self.sleep_frames = []
        self.animating = False

    def make_coffee(self):
        self.stop_all()
        self.canvas.start_animation()

    def sleep_instead(self):
        self.stop_all()
        self.animating = True
        self.sleep_label = tk.Label(self.canvas, bg="#f3e9dc")
        self.sleep_label.place(relx=0.5, rely=0.5, anchor=tk.CENTER)

        gif = Image.open(SLEEP_GIF)
        self.sleep_frames = [ImageTk.PhotoImage(frame.copy().convert("RGBA")) for frame in ImageSequence.Iterator(gif)]

        def animate(index=0):
            if not self.animating:
                return
            frame = self.sleep_frames[index]
            self.sleep_label.configure(image=frame)
            self.root.after(100, animate, (index + 1) % len(self.sleep_frames))

        animate()

    def stop_all(self):
        self.animating = False
        self.canvas.stop()
        if self.sleep_label:
            self.sleep_label.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.mainloop()

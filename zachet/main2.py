import tkinter as tk

class SolarEclipseSimulator:
    def __init__(self, root):
        self.root = root
        self.root.title("Симуляция солнечного затмения")

        self.sun_radius = 100
        self.moon_radius = 30
        self.distance = 300  
        self.speed = 2  
        self.moon_position = -self.moon_radius
        self.running = True  

   
        self.canvas = tk.Canvas(root, width=800, height=600, bg='black')
        self.canvas.pack()


        self.create_controls()

        self.animate()

    def create_controls(self):
        control_frame = tk.Frame(self.root)
        control_frame.pack()

        tk.Label(control_frame, text="Радиус Луны:").grid(row=0, column=0)
        self.moon_radius_slider = tk.Scale(control_frame, from_=10, to=100, orient=tk.HORIZONTAL, command=self.update_moon_radius)
        self.moon_radius_slider.set(self.moon_radius)
        self.moon_radius_slider.grid(row=0, column=1)

        tk.Label(control_frame, text="Скорость Луны:").grid(row=1, column=0)
        self.speed_slider = tk.Scale(control_frame, from_=1, to=10, orient=tk.HORIZONTAL, command=self.update_speed)
        self.speed_slider.set(self.speed)
        self.speed_slider.grid(row=1, column=1)

        self.toggle_button = tk.Button(control_frame, text="Пауза", command=self.toggle_animation)
        self.toggle_button.grid(row=2, columnspan=2)

        self.reset_button = tk.Button(control_frame, text="Сброс", command=self.reset_parameters)
        self.reset_button.grid(row=3, columnspan=2)

    def update_moon_radius(self, value):
        self.moon_radius = int(value)

    def update_speed(self, value):
        self.speed = int(value)

    def toggle_animation(self):
        self.running = not self.running
        if self.running:
            self.toggle_button.config(text="Пауза")
            self.animate()  

        else:
            self.toggle_button.config(text="Запуск")

    def reset_parameters(self):
        self.moon_radius = 30
        self.speed = 2
        self.moon_position = -self.moon_radius
        self.moon_radius_slider.set(self.moon_radius)
        self.speed_slider.set(self.speed)

    def animate(self):
        if not self.running:
            return

        self.canvas.delete("all")

 
        self.canvas.create_oval(350, 250, 450, 350, fill='yellow', outline='')

        moon_x = 400 + self.moon_position
        moon_y = 300
        self.canvas.create_oval(moon_x - self.moon_radius, moon_y - self.moon_radius,
                                moon_x + self.moon_radius, moon_y + self.moon_radius,
                                fill='white', outline='')

        # Обновляем позицию Луны
        self.moon_position += self.speed
        if self.moon_position > 800 + self.moon_radius:  # Если Луна прошла экран
            self.moon_position = -self.moon_radius

        self.root.after(50, self.animate)  

if __name__ == "__main__":
    root = tk.Tk()
    simulator = SolarEclipseSimulator(root)
    root.mainloop()

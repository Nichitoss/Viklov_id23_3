import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import tkinter as tk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

class SolarEclipseSimulation:
    def __init__(self, master):
        self.master = master
        self.master.title("Симуляция солнечного затмения")

        self.sun_radius = 1.0
        self.moon_radius = 0.3
        self.distance_earth_moon = 5.0
        self.speed = 0.05
        self.ani_running = False

        self.fig, self.ax = plt.subplots()
        self.ax.set_xlim(-3, 3)
        self.ax.set_ylim(-3, 3)
        self.ax.set_aspect('equal')

        self.sun = plt.Circle((0, 0), self.sun_radius, color='yellow')
        self.moon = plt.Circle((self.distance_earth_moon, 0), self.moon_radius, color='gray')

        self.ax.add_artist(self.sun)
        self.ax.add_artist(self.moon)

        self.create_controls()

        self.ani = FuncAnimation(self.fig, self.update, frames=np.arange(0, 100), interval=50)

        self.canvas = FigureCanvasTkAgg(self.fig, master=self.master)
        self.canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        self.animate_loop()

    def create_controls(self):

        speed_slider = tk.Scale(self.master, from_=0.01, to=1.0, resolution=0.01,
                                label='Скорость движения Луны', orient='horizontal',
                                command=self.update_speed)
        speed_slider.pack()

        radius_label = tk.Label(self.master, text="Радиус Луны:")
        radius_label.pack()

        self.radius_entry = tk.Entry(self.master)
        self.radius_entry.insert(0, str(self.moon_radius))
        self.radius_entry.pack()

        radius_button = tk.Button(self.master, text="Установить радиус Луны", command=self.set_moon_radius)
        radius_button.pack()

        distance_slider = tk.Scale(self.master, from_=1.0, to=10.0, resolution=0.1,
                                   label='Расстояние до Луны', orient='horizontal',
                                   command=self.update_distance)
        distance_slider.set(self.distance_earth_moon)
        distance_slider.pack()


        start_button = tk.Button(self.master, text="Запустить анимацию", command=self.start_animation)
        start_button.pack()

        reset_button = tk.Button(self.master, text="Сбросить параметры", command=self.reset_parameters)
        reset_button.pack()

    def update_speed(self, val):

        self.speed = float(val)

    def set_moon_radius(self):

        try:
            new_radius = float(self.radius_entry.get())
            if new_radius > 0:
                self.moon_radius = new_radius
                self.moon.set_radius(self.moon_radius)
            else:
                print("Радиус должен быть положительным.")

            self.canvas.draw()

        except ValueError:
            print("Введите корректное значение радиуса.")

    def update_distance(self, val):

        self.distance_earth_moon = float(val)
        self.moon.center = (self.distance_earth_moon, 0)

    def start_animation(self):

        self.ani_running = True

    def reset_parameters(self):

        self.distance_earth_moon = 5.0
        self.moon_radius = 0.3
        self.speed = 0.05

        for widget in self.master.winfo_children():
            if isinstance(widget, tk.Scale) and widget.cget("label") == 'Расстояние до Луны':
                widget.set(self.distance_earth_moon)
            if isinstance(widget, tk.Entry):
                widget.delete(0, tk.END)
                widget.insert(0, str(self.moon_radius))

            if isinstance(widget, tk.Scale) and widget.cget("label") == 'Скорость движения Луны':
                widget.set(self.speed)

    def update(self, frame):

        if not self.ani_running:
            return

        new_x_position = self.moon.center[0] - self.speed

        if new_x_position < -self.sun_radius:
            new_x_position = self.distance_earth_moon

        self.moon.center = (new_x_position, 0)

    def animate_loop(self):

        if not self.ani_running:
            return
        self.canvas.draw()
        self.master.after(50, self.animate_loop)


if __name__ == "__main__":
    root = tk.Tk()
    app = SolarEclipseSimulation(root)
    root.mainloop()

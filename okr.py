from tkinter import *
from math import *
window = Tk() #главное окно
size = 600
canvas = Canvas(window, width=size,height=size)#установка размеров
canvas.pack()

radius = 200
center = 300,300
canvas.create_oval(center[0]-radius,center[1]-radius, center[0]+radius,center[1]+radius)

angle = 0
speed = 10
direction = -1
def move():
    global angle 
    r_angle = radians(angle) # Конвертируем угол в радианы
    #вычисление координты точки на окружности
    point_x  = center[0]+ radius * cos(r_angle)
    point_y = center[1] + radius * sin(r_angle)
    canvas.delete("point") #удаляем пред полож точки
    #рисуем точку
    canvas.create_oval(point_x - 5, point_y - 5, point_x + 5, point_y + 5, fill="red", tag="point")
    angle += direction*speed# Увеличиваем угол для создания движения точки
    window.after(60, move)
window.mainloop()
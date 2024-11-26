import sys
import json
import random
from PyQt6.QtCore import *
from PyQt6.QtWidgets import *
from PyQt6.QtGui import *

class Frog(QGraphicsEllipseItem):
    def __init__(self, x, y, weight, max_jump_distance, direction='right'):
        super().__init__(-15, -15, 30, 30)
        self.setPos(QPointF(x, y))
        self.weight = weight
        self.max_jump_distance = max_jump_distance
        self.setBrush(QBrush(QColor("dark red")))
        self.setZValue(10)
        self.direction = direction

    def jump(self, where):
        self.setPos(where.x(), where.y())

class LilyPad(QGraphicsEllipseItem):
    def __init__(self, x, y, strength):
        super().__init__(-25, -25, 50, 50)
        self.setPos(x, y)
        self.strength = strength
        self.setBrush(QBrush(QColor("dark green")))

    def fall(self, speed):
        current_pos = self.pos()
        self.setPos(current_pos.x(), current_pos.y() + speed)
    
    def getPos(self):
        return self.pos()

class FrogDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setWindowTitle("Настройки лягушки")
        layout = QVBoxLayout(self)
       
        l1 = QLabel()
        l1.setText('Параметры :')
        l1.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(l1)

        self.weight_input = QLineEdit()
        self.weight_input.setPlaceholderText("Вес лягушки")
        self.jump_distance_input = QLineEdit()
        self.jump_distance_input.setPlaceholderText("Максимальное расстояние прыжка")  
        self.add_button = QPushButton("Добавить лягушку")
        self.add_button.clicked.connect(self.accept)
        
        layout.addWidget(QLabel("Вес лягушки:"))
        layout.addWidget(self.weight_input)
        layout.addWidget(QLabel("Максимальное расстояние прыжка:"))
        layout.addWidget(self.jump_distance_input)
        layout.addWidget(self.add_button)

    def get_frog_params(self):
        weight = int(self.weight_input.text()) if self.weight_input.text() else 1
        jump_distance = int(self.jump_distance_input.text()) if self.jump_distance_input.text() else 50
        return weight, jump_distance

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setFixedSize(1000, 600) 
        self.scene = QGraphicsScene(0, 0, 800, 600)
        self.view = QGraphicsView(self.scene, self)
        self.view.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.view.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.view.setGeometry(200, 0, 800, 600)

        self.settings_panel = QWidget(self)
        self.settings_panel.setGeometry(0, 0, 200, 200)
        self.settings_layout = QVBoxLayout(self.settings_panel)

        self.tail = 5
        self.fl_speed = 1
        self.spwn_int = 600
        self.m_lil_w = 20
        self.j_up_int = 100
        self.lilp_f_upd_it = 20
        self.max_lil = 5
        self.frog_weight = 10
        self.frog_jump_distance = 200

        self.fall_speed_slider = QSlider(Qt.Orientation.Horizontal)
        self.fall_speed_slider.setRange(1, 5)
        self.fall_speed_slider.setValue(self.fl_speed)
        self.fall_speed_slider.valueChanged.connect(self.update_fall_speed)
        self.settings_layout.addWidget(QLabel("Скорость падения"))
        self.settings_layout.addWidget(self.fall_speed_slider)

        self.spawn_interval_slider = QSlider(Qt.Orientation.Horizontal)
        self.spawn_interval_slider.setRange(100, 750)
        self.spawn_interval_slider.setValue(self.spwn_int)
        self.spawn_interval_slider.valueChanged.connect(self.update_spawn_interval)
        self.settings_layout.addWidget(QLabel("Интервал спавна"))
        self.settings_layout.addWidget(self.spawn_interval_slider)
        
        self.pause_button = QPushButton("Пауза")
        self.pause_button.clicked.connect(self.f_pause)
        self.settings_layout.addWidget(self.pause_button)

        self.lines = []

        self.l_ber = 0
        self.r_ber = self.scene.width()

        self.lilies = []

        self.previous_lily_pad = None

        self.pause = False

        self.frog = Frog(400, 300, weight=self.frog_weight, max_jump_distance=self.frog_jump_distance, direction='right')
        self.scene.addItem(self.frog)
        self.frogs = [self.frog]

        self.timer_frog = QTimer()
        self.timer_frog.timeout.connect(self.upd_f_pos)
        self.timer_frog.start(self.j_up_int)

        self.timer = QTimer()
        self.timer.timeout.connect(self.upd_l_pos)
        self.timer.start(self.lilp_f_upd_it)

        self.spawn_timer = QTimer()
        self.spawn_timer.timeout.connect(self.create_lil)
        self.spawn_timer.start(0)
    
    def update_fall_speed(self, value):
        self.lilp_f_upd_it = value
        self.timer.start(self.lilp_f_upd_it)

    def update_frog_jump_distance(self, value):
        self.frog_jump_distance = value
        self.frog.max_jump_distance = value

    def update_spawn_interval(self, value):
        self.spwn_int = value

    def update_lily_weight_max(self, value):
        self.m_lil_w = value

        self.load_or_create_state()

    def upd_l_pos(self):
        if self.pause:
            return
        for lily in self.lilies:
            lily.fall(self.fl_speed)
            if lily.pos().y() > self.scene.height():
                self.scene.removeItem(lily)
                self.lilies.remove(lily)

    def upd_f_pos(self):
        if self.pause:
            return
        for frog in self.frogs:
            next_pos = self.find_next_pos(frog)

            if next_pos:
                jumped_lily = None
                for lily in self.lilies:
                    if lily.pos() == next_pos:
                        jumped_lily = lily
                        break
                    
                self.draw_line(frog.pos(), next_pos)
                frog.jump(next_pos)
                if self.previous_lily_pad:
                    if self.previous_lily_pad in self.lilies:
                        self.previous_lily_pad.strength -= frog.weight
                        if self.previous_lily_pad.strength <= 0:
                            self.scene.removeItem(self.previous_lily_pad)
                            self.lilies.remove(self.previous_lily_pad)
                self.previous_lily_pad = jumped_lily

            else:
                current_pos = frog.pos()
                self.draw_line(frog.pos(), current_pos)
                for lily in self.lilies:
                    if abs(lily.pos().x() - current_pos.x()) < 1:
                        frog.setPos(lily.pos().x(), lily.pos().y())
            if frog.direction == 'right' and frog.pos().x() >= self.r_ber:
                frog.direction = 'left'
            elif frog.direction == 'left' and frog.pos().x() <= self.l_ber:
                frog.direction = 'right'

    def load_or_create_state(self):
        if not OSError.path.exists(self.STATE_FILE):
            print("Файл состояния отсутствует. Создаём новый с начальными значениями.")
            state = {
                "frogs": [{"x": 400, "y": 300, "weight": 10, "max_jump_distance": 200, "direction": "right"}],
                "lilies": [{"x": 100, "y": 0, "strength": 10}]
            }
            with open(self.STATE_FILE, "w") as f:
                json.dump(state, f, indent=4)
        else:
            with open(self.STATE_FILE, "r") as f:
                state = json.load(f)

    def f_pause(self):
        if not self.pause:
            self.pause = True
            self.pause_button.setText("Продолжить")
            self.timer_frog.stop()
            self.spawn_timer.stop()
            self.timer.stop()
            print("Анимация поставлена на паузу.")
        else:
            self.pause = False
            self.pause_button.setText("Пауза")
            self.timer_frog.start(100) 
            self.spawn_timer.start(20)
            self.timer.start(20) 
            print("Анимация возобновлена.")

    def mousePressEvent(self, event):
        posi = self.view.mapToScene(event.pos())
        if event.button() == Qt.MouseButton.LeftButton:
            dialog = FrogDialog(self)
            if dialog.exec():
                weight, jump_distance = dialog.get_frog_params()
                new_frog = Frog(posi.x(), posi.y(), weight=weight,
                            max_jump_distance=jump_distance)
                new_frog.direction = 'left'
                self.frogs.append(new_frog)
                self.scene.addItem(new_frog)
    
    def create_lil(self):
        self.spawn_timer.start(random.randint(self.spwn_int - 100, self.spwn_int + 100))

        count = random.randint(1, self.max_lil)
        positions = set()

        while len(positions) < count:
            x = random.randint(self.frog_jump_distance // 4, int(self.scene.width()) - self.frog_jump_distance // 4)
            if all(abs(x - pos) > 40 for pos in positions):
                positions.add(x)
        for x in positions:
            strength = random.randint(1, self.m_lil_w)  
            lily_pad = LilyPad(x, 0, strength)
            self.scene.addItem(lily_pad) 
            self.lilies.append(lily_pad)

    def find_next_pos(self,frog):
        possible_lilies = []
        current_pos = frog.pos()

        distance_to_l_ber = abs(current_pos.x() - self.l_ber)
        distance_to_r_ber = abs(current_pos.x() - self.r_ber)

        if frog.direction == 'right' and distance_to_r_ber <= frog.max_jump_distance:
            return QPointF(self.r_ber, current_pos.y())

        if frog.direction == 'left' and distance_to_l_ber <= frog.max_jump_distance:
            return QPointF(self.l_ber, current_pos.y())

        for lily in self.lilies:
            distance_x = abs(lily.pos().x() - current_pos.x())
            distance_y = abs(lily.pos().y() - current_pos.y())
            distance = (distance_x ** 2 + distance_y ** 2) ** 0.5

            if distance <= frog.max_jump_distance and distance > 20:
                possible_lilies.append(lily)

        if possible_lilies:
            if frog.direction == 'right':
                next_lily = max(possible_lilies, key=lambda l: l.pos().x())
            else:
                next_lily = min(possible_lilies, key=lambda l: l.pos().x())
            return next_lily.pos()  
        return None
    
    def draw_line(self, start_pos, end_pos): 
        pen = QPen(QColor("yellow"))
        pen.setWidth(3)
        line = self.scene.addLine(start_pos.x(), start_pos.y(), end_pos.x(), end_pos.y(), pen)
        self.lines.append(line)
        if len(self.lines) > self.tail:
            while len(self.lines) > self.tail:
                old_line = self.lines.pop(0)
                self.scene.removeItem(old_line)
    
    def keyPressEvent(self, e):
      if e.key() == Qt.Key.Key_Escape:  
          print("Closing application.")
          QApplication.quit()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


import sys
import json
import random
import os
from PyQt6.QtCore import *
from PyQt6.QtWidgets import *
from PyQt6.QtGui import *
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')

class Frog(QGraphicsEllipseItem):
    def __init__(self, x, y, weight, max_jump_distance, direction='right'):
        super().__init__(-15, -15, 30, 30)
        self.setPos(QPointF(x, y))
        self.weight = weight
        self.max_jump_distance = max_jump_distance
        self.setBrush(QBrush(QColor("dark red")))
        self.setZValue(10)
        self.direction = direction
        logging.info(f"Создана лягушка на позиции ({x}, {y})")
    def jump_to(self, destination):
        logging.info(f"Лягушка прыгает на {destination}")
        self.setPos(destination.x(), destination.y())

class Lil(QGraphicsEllipseItem):
    def __init__(self, x, y, strength):
        super().__init__(-25, -25, 50, 50)
        self.setPos(x, y)
        self.strength = strength
        self.setBrush(QBrush(QColor("dark green")))

    def fall(self, speed):
        current_pos = self.pos()
        self.setPos(current_pos.x(), current_pos.y() + speed)
    
    def get_p(self):
        return self.pos()
#3 
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
        jump_distance = int(self.jump_distance_input.text()) if self.jump_distance_input.text() else 100
        return weight, jump_distance
class LeafPad(QGraphicsEllipseItem):
    def __init__(self, x, y, durability):
        super().__init__(-25, -25, 50, 50)
        self.setPos(x, y)
        self.durability = durability
        self.update_color()

    def update_color(self):
        if self.durability > 15:
            self.setBrush(QBrush(QColor("green")))
        elif self.durability > 5:
            self.setBrush(QBrush(QColor("yellow")))
        else:
            self.setBrush(QBrush(QColor("red")))

    def randomize_position(self):
        if random.random() > 0.7:  # 30% шанс на перемещение
            new_x = self.pos().x() + random.randint(-50, 50)
            new_y = self.pos().y() + random.randint(-20, 20)
            self.setPos(new_x, new_y)
    
class Game(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setFixedSize(1000, 600) 
        self.scene = QGraphicsScene(0, 0, 800, 600)
        self.scene.setBackgroundBrush(QBrush(QColor("lightblue")))
        self.view = QGraphicsView(self.scene, self)
        self.view.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.view.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.view.setGeometry(200, 0, 800, 600)

        self.settings_panel = QWidget(self)
        self.settings_panel.setGeometry(0, 0, 200, 200)
        self.settings_layout = QVBoxLayout(self.settings_panel)
        
        #парметры
        self.path = 5
        self.fl_speed = 1
        self.spwn_int = 600
        self.m_lil_w = 20
        self.max_lil = 5
        self.frog_weight = 10
        self.j_up_int = 100
        self.lilp_f_upd_it = 20 
        self.frog_jump_distance = 200
        self.paths = []
        self.l_ber = 0
        self.r_ber = self.scene.width()
        self.lils = []
        self.prev_lil = None
        self.pause = False
        #3 laba
        self.fall_speed_slider = QSlider(Qt.Orientation.Horizontal)
        self.fall_speed_slider.setRange(1, 5)
        self.fall_speed_slider.setValue(self.fl_speed)
        self.fall_speed_slider.valueChanged.connect(self.upd_fsp)
        self.settings_layout.addWidget(QLabel("Скорость течения реки"))
        self.settings_layout.addWidget(self.fall_speed_slider)
        #3 laba
        self.spawn_interval_slider = QSlider(Qt.Orientation.Horizontal)
        self.spawn_interval_slider.setRange(100, 1000)
        self.spawn_interval_slider.setValue(self.spwn_int)
        self.spawn_interval_slider.valueChanged.connect(self.upd_sppwn_int)
        self.settings_layout.addWidget(QLabel("Интервал спавна"))
        self.settings_layout.addWidget(self.spawn_interval_slider)
        
        self.pause_button = QPushButton("Пауза")
        self.pause_button.clicked.connect(self.f_pause)
        self.settings_layout.addWidget(self.pause_button)

        self.frog = Frog(400, 300, weight=self.frog_weight, max_jump_distance=self.frog_jump_distance, direction='right')
        self.scene.addItem(self.frog)
        self.frogs = [self.frog]
        self.add_gif_to_scene("C:/Users/user/Desktop/python/prakt/river.gif", x=300, y=200)

        self.temer_fr = QTimer()
        self.temer_fr.timeout.connect(self.upd_f_pos)
        self.temer_fr.start(self.j_up_int)

        self.temer_updlilpos = QTimer()
        self.temer_updlilpos.timeout.connect(self.upd_l_pos)
        self.temer_updlilpos.start(self.lilp_f_upd_it)

        self.tim_cr_lil = QTimer()
        self.tim_cr_lil.timeout.connect(self.crt_lil)
        self.tim_cr_lil.start(0)

    def add_gif_to_scene(self, gif_path, x, y):
        """Добавление GIF на сцену."""
    
        # Проверка существования файла GIF
        if not os.path.isfile(gif_path):
            print(f"Ошибка: файл '{gif_path}' не найден.")
            return

        # Создание объекта QMovie
        movie = QMovie(gif_path)
    
        # Проверка, успешно ли загружен GIF
        if not movie.isValid():
            print(f"Ошибка: файл '{gif_path}' не является корректным GIF.")
            return

        movie.start()  # Запускаем воспроизведение GIF 

        # Создание элемента для отображения изображения
        pixmap_item = QGraphicsPixmapItem()
        self.scene.addItem(pixmap_item)

        # Связываем изменение текущего кадра с обновлением pixmap 
        movie.frameChanged.connect(lambda: pixmap_item.setPixmap(movie.currentPixmap()))
    
        # Установка позиции элемента на сцене
        pixmap_item.setPos(x, y)

    #обновления
    def upd_fsp(self, value):
        self.lilp_f_upd_it = value
        self.temer_updlilpos.start(self.lilp_f_upd_it)

    def upd_fr_jpdist(self, value):
        self.frog_jump_distance = value
        self.frog.max_jump_distance = value

    def upd_sppwn_int(self, value):
        self.spwn_int = value

    def upd_lil_maxw(self, value):
        self.m_lil_w = value
    #позиция кувшинки
    def upd_l_pos(self):
        if self.pause: return
        for lily in self.lils:
            lily.fall(self.fl_speed)
            if lily.pos().y() > self.scene.height():
                self.scene.removeItem(lily)
                self.lils.remove(lily)
    #позиция лягушки
    def upd_f_pos(self):
        if self.pause:
            return
        for frog in self.frogs:
            next_pos = self.find_next_pos(frog)

            if next_pos:
                jumped_lily = None
                for lily in self.lils:
                    if lily.pos() == next_pos:
                        jumped_lily = lily
                        break
                    
                self.render_line(frog.pos(), next_pos)
                frog.jump_to(next_pos)
                if self.prev_lil:
                    if self.prev_lil in self.lils:
                        self.prev_lil.strength -= frog.weight
                        if self.prev_lil.strength <= 0:
                            self.scene.removeItem(self.prev_lil)
                            self.lils.remove(self.prev_lil)
                self.prev_lil = jumped_lily

            else:
                current_pos = frog.pos()
                self.render_line(frog.pos(), current_pos)
                for lily in self.lils:
                    if abs(lily.pos().x() - current_pos.x()) < 1:
                        frog.setPos(lily.pos().x(), lily.pos().y())
            if frog.direction == 'right' and frog.pos().x() >= self.r_ber:
                frog.direction = 'left'
            elif frog.direction == 'left' and frog.pos().x() <= self.l_ber:
                frog.direction = 'right'
    def create_rain_effect(self):
        for _ in range(50):  # Создаём 50 капель
            drop = QGraphicsEllipseItem(-2, -2, 4, 4)
            drop.setBrush(QBrush(QColor("blue")))
            drop.setPos(random.randint(0, 800), random.randint(0, 600))
            self.scene.addItem(drop)
            self.animate_drop(drop)

    def animate_drop(self, drop):
        animation = QPropertyAnimation(drop, b"pos")
        animation.setDuration(2000)
        animation.setStartValue(drop.pos())
        animation.setEndValue(QPointF(drop.pos().x(), 600))
        animation.start()
    def create_initial_state():
        print("Файл состояния отсутствует. Создаём новый с начальными значениями.")
        return {
            "frogs": [{"x": 400, "y": 300, "weight": 10, "max_jump_distance": 200, "direction": "right"}],
            "lils": [{"x": 100, "y": 0, "strength": 10}]
        }

    def load_state(self,file_path):
        if not os.path.exists(file_path):
            state = self.create_initial_state()
        try:
            with open(file_path, "w") as f:
                json.dump(state, f, indent=4)
        except IOError as e:
            print(f"Ошибка при записи файла: {e}")
            state = None
        else:
            try:
                with open(file_path, "r") as f:
                    state = json.load(f)
            except (IOError, json.JSONDecodeError) as e:
                print(f"Ошибка при чтении файла: {e}")
                state = None

        return state

    def f_pause(self):
        if self.pause:
            self.pause = False
            self.pause_button.setText("Пауза")
            self.start_timers()
            print("Анимация возобновлена.")
        else:
            self.pause = True
            self.pause_button.setText("Продолжить")
            self.stop_timers()
            print("Анимация поставлена на паузу.")

    def start_timers(self):
        self.temer_fr.start(100)
        self.tim_cr_lil.start(20)
        self.temer_updlilpos.start(20)

    def stop_timers(self):
        self.temer_fr.stop()
        self.tim_cr_lil.stop()
        self.temer_updlilpos.stop() 
    #3 laba
    def mousePressEvent(self, event):
        posi = self.view.mapToScene(event.pos())
        if event.button() == Qt.MouseButton.LeftButton: 
            dialog = FrogDialog(self)
            if dialog.exec():
                weight, jump_distance = dialog.get_frog_params()
                new_frog = Frog(posi.x(), posi.y(), weight=weight, max_jump_distance=jump_distance)
                new_frog.direction = 'left'
                self.frogs.append(new_frog)
                self.scene.addItem(new_frog)
    
    def crt_lil(self):
        self.tim_cr_lil.start(random.randint(self.spwn_int - 100, self.spwn_int + 100))
        count = random.randint(1, self.max_lil)
        positions = set()
        while len(positions) < count:
            x = random.randint(self.frog_jump_distance // 4, int(self.scene.width()) - self.frog_jump_distance // 4)
            if all(abs(x - pos) > 40 for pos in positions): positions.add(x)
        for x in positions:
            strength = random.randint(1, self.m_lil_w)  
            lily_pad = Lil(x, 0, strength)
            self.scene.addItem(lily_pad) 
            self.lils.append(lily_pad)

    def find_next_pos(self,frog):
        current_pos = frog.pos()

        distance_to_l_ber = abs(current_pos.x() - self.l_ber)
        distance_to_r_ber = abs(current_pos.x() - self.r_ber)

        pos_lil = []
        if frog.direction == 'right' and distance_to_r_ber <= frog.max_jump_distance: return QPointF(self.r_ber, current_pos.y())
        if frog.direction == 'left' and distance_to_l_ber <= frog.max_jump_distance: return QPointF(self.l_ber, current_pos.y())

        for lily in self.lils:
            dst_x = abs(lily.pos().x() - current_pos.x())
            dst_y = abs(lily.pos().y() - current_pos.y())
            dst = (dst_x ** 2 + dst_y ** 2) ** 0.5
            if dst <= frog.max_jump_distance and dst > 20:pos_lil.append(lily)
        if pos_lil:
            if frog.direction == 'right': nxtlil = max(pos_lil, key=lambda l: l.pos().x())
            else: nxtlil = min(pos_lil, key=lambda l: l.pos().x())
            return nxtlil.pos()  
        return None
    
    # отрисовка следа
    def render_line(self, begin_point, finish_point): 
        # Создаем перо для линии с заданными цветом и шириной
        line_pen = QPen(QColor("yellow"))
        line_pen.setWidth(3)

        # Добавляем линию на сцену
        new_line = self.scene.addLine(begin_point.x(), begin_point.y(), finish_point.x(), finish_point.y(), line_pen)
        self.paths.append(new_line)

        # Удаляем старые линии, если превышен лимит
        if len(self.paths) > self.path:
            while len(self.paths) > self.path:
                outdated_line = self.paths.pop(0)
                self.scene.removeItem(outdated_line)
    #3 laba
    def keyPressEvent(self, e):
      
      if e.key() == Qt.Key.Key_Escape:  
          print("Closing application.")
          QApplication.quit()
      elif e.key() == Qt.Key.Key_Pause:
          QApplication.pause()
      elif e.key() == Qt.Key.Key_S:
        for frog in self.frogs:
            frog.setPos(frog.pos().x(), frog.pos().y() + 20)
      elif e.key() == Qt.Key.Key_A:
        for frog in self.frogs:
            frog.setPos(frog.pos().x() - 20, frog.pos().y())
      elif e.key() == Qt.Key.Key_D:
        for frog in self.frogs:
            frog.setPos(frog.pos().x() + 20, frog.pos().y())
     
if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = Game()
    window.show()
    sys.exit(app.exec())

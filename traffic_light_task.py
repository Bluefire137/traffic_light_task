import threading
from queue import Queue

class TrafficLight:
    '''Класс Светофор'''
    def __init__(self, id, is_pedestrian=False, queue_size=0):
        self.id = id
        self.state = "red"  # типы состояний: 'red', 'green', 'yellow' (только для автомобильных)
        self.queue_size = queue_size # размер очереди
        self.is_pedestrian = is_pedestrian # признак, является ли светофор пешеходным
        self.event_queue = Queue()
        self.lock = threading.Lock()
        self.timer = None

    def set_state(self, state):
        '''Метод установки цвета сигнала светофора в зависимости от его типа (автомобильный/пешеходный)'''
        with self.lock:
            self.state = state
            light_type = "Pedestrian" if self.is_pedestrian else "Car"
            print(f"{light_type} traffic light {self.id} switched to {state}.")

    def increment_queue(self):
        '''Метод увеличивает размер очереди (количество автомобилей или пешеходов,
        ожидающих на светофоре) на единицу'''
        with self.lock:
            self.queue_size += 1

    def decrement_queue(self):
        '''Метод уменьшает размер очереди на единицу'''
        with self.lock:
            if self.queue_size > 0:
                self.queue_size -= 1

    def start_timer(self, duration, event):
        '''Таймер, который через определённое время добавляет указанное событие в очередь событий светофора'''
        if self.timer:
            self.timer.cancel()
        self.timer = threading.Timer(duration, self.event_queue.put, args=[event])
        self.timer.start()

    def process_events(self, other_lights):
        '''Основной метод для управления поведением сигналов обоих типов светофоров
        в зависимости от очереди автомобилей/пешеходов'''
        while True:
            event = self.event_queue.get()
            if event == "switch_to_green":
                max_queue_light = max(other_lights, key=lambda light: light.queue_size)
                if max_queue_light.queue_size > self.queue_size:
                    self.start_timer(5, "switch_to_green")
                else:
                    self.set_state("green")
                    if self.is_pedestrian:
                        self.start_timer(10, "switch_to_red")  # пешеходный светофор: переключение сразу на красный
                    else:
                        self.start_timer(10, "switch_to_yellow")  # автомобильный светофор: переключение на жёлтый
            elif event == "switch_to_yellow" and not self.is_pedestrian:
                self.set_state("yellow")
                self.start_timer(2, "switch_to_red")
            elif event == "switch_to_red":
                self.set_state("red")
                max_queue_light = max(other_lights, key=lambda light: light.queue_size)
                max_queue_light.event_queue.put("switch_to_green")

def main():
    # инициализация светофоров для автомобилей и пешеходов
    car_lights = [TrafficLight(id=i, queue_size=5*i) for i in range(1, 5)]
    pedestrian_lights = [TrafficLight(id=i, is_pedestrian=True, queue_size=2*i) for i in range(5, 13)]

    lights = car_lights + pedestrian_lights

    # запуск обработки событий для каждого светофора в отдельном потоке
    for light in lights:
        threading.Thread(target=light.process_events, args=(lights,)).start()

    # старт первой фазы
    car_lights[0].event_queue.put("switch_to_green")

if __name__ == "__main__":
    main()

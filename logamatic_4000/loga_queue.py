import threading
import time
from queue import Queue
from c3964r import Dust3964r  # lokale Bibliothek einbinden
from id_offset_mapping import ID_OFFSET_MAPPING

# Konstanten definieren
COM_PORT = '/dev/ttyUSB0'
BUDERUS_TIMEOUT = 60
CYCLE_TIME_DELAY = 3


class Logamatic4000(Dust3964r, threading.Thread):
    def __init__(self, data_queue):
        super().__init__(port=COM_PORT, SLP=0.1)
        threading.Thread.__init__(self)
        self.last_update_time = None
        self.stop_polling = False
        self.data_queue = data_queue

    def run(self):
        while not self.stop_polling:
            if self.should_inject():
                self.inject_commands()
            self.running()
            time.sleep(1.0 / 10.0)

    def should_inject(self):
        return self.last_update_time is None or time.time() > (self.last_update_time + BUDERUS_TIMEOUT)

    def inject_commands(self):
        if self.last_update_time:
            time.sleep(CYCLE_TIME_DELAY)
        self.last_update_time = time.time()
        print("Injecting commands...")
        print("Inject: DD")
        self.newJob(b"\xDD")
        print("Inject: A2 00")
        self.newJob(b"\xA2\x00")

    def process_telegram(self, id, offset, data):
        if id in ID_OFFSET_MAPPING and offset in ID_OFFSET_MAPPING[id]:
            topics = ID_OFFSET_MAPPING[id][offset]
            for index, topic_offset in topics.items():
                self.data_queue.put((topic_offset, data[index]))


class Logamatic4000Sensor:
    def __init__(self, data_queue):
        self.data_queue = data_queue
        self.stop_polling = False
        self.entity_id = None  # Setzen Sie hier den Wert der Entitäts-ID für Ihren Sensor

    def start(self):
        while not self.stop_polling:
            # Überprüfen, ob neue Daten in der Warteschlange verfügbar sind
            while not self.data_queue.empty():
                topic_offset, value = self.data_queue.get()
                self.update_entity(topic_offset, value)  # Aktualisieren Sie die Entität mit den neuen Daten
            time.sleep(1)

    def update_entity(self, topic_offset, value):
        # Hier wird die Entität mit den neuen Daten aktualisiert
        print(f"Updating entity {self.entity_id} with data: {topic_offset} - {value}")


def main():
    # Queue für die Dateninitialisieren
    data_queue = Queue()

    # Globale Variablen initialisieren
    loga = Logamatic4000(data_queue)
    loga.CFG_PRINT = False  # Setze auf True, um Debugging-Informationen zu drucken

    # Custom Component initialisieren
    sensor = Logamatic4000Sensor(data_queue)
    sensor.entity_id = "sensor.logamatic_4000"  # Beispiel-Entitäts-ID

    try:
        print("Starting Logamatic4000")
        loga.start()

        # Starten des Threads oder Tasks für die Custom Component
        thread = threading.Thread(target=sensor.start)
        thread.start()

        # Warten auf KeyboardInterrupt
        while True:
            time.sleep(1)

    except KeyboardInterrupt:
        print('Stopping Logamatic4000 polling...')
        loga.stop_polling = True
        loga.join()
        print('Logamatic4000 polling stopped.')


if __name__ == "__main__":
    main()

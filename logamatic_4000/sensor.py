"""Platform for sensor integration."""
from __future__ import annotations
import asyncio
import threading
import time
from queue import Queue
import logging

from homeassistant.components.sensor import SensorEntity
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import ConfigType, DiscoveryInfoType

# import local custom classes
from .c3964r import Dust3964r
from .id_offset_mapping import ID_OFFSET_MAPPING

_LOGGER = logging.getLogger(__name__)

# Klasse für Logamatic4000
class Logamatic4000(Dust3964r, threading.Thread):
    def __init__(self, data_queue, com_port, update_rate):
        super().__init__(port=com_port, SLP=0.1)
        threading.Thread.__init__(self)
        self.last_update_time = None
        self.stop_polling = False
        self.data_queue = data_queue
        self.update_rate = update_rate

    def run(self):
        while not self.stop_polling:
            if self.should_inject():
                self.inject_commands()
            self.running()
            time.sleep(1.0 / 10.0)

    def should_inject(self):
        return self.last_update_time is None or time.time() > (self.last_update_time + self.update_rate)

    def inject_commands(self):
        if self.last_update_time:
            time.sleep(3)
        self.last_update_time = time.time()
        _LOGGER.debug("Enter direct mode, Inject: DD")
        self.newJob(b"\xDD")
        _LOGGER.debug("Request values from ID 00, Inject: A2 00")
        self.newJob(b"\xA2\x00")

    def process_telegram(self, id, offset, data):
        if id in ID_OFFSET_MAPPING and offset in ID_OFFSET_MAPPING[id]:
            topics = ID_OFFSET_MAPPING[id][offset]
            for index, topic_offset in topics.items():
                self.data_queue.put((topic_offset, data[index]))

    def ReadSuccess(self, telegram):
        if len(telegram) > 4:
            id, offset, data = telegram[:3], telegram[3], telegram[4:]
            self.process_telegram(id, offset, data)

class LogamaticSensor(SensorEntity):
    """Representation of a Logamatic Sensor."""

    def __init__(self, data_queue, sensor_name, update_rate):
        """Initialize the sensor."""
        super().__init__()
        self.data_queue = data_queue
        self._sensor_name = sensor_name
        self._update_interval = update_rate
        self._attributes = {}
        
    @property
    def name(self):
        """Return the name of the sensor."""
        return f"logamatic_{self._sensor_name}"

    @property
    def state_attributes(self):
        """Return the state attributes."""
        return self._attributes

    async def async_update_sensor(self) -> None:
        """Update the sensor."""
        while True:
            while not self.data_queue.empty():
                topic_offset, value = self.data_queue.get()
                self._attributes[topic_offset] = value
                _LOGGER.debug(f"Updated sensor {self._sensor_name} attribute {topic_offset} to {value}")
            await asyncio.sleep(self._update_interval)
    
    async def async_added_to_hass(self):
        """Run when this Entity has been added to HA."""
        self._task = asyncio.create_task(self.async_update_sensor())

    async def async_will_remove_from_hass(self):
        """Run when Entity will be removed from HA."""
        self._task.cancel()
        await self._task

def setup_platform(
    hass: HomeAssistant,
    config: ConfigType,
    add_entities: AddEntitiesCallback,
    discovery_info: DiscoveryInfoType | None = None
) -> None:
    """Set up the sensor platform."""
    data_queue = Queue()
    
    #load component configurations or consider default values
    com_port = config.get('com_port', '/dev/ttyUSB0') #todo define defaults as constants
    update_rate = config.get('update_rate', 60) #todo define defaults as constants
    protocol_deep = config.get('protocol_deep', False) #todo define defaults as constants

    loga = Logamatic4000(data_queue, com_port, update_rate)
    loga.CFG_PRINT = protocol_deep  # deep level protocol debug
    loga.start()
    _LOGGER.debug("Data Request running....")

    #add sensor
    add_entities([LogamaticSensor(data_queue, 'logamatic', update_rate)])
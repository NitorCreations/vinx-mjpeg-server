import asyncio
import logging

import aiohttp

from attr import dataclass
from pylw3 import LW3, NodeResponse, is_encoder_discovery_node

from vinx_mjpeg_server.settings import CAPTURE_INTERVAL, CAPTURE_TIMEOUT

logger = logging.getLogger(__name__)


@dataclass
class PreviewImage:
    available: bool
    data: bytes
    update_event: asyncio.Event


class Encoder:
    def __init__(self, device_name: str, ip_address: str):
        self.device_name = device_name
        self.ip_address = ip_address
        self.preview_image = PreviewImage(False, b"", asyncio.Event())

    async def capture_image_task(self):
        while True:
            try:
                await asyncio.wait_for(self.capture_image(), CAPTURE_TIMEOUT.seconds)
            except TimeoutError:
                self.preview_image.available = False
                logger.error(f"Timeout while getting capture image from {self.device_name} at {self.ip_address}")
            except Exception as e:
                self.preview_image.available = False
                logger.error(
                    f"An exception occured when getting capture image from {self.device_name} at {self.ip_address}: {e}"
                )
            finally:
                self.preview_image.update_event.set()
                await asyncio.sleep(CAPTURE_INTERVAL.seconds)

    async def capture_image(self):
        async with aiohttp.ClientSession() as session:
            async with session.get(self.get_capture_url()) as resp:
                if resp.status != 200:
                    self.preview_image.available = False
                    logger.error(f"Capture endpoint returned bad HTTP status ({resp.status}), marking as unavailable")
                else:
                    self.preview_image.available = resp.content_length > 0
                    self.preview_image.data = await resp.read()

    def get_capture_url(self) -> str:
        return f"http://{self.ip_address}/capture.jpg"


async def discover_encoders(bootstrap_node: str) -> list[Encoder]:
    encoders = []
    bootstrap_device = LW3(host=bootstrap_node, port=6107)

    async with bootstrap_device.connection():
        discovery_nodes = await bootstrap_device.get_all("/DISCOVERY")
        encoder_nodes: list[NodeResponse] = list(filter(is_encoder_discovery_node, discovery_nodes))

        for encoder_node in encoder_nodes:
            device_name = await bootstrap_device.get_property(f"{encoder_node.path}.DeviceName")
            ip_address = await bootstrap_device.get_property(f"{encoder_node.path}.IpAddress")

            logger.debug(f"Discovered encoder {device_name} at {ip_address}")
            encoders.append(Encoder(str(device_name), str(ip_address)))

    return encoders

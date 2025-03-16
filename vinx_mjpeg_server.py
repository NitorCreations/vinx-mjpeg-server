import argparse
import asyncio
import logging
import os

from aiohttp import web

from vinx_mjpeg_server.encoder import discover_encoders
from vinx_mjpeg_server.http import HttpRequestHandler

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger("vinx_mjpeg_server")


async def main():
    # Parse arguments
    parser = argparse.ArgumentParser(
        prog="vinx-mjpeg-server", description="Serves MJPEG streams from VINX HDMI encoder preview images"
    )
    parser.add_argument(
        "--bootstrap-node", required=True, help="A VINX encoder to use as bootstrap node for auto-discovery"
    )
    parser.add_argument(
        "--fallback-image", help="A JPEG image to use as fallback when the encoder preview is unavailable"
    )
    parser.add_argument("-l", "--listen-address", default="0.0.0.0",
                        help="The address the HTTP server should listen on")
    parser.add_argument("-p", "--port", default=6180, type=int, help="The port the HTTP should listen on")
    args = parser.parse_args()

    if not os.access(args.fallback_image, os.R_OK):
        parser.error("--fallback-image must point to a readable file")

    # Use the bootstrap node to discover all encoders on the network
    try:
        logger.info(f"Discovering encoders using bootstrap node {args.bootstrap_node}")
        encoders = await discover_encoders(args.bootstrap_node)
        logger.info(f"Discovered {len(encoders)} encoders in total")
    except Exception:
        logger.exception("Failed to query for discovered encoders")
        return

    # Read the fallback image
    with open(args.fallback_image, mode="rb") as f:
        fallback_image = f.read()

    # Start polling the encoders
    logger.info("Starting background tasks for all encoders")
    tasks = set()
    for encoder in encoders:
        tasks.add(asyncio.create_task(encoder.capture_image_task()))

    # Start HTTP server
    logger.info("Starting web server")
    handler = HttpRequestHandler(encoders, fallback_image)
    server = web.Server(handler.handle)
    runner = web.ServerRunner(server)
    await runner.setup()

    site = web.TCPSite(runner, args.listen_address, args.port)
    await site.start()

    # Wait indefinitely for the background tasks to complete
    logger.info("Server started")
    await asyncio.gather(*tasks)


asyncio.run(main())

# vinx-mjpeg-server

[![Linting](https://github.com/NitorCreations/vinx-mjpeg-server/actions/workflows/ruff.yaml/badge.svg)](https://github.com/NitorCreations/vinx-mjpeg-server/actions/workflows/ruff.yaml)

This is an MJPEG server for Lightware VINX HDMI encoders. It provides a basic HTTP server that serves static images and 
MJPEG streams for each encoder on the network. Encoders are automatically enumerated by contacting a bootstrap node
(can be any VINX device on the network) and looking at the devices it has discovered.

Each encoder's capture HTTP endpoint is polled at regular intervals. The images are stored in memory and served 
on-demand to any/all connected MJPEG clients.

A fallback image can be provided which will be returned whenever the encoder doesn't have signal present, or when 
there was an issue in fetching the preview image.

This application uses our [pylw3](https://github.com/NitorCreations/pylw3) library under the hood to discover encoders 
and [aiohttp](https://github.com/aio-libs/aiohttp) for HTTP.

## License

GNU GENERAL PUBLIC LICENSE version 3

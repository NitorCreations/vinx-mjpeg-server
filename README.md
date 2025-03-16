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

## Usage

The recommended way is to run the server using the supplied Dockerfile:

```bash
$ docker build -t vinx-mjpeg-server:latest .
$ docker run vinx-mjpeg-server:latest -h
DEBUG:asyncio:Using selector: EpollSelector
usage: vinx-mjpeg-server [-h] --bootstrap-node BOOTSTRAP_NODE
                         [--fallback-image FALLBACK_IMAGE] [-l LISTEN_ADDRESS]
                         [-p PORT]

Serves MJPEG streams from VINX HDMI encoder preview images

options:
  -h, --help            show this help message and exit
  --bootstrap-node BOOTSTRAP_NODE
                        A VINX encoder to use as bootstrap node for auto-
                        discovery
  --fallback-image FALLBACK_IMAGE
                        A JPEG image to use as fallback when the encoder
                        preview is unavailable
  -l, --listen-address LISTEN_ADDRESS
                        The address the HTTP server should listen on
  -p, --port PORT       The port the HTTP should listen on
```

## License

GNU GENERAL PUBLIC LICENSE version 3

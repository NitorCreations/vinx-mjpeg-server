import logging

from aiohttp import MultipartWriter, web
from aiohttp.web_exceptions import HTTPNotFound

from vinx_mjpeg_server.encoder import Encoder, PreviewImage

logger = logging.getLogger(__name__)


class HttpRequestHandler:
    def __init__(self, encoders: list[Encoder], fallback_image: bytes):
        self.encoders = encoders
        self.fallback_image = fallback_image

    async def handle(self, req: web.BaseRequest) -> web.Response | web.StreamResponse:
        if req.path == "/":
            return web.Response(text="vinx-mjpeg-server")
        elif req.path.startswith("/encoder/"):
            encoder_name = req.path[len("/encoder/") :]
            encoder = self.get_encoder_by_name(encoder_name)

            if encoder is None:
                raise HTTPNotFound()

            # Stream if told to
            if req.query.get("stream"):
                return await self.serve_mjpeg_stream(req, encoder.preview_image)

            # Serve fallback image if preview not available
            image_data = encoder.preview_image.data if encoder.preview_image.available else self.fallback_image
            return web.Response(status=200, content_type="image/jpeg", body=image_data)

        raise HTTPNotFound()

    def get_encoder_by_name(self, name: str) -> Encoder | None:
        return next((encoder for encoder in self.encoders if encoder.device_name == name), None)

    async def serve_mjpeg_stream(self, req: web.BaseRequest, preview_image: PreviewImage) -> web.StreamResponse:
        boundary = "frame"
        resp = web.StreamResponse(
            status=200, headers={"Content-Type": f"multipart/x-mixed-replace;boundary={boundary}"}
        )
        await resp.prepare(req)

        # Start writing "frames"
        while True:
            with MultipartWriter("image/jpeg", boundary=boundary) as writer:
                # Serve fallback image if preview not available
                image_data = preview_image.data if preview_image.available else self.fallback_image
                writer.append(image_data, {"Content-Type": "image/jpeg"})

                # Send a new boundary every time we capture a new image from the encoder, keep going until the client
                # closes the connection
                try:
                    await writer.write(resp, close_boundary=False)
                    await preview_image.update_event.wait()
                except ConnectionResetError:
                    break
                finally:
                    preview_image.update_event.clear()

        return resp

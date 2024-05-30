"""Middleware to log requests."""

from loguru import logger
import logging

from fastapi import Request
from fastapi.logger import logger as fastapi_logger
from starlette.middleware.base import BaseHTTPMiddleware

fastapi_logger.setLevel(logging.INFO)


class LoggingMiddleware(BaseHTTPMiddleware):
    """Middleware to log requests."""

    async def dispatch(self, request: Request, call_next):
        """
        Log requests.

        :param request: The request.
        :param call_next: The next call.
        :param logger: The logger.
        :return: The response.
        """
        # Log request method and URL
        logger.info(f"Request URL: {request.url} | Method: {request.method}")

        # Log request headers
        # logger.info(f"Headers: {dict(request.headers)}")

        # If you need the request body, handle with care:
        # body = await request.body()
        # logger.info(f"Body: {body.decode()}")
        #
        # Since the body is read and can't be read again,
        # you need to make it available for the actual route again
        # request._body = body

        response = await call_next(request)
        return response

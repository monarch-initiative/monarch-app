import contextvars
import logging
import re
import sys

from google.cloud.logging_v2.handlers import CloudLoggingFilter
from fastapi.logger import logger
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response, JSONResponse
from google.cloud.logging_v2.resource import Resource

cloud_trace_context = contextvars.ContextVar('cloud_trace_context', default='')
http_request_context = contextvars.ContextVar('http_request_context', default=dict({}))


class CloudLoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(
            self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        http_request = {
            'requestMethod': request.method,
            'requestUrl': request.url.path,
            'requestSize': sys.getsizeof(request),
            'remoteIp': request.client.host,
            'protocol': request.url.scheme,
        }

        if 'referrer' in request.headers:
            http_request['referrer'] = request.headers.get('referrer')

        if 'user-agent' in request.headers:
            http_request['userAgent'] = request.headers.get('user-agent')

        http_request_context.set(http_request)

        logger.debug(f'Request: {http_request}')
        try:
            return await call_next(request)
        except Exception as ex:
            logger.debug(f'Request failed: {ex}')
            return JSONResponse(
                status_code=500,
                content={
                    'success': False,
                    'message': ex
                }
            )


class CloudLogFilter(CloudLoggingFilter):

    def filter(self, record: logging.LogRecord) -> bool:

        record.http_request = http_request_context.get()

#        trace = cloud_trace_context.get()
#        split_header = trace.split('/', 1)

#        record.trace = f"projects/{self.project}/traces/{split_header[0]}"

 #       header_suffix = split_header[1]
#        record.span_id = re.findall(r'^\w+', header_suffix)[0]

        super().filter(record)

        return True
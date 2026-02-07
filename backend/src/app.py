"""
The Web-Application
"""

import os

from fastapi import FastAPI, Request
from fastapi.exceptions import HTTPException, RequestValidationError
from fastapi.middleware.cors import CORSMiddleware

from .routers import routers
from .utils import exception_response, JSONResponse, DEFAULT_ERROR_MESSAGES


class HelloWorldApp(FastAPI):
    def __init__(self, *args, **kwargs):
        super().__init__(
            title="Hello-World!",
            description="A Simple Coding Tutorial Platform",
            version="1.0.0",
            docs_url=None,
            redoc_url=None,
            on_startup=[self.on_start],
            exception_handlers={
                RequestValidationError: self.validation_exception_handler,
                HTTPException: self.http_exception_handler,
                Exception: self.any_exception_handler
            },
            *args, **kwargs
        )

        self.add_middleware(
            CORSMiddleware,
            allow_origins=os.environ.get(
                'ALLOWED_ORIGINS',
                'http://localhost,http://localhost:3000'
            ).split(","),
            allow_credentials=True,
            allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
            allow_headers=["Content-Type", "Authorization"],
        )
        
        for router in routers:
            self.include_router(router, prefix="/api")

    
    async def on_start(self) -> None:
        pass


    @staticmethod
    async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
        if request.app.debug:
            print(exc)

        return exception_response(
            status_code=422,
            message="Invalid Request"
        )


    @staticmethod
    async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
        if exc.detail.upper() == DEFAULT_ERROR_MESSAGES[exc.status_code]['short'].upper():
            message = DEFAULT_ERROR_MESSAGES[exc.status_code]['long']
        else:
            message = exc.detail

        return exception_response(
            status_code=exc.status_code,
            message=message
        )


    @staticmethod
    async def any_exception_handler(request: Request, exc: Exception) -> JSONResponse:
        return exception_response(
            status_code=500,
        )

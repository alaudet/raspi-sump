"""Thin async client for the raspi-sump JSON API."""

from __future__ import annotations

import asyncio
from typing import Any

import aiohttp

from .const import SUPPORTED_API_VERSION

REQUEST_TIMEOUT = 10


class RaspiSumpError(Exception):
    """The raspi-sump web service could not be reached or understood."""


class UnsupportedApiVersion(RaspiSumpError):
    """The appliance speaks an /api/status version this integration cannot read."""


class RaspiSumpClient:
    """Fetches status and readings from a raspi-sump web instance."""

    def __init__(self, session: aiohttp.ClientSession, base_url: str) -> None:
        """Initialise the client.

        The session is expected to come from async_get_clientsession(), which
        already carries the entry's verify_ssl preference.
        """
        self._session = session
        self._base_url = base_url.rstrip("/")

    @property
    def base_url(self) -> str:
        """Return the root URL of the raspi-sump web UI."""
        return self._base_url

    async def async_get_status(self) -> dict[str, Any]:
        """Return the current state summary from /api/status."""
        data = await self._async_get("/api/status")
        version = data.get("api_version")
        if version != SUPPORTED_API_VERSION:
            raise UnsupportedApiVersion(
                f"{self._base_url} reports API version {version!r}, "
                f"expected {SUPPORTED_API_VERSION}"
            )
        return data

    async def async_get_readings(
        self,
        date: str | None = None,
        start: str | None = None,
        end: str | None = None,
    ) -> dict[str, Any]:
        """Return a readings series in the shape the uPlot chart consumes.

        Pass either *date* (a single day) or both *start* and *end* (a range).
        """
        if start and end:
            return await self._async_get(
                "/api/readings/range", {"start": start, "end": end}
            )
        return await self._async_get(
            "/api/readings", {"date": date} if date else None
        )

    async def _async_get(
        self, path: str, params: dict[str, str] | None = None
    ) -> dict[str, Any]:
        url = f"{self._base_url}{path}"
        try:
            async with asyncio.timeout(REQUEST_TIMEOUT):
                response = await self._session.get(url, params=params)
                response.raise_for_status()
                # raspi-sump serves application/json, but a reverse proxy in
                # front of it may not, so don't insist on the content type.
                return await response.json(content_type=None)
        except TimeoutError as err:
            raise RaspiSumpError(f"Timeout connecting to {url}") from err
        except aiohttp.ClientError as err:
            raise RaspiSumpError(f"Error connecting to {url}: {err}") from err
        except ValueError as err:
            raise RaspiSumpError(f"Invalid JSON from {url}: {err}") from err

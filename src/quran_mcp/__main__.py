"""Run the Quran MCP server with ``python -m quran_mcp``."""

from quran_mcp.lib.config.settings import get_settings
from quran_mcp.server import get_or_create_mcp


if __name__ == "__main__":
    settings = get_settings()
    get_or_create_mcp().run(
        transport="http",
        host="0.0.0.0",
        path="/",
        port=settings.server.port,
    )

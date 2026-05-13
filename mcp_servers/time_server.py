from mcp.server.fastmcp import FastMCP

mcp = FastMCP("Time MCP Server")


# ── Tool 1: Current Date & Time ───────────────────────────────────────────────
@mcp.tool()
def current_datetime(timezone: str = "UTC") -> str:
    """
    Return the current date and time for a given timezone.
    Optionally pass a timezone name (e.g. 'Asia/Kolkata', 'US/Eastern', 'Europe/London').
    Defaults to UTC.
    Example: timezone='Asia/Kolkata'
    """
    from datetime import datetime, timezone as tz
    import zoneinfo

    try:
        zone = zoneinfo.ZoneInfo(timezone)
        now = datetime.now(zone)
    except Exception:
        now = datetime.now(tz.utc)
        timezone = "UTC (fallback — unknown timezone supplied)"

    return f"Current datetime in {timezone}: {now.strftime('%Y-%m-%d %H:%M:%S %Z')}"


# ── Tool 2: Time in Multiple Timezones ────────────────────────────────────────
@mcp.tool()
def world_clock(timezones: list[str] = None) -> dict:
    """
    Return the current time in multiple timezones at once.
    Pass a list of timezone names.
    Defaults to a set of popular timezones.
    Example: timezones=['Asia/Kolkata', 'US/Eastern', 'Europe/London']
    """
    from datetime import datetime
    import zoneinfo

    if not timezones:
        timezones = [
            "UTC",
            "Asia/Kolkata",
            "US/Eastern",
            "US/Pacific",
            "Europe/London",
            "Asia/Tokyo",
        ]

    result = {}
    for zone_name in timezones:
        try:
            zone = zoneinfo.ZoneInfo(zone_name)
            now = datetime.now(zone)
            result[zone_name] = now.strftime("%Y-%m-%d %H:%M:%S %Z")
        except Exception:
            result[zone_name] = "Unknown timezone"

    return result


# ── Tool 3: Time Difference Between Two Timezones ─────────────────────────────
@mcp.tool()
def time_difference(timezone1: str, timezone2: str) -> str:
    """
    Return the hour difference between two timezones.
    Example: timezone1='Asia/Kolkata', timezone2='US/Eastern'
    """
    from datetime import datetime
    import zoneinfo

    try:
        zone1 = zoneinfo.ZoneInfo(timezone1)
        zone2 = zoneinfo.ZoneInfo(timezone2)
        offset1 = datetime.now(zone1).utcoffset()
        offset2 = datetime.now(zone2).utcoffset()
        diff = (offset1 - offset2).total_seconds() / 3600
        direction = "ahead of" if diff > 0 else "behind"
        return (
            f"{timezone1} is {abs(diff):.1f} hour(s) {direction} {timezone2}"
        )
    except Exception as e:
        return f"Error computing time difference: {e}"


# ── Tool 4: Unix Timestamp ────────────────────────────────────────────────────
@mcp.tool()
def unix_timestamp() -> dict:
    """Return the current Unix timestamp (seconds since epoch)."""
    from datetime import datetime, timezone as tz
    import time as _time

    ts = int(_time.time())
    return {
        "unix_timestamp": ts,
        "utc_datetime": datetime.now(tz.utc).strftime("%Y-%m-%d %H:%M:%S UTC"),
    }


# ── Resource: Server info ─────────────────────────────────────────────────────
@mcp.resource("info://server")
def server_info() -> str:
    """Static resource describing this MCP server."""
    return (
        "Time MCP Server\n"
        "Tools: current_datetime, world_clock, time_difference, unix_timestamp\n"
        "Transport: stdio"
    )


# ── Entry point ───────────────────────────────────────────────────────────────
if __name__ == "__main__":
    mcp.run(transport="stdio")



"""Verify both Bale transport connectivity and remote account authorization.

A local session file and an open WebSocket are not proof that Bale still accepts
that session.  The final check therefore performs a small read-only account RPC
(list up to one dialog) before the UI unlocks the workspace.
"""
from __future__ import annotations

import asyncio
from typing import Any, Dict


# balelink's own transport startup waits up to ~20 seconds.
START_TIMEOUT_SECONDS = 30
CONNECTED_SETTLE_SECONDS = 5
AUTH_PROBE_TIMEOUT_SECONDS = 12
STOP_TIMEOUT_SECONDS = 8


def _account_name(client: Any) -> str:
    me = getattr(client, "me", None)
    if me is None:
        return ""
    return str(getattr(me, "name", None) or getattr(me, "id", "") or "")


async def verify_saved_session(client: Any) -> Dict[str, Any]:
    """Verify that a saved session is accepted by Bale, not merely present.

    ``BaleClient.is_logged_in`` only reports a locally saved login, while
    ``is_connected`` reports the transport state.  Neither alone confirms that
    the remote account session is still authorized.  ``dialogs(limit=1)`` is a
    read-only authenticated RPC; an empty result is still a successful probe.

    The client is always stopped, including after timeout or a failed probe.
    """
    logged_in = bool(getattr(client, "is_logged_in", False))
    if not logged_in:
        return {
            "logged": False,
            "transport_connected": False,
            "authenticated": False,
            "account": "",
            "probe_error": "no_local_session",
        }

    transport_connected = False
    try:
        await asyncio.wait_for(client.start(), timeout=START_TIMEOUT_SECONDS)

        transport_connected = bool(getattr(client, "is_connected", False))
        if not transport_connected:
            waiter = getattr(client, "wait_until_connected", None)
            if callable(waiter):
                transport_connected = bool(
                    await asyncio.wait_for(
                        waiter(CONNECTED_SETTLE_SECONDS),
                        timeout=CONNECTED_SETTLE_SECONDS + 1,
                    )
                )

        if not transport_connected:
            return {
                "logged": True,
                "transport_connected": False,
                "authenticated": False,
                "account": _account_name(client),
                "probe_error": "transport_unavailable",
            }

        # Do not trust a locally cached Me object or an open WebSocket. Ask
        # Bale to return one dialog, which requires an authenticated API call.
        try:
            await asyncio.wait_for(
                client.dialogs(limit=1), timeout=AUTH_PROBE_TIMEOUT_SECONDS
            )
        except asyncio.TimeoutError:
            return {
                "logged": True,
                "transport_connected": bool(getattr(client, "is_connected", False)),
                "authenticated": False,
                "account": _account_name(client),
                "probe_error": "auth_probe_timeout",
            }
        except Exception as exc:
            # Keep raw exception text out of the UI/logs; some transports may
            # include implementation details. The exception class is enough
            # for diagnostics without exposing session material.
            return {
                "logged": True,
                "transport_connected": bool(getattr(client, "is_connected", False)),
                "authenticated": False,
                "account": _account_name(client),
                "probe_error": type(exc).__name__,
            }

        # The RPC may have succeeded just as the transport was lost. Require
        # the transport to remain up at the end of the probe as well.
        transport_connected = bool(getattr(client, "is_connected", False))
        if not transport_connected:
            return {
                "logged": True,
                "transport_connected": False,
                "authenticated": False,
                "account": _account_name(client),
                "probe_error": "connection_lost_after_probe",
            }

        return {
            "logged": True,
            "transport_connected": True,
            "authenticated": True,
            "account": _account_name(client),
            "probe_error": "",
        }
    finally:
        try:
            await asyncio.wait_for(client.stop(), timeout=STOP_TIMEOUT_SECONDS)
        except Exception:
            # Preserve the verification result/error; always make a best effort
            # to release the temporary connection.
            pass

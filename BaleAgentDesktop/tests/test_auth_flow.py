import asyncio
import unittest
from unittest.mock import patch

from ui import auth_flow


class FakeClient:
    def __init__(
        self,
        *,
        logged=True,
        start_delay=0.0,
        fail=None,
        connected=True,
        auth_error=None,
        dialogs_result=None,
    ):
        self.is_logged_in = logged
        self.is_connected = False
        self.start_delay = start_delay
        self.fail = fail
        self.connected_after_start = connected
        self.auth_error = auth_error
        self.dialogs_result = dialogs_result if dialogs_result is not None else []
        self.dialogs_called = 0
        self.stop_called = False
        self.me = type("Me", (), {"id": 12345, "name": "Test Account"})()

    async def start(self):
        await asyncio.sleep(self.start_delay)
        if self.fail:
            raise RuntimeError(self.fail)
        self.is_connected = self.connected_after_start

    async def wait_until_connected(self, timeout):
        await asyncio.sleep(0)
        return self.is_connected

    async def dialogs(self, limit=40):
        self.dialogs_called += 1
        if self.auth_error:
            raise self.auth_error
        return self.dialogs_result[:limit]

    async def stop(self):
        self.stop_called = True
        self.is_connected = False


class AuthFlowTests(unittest.IsolatedAsyncioTestCase):
    async def test_saved_session_requires_remote_auth_probe(self):
        client = FakeClient(start_delay=0.02, dialogs_result=[])
        result = await auth_flow.verify_saved_session(client)
        self.assertTrue(result["logged"])
        self.assertTrue(result["transport_connected"])
        self.assertTrue(result["authenticated"])
        self.assertEqual(client.dialogs_called, 1)
        self.assertEqual(result["account"], "Test Account")
        self.assertTrue(client.stop_called)

    async def test_socket_connected_but_revoked_session_is_not_authenticated(self):
        client = FakeClient(auth_error=RuntimeError("unauthorized"))
        result = await auth_flow.verify_saved_session(client)
        self.assertTrue(result["logged"])
        self.assertTrue(result["transport_connected"])
        self.assertFalse(result["authenticated"])
        self.assertEqual(result["probe_error"], "RuntimeError")
        self.assertTrue(client.stop_called)

    async def test_not_logged_in_does_not_attempt_network_or_probe(self):
        client = FakeClient(logged=False)
        result = await auth_flow.verify_saved_session(client)
        self.assertFalse(result["logged"])
        self.assertFalse(result["authenticated"])
        self.assertEqual(client.dialogs_called, 0)
        self.assertFalse(client.stop_called)

    async def test_cleanup_runs_when_start_raises(self):
        client = FakeClient(fail="connection refused")
        with self.assertRaisesRegex(RuntimeError, "connection refused"):
            await auth_flow.verify_saved_session(client)
        self.assertTrue(client.stop_called)

    async def test_outer_timeout_allows_longer_than_transport_start_deadline(self):
        self.assertGreater(auth_flow.START_TIMEOUT_SECONDS, 20)

    async def test_cleanup_runs_when_start_times_out(self):
        client = FakeClient(start_delay=0.2)
        with patch.object(auth_flow, "START_TIMEOUT_SECONDS", 0.01):
            with self.assertRaises(asyncio.TimeoutError):
                await auth_flow.verify_saved_session(client)
        self.assertTrue(client.stop_called)

    async def test_no_transport_means_no_auth_probe(self):
        client = FakeClient(connected=False)
        result = await auth_flow.verify_saved_session(client)
        self.assertTrue(result["logged"])
        self.assertFalse(result["transport_connected"])
        self.assertFalse(result["authenticated"])
        self.assertEqual(client.dialogs_called, 0)
        self.assertTrue(client.stop_called)


if __name__ == "__main__":
    unittest.main()

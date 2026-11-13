import asyncio
import tempfile
import unittest
from pathlib import Path

from bale_agent import BaleAgent


class FakeClient:
    def __init__(self, *, probe_error=None):
        self.is_logged_in = True
        self.is_connected = False
        self.probe_error = probe_error
        self.stopped = False

    async def start(self):
        self.is_connected = True

    async def wait_until_connected(self, timeout):
        return self.is_connected

    async def dialogs(self, limit=40):
        if self.probe_error:
            raise self.probe_error
        return []

    async def stop(self):
        self.stopped = True
        self.is_connected = False


class CoreAuthGuardTests(unittest.IsolatedAsyncioTestCase):
    async def test_core_rejects_locally_saved_but_revoked_session(self):
        with tempfile.TemporaryDirectory() as home:
            agent = BaleAgent("test", Path(home))
            client = FakeClient(probe_error=RuntimeError("unauthorized"))
            agent._client = lambda: client
            with self.assertRaisesRegex(RuntimeError, "did not confirm account access"):
                await agent._connected_client()
            self.assertTrue(client.stopped)

    async def test_core_accepts_successful_read_only_probe(self):
        with tempfile.TemporaryDirectory() as home:
            agent = BaleAgent("test", Path(home))
            client = FakeClient()
            agent._client = lambda: client
            result = await agent._connected_client()
            self.assertIs(result, client)
            self.assertFalse(client.stopped)


if __name__ == "__main__":
    unittest.main()

"""MQS channel implementation for message queue communication."""

import asyncio
import base64
import json
from datetime import datetime
from typing import Any

import httpx
from loguru import logger

from nanobot.bus.events import OutboundMessage
from nanobot.bus.queue import MessageBus
from nanobot.channels.base import BaseChannel
from nanobot.config.schema import MqsConfig


class MqsChannel(BaseChannel):
    """
    MQS (Message Queue Service) channel.

    Inbound:
    - Poll MQS consume endpoint for messages.
    - Decode and validate message format.
    - Forward to nanobot message bus.

    Outbound:
    - Send responses via MQS produce endpoint.
    """

    name = "mqs"

    REQUIRED_INBOUND_FIELDS = [
        "businessType",
        "messageType",
        "businessBody",
        "source",
        "appid",
        "requestId",
        "requestTime",
        "sessionId",
    ]

    REQUIRED_OUTBOUND_FIELDS = [
        "businessType",
        "messageType",
        "businessBody",
        "source",
        "appid",
        "requestId",
        "responseTime",
        "sessionId",
    ]

    def __init__(self, config: MqsConfig, bus: MessageBus):
        super().__init__(config, bus)
        self.config: MqsConfig = config
        self._http_client: httpx.AsyncClient | None = None
        self._consume_task: asyncio.Task | None = None

    async def start(self) -> None:
        """Start polling MQS for inbound messages."""
        if not self._validate_config():
            return

        self._running = True
        self._http_client = httpx.AsyncClient(timeout=30.0)
        logger.info("Starting MQS channel...")

        self._consume_task = asyncio.create_task(self._consume_messages())

    async def stop(self) -> None:
        """Stop polling loop and cleanup resources."""
        self._running = False

        if self._consume_task:
            self._consume_task.cancel()
            try:
                await self._consume_task
            except asyncio.CancelledError:
                pass
            self._consume_task = None

        if self._http_client:
            await self._http_client.aclose()
            self._http_client = None

        logger.info("MQS channel stopped")

    async def send(self, msg: OutboundMessage) -> None:
        """Send message to MQS produce endpoint."""
        if not self._http_client:
            logger.warning("MQS channel not started, cannot send message")
            return

        try:
            message_body = self._prepare_outbound_message(msg)
            await self._produce(message_body)
            logger.info("Message sent to MQS successfully")
        except Exception as e:
            logger.error("Error sending message to MQS: {}", e)
            raise

    async def _consume_messages(self) -> None:
        """Main loop for consuming messages from MQS."""
        poll_interval = max(1, int(self.config.poll_interval_seconds))

        while self._running:
            try:
                messages = await self._consume()
                if messages:
                    for message in messages:
                        await self._process_message(message)
            except Exception as e:
                logger.error("Error in consume loop: {}", e)

            await asyncio.sleep(poll_interval)

    async def _consume(self) -> list[dict[str, Any]]:
        """Call MQS consume endpoint to get messages."""
        if not self._http_client:
            return []

        url = f"{self.config.base_url}/api/mqs/consume"
        headers = self._build_headers(topic=self.config.consumer_topic)

        try:
            response = await self._http_client.get(url, headers=headers)
            response.raise_for_status()
            data = response.json()

            if isinstance(data, list):
                return data
            return []
        except httpx.HTTPStatusError as e:
            logger.error("HTTP error consuming messages: {}", e)
            return []
        except Exception as e:
            logger.error("Error consuming messages: {}", e)
            return []

    async def _process_message(self, message: dict[str, Any]) -> None:
        """Process a single message from MQS."""
        receipt_handle = message.get("receiptHandle")
        body = message.get("body")

        if not self._validate_message_format(message):
            logger.error("Invalid message format: {}", message)
            if receipt_handle:
                await self._ack_message(receipt_handle)
            return

        try:
            decoded_message = self._decode_and_parse_message(body)
            if not decoded_message:
                logger.error("Failed to decode message body")
                await self._ack_message(receipt_handle)
                return

            if not self._validate_required_fields(decoded_message, self.REQUIRED_INBOUND_FIELDS):
                logger.error("Missing required fields in message: {}", decoded_message)
                await self._ack_message(receipt_handle)
                return

            await self._handle_message(
                sender_id=decoded_message.get("appid", ""),
                chat_id=decoded_message.get("sessionId", ""),
                content=decoded_message.get("businessBody", ""),
                metadata={
                    "businessType": decoded_message.get("businessType"),
                    "messageType": decoded_message.get("messageType"),
                    "source": decoded_message.get("source"),
                    "requestId": decoded_message.get("requestId"),
                    "requestTime": decoded_message.get("requestTime"),
                },
            )

        except Exception as e:
            logger.error("Error processing message: {}", e)
        finally:
            if receipt_handle:
                await self._ack_message(receipt_handle)

    async def _ack_message(self, receipt_handle: str) -> None:
        """Acknowledge a message to MQS."""
        if not self._http_client:
            return

        url = f"{self.config.base_url}/api/mqs/ack"
        headers = self._build_headers(topic=self.config.consumer_topic, receipt_handle=receipt_handle)

        try:
            response = await self._http_client.delete(url, headers=headers)
            response.raise_for_status()
            logger.debug("Message acknowledged successfully")
        except httpx.HTTPStatusError as e:
            logger.error("HTTP error acknowledging message: {}", e)
        except Exception as e:
            logger.error("Error acknowledging message: {}", e)

    async def _produce(self, message_body: dict[str, Any]) -> None:
        """Produce a message to MQS."""
        if not self._http_client:
            return

        url = f"{self.config.base_url}/api/mqs/produce"
        headers = self._build_headers(topic=self.config.product_topic)

        body_json = json.dumps(message_body, ensure_ascii=False)
        body_base64 = base64.b64encode(body_json.encode("utf-8")).decode("utf-8")

        try:
            response = await self._http_client.post(url, headers=headers, content=body_base64)
            response.raise_for_status()
            logger.debug("Message produced successfully")
        except httpx.HTTPStatusError as e:
            logger.error("HTTP error producing message: {}", e)
            raise
        except Exception as e:
            logger.error("Error producing message: {}", e)
            raise

    def _build_headers(self, topic: str, receipt_handle: str | None = None) -> dict[str, str]:
        """Build HTTP headers for MQS API calls."""
        headers = {
            "X-HW-ID": self.config.appid,
            "X-HW-APPKEY": self.config.appkey,
            "MsgTopic": topic,
            "MsgGroupId": self.config.msg_group_id,
        }

        if receipt_handle:
            headers["receiptHandle"] = receipt_handle

        return headers

    def _validate_message_format(self, message: dict[str, Any]) -> bool:
        """Validate message format contains required fields."""
        return "body" in message and "receiptHandle" in message

    def _decode_and_parse_message(self, body: str) -> dict[str, Any] | None:
        """Decode Base64 body and parse JSON."""
        try:
            decoded_bytes = base64.b64decode(body)
            decoded_str = decoded_bytes.decode("utf-8")
            return json.loads(decoded_str)
        except Exception as e:
            logger.error("Error decoding and parsing message: {}", e)
            return None

    def _validate_required_fields(self, message: dict[str, Any], required_fields: list[str]) -> bool:
        """Validate that all required fields are present in the message."""
        missing_fields = [field for field in required_fields if field not in message or not message[field]]
        if missing_fields:
            logger.error("Missing required fields: {}", ", ".join(missing_fields))
            return False
        return True

    def _prepare_outbound_message(self, msg: OutboundMessage) -> dict[str, Any]:
        """Prepare outbound message for MQS produce endpoint."""
        metadata = msg.metadata or {}

        message_body = {
            "businessType": metadata.get("businessType", ""),
            "messageType": metadata.get("messageType", "JSON"),
            "businessBody": msg.content or "",
            "source": metadata.get("source", self.config.appid),
            "appid": self.config.appid,
            "requestId": metadata.get("requestId", ""),
            "responseTime": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "sessionId": msg.chat_id,
        }

        if not self._validate_required_fields(message_body, self.REQUIRED_OUTBOUND_FIELDS):
            logger.warning("Outbound message missing required fields: {}", message_body)

        return message_body

    def _validate_config(self) -> bool:
        """Validate MQS channel configuration."""
        missing = []
        if not self.config.base_url:
            missing.append("base_url")
        if not self.config.consumer_topic:
            missing.append("consumer_topic")
        if not self.config.product_topic:
            missing.append("product_topic")
        if not self.config.appid:
            missing.append("appid")
        if not self.config.appkey:
            missing.append("appkey")
        if not self.config.msg_group_id:
            missing.append("msg_group_id")

        if missing:
            logger.error("MQS channel not configured, missing: {}", ", ".join(missing))
            return False
        return True

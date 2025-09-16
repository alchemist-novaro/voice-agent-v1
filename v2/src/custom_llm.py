from __future__ import annotations

import asyncio
import openai
from livekit.agents import APITimeoutError, llm
from livekit.agents.llm import ToolChoice, utils as llm_utils
from livekit.agents.llm.chat_context import ChatContext
from livekit.agents.llm.tool_context import FunctionTool, RawFunctionTool
from livekit.agents.types import (
    DEFAULT_API_CONNECT_OPTIONS,
    NOT_GIVEN,
    APIConnectOptions,
    NotGivenOr,
)
from openai.types.chat.chat_completion_chunk import Choice
from typing import Callable

from .workflow import Workflow

class CustomLLM(llm.LLM):
    def __init__(self, customer_id: str, config_path: str, disconnect: Callable) -> None:
        super().__init__()
        self.workflow = Workflow()

    def chat(
        self,
        *,
        chat_ctx: ChatContext,
        tools: list[FunctionTool | RawFunctionTool] | None = None,
        conn_options: APIConnectOptions = DEFAULT_API_CONNECT_OPTIONS,
        parallel_tool_calls: NotGivenOr[bool] = NOT_GIVEN,
        tool_choice: NotGivenOr[ToolChoice] = NOT_GIVEN,
        extra_kwargs: NotGivenOr[dict[str,]] = NOT_GIVEN,
    ) -> LLMStream:
        return LLMStream(
            self,
            chat_ctx=chat_ctx,
            tools=tools,
            conn_options=conn_options,
            workflow=self.workflow
        )

class LLMStream(llm.LLMStream):
    def __init__(
        self,
        llm: llm.LLM,
        *,
        chat_ctx: ChatContext,
        tools: list[FunctionTool | RawFunctionTool],
        conn_options: APIConnectOptions,
        workflow: Workflow
    ) -> None:
        super().__init__(llm, chat_ctx=chat_ctx, tools=tools, conn_options=conn_options)
        self._workflow = workflow

    async def _run(self) -> None:
        try:
            chat_ctx = self._chat_ctx.to_provider_format("openai")
            self._tool_call_id: str | None = None
            self._fnc_name: str | None = None
            self._fnc_raw_arguments: str | None = None
            self._tool_index: int | None = None
            retryable = True

            stream = self._workflow.process(
                message=chat_ctx[0][-1]["content"]
            )

            thinking = asyncio.Event()
            async for chunk in stream:
                for choice in chunk.choices:
                    chat_chunk = self._parse_choice(chunk.id, choice, thinking)
                    if chat_chunk is not None:
                        retryable = False
                        self._event_ch.send_nowait(chat_chunk)

                if chunk.usage is not None:
                    retryable = False
                    tokens_details = chunk.usage.prompt_tokens_details
                    cached_tokens = tokens_details.cached_tokens if tokens_details else 0
                    chunk = llm.ChatChunk(
                        id=chunk.id,
                        usage=llm.CompletionUsage(
                            completion_tokens=chunk.usage.completion_tokens,
                            prompt_tokens=chunk.usage.prompt_tokens,
                            prompt_cached_tokens=cached_tokens or 0,
                            total_tokens=chunk.usage.total_tokens,
                        ),
                    )
                    self._event_ch.send_nowait(chunk)
        
        except openai.APITimeoutError:
            raise APITimeoutError(retryable=retryable) from None
                    
    def _parse_choice(
        self, id: str, choice: Choice, thinking: asyncio.Event
    ) -> llm.ChatChunk | None:
        delta = choice.delta

        if delta is None:
            return None

        if delta.tool_calls:
            for tool in delta.tool_calls:
                if not tool.function:
                    continue

                call_chunk = None
                if self._tool_call_id and tool.id and tool.index != self._tool_index:
                    call_chunk = llm.ChatChunk(
                        id=id,
                        delta=llm.ChoiceDelta(
                            role="assistant",
                            content=delta.content,
                            tool_calls=[
                                llm.FunctionToolCall(
                                    arguments=self._fnc_raw_arguments or "",
                                    name=self._fnc_name or "",
                                    call_id=self._tool_call_id or "",
                                )
                            ],
                        ),
                    )
                    self._tool_call_id = self._fnc_name = self._fnc_raw_arguments = None

                if tool.function.name:
                    self._tool_index = tool.index
                    self._tool_call_id = tool.id
                    self._fnc_name = tool.function.name
                    self._fnc_raw_arguments = tool.function.arguments or ""
                elif tool.function.arguments:
                    self._fnc_raw_arguments += tool.function.arguments  # type: ignore

                if call_chunk is not None:
                    return call_chunk

        if choice.finish_reason in ("tool_calls", "stop") and self._tool_call_id:
            call_chunk = llm.ChatChunk(
                id=id,
                delta=llm.ChoiceDelta(
                    role="assistant",
                    content=delta.content,
                    tool_calls=[
                        llm.FunctionToolCall(
                            arguments=self._fnc_raw_arguments or "",
                            name=self._fnc_name or "",
                            call_id=self._tool_call_id or "",
                        )
                    ],
                ),
            )
            self._tool_call_id = self._fnc_name = self._fnc_raw_arguments = None
            return call_chunk

        delta.content = llm_utils.strip_thinking_tokens(delta.content, thinking)

        if not delta.content:
            return None

        return llm.ChatChunk(
            id=id,
            delta=llm.ChoiceDelta(content=delta.content, role="assistant"),
        )
"""统一的重试工具，封装 tenacity 配置，确保外部服务调用稳定。"""

from __future__ import annotations

from typing import Any, Callable

import logging
from tenacity import RetryCallState, Retrying, retry_if_exception_type, stop_after_attempt, wait_exponential


logger = logging.getLogger(__name__)

DEFAULT_MAX_ATTEMPTS = 3
DEFAULT_WAIT_EXP_BASE = 1
DEFAULT_WAIT_EXP_MULTIPLIER = 1


def _log_retry(retry_state: RetryCallState) -> None:
    """tenacity 重试回调，记录错误信息。"""
    last_exc = retry_state.outcome.exception() if retry_state.outcome else None
    if last_exc:
        attempt = retry_state.attempt_number
        logger.warning("重试第 %s 次失败：%s", attempt, last_exc)


def run_with_retry(
    func: Callable[..., Any],
    *args: Any,
    exceptions: tuple[type[BaseException], ...] = (Exception,),
    max_attempts: int = DEFAULT_MAX_ATTEMPTS,
    wait_multiplier: int = DEFAULT_WAIT_EXP_MULTIPLIER,
    wait_exp_base: int = DEFAULT_WAIT_EXP_BASE,
    **kwargs: Any,
) -> Any:
    """执行带重试的函数调用。

    Args:
        func: 目标函数。
        exceptions: 触发重试的异常类型。
        max_attempts: 最大重试次数。
        wait_multiplier: 指数退避基础倍率。
        wait_exp_base: 指数退避底数。

    Returns:
        函数执行结果。
    """

    retrying = Retrying(
        retry=retry_if_exception_type(exceptions),
        stop=stop_after_attempt(max_attempts),
        wait=wait_exponential(multiplier=wait_multiplier, min=wait_exp_base, exp_base=2),
        after=_log_retry,
        reraise=True,
    )

    for attempt in retrying:
        with attempt:
            return func(*args, **kwargs)

    # 理论上不会执行到此处，添加返回以满足类型检查
    raise RuntimeError("重试执行未获得结果")

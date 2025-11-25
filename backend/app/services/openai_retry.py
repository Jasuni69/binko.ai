"""
OpenAI retry logic with exponential backoff.
Import and use instead of direct OpenAI calls in generation.py
"""
import json
import asyncio
from openai import AsyncOpenAI, APIError, RateLimitError, APIConnectionError
from fastapi import HTTPException, status
from app.logging_config import get_logger

logger = get_logger(__name__)


async def call_openai_with_retry(
    client: AsyncOpenAI,
    system_prompt: str,
    user_prompt: str,
    max_retries: int = 3
) -> dict:
    """
    Call OpenAI with exponential backoff retry.

    Retries on connection errors and API errors.
    Fails fast on rate limits.
    Returns parsed JSON dict or raises HTTPException.
    """
    for attempt in range(max_retries):
        try:
            logger.info(f"OpenAI call attempt {attempt + 1}/{max_retries}")

            response = await client.chat.completions.create(
                model="gpt-4-turbo-preview",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                response_format={"type": "json_object"},
                temperature=0.8,
                max_tokens=2000,
            )

            result = json.loads(response.choices[0].message.content)
            logger.info("OpenAI call successful")
            return result

        except (APIConnectionError, APIError) as e:
            if attempt < max_retries - 1:
                wait_time = 2 ** attempt  # 1s, 2s, 4s
                logger.warning(f"OpenAI error, retrying in {wait_time}s: {str(e)}")
                await asyncio.sleep(wait_time)
            else:
                logger.error(f"OpenAI call failed after {max_retries} attempts")
                raise HTTPException(
                    status_code=status.HTTP_502_BAD_GATEWAY,
                    detail="AI service error. Try again later."
                )

        except RateLimitError as e:
            logger.error("OpenAI rate limit hit")
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="AI service rate limit reached. Try again in a moment."
            )

        except json.JSONDecodeError as e:
            if attempt < max_retries - 1:
                logger.warning(f"JSON parse error, retrying: {str(e)}")
                await asyncio.sleep(1)
            else:
                logger.error("Failed to parse JSON after retries")
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Failed to parse AI response"
                )

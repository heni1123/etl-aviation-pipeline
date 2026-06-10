import logging
import time
from typing import Callable, Any

class ErrorHandler:
    def __init__(self) -> None:
        logging.basicConfig(level=logging.ERROR, format='%(asctime)s - %(levelname)s - %(message)s')
        self.logger = logging.getLogger(__name__)

    def handle_error(self, error: Exception) -> None:
        self.logger.error(f"An error occurred: {str(error)}")

    async def retry(self, func: Callable[..., Any], retries: int = 3, delay: int = 5, *args: Any, **kwargs: Any) -> Any:
        for attempt in range(retries):
            try:
                return await func(*args, **kwargs)
            except Exception as e:
                self.handle_error(e)
                if attempt < retries - 1:
                    time.sleep(delay)
                else:
                    raise e from None
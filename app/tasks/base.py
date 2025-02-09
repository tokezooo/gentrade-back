from celery import Task
import time
from typing import Any

from app.util.logger import setup_logger, set_correlation_id

logger = setup_logger("tasks.base")


class LoggedTask(Task):
    """Base task class that includes logging functionality."""

    def apply_async(self, *args: Any, **kwargs: Any) -> Any:
        """Override to ensure correlation ID is passed to the task."""
        # Get the correlation ID from the current context, if any
        correlation_id = kwargs.pop("correlation_id", None)
        if correlation_id:
            # Store correlation ID in task headers
            headers = kwargs.get("headers", {})
            headers["correlation_id"] = correlation_id
            kwargs["headers"] = headers

        return super().apply_async(*args, **kwargs)

    def __call__(self, *args: Any, **kwargs: Any) -> Any:
        """Override to add logging around task execution."""
        # Get correlation ID from task headers
        headers = self.request.headers or {}
        correlation_id = headers.get("correlation_id")
        if correlation_id:
            set_correlation_id(correlation_id)

        # Start timing
        start_time = time.time()

        # Log task start
        logger.info(
            f"Starting task {self.name}",
            extra={
                "data": {
                    "task_id": self.request.id,
                    "task_name": self.name,
                    "args": args,
                    "kwargs": kwargs,
                }
            },
        )

        try:
            # Execute the task
            result = super().__call__(*args, **kwargs)

            # Calculate duration
            duration = time.time() - start_time

            # Log successful completion
            logger.info(
                f"Task {self.name} completed successfully",
                extra={
                    "data": {
                        "task_id": self.request.id,
                        "task_name": self.name,
                        "duration": f"{duration:.3f}s",
                    }
                },
            )

            return result

        except Exception as e:
            # Calculate duration
            duration = time.time() - start_time

            # Log the error
            logger.error(
                f"Task {self.name} failed",
                extra={
                    "data": {
                        "task_id": self.request.id,
                        "task_name": self.name,
                        "error": str(e),
                        "duration": f"{duration:.3f}s",
                    }
                },
            )
            raise  # Re-raise the exception

    def on_retry(
        self, exc: Exception, task_id: str, args: Any, kwargs: Any, einfo: Any
    ) -> None:
        """Called when the task is to be retried."""
        logger.warning(
            f"Retrying task {self.name}",
            extra={
                "data": {
                    "task_id": task_id,
                    "task_name": self.name,
                    "error": str(exc),
                    "args": args,
                    "kwargs": kwargs,
                }
            },
        )

    def on_failure(
        self, exc: Exception, task_id: str, args: Any, kwargs: Any, einfo: Any
    ) -> None:
        """Called when the task fails."""
        logger.error(
            f"Task {self.name} failed permanently",
            extra={
                "data": {
                    "task_id": task_id,
                    "task_name": self.name,
                    "error": str(exc),
                    "args": args,
                    "kwargs": kwargs,
                }
            },
        )


# Example usage:
# @app.task(base=LoggedTask)
# def my_task():
#     pass

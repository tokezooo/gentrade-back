from fastapi import APIRouter, Request, Response, status
from svix.webhooks import Webhook, WebhookVerificationError
from pydantic import ValidationError
from sqlalchemy.exc import IntegrityError

from app.config import Settings
from app.db.services.service_users import UsersService
from app.dependencies import UOWDep
from app.schemas.schema_clerk_webhook_event import ClerkWebhookEvent
from app.schemas.schema_users import UserSchemaAdd
from app.util.ft.ft_userdir import FTUserDir
import logging

settings = Settings()

router = APIRouter(
    prefix="/webhooks",
    tags=["webhooks"],
)


@router.post("/clerk", status_code=status.HTTP_204_NO_CONTENT)
async def clerk_webhook_handler(request: Request, response: Response, uow: UOWDep):
    """
    Handle incoming webhook events from Clerk.
    Creates a user if the event type is "user.created" and deletes a user if the event type is "user.deleted".
    Also initializes the user's directory and removes it if the user is deleted.

    Args:
        request (Request): The incoming HTTP request containing headers and body.
        response (Response): The HTTP response object to modify status codes.
        uow (UOWDep): Unit of Work dependency for database operations.

    Raises:
        WebhookVerificationError: If the webhook signature verification fails.
        ValidationError: If the event data validation fails.
        IntegrityError: If this user already exists.
    """
    headers = request.headers
    payload = await request.body()

    try:
        wh = Webhook(settings.WH_SECRET)
        event = wh.verify(payload, headers)
        clerk_event = ClerkWebhookEvent.model_validate(event)

        if clerk_event.type == "user.created":
            user = UserSchemaAdd(
                clerk_id=clerk_event.data.id,
                name=f"{clerk_event.data.first_name} {clerk_event.data.last_name}".strip(),
                email=(
                    clerk_event.data.email_addresses[0].email_address
                    if clerk_event.data.email_addresses
                    else None
                ),
            )
            await UsersService().add_user(uow, user)
            ft_userdir = FTUserDir(user.clerk_id)
            ft_userdir.initialize()
            return
        elif clerk_event.type == "user.deleted":
            ft_userdir = FTUserDir(clerk_event.data.id)
            ft_userdir.remove()
            await UsersService().delete_user(uow, clerk_event.data.id)

    except WebhookVerificationError as e:
        logging.error(f"Webhook verification error in clerk_webhook_handler: {e}")
        response.status_code = status.HTTP_400_BAD_REQUEST
        return
    except ValidationError as e:
        logging.error(f"Validation error in clerk_webhook_handler: {e}")
        response.status_code = status.HTTP_422_UNPROCESSABLE_ENTITY
        return
    except IntegrityError as e:
        logging.error(f"Integrity error in clerk_webhook_handler: {e}")
        response.status_code = status.HTTP_409_CONFLICT
        return

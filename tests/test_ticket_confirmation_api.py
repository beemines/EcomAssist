import pytest
from pydantic import ValidationError
from uuid import uuid4
from app.schemas.ticket_confirmation import TicketConfirmationRequest


@pytest.mark.parametrize('patch', [{'turn_id': 1}, {'turn_id': '01'}, {'decision': 'yes'},
    {'confirmation_id': 'bad'}, {'checkpoint_id': 'bad'}, {'description': '篡改'}, {'approved': True}])
def test_confirmation_only_accepts_strict_locator_and_decision(patch):
    value = {'turn_id': '1', 'confirmation_id': str(uuid4()), 'checkpoint_id': str(uuid4()), 'decision': 'confirm'}
    with pytest.raises(ValidationError):
        TicketConfirmationRequest.model_validate(value | patch)

from datetime import datetime
from typing import Optional
from uuid import UUID
from pydantic import BaseModel, ConfigDict


class TurnstilePassage(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    access: bool
    user_id: UUID
    svm_model_id: int
    turnstile_id: int
    user_skipass_id: Optional[int]
    passage_time: datetime

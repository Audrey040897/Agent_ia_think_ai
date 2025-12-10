from pydantic import BaseModel, EmailStr
from typing import List


class Episode(BaseModel):
    title: str
    audio_url: str
    duration: int  # en secondes
    transcript: str
    keywords: List[str]
    category: str
    cover_image: str
    contributor_email: EmailStr
    quality_status: str  # "OK" ou "A_REVOIR"
    quality_score: int   # 0–100
    status: str = "draft"

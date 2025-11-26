"""
Download routes for RSS and get_iplayer
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional

router = APIRouter()


class RSSDownloadRequest(BaseModel):
    feed_url: str
    limit: Optional[int] = None


class IPlayerDownloadRequest(BaseModel):
    query: str


class DownloadResponse(BaseModel):
    success: bool
    message: str
    files: List[str] = []


@router.post("/rss", response_model=DownloadResponse)
async def download_from_rss(request: RSSDownloadRequest):
    """Download episodes from RSS feed"""
    # TODO: Implement using existing RSScraper
    return DownloadResponse(
        success=True,
        message=f"Downloaded from {request.feed_url}",
        files=[]
    )


@router.post("/iplayer", response_model=DownloadResponse)
async def download_with_iplayer(request: IPlayerDownloadRequest):
    """Search and download with get_iplayer"""
    # TODO: Implement using existing GetIPlayerWrapper
    return DownloadResponse(
        success=True,
        message=f"Searched for: {request.query}",
        files=[]
    )


@router.get("/", response_model=List[str])
async def list_downloads():
    """List all downloaded audio files"""
    # TODO: Implement using FileManager
    return []

"""
Reddit API Service - Python implementation
Handles all API calls to Reddit with proper error handling and rate limiting
"""

import json
import asyncio
import aiofiles
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
import httpx
from .config import config
from models.models import (
    RedditPost, RedditComment, RedditSubreddit, RedditUser, 
    RedditSearchResult, ApiCallResult
)


class RedditAPIService:
    """Reddit API Service with rate limiting and error handling"""
    
    def __init__(self):
        self.client_id = config.reddit_client_id
        self.client_secret = config.reddit_client_secret
        self.user_agent = config.reddit_user_agent
        self.timeout = config.timeout_seconds
        self.redirect_uri = config.reddit_redirect_uri
        self.oauth_scopes = config.reddit_oauth_scopes
        self.token_storage_path = "reddit_tokens.json"
        
        # Token management
        self.access_token: Optional[str] = None
        self.token_expiry: datetime = datetime.min
        self.refresh_token: Optional[str] = None
        
        # Rate limiting
        self.rate_limit_remaining: int = 60
        self.rate_limit_reset: int = 0
        
        # Load existing tokens will be called when needed
    
    async def load_tokens_from_storage(self) -> None:
        """Load tokens from persistent storage"""
        try:
            async with aiofiles.open(self.token_storage_path, 'r') as f:
                token_data = json.loads(await f.read())
                self.access_token = token_data.get('access_token')
                self.refresh_token = token_data.get('refresh_token')
                if token_data.get('expires_at'):
                    self.token_expiry = datetime.fromisoformat(token_data['expires_at'])
        except (FileNotFoundError, json.JSONDecodeError, KeyError):
            # No tokens or invalid format, start fresh
            pass
    
    async def save_tokens_to_storage(self) -> None:
        """Save tokens to persistent storage"""
        if not self.access_token:
            return
            
        token_data = {
            'access_token': self.access_token,
            'refresh_token': self.refresh_token,
            'expires_at': self.token_expiry.isoformat(),
            'saved_at': datetime.now().isoformat()
        }
        
        try:
            async with aiofiles.open(self.token_storage_path, 'w') as f:
                await f.write(json.dumps(token_data, indent=2))
        except Exception as e:
            # Warning: Failed to save tokens
            pass
    
    async def get_client_credentials_token(self) -> bool:
        """Get access token using client credentials flow"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    "https://www.reddit.com/api/v1/access_token",
                    data={
                        "grant_type": "client_credentials",
                        "device_id": "mcp_reddit_server"
                    },
                    auth=(self.client_id, self.client_secret),
                    headers={"User-Agent": self.user_agent},
                    timeout=self.timeout
                )
                
                if response.status_code == 200:
                    data = response.json()
                    self.access_token = data.get("access_token")
                    expires_in = data.get("expires_in", 3600)
                    self.token_expiry = datetime.now() + timedelta(seconds=expires_in)
                    await self.save_tokens_to_storage()
                    return True
                else:
                    # Failed to get client credentials token
                    return False
                    
        except Exception as e:
            # Error getting client credentials token
            return False
    
    async def ensure_valid_token(self) -> bool:
        """Ensure we have a valid access token"""
        # Load tokens if not loaded yet
        if not self.access_token:
            await self.load_tokens_from_storage()
        
        if not self.access_token or datetime.now() >= self.token_expiry:
            return await self.get_client_credentials_token()
        return True
    
    async def make_request(self, endpoint: str, params: Optional[Dict[str, Any]] = None) -> ApiCallResult:
        """Make authenticated request to Reddit API"""
        if not await self.ensure_valid_token():
            return ApiCallResult(success=False, error="Failed to get valid access token")
        
        try:
            async with httpx.AsyncClient() as client:
                headers = {
                    "Authorization": f"Bearer {self.access_token}",
                    "User-Agent": self.user_agent
                }
                
                response = await client.get(
                    f"https://oauth.reddit.com{endpoint}",
                    headers=headers,
                    params=params or {},
                    timeout=self.timeout
                )
                
                # Extract rate limit info
                try:
                    self.rate_limit_remaining = int(float(response.headers.get("X-Ratelimit-Remaining", "60")))
                except (ValueError, TypeError):
                    self.rate_limit_remaining = 60
                
                try:
                    self.rate_limit_reset = int(float(response.headers.get("X-Ratelimit-Reset", "0")))
                except (ValueError, TypeError):
                    self.rate_limit_reset = 0
                
                if response.status_code == 200:
                    return ApiCallResult(
                        success=True,
                        data=response.json(),
                        rate_limit_remaining=self.rate_limit_remaining,
                        rate_limit_reset=self.rate_limit_reset
                    )
                else:
                    return ApiCallResult(
                        success=False,
                        error=f"HTTP {response.status_code}: {response.text}",
                        rate_limit_remaining=self.rate_limit_remaining,
                        rate_limit_reset=self.rate_limit_reset
                    )
                    
        except Exception as e:
            return ApiCallResult(success=False, error=str(e))
    
    async def get_subreddit_posts(
        self, 
        subreddit: str, 
        sort: str = "hot", 
        limit: int = 25, 
        time: str = "all"
    ) -> ApiCallResult:
        """Get posts from a subreddit"""
        endpoint = f"/r/{subreddit}/{sort}.json"
        params = {"limit": limit, "t": time}
        return await self.make_request(endpoint, params)
    
    async def search_reddit(
        self, 
        query: str, 
        subreddit: Optional[str] = None, 
        sort: str = "relevance", 
        time: str = "all", 
        limit: int = 25
    ) -> ApiCallResult:
        """Search Reddit posts and comments"""
        endpoint = "/search.json"
        params = {
            "q": query,
            "sort": sort,
            "t": time,
            "limit": limit
        }
        if subreddit:
            params["restrict_sr"] = "true"
            params["subreddit"] = subreddit
            
        return await self.make_request(endpoint, params)
    
    async def get_user_profile(self, username: str) -> ApiCallResult:
        """Get Reddit user profile information"""
        endpoint = f"/user/{username}/about.json"
        return await self.make_request(endpoint)
    
    async def get_subreddit_info(self, subreddit: str) -> ApiCallResult:
        """Get subreddit information"""
        endpoint = f"/r/{subreddit}/about.json"
        return await self.make_request(endpoint)
    
    async def get_post_comments(
        self, 
        post_id: str, 
        sort: str = "best", 
        limit: int = 25
    ) -> ApiCallResult:
        """Get comments for a Reddit post"""
        endpoint = f"/comments/{post_id}.json"
        params = {"sort": sort, "limit": limit}
        return await self.make_request(endpoint, params)
    
    async def get_trending_subreddits(self, limit: int = 25) -> ApiCallResult:
        """Get trending/popular subreddits"""
        endpoint = "/subreddits/popular.json"
        params = {"limit": limit}
        return await self.make_request(endpoint, params)
    
    async def get_cross_posts(self, post_id: str) -> ApiCallResult:
        """Find crossposts of a Reddit post"""
        # Reddit doesn't have a direct crossposts API, so we'll search for the post
        # and look for similar posts in other subreddits
        endpoint = f"/api/info.json"
        params = {"id": f"t3_{post_id}"}
        return await self.make_request(endpoint, params)


# Global service instance
reddit_api = RedditAPIService()

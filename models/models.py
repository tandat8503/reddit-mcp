"""
Pydantic models for Reddit API data structures and MCP tool schemas
"""

from typing import List, Optional, Dict, Any, Union
from pydantic import BaseModel, Field
from enum import Enum


# ========================================
# 🚀 REDDIT API DATA MODELS
# ========================================

class RedditPost(BaseModel):
    """Reddit post data structure"""
    id: str
    title: str
    author: str
    subreddit: str
    score: int
    upvote_ratio: float
    num_comments: int
    created_utc: int
    url: str
    selftext: Optional[str] = None
    is_self: bool
    permalink: str
    domain: str
    thumbnail: Optional[str] = None
    preview: Optional[Dict[str, Any]] = None


class RedditComment(BaseModel):
    """Reddit comment data structure"""
    id: str
    author: str
    body: str
    score: int
    created_utc: int
    parent_id: str
    permalink: str
    replies: Optional[List['RedditComment']] = None


class RedditSubreddit(BaseModel):
    """Reddit subreddit data structure"""
    name: str
    title: str
    display_name: str
    description: str
    subscribers: int
    active_user_count: int
    created_utc: int
    url: str
    over18: bool
    public_description: str
    lang: str


class RedditUser(BaseModel):
    """Reddit user profile data structure"""
    name: str
    id: str
    created_utc: int
    link_karma: int
    comment_karma: int
    is_gold: bool
    is_mod: bool
    has_verified_email: bool
    icon_img: Optional[str] = None
    subreddit: Optional[Dict[str, Any]] = None


class RedditSearchResult(BaseModel):
    """Reddit search result data structure"""
    posts: List[RedditPost]
    comments: List[RedditComment]
    total_results: int


class ApiCallResult(BaseModel):
    """Generic API call result wrapper"""
    success: bool
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    rate_limit_remaining: Optional[int] = None
    rate_limit_reset: Optional[int] = None


# ========================================
# 🛠️ MCP TOOL SCHEMAS
# ========================================

class SortOrder(str, Enum):
    """Sort order options for posts"""
    HOT = "hot"
    NEW = "new"
    TOP = "top"


class CommentSortOrder(str, Enum):
    """Sort order options for comments"""
    BEST = "best"
    TOP = "top"
    NEW = "new"


class SimpleSubredditPostsSchema(BaseModel):
    """Schema for get_subreddit_posts tool"""
    subreddit: str = Field(..., description="Subreddit name (e.g., 'programming', 'AskReddit')")
    sort: SortOrder = Field(default=SortOrder.HOT, description="Sort order (default: hot)")


class SimpleSearchSchema(BaseModel):
    """Schema for search_reddit tool"""
    query: str = Field(..., description="Search query (e.g., 'machine learning', 'python tutorial')")
    subreddit: Optional[str] = Field(None, description="Limit to specific subreddit (optional)")


class SimpleUserProfileSchema(BaseModel):
    """Schema for get_user_profile tool"""
    username: str = Field(..., description="Reddit username to get profile information")


class SimpleSubredditInfoSchema(BaseModel):
    """Schema for get_subreddit_info tool"""
    subreddit: str = Field(..., description="Subreddit name to get information about")


class SimplePostCommentsSchema(BaseModel):
    """Schema for get_post_comments tool"""
    post_id: str = Field(..., description="Reddit post ID to get comments for")
    sort: CommentSortOrder = Field(default=CommentSortOrder.BEST, description="Sort order (default: best)")


class SimpleTrendingSubredditsSchema(BaseModel):
    """Schema for get_trending_subreddits tool"""
    pass  # No parameters needed


class SimpleCrossPostSchema(BaseModel):
    """Schema for get_cross_posts tool"""
    post_id: str = Field(..., description="Reddit post ID to find crossposts for")


# Update forward references
RedditComment.model_rebuild()

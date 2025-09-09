"""
Utility functions for MCP Reddit Server
Common helper functions to eliminate code duplication (DRY principle)
"""

from typing import Dict, Any, List, Callable, Optional
from datetime import datetime


# ========================================
# COMMON HELPER FUNCTIONS (DRY)
# ========================================

def create_error_response(message: str, details: str = "") -> str:
    """Create standardized error response"""
    return f"**Error**: {message}\n\n**Details**: {details}\n\n**Troubleshooting**: Check your Reddit API credentials and network connection."


def create_success_response(message: str, data: str = "") -> str:
    """Create standardized success response"""
    return f"**Success**: {message}\n\n{data}"


def format_timestamp(created_utc) -> str:
    """Format Unix timestamp to readable date"""
    try:
        # Handle both int and float from Reddit API
        timestamp = float(created_utc)
        return datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')
    except (ValueError, TypeError, OSError):
        return "Unknown date"


def format_date(created_utc) -> str:
    """Format Unix timestamp to date only"""
    try:
        # Handle both int and float from Reddit API
        timestamp = float(created_utc)
        return datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d')
    except (ValueError, TypeError, OSError):
        return "Unknown date"


def format_score(score) -> str:
    """Format score with appropriate emoji"""
    # Handle both int and float from Reddit API
    try:
        score_int = int(float(score))
    except (ValueError, TypeError):
        score_int = 0
    
    if score_int >= 1000:
        return f"Hot: {score_int:,}"
    elif score_int >= 100:
        return f"Good: {score_int:,}"
    else:
        return f"Score: {score_int}"


def format_karma(karma) -> str:
    """Format karma with appropriate emoji"""
    # Handle both int and float from Reddit API
    try:
        karma_int = int(float(karma))
    except (ValueError, TypeError):
        karma_int = 0
    
    if karma_int >= 100000:
        return f"Elite: {karma_int:,}"
    elif karma_int >= 10000:
        return f"High: {karma_int:,}"
    else:
        return f"Karma: {karma_int:,}"


def format_subscriber_count(subscribers) -> str:
    """Format subscriber count with appropriate emoji"""
    # Handle both int and float from Reddit API
    try:
        subscribers_int = int(float(subscribers))
    except (ValueError, TypeError):
        subscribers_int = 0
    
    if subscribers_int >= 1000000:
        return f"Large: {subscribers_int/1000000:.1f}M"
    elif subscribers_int >= 1000:
        return f"Medium: {subscribers_int/1000:.1f}K"
    else:
        return f"Subscribers: {subscribers_int:,}"


def truncate_text(text: str, max_length: int = 200) -> str:
    """Truncate text to specified length with ellipsis"""
    if len(text) > max_length:
        return text[:max_length] + "..."
    return text


def create_reddit_link(permalink: str, fallback_url: str = "") -> str:
    """Create Reddit link from permalink or fallback URL"""
    if permalink:
        return f"https://reddit.com{permalink}"
    return fallback_url


def validate_api_response(result: Dict[str, Any], expected_structure: str) -> List[Dict[str, Any]]:
    """Validate API response and extract data"""
    if not result.get('success'):
        raise Exception(result.get('error', 'API call failed'))
    
    data = result.get('data', {})
    if not data or not data.get('data') or not data['data'].get('children'):
        raise Exception(f"No {expected_structure} found")
    
    return [child['data'] for child in data['data']['children']]


def format_data_list(
    items: List[Dict[str, Any]], 
    formatter: Callable[[Dict[str, Any]], str], 
    limit: int, 
    item_type: str
) -> str:
    """Format list of items with preview limit"""
    display_items = items[:limit]
    formatted_items = [formatter(item) for item in display_items]
    result = "\n\n".join(formatted_items)
    
    if len(items) > limit:
        result += f"\n\n... and {len(items) - limit} more {item_type} available"
    
    return result


def create_summary_with_rate_limit(
    message: str, 
    count: int, 
    item_type: str, 
    rate_limit_remaining: Optional[int] = None
) -> str:
    """Create summary message with rate limit info"""
    summary = f"{message} **{count} {item_type}**"
    if rate_limit_remaining:
        summary += f"\n**Rate limit**: {rate_limit_remaining} requests remaining"
    return summary


# ========================================
# FORMATTING FUNCTIONS
# ========================================

def format_reddit_post(post: Dict[str, Any]) -> str:
    """Format Reddit post for display"""
    title = post.get('title', 'No title')
    author = post.get('author', 'Unknown')
    subreddit = post.get('subreddit', 'Unknown')
    score = post.get('score', 0)
    num_comments = post.get('num_comments', 0)
    created_utc = post.get('created_utc', 0)
    url = post.get('url', '')
    permalink = post.get('permalink', '')
    
    # Format components
    timestamp = format_timestamp(created_utc)
    score_display = format_score(score)
    
    # Handle num_comments as float
    try:
        comments_int = int(float(num_comments))
        comments_display = f"Comments: {comments_int:,}" if comments_int > 0 else "Comments: 0"
    except (ValueError, TypeError):
        comments_display = "Comments: 0"
    
    reddit_link = create_reddit_link(permalink, url)
    
    return f"""**{title}**
**Author**: u/{author} | **Subreddit**: r/{subreddit}
{score_display} | {comments_display} | **Posted**: {timestamp}
**Link**: {reddit_link}"""


def format_reddit_comment(comment: Dict[str, Any], depth: int = 0) -> str:
    """Format Reddit comment for display"""
    indent = "  " * depth
    author = comment.get('author', 'Unknown')
    body = comment.get('body', 'No content')
    score = comment.get('score', 0)
    created_utc = comment.get('created_utc', 0)
    
    # Format components
    timestamp = format_timestamp(created_utc)
    
    # Handle score as float
    try:
        score_int = int(float(score))
        score_display = f"Score: {score_int}" if score_int != 0 else "Score: 0"
    except (ValueError, TypeError):
        score_display = "Score: 0"
    
    body_truncated = truncate_text(body, 200)
    
    result = f"{indent}**u/{author}** ({score_display}) - {timestamp}\n{indent}{body_truncated}"
    
    # Add replies (limit to 3 to avoid too much nesting)
    replies = comment.get('replies', {}).get('data', {}).get('children', [])
    if replies:
        for reply in replies[:3]:
            reply_data = reply.get('data', {})
            if reply_data.get('body'):
                result += f"\n{format_reddit_comment(reply_data, depth + 1)}"
    
    return result


def format_reddit_subreddit(subreddit: Dict[str, Any]) -> str:
    """Format Reddit subreddit for display"""
    name = subreddit.get('display_name', subreddit.get('name', 'Unknown'))
    title = subreddit.get('title', 'No title')
    description = subreddit.get('public_description', 'No description')
    subscribers = subreddit.get('subscribers', 0)
    active_users = subreddit.get('active_user_count', 0)
    created_utc = subreddit.get('created_utc', 0)
    over18 = subreddit.get('over18', False)
    
    # Format components
    created_date = format_date(created_utc)
    sub_count = format_subscriber_count(subscribers)
    
    # Handle active_users as float
    try:
        active_users_int = int(float(active_users))
    except (ValueError, TypeError):
        active_users_int = 0
    
    nsfw_indicator = "NSFW" if over18 else "SFW"
    
    return f"""**r/{name}** - {title}
**Description**: {description}
**Subscribers**: {sub_count} | **Active**: {active_users_int:,}
**Created**: {created_date} | {nsfw_indicator}
**URL**: https://reddit.com/r/{name}"""


def format_reddit_user(user: Dict[str, Any]) -> str:
    """Format Reddit user profile for display"""
    name = user.get('name', 'Unknown')
    link_karma = user.get('link_karma', 0)
    comment_karma = user.get('comment_karma', 0)
    created_utc = user.get('created_utc', 0)
    is_gold = user.get('is_gold', False)
    is_mod = user.get('is_mod', False)
    has_verified_email = user.get('has_verified_email', False)
    
    # Format components
    created_date = format_date(created_utc)
    
    # Handle karma as float
    try:
        link_karma_int = int(float(link_karma))
        comment_karma_int = int(float(comment_karma))
        total_karma = link_karma_int + comment_karma_int
    except (ValueError, TypeError):
        link_karma_int = 0
        comment_karma_int = 0
        total_karma = 0
    
    karma_display = format_karma(total_karma)
    
    # Status indicators
    status = []
    if is_gold:
        status.append("Gold")
    if is_mod:
        status.append("Moderator")
    if has_verified_email:
        status.append("Verified")
    
    status_text = " | ".join(status) if status else "Regular User"
    
    return f"""**u/{name}**
**Karma**: {karma_display} (Post: {link_karma_int:,} | Comment: {comment_karma_int:,})
**Member since**: {created_date}
{status_text}
**Profile**: https://reddit.com/u/{name}"""

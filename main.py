#!/usr/bin/env python3
"""
MCP Reddit Server - Python Version
Model Context Protocol server for Reddit API integration
"""

import asyncio
import json
from typing import Any, Dict, List, Optional
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

from services.reddit_api import reddit_api
from models.models import (
    RedditPost, RedditComment, RedditSubreddit, RedditUser,
    SimpleSubredditPostsSchema, SimpleSearchSchema, SimpleUserProfileSchema,
    SimpleSubredditInfoSchema, SimplePostCommentsSchema, 
    SimpleTrendingSubredditsSchema, SimpleCrossPostSchema
)
from utils import (
    create_error_response, create_success_response, format_reddit_post,
    format_reddit_comment, format_reddit_subreddit, format_reddit_user,
    validate_api_response, format_data_list, create_summary_with_rate_limit
)

# ========================================
# 🚀 MCP SERVER SETUP
# ========================================

# Create MCP server instance
server = Server("mcp-reddit-python")

# Constants for data limits
POST_PREVIEW_LIMIT = 10
COMMENT_PREVIEW_LIMIT = 10
SEARCH_RESULT_LIMIT = 8
TRENDING_SUBREDDIT_LIMIT = 15

# ========================================
# 🛠️ MCP TOOLS IMPLEMENTATION
# ========================================

@server.list_tools()
async def list_tools() -> List[Tool]:
    """List all available MCP tools"""
    return [
        Tool(
            name="get_subreddit_posts",
            description="📖 Get posts from a subreddit\n🎯 What it does: Fetches posts from any Reddit subreddit with sorting options\n📝 Required: subreddit name (e.g., 'programming', 'AskReddit', 'MachineLearning')\n⚙️ Optional: sort ('hot', 'new', 'top')\n💡 Examples:\n   • Get hot posts: {\"subreddit\": \"programming\"}\n   • Get new posts: {\"subreddit\": \"AskReddit\", \"sort\": \"new\"}\n   • Get top posts: {\"subreddit\": \"MachineLearning\", \"sort\": \"top\"}\n🔍 Output: Formatted list with title, author, score, comments, date, and Reddit link",
            inputSchema={
                "type": "object",
                "properties": {
                    "subreddit": {
                        "type": "string",
                        "description": "Subreddit name (e.g., 'programming', 'AskReddit')"
                    },
                    "sort": {
                        "type": "string",
                        "enum": ["hot", "new", "top"],
                        "default": "hot",
                        "description": "Sort order (default: hot)"
                    }
                },
                "required": ["subreddit"],
                "additionalProperties": False
            }
        ),
        Tool(
            name="search_reddit",
            description="🔍 Search Reddit posts and comments\n🎯 What it does: Searches across Reddit or within a specific subreddit\n📝 Required: query (search terms)\n⚙️ Optional: subreddit (limit search to specific subreddit)\n💡 Examples:\n   • Global search: {\"query\": \"machine learning\"}\n   • Subreddit search: {\"query\": \"python tutorial\", \"subreddit\": \"programming\"}\n   • Tech search: {\"query\": \"TypeScript\", \"subreddit\": \"typescript\"}\n🔍 Output: Formatted search results with title, author, subreddit, score, and link",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Search query (e.g., 'machine learning', 'python tutorial')"
                    },
                    "subreddit": {
                        "type": "string",
                        "description": "Limit to specific subreddit (optional)"
                    }
                },
                "required": ["query"],
                "additionalProperties": False
            }
        ),
        Tool(
            name="get_user_profile",
            description="👤 Get Reddit user profile information\n🎯 What it does: Fetches detailed profile info for any Reddit user\n📝 Required: username (Reddit username without u/ prefix)\n💡 Examples:\n   • Get profile: {\"username\": \"spez\"}\n   • Check user: {\"username\": \"AwkwardTension4482\"}\n   • View profile: {\"username\": \"gallowboob\"}\n🔍 Output: User info with karma, account age, gold status, moderator status, and profile link",
            inputSchema={
                "type": "object",
                "properties": {
                    "username": {
                        "type": "string",
                        "description": "Reddit username to get profile information"
                    }
                },
                "required": ["username"],
                "additionalProperties": False
            }
        ),
        Tool(
            name="get_subreddit_info",
            description="🏠 Get subreddit information\n🎯 What it does: Fetches detailed info about any Reddit subreddit\n📝 Required: subreddit name (without r/ prefix)\n💡 Examples:\n   • Get info: {\"subreddit\": \"programming\"}\n   • Check subreddit: {\"subreddit\": \"AskReddit\"}\n   • View details: {\"subreddit\": \"MachineLearning\"}\n🔍 Output: Subreddit details with description, subscribers, active users, creation date, NSFW status, and URL",
            inputSchema={
                "type": "object",
                "properties": {
                    "subreddit": {
                        "type": "string",
                        "description": "Subreddit name to get information about"
                    }
                },
                "required": ["subreddit"],
                "additionalProperties": False
            }
        ),
        Tool(
            name="get_post_comments",
            description="💬 Get comments for a Reddit post\n🎯 What it does: Fetches comments and replies for any Reddit post\n📝 Required: post_id (Reddit post ID, found in post URLs)\n⚙️ Optional: sort ('best', 'top', 'new')\n💡 Examples:\n   • Get comments: {\"post_id\": \"1n1nlse\"}\n   • Best comments: {\"post_id\": \"1n1nlse\", \"sort\": \"best\"}\n   • New comments: {\"post_id\": \"1n1nlse\", \"sort\": \"new\"}\n🔍 Output: Formatted comment tree with author, score, timestamp, and nested replies",
            inputSchema={
                "type": "object",
                "properties": {
                    "post_id": {
                        "type": "string",
                        "description": "Reddit post ID to get comments for"
                    },
                    "sort": {
                        "type": "string",
                        "enum": ["best", "top", "new"],
                        "default": "best",
                        "description": "Sort order (default: best)"
                    }
                },
                "required": ["post_id"],
                "additionalProperties": False
            }
        ),
        Tool(
            name="get_trending_subreddits",
            description="🔥 Get trending/popular subreddits\n🎯 What it does: Fetches list of currently popular and trending subreddits\n📝 Required: None (no parameters needed)\n💡 Examples:\n   • Get trending: {}\n   • Simple call: {}\n🔍 Output: List of trending subreddits with name, title, subscribers, description, and URL",
            inputSchema={
                "type": "object",
                "properties": {},
                "additionalProperties": False
            }
        ),
        Tool(
            name="get_cross_posts",
            description="🔄 Find crossposts of a Reddit post\n🎯 What it does: Finds posts that were cross-posted from the original post\n📝 Required: post_id (Reddit post ID to find crossposts for)\n💡 Examples:\n   • Find crossposts: {\"post_id\": \"1n1nlse\"}\n   • Check shares: {\"post_id\": \"1abc123\"}\n🔍 Output: List of crossposts with title, author, subreddit, score, and Reddit link",
            inputSchema={
                "type": "object",
                "properties": {
                    "post_id": {
                        "type": "string",
                        "description": "Reddit post ID to find crossposts for"
                    }
                },
                "required": ["post_id"],
                "additionalProperties": False
            }
        )
    ]

@server.call_tool()
async def call_tool(name: str, arguments: Dict[str, Any]) -> List[TextContent]:
    """Handle tool calls"""
    try:
        if name == "get_subreddit_posts":
            return await handle_get_subreddit_posts(arguments)
        elif name == "search_reddit":
            return await handle_search_reddit(arguments)
        elif name == "get_user_profile":
            return await handle_get_user_profile(arguments)
        elif name == "get_subreddit_info":
            return await handle_get_subreddit_info(arguments)
        elif name == "get_post_comments":
            return await handle_get_post_comments(arguments)
        elif name == "get_trending_subreddits":
            return await handle_get_trending_subreddits(arguments)
        elif name == "get_cross_posts":
            return await handle_get_cross_posts(arguments)
        else:
            return [TextContent(type="text", text=create_error_response(f"Unknown tool: {name}"))]
    except Exception as e:
        return [TextContent(type="text", text=create_error_response("Tool execution failed", str(e)))]

# ========================================
# 🛠️ TOOL HANDLERS
# ========================================

async def handle_get_subreddit_posts(arguments: Dict[str, Any]) -> List[TextContent]:
    """Handle get_subreddit_posts tool"""
    try:
        subreddit = arguments.get("subreddit", "")
        sort = arguments.get("sort", "hot")
        
        if not subreddit:
            return [TextContent(type="text", text=create_error_response("Subreddit name is required"))]
        
        result = await reddit_api.get_subreddit_posts(subreddit, sort)
        
        if not result.success:
            return [TextContent(type="text", text=create_error_response("Failed to get subreddit posts", result.error or "Unknown error"))]
        
        posts = validate_api_response(result.__dict__, "posts")
        
        if not posts:
            return [TextContent(type="text", text=create_success_response(f"No posts found in r/{subreddit}"))]
        
        # Format posts
        formatted_posts = format_data_list(posts, format_reddit_post, POST_PREVIEW_LIMIT, "posts")
        
        summary = create_summary_with_rate_limit(
            f"📊 **Found {len(posts)} posts** in r/{subreddit} (sorted by {sort})",
            len(posts),
            "posts",
            result.rate_limit_remaining
        )
        
        response_text = f"{summary}\n\n{formatted_posts}"
        return [TextContent(type="text", text=create_success_response(f"Successfully retrieved posts from r/{subreddit}", response_text))]
        
    except Exception as e:
        return [TextContent(type="text", text=create_error_response("Failed to get subreddit posts", str(e)))]

async def handle_search_reddit(arguments: Dict[str, Any]) -> List[TextContent]:
    """Handle search_reddit tool"""
    try:
        query = arguments.get("query", "")
        subreddit = arguments.get("subreddit")
        
        if not query:
            return [TextContent(type="text", text=create_error_response("Search query is required"))]
        
        result = await reddit_api.search_reddit(query, subreddit)
        
        if not result.success:
            return [TextContent(type="text", text=create_error_response("Failed to search Reddit", result.error or "Unknown error"))]
        
        posts = validate_api_response(result.__dict__, "search results")
        
        if not posts:
            search_scope = f" in r/{subreddit}" if subreddit else ""
            return [TextContent(type="text", text=create_success_response(f"No results found for '{query}'{search_scope}"))]
        
        # Format search results
        formatted_posts = format_data_list(posts, format_reddit_post, SEARCH_RESULT_LIMIT, "results")
        
        search_scope = f" in r/{subreddit}" if subreddit else " across Reddit"
        summary = create_summary_with_rate_limit(
            f"🔍 **Found {len(posts)} results** for '{query}'{search_scope}",
            len(posts),
            "results",
            result.rate_limit_remaining
        )
        
        response_text = f"{summary}\n\n{formatted_posts}"
        return [TextContent(type="text", text=create_success_response(f"Search completed for '{query}'", response_text))]
        
    except Exception as e:
        return [TextContent(type="text", text=create_error_response("Failed to search Reddit", str(e)))]

async def handle_get_user_profile(arguments: Dict[str, Any]) -> List[TextContent]:
    """Handle get_user_profile tool"""
    try:
        username = arguments.get("username", "")
        
        if not username:
            return [TextContent(type="text", text=create_error_response("Username is required"))]
        
        result = await reddit_api.get_user_profile(username)
        
        if not result.success:
            return [TextContent(type="text", text=create_error_response("Failed to get user profile", result.error or "Unknown error"))]
        
        user_data = result.data.get('data', {})
        
        if not user_data:
            return [TextContent(type="text", text=create_error_response(f"User '{username}' not found"))]
        
        formatted_user = format_reddit_user(user_data)
        
        summary = create_summary_with_rate_limit(
            f"👤 **Profile for u/{username}**",
            1,
            "profile",
            result.rate_limit_remaining
        )
        
        response_text = f"{summary}\n\n{formatted_user}"
        return [TextContent(type="text", text=create_success_response(f"Successfully retrieved profile for u/{username}", response_text))]
        
    except Exception as e:
        return [TextContent(type="text", text=create_error_response("Failed to get user profile", str(e)))]

async def handle_get_subreddit_info(arguments: Dict[str, Any]) -> List[TextContent]:
    """Handle get_subreddit_info tool"""
    try:
        subreddit = arguments.get("subreddit", "")
        
        if not subreddit:
            return [TextContent(type="text", text=create_error_response("Subreddit name is required"))]
        
        result = await reddit_api.get_subreddit_info(subreddit)
        
        if not result.success:
            return [TextContent(type="text", text=create_error_response("Failed to get subreddit info", result.error or "Unknown error"))]
        
        subreddit_data = result.data.get('data', {})
        
        if not subreddit_data:
            return [TextContent(type="text", text=create_error_response(f"Subreddit 'r/{subreddit}' not found"))]
        
        formatted_subreddit = format_reddit_subreddit(subreddit_data)
        
        summary = create_summary_with_rate_limit(
            f"🏠 **Subreddit info for r/{subreddit}**",
            1,
            "subreddit",
            result.rate_limit_remaining
        )
        
        response_text = f"{summary}\n\n{formatted_subreddit}"
        return [TextContent(type="text", text=create_success_response(f"Successfully retrieved info for r/{subreddit}", response_text))]
        
    except Exception as e:
        return [TextContent(type="text", text=create_error_response("Failed to get subreddit info", str(e)))]

async def handle_get_post_comments(arguments: Dict[str, Any]) -> List[TextContent]:
    """Handle get_post_comments tool"""
    try:
        post_id = arguments.get("post_id", "")
        sort = arguments.get("sort", "best")
        
        if not post_id:
            return [TextContent(type="text", text=create_error_response("Post ID is required"))]
        
        result = await reddit_api.get_post_comments(post_id, sort)
        
        if not result.success:
            return [TextContent(type="text", text=create_error_response("Failed to get post comments", result.error or "Unknown error"))]
        
        # Reddit comments API returns a list with post data and comments
        if not result.data or len(result.data) < 2:
            return [TextContent(type="text", text=create_error_response("No comments data found"))]
        
        comments_data = result.data[1].get('data', {}).get('children', [])
        
        if not comments_data:
            return [TextContent(type="text", text=create_success_response(f"No comments found for post {post_id}"))]
        
        # Format comments
        formatted_comments = format_data_list(comments_data, format_reddit_comment, COMMENT_PREVIEW_LIMIT, "comments")
        
        summary = create_summary_with_rate_limit(
            f"💬 **Found {len(comments_data)} comments** for post {post_id} (sorted by {sort})",
            len(comments_data),
            "comments",
            result.rate_limit_remaining
        )
        
        response_text = f"{summary}\n\n{formatted_comments}"
        return [TextContent(type="text", text=create_success_response(f"Successfully retrieved comments for post {post_id}", response_text))]
        
    except Exception as e:
        return [TextContent(type="text", text=create_error_response("Failed to get post comments", str(e)))]

async def handle_get_trending_subreddits(arguments: Dict[str, Any]) -> List[TextContent]:
    """Handle get_trending_subreddits tool"""
    try:
        result = await reddit_api.get_trending_subreddits()
        
        if not result.success:
            return [TextContent(type="text", text=create_error_response("Failed to get trending subreddits", result.error or "Unknown error"))]
        
        subreddits = validate_api_response(result.__dict__, "trending subreddits")
        
        if not subreddits:
            return [TextContent(type="text", text=create_success_response("No trending subreddits found"))]
        
        # Format subreddits
        formatted_subreddits = format_data_list(subreddits, format_reddit_subreddit, TRENDING_SUBREDDIT_LIMIT, "subreddits")
        
        summary = create_summary_with_rate_limit(
            f"🔥 **Found {len(subreddits)} trending subreddits**",
            len(subreddits),
            "subreddits",
            result.rate_limit_remaining
        )
        
        response_text = f"{summary}\n\n{formatted_subreddits}"
        return [TextContent(type="text", text=create_success_response("Successfully retrieved trending subreddits", response_text))]
        
    except Exception as e:
        return [TextContent(type="text", text=create_error_response("Failed to get trending subreddits", str(e)))]

async def handle_get_cross_posts(arguments: Dict[str, Any]) -> List[TextContent]:
    """Handle get_cross_posts tool"""
    try:
        post_id = arguments.get("post_id", "")
        
        if not post_id:
            return [TextContent(type="text", text=create_error_response("Post ID is required"))]
        
        result = await reddit_api.get_cross_posts(post_id)
        
        if not result.success:
            return [TextContent(type="text", text=create_error_response("Failed to get cross posts", result.error or "Unknown error"))]
        
        posts = validate_api_response(result.__dict__, "cross posts")
        
        if not posts:
            return [TextContent(type="text", text=create_success_response(f"No cross posts found for post {post_id}"))]
        
        # Format cross posts
        formatted_posts = format_data_list(posts, format_reddit_post, POST_PREVIEW_LIMIT, "cross posts")
        
        summary = create_summary_with_rate_limit(
            f"🔄 **Found {len(posts)} cross posts** for post {post_id}",
            len(posts),
            "cross posts",
            result.rate_limit_remaining
        )
        
        response_text = f"{summary}\n\n{formatted_posts}"
        return [TextContent(type="text", text=create_success_response(f"Successfully retrieved cross posts for post {post_id}", response_text))]
        
    except Exception as e:
        return [TextContent(type="text", text=create_error_response("Failed to get cross posts", str(e)))]

# ========================================
# 🚀 MAIN FUNCTION
# ========================================

async def main():
    """Main function to run the MCP server"""
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            server.create_initialization_options()
        )

if __name__ == "__main__":
    asyncio.run(main())

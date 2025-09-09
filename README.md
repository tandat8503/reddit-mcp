# MCP Reddit Server - Python Version

A Model Context Protocol (MCP) server for Reddit API integration, written in Python. This server provides read-only access to Reddit data through 7 powerful tools, perfect for content research, market analysis, and social media monitoring.

## 🚀 Features

### **7 Read-Only Reddit Tools**
- **get_subreddit_posts** - Fetch posts from any subreddit with sorting options
- **search_reddit** - Search Reddit posts and comments globally or within subreddits
- **get_user_profile** - Get detailed Reddit user profile information
- **get_subreddit_info** - Get subreddit details, stats, and metadata
- **get_post_comments** - Retrieve comments and replies for any Reddit post
- **get_trending_subreddits** - Discover popular and trending subreddits
- **get_cross_posts** - Find crossposts and related content

### **Key Capabilities**
- ✅ **No OAuth Required** - Uses Reddit's public API with client credentials
- ✅ **Rate Limiting** - Built-in rate limit handling and monitoring
- ✅ **Error Handling** - Comprehensive error handling with user-friendly messages
- ✅ **Data Formatting** - Clean, readable output with proper formatting
- ✅ **Type Safety** - Full Pydantic model validation
- ✅ **Persistent Tokens** - Automatic token management and storage
- ✅ **MCP Compatible** - Works seamlessly with Cursor IDE and other MCP clients

## 📋 Prerequisites

- Python 3.8 or higher
- Reddit API credentials (Client ID and Secret)
- MCP-compatible client (Cursor IDE, etc.)

## 🛠️ Installation

### 1. Clone the Repository
```bash
git clone <repository-url>
cd mcp-reddit-python
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Set Up Environment Variables
Create a `.env` file in the project root:

```bash
cp env.example .env
```

Edit `.env` with your Reddit API credentials:
```env
REDDIT_CLIENT_ID=your_client_id_here
REDDIT_CLIENT_SECRET=your_client_secret_here
REDDIT_USER_AGENT=YourApp/1.0.0
REDDIT_REDIRECT_URI=http://localhost:8080
REDDIT_OAUTH_SCOPES=read submit vote history privatemessages subscribe
TIMEOUT_SECONDS=30
```

### 4. Get Reddit API Credentials
1. Go to [Reddit App Preferences](https://www.reddit.com/prefs/apps)
2. Click "Create App" or "Create Another App"
3. Choose "script" as the app type
4. Note down your Client ID and Secret

## 🔧 Configuration

### Cursor IDE Integration

Add to your `~/.cursor/mcp.json`:

```json
{
  "mcpServers": {
    "reddit-mcp-python": {
      "command": "python3",
      "args": ["/path/to/mcp-reddit-python/main.py"],
      "env": {
        "PYTHONPATH": "/path/to/mcp-reddit-python",
        "REDDIT_CLIENT_ID": "your_client_id",
        "REDDIT_CLIENT_SECRET": "your_client_secret",
        "REDDIT_USER_AGENT": "YourApp/1.0.0",
        "REDDIT_REDIRECT_URI": "http://localhost:8080",
        "REDDIT_OAUTH_SCOPES": "read submit vote history privatemessages subscribe",
        "TIMEOUT_SECONDS": "30",
        "MCP_SERVER_NAME": "reddit-mcp-python",
        "MCP_SERVER_VERSION": "1.0.0",
        "LOG_LEVEL": "INFO"
      }
    }
  }
}
```

### Manual Testing

Run the server directly:
```bash
python3 main.py
```

## 📖 Tool Documentation

### 1. get_subreddit_posts
**Purpose**: Fetch posts from any Reddit subreddit

**Parameters**:
- `subreddit` (required): Subreddit name (e.g., "programming", "AskReddit")
- `sort` (optional): Sort order - "hot", "new", "top", "rising" (default: "hot")
- `limit` (optional): Number of posts to fetch (default: 25, max: 100)
- `time` (optional): Time period for "top" sort - "hour", "day", "week", "month", "year", "all" (default: "all")

**Example**:
```json
{
  "subreddit": "programming",
  "sort": "hot",
  "limit": 10
}
```

### 2. search_reddit
**Purpose**: Search Reddit posts and comments

**Parameters**:
- `query` (required): Search terms
- `subreddit` (optional): Limit search to specific subreddit
- `sort` (optional): Sort order - "relevance", "hot", "top", "new", "comments" (default: "relevance")
- `time` (optional): Time period - "hour", "day", "week", "month", "year", "all" (default: "all")
- `limit` (optional): Number of results (default: 25)

**Example**:
```json
{
  "query": "python tutorial",
  "subreddit": "programming",
  "sort": "relevance",
  "limit": 15
}
```

### 3. get_user_profile
**Purpose**: Get Reddit user profile information

**Parameters**:
- `username` (required): Reddit username (without u/ prefix)

**Example**:
```json
{
  "username": "spez"
}
```

### 4. get_subreddit_info
**Purpose**: Get subreddit information and statistics

**Parameters**:
- `subreddit` (required): Subreddit name

**Example**:
```json
{
  "subreddit": "programming"
}
```

### 5. get_post_comments
**Purpose**: Get comments for a Reddit post

**Parameters**:
- `post_id` (required): Reddit post ID (found in post URLs)
- `sort` (optional): Sort order - "best", "top", "new", "controversial", "old", "qa" (default: "best")
- `limit` (optional): Number of comments (default: 25)

**Example**:
```json
{
  "post_id": "1n1nlse",
  "sort": "best",
  "limit": 20
}
```

### 6. get_trending_subreddits
**Purpose**: Get trending/popular subreddits

**Parameters**:
- `limit` (optional): Number of subreddits (default: 25)

**Example**:
```json
{
  "limit": 15
}
```

### 7. get_cross_posts
**Purpose**: Find crossposts of a Reddit post

**Parameters**:
- `post_id` (required): Reddit post ID

**Example**:
```json
{
  "post_id": "1n1nlse"
}
```

## 🏗️ Project Structure

```
mcp-reddit-python/
├── main.py                 # Main MCP server implementation
├── models/
│   ├── __init__.py
│   └── models.py          # Pydantic data models
├── services/
│   ├── __init__.py
│   ├── config.py          # Configuration management
│   └── reddit_api.py      # Reddit API service
├── utils.py               # Helper functions and formatters
├── requirements.txt       # Python dependencies
├── pyproject.toml         # Project configuration
├── env.example           # Environment variables template
├── mcp.json              # MCP configuration for Cursor
├── .gitignore            # Git ignore rules
└── README.md             # This file
```

## 🔧 Development

### Running Tests
```bash
# Test server startup
python3 -c "from main import server; print('Server loaded successfully')"

# Test imports
python3 -c "from services.reddit_api import reddit_api; print('API service loaded')"
```

### Code Quality
- **Type Safety**: Full Pydantic model validation
- **Error Handling**: Comprehensive error handling with user-friendly messages
- **DRY Principle**: Centralized utility functions to avoid code duplication
- **Clean Code**: Well-documented, readable code structure

## 📊 Rate Limiting

The server includes built-in rate limiting:
- **Reddit API**: 60 requests per minute (default)
- **Automatic Handling**: Server manages rate limits automatically
- **Token Refresh**: Automatic token refresh when expired
- **Error Recovery**: Graceful handling of rate limit exceeded errors

## 🚨 Error Handling

The server provides detailed error messages for common issues:
- **Invalid Credentials**: Clear messages for authentication failures
- **Rate Limit Exceeded**: Automatic retry with backoff
- **Network Issues**: Timeout handling and retry logic
- **Invalid Parameters**: Validation errors with helpful suggestions

## 🔒 Security

- **No OAuth Required**: Uses Reddit's public API with client credentials
- **Token Storage**: Secure local token storage (not committed to git)
- **Environment Variables**: Sensitive data stored in environment variables
- **Input Validation**: All inputs validated with Pydantic models

## 📈 Performance

- **Async Operations**: Full async/await support for better performance
- **Connection Pooling**: Efficient HTTP client with connection reuse
- **Caching**: Token caching to reduce API calls
- **Batch Operations**: Efficient data processing and formatting

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

If you encounter any issues:
1. Check the error messages for helpful hints
2. Verify your Reddit API credentials
3. Ensure all dependencies are installed
4. Check the MCP client configuration

## 🔄 Changelog

### v1.0.0
- Initial release
- 7 read-only Reddit tools
- Full MCP compatibility
- Cursor IDE integration
- Comprehensive error handling
- Rate limiting support

---

**Made with ❤️ for the Reddit and MCP communities**
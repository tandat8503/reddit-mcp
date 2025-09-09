"""
Configuration management for MCP Reddit Server
"""

import os
from typing import List
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class Config:
    """Configuration class for Reddit API settings"""
    
    def __init__(self):
        self.reddit_client_id = self._get_env("REDDIT_CLIENT_ID", "")
        self.reddit_client_secret = self._get_env("REDDIT_CLIENT_SECRET", "")
        self.reddit_user_agent = self._get_env(
            "REDDIT_USER_AGENT", 
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        )
        self.reddit_redirect_uri = self._get_env("REDDIT_REDIRECT_URI", "http://localhost:8080")
        self.reddit_oauth_scopes = self._get_env("REDDIT_OAUTH_SCOPES", "read").split()
        self.timeout_seconds = int(self._get_env("TIMEOUT_SECONDS", "30"))
        
        # Validate required settings
        if not self.reddit_client_id:
            raise ValueError("REDDIT_CLIENT_ID is required")
        if not self.reddit_client_secret:
            raise ValueError("REDDIT_CLIENT_SECRET is required")
    
    def _get_env(self, key: str, default: str = "") -> str:
        """Get environment variable with default value"""
        return os.getenv(key, default)


# Global config instance
config = Config()

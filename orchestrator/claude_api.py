#!/usr/bin/env python3
"""
Claude API Client for Orchestrator
Provides interface to communicate with Claude via Anthropic API or AWS Bedrock
"""

import os
import json
from typing import Optional, Dict, Any


class ClaudeAPI:
    """Client for Claude AI via Anthropic API or AWS Bedrock"""

    def __init__(self, default_cwd: Optional[str] = None):
        """
        Initialize Claude API client

        Args:
            default_cwd: Default working directory (for context, not used in API calls)
        """
        self.default_cwd = default_cwd
        self.use_bedrock = os.environ.get("USE_BEDROCK", "0") == "1" or \
                          os.environ.get("CLAUDE_CODE_USE_BEDROCK", "0") == "1"

        if self.use_bedrock:
            self._init_bedrock()
        else:
            self._init_anthropic()

    def _init_anthropic(self):
        """Initialize Anthropic API client"""
        try:
            import anthropic
            api_key = os.environ.get("ANTHROPIC_API_KEY")
            if not api_key:
                raise ValueError("ANTHROPIC_API_KEY environment variable not set")
            self.client = anthropic.Anthropic(api_key=api_key)
            self.model = "claude-sonnet-4-5-20250929"
        except ImportError:
            raise ImportError("anthropic package not installed. Run: pip install anthropic")

    def _init_bedrock(self):
        """Initialize AWS Bedrock client"""
        try:
            import boto3
            region = os.environ.get("BEDROCK_REGION", "eu-central-1")
            self.model = os.environ.get("BEDROCK_MODEL", "global.anthropic.claude-sonnet-4-5-20250929-v1:0")

            # Create Bedrock Runtime client
            self.client = boto3.client(
                service_name='bedrock-runtime',
                region_name=region,
                aws_access_key_id=os.environ.get("AWS_ACCESS_KEY_ID"),
                aws_secret_access_key=os.environ.get("AWS_SECRET_ACCESS_KEY"),
                aws_session_token=os.environ.get("AWS_SESSION_TOKEN")
            )
        except ImportError:
            raise ImportError("boto3 package not installed. Run: pip install boto3")

    def query(self, prompt: str, cwd: Optional[str] = None, timeout: int = 600) -> Dict[str, Any]:
        """
        Send a query to Claude

        Args:
            prompt: The prompt to send
            cwd: Working directory (for context only)
            timeout: Request timeout in seconds (not fully implemented)

        Returns:
            Dict with 'response' and 'success' keys
        """
        try:
            if self.use_bedrock:
                return self._query_bedrock(prompt)
            else:
                return self._query_anthropic(prompt)
        except Exception as e:
            return {
                "response": str(e),
                "success": False,
                "error": str(e)
            }

    def _query_anthropic(self, prompt: str) -> Dict[str, Any]:
        """Query Claude via Anthropic API"""
        try:
            message = self.client.messages.create(
                model=self.model,
                max_tokens=4096,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )

            response_text = ""
            for content in message.content:
                if hasattr(content, 'text'):
                    response_text += content.text

            return {
                "response": response_text,
                "success": True
            }
        except Exception as e:
            return {
                "response": str(e),
                "success": False,
                "error": str(e)
            }

    def _query_bedrock(self, prompt: str) -> Dict[str, Any]:
        """Query Claude via AWS Bedrock"""
        try:
            # Prepare request body for Bedrock
            request_body = {
                "anthropic_version": "bedrock-2023-05-31",
                "max_tokens": 4096,
                "messages": [
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            }

            # Invoke model
            response = self.client.invoke_model(
                modelId=self.model,
                body=json.dumps(request_body)
            )

            # Parse response
            response_body = json.loads(response['body'].read())
            response_text = ""
            for content in response_body.get('content', []):
                if content.get('type') == 'text':
                    response_text += content.get('text', '')

            return {
                "response": response_text,
                "success": True
            }
        except Exception as e:
            return {
                "response": str(e),
                "success": False,
                "error": str(e)
            }

    def health_check(self) -> bool:
        """Check if Claude API is available"""
        try:
            if self.use_bedrock:
                # Check if AWS credentials are set
                return bool(os.environ.get("AWS_ACCESS_KEY_ID") and
                          os.environ.get("AWS_SECRET_ACCESS_KEY"))
            else:
                # Check if Anthropic API key is set
                return bool(os.environ.get("ANTHROPIC_API_KEY"))
        except Exception:
            return False

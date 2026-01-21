#!/usr/bin/env python3
"""
Claude Code Client for Orchestrator
Provides interface to communicate with Claude Code CLI directly
"""

import subprocess
import shutil
from typing import Optional, Dict, Any


class ClaudeAPI:
    """Client for Claude Code CLI"""

    def __init__(self, default_cwd: Optional[str] = None):
        """
        Initialize Claude Code client

        Args:
            default_cwd: Default working directory for Claude operations
        """
        self.default_cwd = default_cwd

    def query(self, prompt: str, cwd: Optional[str] = None, timeout: int = 600) -> Dict[str, Any]:
        """
        Send a query to Claude Code CLI

        Args:
            prompt: The prompt to send
            cwd: Working directory (overrides default)
            timeout: Request timeout in seconds

        Returns:
            Dict with 'response' and 'success' keys
        """
        working_dir = cwd or self.default_cwd

        try:
            # Call Claude Code CLI directly
            result = subprocess.run(
                [
                    "claude",
                    "--dangerously-skip-permissions",
                    "--print",
                    "-p", prompt
                ],
                cwd=working_dir,
                capture_output=True,
                text=True,
                timeout=timeout
            )

            return {
                "response": result.stdout,
                "success": result.returncode == 0
            }

        except subprocess.TimeoutExpired:
            return {
                "response": "Claude Code CLI timeout",
                "success": False
            }
        except Exception as e:
            return {
                "response": str(e),
                "success": False
            }

    def health_check(self) -> bool:
        """Check if Claude Code CLI is available"""
        try:
            # Check if 'claude' command exists
            return shutil.which("claude") is not None
        except Exception:
            return False

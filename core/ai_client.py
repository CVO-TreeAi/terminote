"""
OpenRouter AI client for TermiNote v5
Handles communication with OpenRouter API for various AI models.
"""

import os
import openai
from typing import Dict, List, Optional, Generator
from rich.console import Console
from rich.spinner import Spinner
import time

from .config_manager import ConfigManager
from .error_handler import APIError, error_handler, safe_execute

console = Console()

class OpenRouterClient:
    """Client for interacting with OpenRouter API."""
    
    def __init__(self):
        self.config = ConfigManager()
        self.api_key = self.config.get_api_key()
        
        if not self.api_key:
            console.print("[red]❌ No OpenRouter API key found. Run 'terminote setup' first.[/red]")
            return
        
        # Configure OpenAI client to use OpenRouter
        self.client = openai.OpenAI(
            api_key=self.api_key,
            base_url="https://openrouter.ai/api/v1"
        )
    
    def chat_completion(
        self, 
        messages: List[Dict[str, str]], 
        model: Optional[str] = None,
        stream: bool = True,
        task: str = 'default'
    ) -> Generator[str, None, None] or str:
        """
        Generate chat completion using specified model.
        
        Args:
            messages: List of message dictionaries with 'role' and 'content'
            model: Model to use (if None, uses task-specific default)
            stream: Whether to stream response
            task: Task type for model selection ('writing', 'coding', 'quick')
        """
        if not self.api_key:
            yield "❌ API key not configured. Run 'terminote setup' first."
            return
        
        # Get model for task
        if not model:
            model = self.config.get_model(task)
        
        try:
            with console.status(f"[cyan]Thinking with {model}...", spinner="dots"):
                response = self.client.chat.completions.create(
                    model=model,
                    messages=messages,
                    max_tokens=self.config.get_preference('max_tokens'),
                    temperature=self.config.get_preference('temperature'),
                    stream=stream
                )
            
            if stream:
                for chunk in response:
                    if chunk.choices[0].delta.content:
                        yield chunk.choices[0].delta.content
            else:
                return response.choices[0].message.content
                
        except Exception as e:
            # Use centralized error handling
            api_error = APIError(f"Error calling {model}: {str(e)}")
            error_handler.handle_error(
                api_error, 
                context="AI Chat Completion",
                user_message=f"Failed to get response from AI model {model}"
            )
            error_msg = f"❌ Error calling {model}: {str(e)}"
            if stream:
                yield error_msg
            else:
                return error_msg
    
    def get_writing_suggestions(self, content: str, context: str = "") -> Generator[str, None, None]:
        """Get AI suggestions for improving writing."""
        messages = [
            {
                "role": "system",
                "content": """You are NEO, an expert writing assistant living in TermiNote. Provide helpful suggestions to improve the user's writing. Focus on:
                - Clarity and conciseness
                - Flow and structure
                - Grammar and style
                - Engagement and impact
                
                Be constructive and specific in your feedback. You're not just an AI - you're NEO, here to help make their writing amazing."""
            },
            {
                "role": "user", 
                "content": f"Context: {context}\n\nContent to review:\n{content}\n\nPlease provide suggestions for improvement:"
            }
        ]
        
        yield from self.chat_completion(messages, task='writing')
    
    def continue_writing(self, content: str, direction: str = "") -> Generator[str, None, None]:
        """Continue writing based on existing content."""
        messages = [
            {
                "role": "system",
                "content": """You are NEO, a creative writing assistant living in TermiNote. Continue the user's writing in a natural, engaging way that maintains their voice and style. Pay attention to:
                - Tone and voice consistency
                - Natural flow and transitions
                - Narrative or argumentative structure
                - The user's apparent intent and direction
                
                You're NEO - make this continuation flow seamlessly with their work."""
            },
            {
                "role": "user",
                "content": f"Please continue this writing:\n\n{content}\n\n{f'Direction: {direction}' if direction else ''}"
            }
        ]
        
        yield from self.chat_completion(messages, task='writing')
    
    def generate_outline(self, topic: str, type_doc: str = "article") -> Generator[str, None, None]:
        """Generate an outline for a document."""
        messages = [
            {
                "role": "system",
                "content": f"""You are an expert content strategist. Create a detailed, well-structured outline for a {type_doc}. Include:
                - Clear hierarchical structure
                - Logical flow of ideas
                - Key points and sub-points
                - Estimated word counts for sections
                
                Format the outline clearly with proper headings and bullet points."""
            },
            {
                "role": "user",
                "content": f"Create an outline for a {type_doc} about: {topic}"
            }
        ]
        
        yield from self.chat_completion(messages, task='writing')
    
    def brainstorm_ideas(self, topic: str, num_ideas: int = 10) -> Generator[str, None, None]:
        """Brainstorm ideas on a given topic."""
        messages = [
            {
                "role": "system", 
                "content": """You are a creative brainstorming assistant. Generate diverse, innovative ideas that are:
                - Creative and original
                - Practical and actionable
                - Varied in approach and perspective
                - Clearly explained with brief descriptions"""
            },
            {
                "role": "user",
                "content": f"Brainstorm {num_ideas} ideas related to: {topic}"
            }
        ]
        
        yield from self.chat_completion(messages, task='writing')
    
    def develop_project_plan(self, project_description: str) -> Generator[str, None, None]:
        """Generate a detailed project development plan."""
        messages = [
            {
                "role": "system",
                "content": """You are an expert project manager and software architect. Create a comprehensive development plan that includes:
                - Project overview and objectives
                - Technical requirements and architecture
                - Development phases and milestones
                - Resource requirements
                - Risk assessment and mitigation
                - Timeline estimates
                
                Format as a professional project plan with clear sections."""
            },
            {
                "role": "user",
                "content": f"Create a development plan for: {project_description}"
            }
        ]
        
        yield from self.chat_completion(messages, task='coding')
    
    def review_code(self, code: str, language: str = "") -> Generator[str, None, None]:
        """Review code and provide suggestions."""
        messages = [
            {
                "role": "system",
                "content": """You are an expert code reviewer. Analyze the provided code and give feedback on:
                - Code quality and best practices
                - Potential bugs or issues
                - Performance optimizations
                - Security considerations
                - Readability and maintainability
                
                Provide specific, actionable suggestions."""
            },
            {
                "role": "user",
                "content": f"Please review this {language} code:\n\n```{language}\n{code}\n```"
            }
        ]
        
        yield from self.chat_completion(messages, task='coding')
    
    def explain_concept(self, concept: str, level: str = "intermediate") -> Generator[str, None, None]:
        """Explain a concept at the specified level."""
        messages = [
            {
                "role": "system",
                "content": f"""You are an expert educator. Explain concepts clearly at a {level} level. Include:
                - Clear, accessible explanations
                - Relevant examples and analogies
                - Key terminology definitions
                - Practical applications
                
                Adapt your language and depth to the specified level."""
            },
            {
                "role": "user",
                "content": f"Explain this concept at a {level} level: {concept}"
            }
        ]
        
        yield from self.chat_completion(messages, task='quick')
    
    def test_connection(self) -> bool:
        """Test if the API connection is working."""
        if not self.api_key:
            return False
        
        try:
            # Simple test request
            response = self.client.chat.completions.create(
                model=self.config.get_model('quick'),
                messages=[{"role": "user", "content": "Hello"}],
                max_tokens=10
            )
            return True
        except Exception as e:
            # Use centralized error handling
            api_error = APIError(f"Connection test failed: {str(e)}")
            error_handler.handle_error(
                api_error, 
                context="API Connection Test",
                user_message="Failed to connect to OpenRouter API. Check your internet connection and API key."
            )
            return False 
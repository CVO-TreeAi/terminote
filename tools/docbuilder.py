"""
Document builder for TermiNote v5
Generates various types of documentation using AI.
"""

from rich.console import Console
from rich.panel import Panel
from rich.live import Live
from rich.markdown import Markdown
from rich.prompt import Prompt, Confirm
from pathlib import Path
import os

console = Console()

class DocBuilder:
    """Builds documentation using AI assistance."""
    
    def __init__(self):
        from core.ai_client import OpenRouterClient
        self.ai_client = OpenRouterClient()
    
    def generate_document(self, doc_type: str, output_path: str = None):
        """Generate a document of the specified type."""
        generators = {
            'readme': self._generate_readme,
            'spec': self._generate_spec,
            'api-docs': self._generate_api_docs,
            'guide': self._generate_guide
        }
        
        if doc_type not in generators:
            console.print(f"[red]Unknown document type: {doc_type}[/red]")
            console.print(f"Available types: {', '.join(generators.keys())}")
            return
        
        generator = generators[doc_type]
        content = generator()
        
        if content and output_path:
            self._save_document(content, output_path)
    
    def _generate_readme(self) -> str:
        """Generate a README file."""
        project_name = Prompt.ask("Project name")
        description = Prompt.ask("Brief description")
        tech_stack = Prompt.ask("Technology stack (optional)", default="")
        
        prompt = f"""Generate a comprehensive README.md file for a project called "{project_name}".
        
Project description: {description}
Technology stack: {tech_stack}

Include the following sections:
- Project title and description
- Features/capabilities
- Installation instructions
- Usage examples
- Configuration
- Contributing guidelines
- License information

Make it professional, clear, and well-formatted in Markdown."""
        
        return self._generate_with_ai(prompt, "README Generation")
    
    def _generate_spec(self) -> str:
        """Generate a technical specification."""
        project_name = Prompt.ask("Project/Feature name")
        requirements = Prompt.ask("Key requirements or goals")
        constraints = Prompt.ask("Technical constraints (optional)", default="")
        
        prompt = f"""Generate a detailed technical specification for "{project_name}".
        
Requirements: {requirements}
Constraints: {constraints}

Include these sections:
- Overview and objectives
- Functional requirements
- Technical requirements
- System architecture
- Data models/schemas
- API specifications (if applicable)
- Security considerations
- Testing strategy
- Implementation timeline
- Risk assessment

Format as a professional technical specification document."""
        
        return self._generate_with_ai(prompt, "Technical Specification")
    
    def _generate_api_docs(self) -> str:
        """Generate API documentation."""
        api_name = Prompt.ask("API name")
        base_url = Prompt.ask("Base URL (optional)", default="")
        endpoints = Prompt.ask("Key endpoints or functionality")
        
        prompt = f"""Generate comprehensive API documentation for "{api_name}".
        
Base URL: {base_url}
Key functionality: {endpoints}

Include:
- API overview
- Authentication methods
- Base URL and versioning
- Endpoint documentation with:
  - HTTP methods
  - Request/response schemas
  - Example requests and responses
  - Error codes and handling
- Rate limiting
- SDKs and client libraries
- Testing and development guides

Format as professional API documentation."""
        
        return self._generate_with_ai(prompt, "API Documentation")
    
    def _generate_guide(self) -> str:
        """Generate a user guide."""
        guide_topic = Prompt.ask("Guide topic/title")
        audience = Prompt.ask("Target audience", default="general users")
        key_tasks = Prompt.ask("Key tasks or workflows to cover")
        
        prompt = f"""Generate a comprehensive user guide for "{guide_topic}".
        
Target audience: {audience}
Key tasks: {key_tasks}

Include:
- Introduction and overview
- Getting started section
- Step-by-step tutorials for main tasks
- Best practices and tips
- Troubleshooting section
- FAQ
- Glossary of terms
- Additional resources

Write in a clear, friendly tone appropriate for the target audience."""
        
        return self._generate_with_ai(prompt, "User Guide")
    
    def _generate_with_ai(self, prompt: str, title: str) -> str:
        """Generate content using AI."""
        console.print(f"[cyan]🤖 Generating {title}...[/cyan]")
        
        messages = [
            {
                "role": "system",
                "content": """You are an expert technical writer. Create high-quality, professional documentation that is:
                - Clear and well-structured
                - Comprehensive but concise
                - Properly formatted in Markdown
                - Includes relevant examples
                - Follows documentation best practices"""
            },
            {
                "role": "user",
                "content": prompt
            }
        ]
        
        response_text = ""
        with Live(console=console, refresh_per_second=4) as live:
            for chunk in self.ai_client.chat_completion(messages, task='writing'):
                response_text += chunk
                live.update(Panel(
                    Markdown(response_text),
                    title=title
                ))
        
        return response_text
    
    def _save_document(self, content: str, output_path: str):
        """Save document to file."""
        try:
            # Ensure directory exists
            Path(output_path).parent.mkdir(parents=True, exist_ok=True)
            
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            console.print(f"[green]✅ Document saved to: {output_path}[/green]")
            
        except Exception as e:
            console.print(f"[red]❌ Error saving document: {e}[/red]")

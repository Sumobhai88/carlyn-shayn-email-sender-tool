import re
from typing import Dict, Any

class TemplateRenderer:
    """
    A reusable service for rendering email templates with personalization variables.
    Supports variables like {{first_name}}, {{last_name}}, {{email}}.
    """

    @staticmethod
    def render(template_content: str, variables: Dict[str, Any]) -> str:
        """
        Renders a template string by replacing {variable_name} or {{variable_name}} with values from the variables dictionary.
        
        Args:
            template_content: The template string with {variable} or {{variable}} placeholders.
            variables: A dictionary containing the values for the variables.
            
        Returns:
            The rendered string with variables replaced.
        """
        if not template_content:
            return ""

        # Function to replace the matched variable with its value
        def replace_var(match):
            key = match.group(1).strip()
            value = variables.get(key)
            # Handle missing values safely by defaulting to an empty string
            if value is None:
                return ""
            return str(value)

        # First handle {{variable}} format
        rendered_content = re.sub(r'\{\{(.*?)\}\}', replace_var, template_content)
        # Then handle {variable} format
        rendered_content = re.sub(r'\{(first_name|last_name|email|phone|company)\}', replace_var, rendered_content)
        return rendered_content

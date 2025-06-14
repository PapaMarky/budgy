"""
Template for generating pygame_gui panel classes from JSON layouts.

This template generates clean, well-formatted Python code that follows
the same patterns used in the budgy codebase.
"""

# Template variables available:
# - class_name: Name of the generated class
# - base_class: Base class to inherit from (UIPanel, GuiApp, etc.)
# - imports: Set of required imports
# - constants: Dictionary of constants used
# - components: List of Component objects
# - metadata: Layout metadata

PANEL_TEMPLATE = '''"""
{description}

Generated from layout: {source_file}
"""

{imports}

{constants}

class {class_name}({base_class}):
    """
    {class_description}
    
    This class was generated from a JSON layout specification.
    """
    
{class_constants}
    
    def __init__(self{init_params}):
        """Initialize the {class_name}"""
{init_setup}
        super().__init__({super_args})
        
        # Create UI components
{component_creation}
        
{post_init}

{component_methods}
'''

IMPORT_TEMPLATE = '''import pygame
from pygame_gui.elements import {ui_elements}
from pygame_gui.core import ObjectID
{additional_imports}'''

COMPONENT_TEMPLATE = '''        # {comment}
        {variable_name} = {component_type}(
            {args}
        )'''

PROPERTY_TEMPLATE = '''    @property
    def {property_name}(self):
        """Get {property_description}"""
        return self.{variable_name}'''

METHOD_TEMPLATE = '''    def {method_name}(self{params}):
        """
        {method_description}
        """
{method_body}'''
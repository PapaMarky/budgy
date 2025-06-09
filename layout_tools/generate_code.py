#!/usr/bin/env python3
"""
Code Generator for pygame_gui Layout

This tool generates Python code from JSON layout descriptions,
creating clean, well-formatted pygame_gui components.
"""

import argparse
import re
from pathlib import Path
from typing import Dict, List, Set, Optional, Any
from dataclasses import dataclass

from layout_schema import Layout, Component, Rect, Anchors


@dataclass
class GenerationContext:
    """Context for code generation"""
    class_name: str
    base_class: str
    imports: Set[str]
    constants: Dict[str, Any]
    variable_names: Dict[str, str]  # component_id -> variable_name
    init_params: List[str]
    super_args: List[str]


class CodeGenerator:
    """Generates Python code from layout specifications"""
    
    def __init__(self):
        self.ui_element_imports = {
            'UIPanel', 'UILabel', 'UIButton', 'UIDropDownMenu', 'UIProgressBar',
            'UITextEntryLine', 'UISelectionList', 'UIScrollingContainer',
            'UIVerticalScrollBar', 'UIHorizontalScrollBar', 'UIImage',
            'UITextBox', 'UIWindow'
        }
        
    def generate_code(self, layout: Layout, class_name: str, 
                     output_path: Optional[Path] = None) -> str:
        """Generate Python code from layout"""
        
        # Build generation context
        context = self._build_context(layout, class_name)
        
        # Generate code sections
        imports = self._generate_imports(context)
        constants = self._generate_constants(context)
        class_def = self._generate_class(layout, context)
        
        # Combine into final code
        code = f"{imports}\n\n{constants}\n\n{class_def}"
        
        # Format and clean up
        code = self._format_code(code)
        
        # Write to file if specified
        if output_path:
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(code)
        
        return code
    
    def _build_context(self, layout: Layout, class_name: str) -> GenerationContext:
        """Build generation context from layout"""
        
        # Determine base class
        root_components = [c for c in layout.components.values() if not c.container]
        if root_components:
            base_class = root_components[0].type
        else:
            base_class = "UIPanel"
        
        # Handle special base classes
        if base_class == "GuiApp":
            base_class = "GuiApp"
        
        # Collect imports needed
        imports = set()
        for component in layout.components.values():
            if component.type in self.ui_element_imports:
                imports.add(component.type)
        
        # Generate variable names
        variable_names = {}
        for comp_id, component in layout.components.items():
            if comp_id == class_name:
                # Root component uses 'self'
                variable_names[comp_id] = "self"
            else:
                # Generate clean variable name
                var_name = self._generate_variable_name(comp_id, component)
                variable_names[comp_id] = var_name
        
        # Standard init parameters
        init_params = []
        super_args = []
        
        if base_class == "GuiApp":
            init_params = ["size=(1280, 960)"]
            super_args = ["size"]
        else:
            init_params = ["*args", "**kwargs"]
            super_args = ["*args", "**kwargs"]
        
        return GenerationContext(
            class_name=class_name,
            base_class=base_class,
            imports=imports,
            constants=layout.metadata.constants,
            variable_names=variable_names,
            init_params=init_params,
            super_args=super_args
        )
    
    def _generate_variable_name(self, comp_id: str, component: Component) -> str:
        """Generate clean variable name from component ID"""
        # Remove class prefix if present
        name = comp_id
        if '_' in name:
            parts = name.split('_')
            if len(parts) > 1:
                name = '_'.join(parts[1:])  # Remove first part (likely class name)
        
        # Convert to snake_case and ensure it's a valid Python identifier
        name = re.sub(r'[^a-zA-Z0-9_]', '_', name)
        name = re.sub(r'_+', '_', name)  # Remove duplicate underscores
        name = name.strip('_')
        
        # Ensure it doesn't start with a number
        if name and name[0].isdigit():
            name = f"_{name}"
        
        # Use component type if name is empty or invalid
        if not name or not name.isidentifier():
            type_name = component.type.lower()
            if type_name.startswith('ui'):
                type_name = type_name[2:]  # Remove 'ui' prefix
            name = type_name
        
        return name
    
    def _generate_imports(self, context: GenerationContext) -> str:
        """Generate import statements"""
        lines = ["import pygame"]
        
        # pygame_gui imports
        if context.imports:
            ui_imports = ", ".join(sorted(context.imports))
            lines.append(f"from pygame_gui.elements import {ui_imports}")
        
        lines.append("from pygame_gui.core import ObjectID")
        
        # Special imports for base classes
        if context.base_class == "GuiApp":
            lines.append("from pygame_gui_extras.app import GuiApp")
        
        return "\n".join(lines)
    
    def _generate_constants(self, context: GenerationContext) -> str:
        """Generate constants section"""
        if not context.constants:
            return ""
        
        lines = ["# Layout constants"]
        for name, value in sorted(context.constants.items()):
            if isinstance(value, str):
                lines.append(f'{name} = "{value}"')
            else:
                lines.append(f"{name} = {value}")
        
        return "\n".join(lines)
    
    def _generate_class(self, layout: Layout, context: GenerationContext) -> str:
        """Generate class definition"""
        lines = []
        
        # Class definition
        class_doc = f"Generated from {layout.metadata.source_file or 'JSON layout'}"
        lines.extend([
            f"class {context.class_name}({context.base_class}):",
            f'    """',
            f"    {class_doc}",
            f'    """'
        ])
        
        # Class constants (if any component-specific constants)
        class_constants = self._generate_class_constants(layout, context)
        if class_constants:
            lines.append("")
            lines.extend(class_constants)
        
        # __init__ method
        init_method = self._generate_init_method(layout, context)
        lines.append("")
        lines.extend(init_method)
        
        # Component property methods
        property_methods = self._generate_property_methods(layout, context)
        if property_methods:
            lines.append("")
            lines.extend(property_methods)
        
        return "\n".join(lines)
    
    def _generate_class_constants(self, layout: Layout, context: GenerationContext) -> List[str]:
        """Generate class-level constants"""
        lines = []
        
        # Extract unique widths, heights for constants
        widths = set()
        heights = set()
        
        for component in layout.components.values():
            if component.rect.w > 0:
                widths.add(component.rect.w)
            if component.rect.h > 0:
                heights.add(component.rect.h)
        
        # Generate meaningful constants for common values
        common_widths = {200: "DROPDOWN_WIDTH", 175: "LABEL_WIDTH", 150: "BUTTON_WIDTH"}
        common_heights = {25: "BUTTON_HEIGHT", 30: "INPUT_HEIGHT"}
        
        for width in sorted(widths):
            if width in common_widths:
                lines.append(f"    {common_widths[width]} = {width}")
        
        for height in sorted(heights):
            if height in common_heights:
                lines.append(f"    {common_heights[height]} = {height}")
        
        return lines
    
    def _generate_init_method(self, layout: Layout, context: GenerationContext) -> List[str]:
        """Generate __init__ method"""
        lines = []
        
        # Method signature
        params = ", ".join(context.init_params)
        if params:
            lines.append(f"    def __init__(self, {params}):")
        else:
            lines.append("    def __init__(self):")
        
        lines.append(f'        """Initialize {context.class_name}"""')
        
        # Super call
        super_args = ", ".join(context.super_args)
        lines.append(f"        super().__init__({super_args})")
        lines.append("")
        
        # Component creation
        components = self._sort_components_for_creation(layout)
        
        for component in components:
            if component.id == context.class_name:
                continue  # Skip root component (it's 'self')
            
            component_lines = self._generate_component_creation(component, context)
            lines.extend(component_lines)
            lines.append("")
        
        return lines
    
    def _sort_components_for_creation(self, layout: Layout) -> List[Component]:
        """Sort components in creation order (containers first)"""
        components = list(layout.components.values())
        
        def sort_key(comp: Component) -> tuple:
            # Root components first, then by whether they're containers, then by position
            is_root = not comp.container
            is_container = len(comp.children) > 0
            return (not is_root, not is_container, comp.rect.y, comp.rect.x)
        
        return sorted(components, key=sort_key)
    
    def _generate_component_creation(self, component: Component, context: GenerationContext) -> List[str]:
        """Generate component creation code"""
        lines = []
        var_name = context.variable_names[component.id]
        
        # Comment
        comment = f"Create {component.type}"
        if component.text:
            comment += f': "{component.text}"'
        lines.append(f"        # {comment}")
        
        # Component creation
        args = self._generate_component_args(component, context)
        
        lines.append(f"        self._{var_name} = {component.type}(")
        for arg in args[:-1]:
            lines.append(f"            {arg},")
        if args:
            lines.append(f"            {args[-1]}")
        lines.append("        )")
        
        return lines
    
    def _generate_component_args(self, component: Component, context: GenerationContext) -> List[str]:
        """Generate arguments for component constructor"""
        args = []
        
        # Rect argument
        rect = component.rect
        args.append(f"pygame.Rect({rect.x}, {rect.y}, {rect.w}, {rect.h})")
        
        # Text argument (for components that take text)
        text_components = {'UILabel', 'UIButton', 'UIDropDownMenu', 'UITextEntryLine'}
        if component.type in text_components and component.text:
            args.append(f'"{component.text}"')
        elif component.type == 'UIDropDownMenu':
            # Dropdown needs option list and default
            if component.text:
                args.append(f'["{component.text}", "Option 2", "Option 3"]')
                args.append(f'"{component.text}"')
            else:
                args.append('["Option 1", "Option 2", "Option 3"]')
                args.append('"Option 1"')
        
        # Manager argument (common to most components)
        if component.type != 'GuiApp':
            args.append("manager=self.ui_manager")
        
        # Container argument
        if component.container and component.container in context.variable_names:
            container_var = context.variable_names[component.container]
            if container_var == "self":
                args.append("container=self")
            else:
                args.append(f"container=self._{container_var}")
        
        # Anchors argument
        anchors = component.anchors
        if not self._is_default_anchors(anchors):
            anchors_dict = self._format_anchors_dict(anchors)
            args.append(f"anchors={anchors_dict}")
        
        # Object ID argument
        if component.styling.object_id:
            args.append(f'object_id=ObjectID(class_id="{component.styling.object_id}")')
        
        return args
    
    def _is_default_anchors(self, anchors: Anchors) -> bool:
        """Check if anchors are the default values"""
        return (anchors.top == "top" and anchors.left == "left" and 
                anchors.bottom == "top" and anchors.right == "left")
    
    def _format_anchors_dict(self, anchors: Anchors) -> str:
        """Format anchors as a Python dictionary"""
        items = []
        for key, value in anchors.to_dict().items():
            items.append(f"'{key}': '{value}'")
        return "{" + ", ".join(items) + "}"
    
    def _generate_property_methods(self, layout: Layout, context: GenerationContext) -> List[str]:
        """Generate property methods for accessing components"""
        lines = []
        
        # Generate properties for non-root components
        for comp_id, component in layout.components.items():
            if comp_id == context.class_name:
                continue
            
            var_name = context.variable_names[comp_id]
            
            # Use different property name if it would conflict with variable name
            prop_name = f"get_{var_name}" if var_name in ["panel", "self"] else var_name
            
            lines.extend([
                f"    @property",
                f"    def {prop_name}(self):",
                f'        """Access the {component.type} component"""',
                f"        return self._{var_name}",  # Use private variable
                ""
            ])
        
        return lines[:-1] if lines else []  # Remove last empty line
    
    def _format_code(self, code: str) -> str:
        """Format and clean up generated code"""
        lines = code.split('\n')
        
        # Remove excessive blank lines
        formatted_lines = []
        prev_blank = False
        
        for line in lines:
            is_blank = not line.strip()
            
            if is_blank and prev_blank:
                continue  # Skip consecutive blank lines
            
            formatted_lines.append(line)
            prev_blank = is_blank
        
        # Ensure file ends with single newline
        while formatted_lines and not formatted_lines[-1].strip():
            formatted_lines.pop()
        formatted_lines.append("")
        
        return '\n'.join(formatted_lines)


def main():
    """Command line interface"""
    parser = argparse.ArgumentParser(description='Generate Python code from layout JSON')
    parser.add_argument('input', type=Path, help='Input JSON layout file')
    parser.add_argument('--output', '-o', type=Path, help='Output Python file')
    parser.add_argument('--class-name', '-c', type=str, help='Generated class name')
    parser.add_argument('--validate', action='store_true', help='Validate input layout')
    
    args = parser.parse_args()
    
    if not args.input.exists():
        print(f"Error: Input file {args.input} does not exist")
        return 1
    
    try:
        # Load layout
        layout = Layout.load_json(args.input)
        
        # Validate if requested
        if args.validate:
            issues = layout.validate()
            if issues:
                print("Layout validation issues:")
                for issue in issues:
                    print(f"  ⚠️  {issue}")
                print()
        
        # Determine class name
        class_name = args.class_name
        if not class_name:
            # Use filename or main component name
            class_name = args.input.stem.replace('_', '').title()
            if class_name.endswith('Panel'):
                pass  # Keep Panel suffix
            elif class_name.endswith('Dialog'):
                pass  # Keep Dialog suffix
            else:
                class_name += "Panel"
        
        # Determine output path
        output_path = args.output
        if not output_path:
            output_path = args.input.with_suffix('.py')
        
        # Generate code
        generator = CodeGenerator()
        code = generator.generate_code(layout, class_name, output_path)
        
        print(f"Generated class {class_name} with {len(layout.components)} components")
        print(f"Output: {output_path}")
        
        # Show code preview
        lines = code.split('\n')
        print("\nCode preview (first 20 lines):")
        print("-" * 50)
        for i, line in enumerate(lines[:20], 1):
            print(f"{i:2d}: {line}")
        if len(lines) > 20:
            print("...")
        
        return 0
        
    except Exception as e:
        print(f"Error: {e}")
        return 1


if __name__ == '__main__':
    exit(main())
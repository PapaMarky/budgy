#!/usr/bin/env python3
"""
Code Analyzer for pygame_gui Layout Extraction

This tool analyzes Python files containing pygame_gui components and extracts
their layout structure into standardized JSON format.
"""

import ast
import argparse
import re
from pathlib import Path
from typing import Dict, List, Any, Optional, Union, Set
from dataclasses import dataclass, field

from layout_schema import Layout, Component, Rect, Anchors, Styling, Metadata


@dataclass
class AnalysisContext:
    """Context information during AST analysis"""
    constants: Dict[str, Union[int, str]] = field(default_factory=dict)
    current_class: Optional[str] = None
    current_method: Optional[str] = None
    component_counter: int = 0
    self_attributes: Dict[str, str] = field(default_factory=dict)  # self.attr -> component_id
    imported_modules: Set[str] = field(default_factory=set)
    
    def get_unique_id(self, base_name: str) -> str:
        """Generate unique component ID"""
        if self.current_class:
            component_id = f"{self.current_class}_{base_name}"
        else:
            component_id = base_name
            
        # Handle duplicate IDs
        original_id = component_id
        counter = 1
        while component_id in self.self_attributes.values():
            component_id = f"{original_id}_{counter}"
            counter += 1
            
        return component_id


class PygameUIAnalyzer(ast.NodeVisitor):
    """AST visitor to analyze pygame_gui component creation"""
    
    def __init__(self, source_file: Path):
        self.source_file = source_file
        self.context = AnalysisContext()
        self.components: Dict[str, Component] = {}
        self.component_hierarchy: Dict[str, List[str]] = {}  # parent -> children
        
    def analyze(self, source_code: str) -> Layout:
        """Analyze source code and return Layout"""
        try:
            tree = ast.parse(source_code)
            self.visit(tree)
            
            # Build final layout
            layout = self._build_layout()
            return layout
            
        except SyntaxError as e:
            raise ValueError(f"Syntax error in {self.source_file}: {e}")
        except Exception as e:
            raise ValueError(f"Analysis error in {self.source_file}: {e}")
    
    def visit_Import(self, node):
        """Track imported modules"""
        for alias in node.names:
            self.context.imported_modules.add(alias.name)
        self.generic_visit(node)
    
    def visit_ImportFrom(self, node):
        """Track from imports"""
        if node.module:
            self.context.imported_modules.add(node.module)
            for alias in node.names:
                self.context.imported_modules.add(f"{node.module}.{alias.name}")
        self.generic_visit(node)
    
    def visit_ClassDef(self, node):
        """Track current class context and detect UI component classes"""
        old_class = self.context.current_class
        self.context.current_class = node.name
        
        # Check if class inherits from pygame_gui component
        base_component_type = self._extract_base_component_type(node)
        if base_component_type:
            # Create component for the class itself
            class_component = Component(
                id=node.name,
                type=base_component_type,
                rect=Rect(0, 0, 100, 100),  # Will be determined from constructor args
                anchors=Anchors("top", "left", "bottom", "right"),
                text="",
                styling=Styling()
            )
            self.components[node.name] = class_component
            # Map self references to this class component
            self.context.self_attributes[''] = node.name  # Empty string for bare 'self'
        
        self.generic_visit(node)
        self.context.current_class = old_class
    
    def visit_FunctionDef(self, node):
        """Track current method context"""
        old_method = self.context.current_method
        self.context.current_method = node.name
        self.generic_visit(node)
        self.context.current_method = old_method
        
    def visit_Assign(self, node):
        """Extract constants and component assignments"""
        # Extract constants (class-level and module-level assignments)
        if (len(node.targets) == 1 and 
            isinstance(node.targets[0], ast.Name) and
            isinstance(node.value, ast.Constant)):
            name = node.targets[0].id
            if isinstance(node.value.value, (int, str)):
                self.context.constants[name] = node.value.value
        
        # Also extract from imported constants
        if (len(node.targets) == 1 and 
            isinstance(node.targets[0], ast.Name) and
            isinstance(node.value, ast.Attribute)):
            # Handle patterns like: MARGIN = some_module.MARGIN
            if isinstance(node.value.value, ast.Name):
                name = node.targets[0].id
                # Use common defaults for known constants
                if name == 'MARGIN':
                    self.context.constants[name] = 2
                elif name == 'BUTTON_HEIGHT':
                    self.context.constants[name] = 25
        
        # Extract component assignments (self.attr = UIComponent(...))
        if (len(node.targets) == 1 and 
            isinstance(node.targets[0], ast.Attribute) and
            isinstance(node.targets[0].value, ast.Name) and
            node.targets[0].value.id == 'self' and
            isinstance(node.value, ast.Call)):
            
            attr_name = node.targets[0].attr
            component = self._parse_ui_component(node.value, attr_name)
            if component:
                self.components[component.id] = component
                self.context.self_attributes[attr_name] = component.id
        
        self.generic_visit(node)
    
    def _parse_ui_component(self, call_node: ast.Call, var_name: str) -> Optional[Component]:
        """Parse a pygame_gui component constructor call"""
        # Get component type from function name
        component_type = self._extract_component_type(call_node.func)
        if not component_type or not self._is_pygame_gui_component(component_type):
            return None
        
        # Generate unique component ID
        component_id = self.context.get_unique_id(var_name)
        
        # Extract constructor arguments
        rect = self._extract_rect(call_node.args)
        text = self._extract_text(call_node.args)
        anchors = self._extract_anchors(call_node.keywords)
        container = self._extract_container(call_node.keywords)
        object_id = self._extract_object_id(call_node.keywords)
        margins = self._extract_margins(call_node.keywords)
        
        # Build styling info
        styling = Styling(object_id=object_id)
        
        # Create component
        component = Component(
            id=component_id,
            type=component_type,
            rect=rect or Rect(0, 0, 100, 25),
            anchors=anchors or Anchors("top", "left", "top", "left"),
            container=container,
            text=text or "",
            styling=styling,
            margins=margins
        )
        
        return component
    
    def _extract_component_type(self, func_node: ast.AST) -> Optional[str]:
        """Extract component type from function call"""
        if isinstance(func_node, ast.Name):
            return func_node.id
        elif isinstance(func_node, ast.Attribute):
            return func_node.attr
        return None
    
    def _is_pygame_gui_component(self, type_name: str) -> bool:
        """Check if type name is a pygame_gui component"""
        pygame_gui_types = {
            'UIPanel', 'UILabel', 'UIButton', 'UIDropDownMenu', 'UIProgressBar',
            'UITextEntryLine', 'UISelectionList', 'UIScrollingContainer',
            'UIVerticalScrollBar', 'UIHorizontalScrollBar', 'UIImage',
            'UITextBox', 'UIWindow', 'UIFileDialog', 'UIColourPickerDialog',
            'GuiApp'  # pygame_gui_extras base class
        }
        return type_name in pygame_gui_types
    
    def _extract_rect(self, args: List[ast.AST]) -> Optional[Rect]:
        """Extract pygame.Rect from constructor arguments"""
        for arg in args:
            if isinstance(arg, ast.Call):
                # pygame.Rect(x, y, w, h)
                if self._is_rect_call(arg):
                    if len(arg.args) >= 4:
                        try:
                            x = self._eval_expression(arg.args[0])
                            y = self._eval_expression(arg.args[1])
                            w = self._eval_expression(arg.args[2])
                            h = self._eval_expression(arg.args[3])
                            return Rect(x, y, w, h)
                        except Exception as e:
                            # Fallback for complex expressions - try to extract basic numbers
                            x = self._extract_basic_number(arg.args[0])
                            y = self._extract_basic_number(arg.args[1])
                            w = self._extract_basic_number(arg.args[2])
                            h = self._extract_basic_number(arg.args[3])
                            return Rect(x, y, w, h)
            elif isinstance(arg, ast.Name):
                # Could be a variable holding a rect - try to find it
                var_name = arg.id
                if var_name.endswith('_rect') or var_name == 'rr':
                    # Common rect variable names - use placeholder
                    return Rect(0, 0, 200, 25)
        return None
    
    def _extract_basic_number(self, expr: ast.AST) -> int:
        """Extract number from expression, return sensible default if complex"""
        try:
            return self._eval_expression(expr)
        except:
            # Return defaults based on common patterns
            if isinstance(expr, ast.UnaryOp) and isinstance(expr.op, ast.USub):
                return -200  # Likely negative positioning
            return 0
    
    def _is_rect_call(self, call_node: ast.Call) -> bool:
        """Check if call is pygame.Rect construction"""
        if isinstance(call_node.func, ast.Attribute):
            if (isinstance(call_node.func.value, ast.Name) and 
                call_node.func.value.id == 'pygame' and 
                call_node.func.attr == 'Rect'):
                return True
        elif isinstance(call_node.func, ast.Name):
            if call_node.func.id == 'Rect':
                return True
        return False
    
    def _extract_text(self, args: List[ast.AST]) -> Optional[str]:
        """Extract text parameter from arguments"""
        for arg in args:
            if isinstance(arg, ast.Constant) and isinstance(arg.value, str):
                return arg.value
        return None
    
    def _extract_anchors(self, keywords: List[ast.keyword]) -> Optional[Anchors]:
        """Extract anchors dictionary from keyword arguments"""
        for kw in keywords:
            if kw.arg == 'anchors' and isinstance(kw.value, ast.Dict):
                anchors_dict = {}
                for k, v in zip(kw.value.keys, kw.value.values):
                    if isinstance(k, ast.Constant) and isinstance(v, ast.Constant):
                        anchors_dict[k.value] = v.value
                
                return Anchors(
                    top=anchors_dict.get('top', 'top'),
                    left=anchors_dict.get('left', 'left'),
                    bottom=anchors_dict.get('bottom', 'top'),
                    right=anchors_dict.get('right', 'left')
                )
        return None
    
    def _extract_container(self, keywords: List[ast.keyword]) -> Optional[str]:
        """Extract container reference"""
        for kw in keywords:
            if kw.arg == 'container':
                if isinstance(kw.value, ast.Name) and kw.value.id == 'self':
                    # Container is self (current class)
                    return self.context.current_class
                elif isinstance(kw.value, ast.Attribute):
                    # Container is self.some_component
                    if (isinstance(kw.value.value, ast.Name) and 
                        kw.value.value.id == 'self'):
                        attr_name = kw.value.attr
                        return self.context.self_attributes.get(attr_name)
                elif isinstance(kw.value, ast.Constant) and kw.value.value is None:
                    return None
        return None
    
    def _extract_base_component_type(self, class_node: ast.ClassDef) -> Optional[str]:
        """Extract pygame_gui component type from class bases"""
        for base in class_node.bases:
            if isinstance(base, ast.Name):
                base_name = base.id
                if self._is_pygame_gui_component(base_name):
                    return base_name
            elif isinstance(base, ast.Attribute):
                # Handle module.Component style bases
                base_name = base.attr
                if self._is_pygame_gui_component(base_name):
                    return base_name
        return None
    
    def _extract_object_id(self, keywords: List[ast.keyword]) -> Optional[str]:
        """Extract object_id information"""
        for kw in keywords:
            if kw.arg == 'object_id':
                if isinstance(kw.value, ast.Call):
                    # ObjectID(class_id='#something', object_id='@something')
                    return self._extract_object_id_from_call(kw.value)
        return None
    
    def _extract_object_id_from_call(self, call_node: ast.Call) -> Optional[str]:
        """Extract object_id from ObjectID() call"""
        parts = []
        for kw in call_node.keywords:
            if kw.arg in ['class_id', 'object_id'] and isinstance(kw.value, ast.Constant):
                parts.append(kw.value.value)
        return ' '.join(parts) if parts else None
    
    def _extract_margins(self, keywords: List[ast.keyword]) -> Optional[Dict[str, int]]:
        """Extract margins dictionary"""
        for kw in keywords:
            if kw.arg == 'margins' and isinstance(kw.value, ast.Dict):
                margins = {}
                for k, v in zip(kw.value.keys, kw.value.values):
                    if isinstance(k, ast.Constant) and isinstance(v, ast.Constant):
                        margins[k.value] = v.value
                return margins
        return None
    
    def _eval_expression(self, expr: ast.AST) -> int:
        """Evaluate simple expressions with constants"""
        if isinstance(expr, ast.Constant):
            return int(expr.value)
        elif isinstance(expr, ast.Name):
            return self.context.constants.get(expr.id, 0)
        elif isinstance(expr, ast.BinOp):
            left = self._eval_expression(expr.left)
            right = self._eval_expression(expr.right)
            if isinstance(expr.op, ast.Add):
                return left + right
            elif isinstance(expr.op, ast.Sub):
                return left - right
            elif isinstance(expr.op, ast.Mult):
                return left * right
            elif isinstance(expr.op, ast.Div):
                return int(left / right) if right != 0 else 0
        elif isinstance(expr, ast.UnaryOp) and isinstance(expr.op, ast.USub):
            return -self._eval_expression(expr.operand)
        
        # Fallback for complex expressions
        return 0
    
    def _build_layout(self) -> Layout:
        """Build final Layout from analyzed components"""
        # Create metadata
        metadata = Metadata(
            source_file=str(self.source_file),
            constants=self.context.constants,
            description=f"Layout extracted from {self.source_file.name}"
        )
        
        # Build component hierarchy
        self._build_component_hierarchy()
        
        # Update component children lists
        for parent_id, children_ids in self.component_hierarchy.items():
            if parent_id in self.components:
                self.components[parent_id].children = children_ids
        
        # Detect window size from components
        window_size = self._detect_window_size()
        if window_size:
            metadata.window_size = window_size
        
        return Layout(metadata=metadata, components=self.components)
    
    def _build_component_hierarchy(self):
        """Build parent-child relationships"""
        for component in self.components.values():
            if component.container and component.container in self.components:
                parent_id = component.container
                if parent_id not in self.component_hierarchy:
                    self.component_hierarchy[parent_id] = []
                self.component_hierarchy[parent_id].append(component.id)
    
    def _detect_window_size(self) -> Optional[List[int]]:
        """Try to detect window size from root components"""
        # Find components with no container (root level)
        root_components = [comp for comp in self.components.values() if not comp.container]
        
        if root_components:
            # Use the largest root component as window size estimate
            max_width = max(comp.rect.x + comp.rect.w for comp in root_components)
            max_height = max(comp.rect.y + comp.rect.h for comp in root_components)
            
            # Round to common window sizes
            common_widths = [800, 1024, 1280, 1366, 1440, 1920]
            common_heights = [600, 768, 960, 1024, 1080]
            
            width = min((w for w in common_widths if w >= max_width), default=max_width)
            height = min((h for h in common_heights if h >= max_height), default=max_height)
            
            return [width, height]
        
        return None


def analyze_file(file_path: Path) -> Layout:
    """Analyze a Python file and extract pygame_gui layout"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            source_code = f.read()
        
        analyzer = PygameUIAnalyzer(file_path)
        layout = analyzer.analyze(source_code)
        
        return layout
        
    except Exception as e:
        raise ValueError(f"Failed to analyze {file_path}: {e}")


def main():
    """Command line interface"""
    parser = argparse.ArgumentParser(description='Analyze pygame_gui layout from Python code')
    parser.add_argument('input', type=Path, help='Python file to analyze')
    parser.add_argument('--output', '-o', type=Path, help='Output JSON file (default: input.json)')
    parser.add_argument('--svg', action='store_true', help='Also generate SVG visualization')
    parser.add_argument('--validate', action='store_true', help='Validate extracted layout')
    
    args = parser.parse_args()
    
    if not args.input.exists():
        print(f"Error: File {args.input} does not exist")
        return 1
    
    if not args.output:
        args.output = args.input.with_suffix('.json')
    
    try:
        print(f"Analyzing {args.input}...")
        layout = analyze_file(args.input)
        
        if not layout.components:
            print("No pygame_gui components found")
            return 1
        
        print(f"Found {len(layout.components)} components:")
        for comp in layout.components.values():
            container_info = f" (in {comp.container})" if comp.container else " (root)"
            print(f"  - {comp.id} ({comp.type}){container_info}")
        
        # Save JSON
        layout.save_json(args.output)
        print(f"Saved layout: {args.output}")
        
        # Validate if requested
        if args.validate:
            issues = layout.validate()
            if issues:
                print("\nValidation issues:")
                for issue in issues:
                    print(f"  ⚠️  {issue}")
            else:
                print("✅ Layout validation passed")
        
        # Generate SVG if requested
        if args.svg:
            svg_path = args.output.with_suffix('.svg')
            try:
                from generate_svg import SVGGenerator
                generator = SVGGenerator(*layout.metadata.window_size)
                generator.generate_svg(layout, svg_path)
                print(f"Generated SVG: {svg_path}")
            except ImportError:
                print("Warning: Could not import SVG generator")
        
        return 0
        
    except Exception as e:
        print(f"Error: {e}")
        return 1


if __name__ == '__main__':
    exit(main())
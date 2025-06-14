#!/usr/bin/env python3
"""
SVG Layout Generator for pygame_gui Components

This tool analyzes Python files containing pygame_gui components and generates
SVG visualizations of the UI layout structure.

Usage:
    python layout_generator.py <python_file> [--output output.svg] [--width 1280] [--height 960]
"""

import ast
import re
import argparse
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from xml.etree.ElementTree import Element, SubElement, tostring
import xml.etree.ElementTree as ET


@dataclass
class Component:
    """Represents a pygame_gui UI component"""
    id: str
    type: str
    rect: Dict[str, int]  # x, y, width, height
    anchors: Dict[str, str]
    container: Optional[str]
    text: str
    object_id: str
    visible: bool = True
    children: List[str] = None
    margins: Dict[str, int] = None
    
    def __post_init__(self):
        if self.children is None:
            self.children = []
        if self.margins is None:
            self.margins = {"top": 0, "bottom": 0, "left": 0, "right": 0}


class PygameUIAnalyzer(ast.NodeVisitor):
    """AST visitor to analyze pygame_gui component creation"""
    
    def __init__(self):
        self.components: Dict[str, Component] = {}
        self.constants: Dict[str, int] = {}
        self.current_class = None
        self.component_counter = 0
        
    def visit_ClassDef(self, node):
        """Track current class context"""
        old_class = self.current_class
        self.current_class = node.name
        self.generic_visit(node)
        self.current_class = old_class
        
    def visit_Assign(self, node):
        """Extract constants and component assignments"""
        # Extract constants like BUTTON_WIDTH = 150
        if len(node.targets) == 1 and isinstance(node.targets[0], ast.Name):
            name = node.targets[0].id
            if isinstance(node.value, ast.Constant) and isinstance(node.value.value, int):
                self.constants[name] = node.value.value
                
        # Extract component assignments like self.label = UILabel(...)
        if (len(node.targets) == 1 and 
            isinstance(node.targets[0], ast.Attribute) and
            isinstance(node.targets[0].value, ast.Name) and
            node.targets[0].value.id == 'self'):
            
            attr_name = node.targets[0].attr
            if isinstance(node.value, ast.Call):
                component = self._parse_ui_component(node.value, attr_name)
                if component:
                    self.components[component.id] = component
                    
        self.generic_visit(node)
        
    def _parse_ui_component(self, call_node: ast.Call, var_name: str) -> Optional[Component]:
        """Parse a pygame_gui component constructor call"""
        if not isinstance(call_node.func, ast.Name):
            return None
            
        component_type = call_node.func.id
        if not component_type.startswith('UI'):
            return None
            
        # Generate unique ID
        component_id = f"{self.current_class}_{var_name}" if self.current_class else var_name
        
        # Extract arguments
        rect = self._extract_rect(call_node.args)
        text = self._extract_text(call_node.args)
        anchors = self._extract_anchors(call_node.keywords)
        container = self._extract_container(call_node.keywords)
        object_id = self._extract_object_id(call_node.keywords)
        
        return Component(
            id=component_id,
            type=component_type,
            rect=rect or {"x": 0, "y": 0, "width": 100, "height": 25},
            anchors=anchors or {},
            container=container,
            text=text or "",
            object_id=object_id or ""
        )
        
    def _extract_rect(self, args: List[ast.AST]) -> Optional[Dict[str, int]]:
        """Extract pygame.Rect from constructor arguments"""
        for arg in args:
            if isinstance(arg, ast.Call) and isinstance(arg.func, ast.Attribute):
                if (isinstance(arg.func.value, ast.Name) and 
                    arg.func.value.id == 'pygame' and 
                    arg.func.attr == 'Rect'):
                    if len(arg.args) >= 4:
                        try:
                            x = self._eval_expression(arg.args[0])
                            y = self._eval_expression(arg.args[1])
                            w = self._eval_expression(arg.args[2])
                            h = self._eval_expression(arg.args[3])
                            return {"x": x, "y": y, "width": w, "height": h}
                        except:
                            return {"x": 0, "y": 0, "width": 100, "height": 25}
        return None
        
    def _extract_text(self, args: List[ast.AST]) -> Optional[str]:
        """Extract text parameter from arguments"""
        for arg in args:
            if isinstance(arg, ast.Constant) and isinstance(arg.value, str):
                return arg.value
        return None
        
    def _extract_anchors(self, keywords: List[ast.keyword]) -> Optional[Dict[str, str]]:
        """Extract anchors dictionary from keyword arguments"""
        for kw in keywords:
            if kw.arg == 'anchors' and isinstance(kw.value, ast.Dict):
                anchors = {}
                for k, v in zip(kw.value.keys, kw.value.values):
                    if isinstance(k, ast.Constant) and isinstance(v, ast.Constant):
                        anchors[k.value] = v.value
                return anchors
        return None
        
    def _extract_container(self, keywords: List[ast.keyword]) -> Optional[str]:
        """Extract container reference"""
        for kw in keywords:
            if kw.arg == 'container':
                if isinstance(kw.value, ast.Name) and kw.value.id == 'self':
                    return self.current_class
                elif isinstance(kw.value, ast.Constant) and kw.value.value is None:
                    return None
        return None
        
    def _extract_object_id(self, keywords: List[ast.keyword]) -> Optional[str]:
        """Extract object_id information"""
        for kw in keywords:
            if kw.arg == 'object_id':
                # This is complex to parse fully, just extract basic info
                return "object_id_present"
        return None
        
    def _eval_expression(self, expr: ast.AST) -> int:
        """Evaluate simple expressions with constants"""
        if isinstance(expr, ast.Constant):
            return int(expr.value)
        elif isinstance(expr, ast.Name):
            return self.constants.get(expr.id, 0)
        elif isinstance(expr, ast.BinOp):
            if isinstance(expr.op, ast.Add):
                return self._eval_expression(expr.left) + self._eval_expression(expr.right)
            elif isinstance(expr.op, ast.Sub):
                return self._eval_expression(expr.left) - self._eval_expression(expr.right)
            elif isinstance(expr.op, ast.Mult):
                return self._eval_expression(expr.left) * self._eval_expression(expr.right)
        elif isinstance(expr, ast.UnaryOp) and isinstance(expr.op, ast.USub):
            return -self._eval_expression(expr.operand)
        return 0


class SVGGenerator:
    """Generates SVG visualization of pygame_gui layout"""
    
    def __init__(self, width: int = 1280, height: int = 960):
        self.width = width
        self.height = height
        self.colors = {
            'UIPanel': '#E6F3FF',
            'UILabel': '#FFE6E6', 
            'UIButton': '#E6FFE6',
            'UIDropDownMenu': '#FFFFE6',
            'UIProgressBar': '#F0E6FF',
            'default': '#F5F5F5'
        }
        self.stroke_colors = {
            'UIPanel': '#4A90E2',
            'UILabel': '#E24A4A',
            'UIButton': '#4AE24A', 
            'UIDropDownMenu': '#E2E24A',
            'UIProgressBar': '#A24AE2',
            'default': '#999999'
        }
        
    def generate_svg(self, components: Dict[str, Component], filename: str):
        """Generate SVG file from components"""
        root = Element('svg', {
            'width': str(self.width),
            'height': str(self.height),
            'xmlns': 'http://www.w3.org/2000/svg',
            'viewBox': f'0 0 {self.width} {self.height}'
        })
        
        # Add styles
        self._add_styles(root)
        
        # Add title
        title = SubElement(root, 'title')
        title.text = f'pygame_gui Layout Visualization'
        
        # Sort components by hierarchy (containers first)
        sorted_components = self._sort_by_hierarchy(components)
        
        # Render components
        for component in sorted_components:
            self._render_component(root, component)
            
        # Write SVG file
        tree = ET.ElementTree(root)
        ET.indent(tree, space="  ", level=0)
        tree.write(filename, encoding='utf-8', xml_declaration=True)
        print(f"Generated SVG layout: {filename}")
        
    def _add_styles(self, root: Element):
        """Add CSS styles to SVG"""
        style = SubElement(root, 'style')
        style.text = """
            .component-text { font-family: Arial, sans-serif; font-size: 12px; fill: #333; }
            .component-id { font-family: monospace; font-size: 10px; fill: #666; }
            .anchor-point { fill: #FF4444; stroke: #AA0000; stroke-width: 1; }
        """
        
    def _sort_by_hierarchy(self, components: Dict[str, Component]) -> List[Component]:
        """Sort components by container hierarchy (parents before children)"""
        # Simple sorting - containers first, then by y position
        return sorted(components.values(), 
                     key=lambda c: (c.container is not None, c.rect['y'], c.rect['x']))
        
    def _render_component(self, parent: Element, component: Component):
        """Render a single component to SVG"""
        rect = component.rect
        
        # Create group for component
        g = SubElement(parent, 'g', {
            'id': component.id,
            'class': f'component {component.type.lower()}'
        })
        
        # Draw component rectangle
        fill_color = self.colors.get(component.type, self.colors['default'])
        stroke_color = self.stroke_colors.get(component.type, self.stroke_colors['default'])
        
        SubElement(g, 'rect', {
            'x': str(rect['x']),
            'y': str(rect['y']),
            'width': str(rect['width']),
            'height': str(rect['height']),
            'fill': fill_color,
            'stroke': stroke_color,
            'stroke-width': '2',
            'opacity': '0.8'
        })
        
        # Add component type label
        text_y = rect['y'] + 15
        SubElement(g, 'text', {
            'x': str(rect['x'] + 5),
            'y': str(text_y),
            'class': 'component-text'
        }).text = component.type
        
        # Add component text if present
        if component.text:
            text_y += 15
            SubElement(g, 'text', {
                'x': str(rect['x'] + 5),
                'y': str(text_y),
                'class': 'component-text'
            }).text = f'"{component.text}"'
            
        # Add component ID
        SubElement(g, 'text', {
            'x': str(rect['x'] + 5),
            'y': str(rect['y'] + rect['height'] - 5),
            'class': 'component-id'
        }).text = component.id
        
        # Add anchor indicators
        self._add_anchor_indicators(g, component)
        
    def _add_anchor_indicators(self, parent: Element, component: Component):
        """Add visual indicators for anchor points"""
        rect = component.rect
        
        # Draw anchor points based on anchors dict
        anchors = component.anchors
        anchor_size = 4
        
        if anchors.get('top') == 'top':
            # Top anchor
            SubElement(parent, 'circle', {
                'cx': str(rect['x'] + rect['width'] // 2),
                'cy': str(rect['y']),
                'r': str(anchor_size),
                'class': 'anchor-point'
            })
            
        if anchors.get('bottom') == 'bottom':
            # Bottom anchor
            SubElement(parent, 'circle', {
                'cx': str(rect['x'] + rect['width'] // 2),
                'cy': str(rect['y'] + rect['height']),
                'r': str(anchor_size),
                'class': 'anchor-point'
            })
            
        if anchors.get('left') == 'left':
            # Left anchor
            SubElement(parent, 'circle', {
                'cx': str(rect['x']),
                'cy': str(rect['y'] + rect['height'] // 2),
                'r': str(anchor_size),
                'class': 'anchor-point'
            })
            
        if anchors.get('right') == 'right':
            # Right anchor
            SubElement(parent, 'circle', {
                'cx': str(rect['x'] + rect['width']),
                'cy': str(rect['y'] + rect['height'] // 2),
                'r': str(anchor_size),
                'class': 'anchor-point'
            })


def analyze_file(file_path: Path) -> Dict[str, Component]:
    """Analyze a Python file and extract pygame_gui components"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            source = f.read()
            
        tree = ast.parse(source)
        analyzer = PygameUIAnalyzer()
        analyzer.visit(tree)
        
        return analyzer.components
    except Exception as e:
        print(f"Error analyzing {file_path}: {e}")
        return {}


def main():
    parser = argparse.ArgumentParser(description='Generate SVG layout from pygame_gui code')
    parser.add_argument('file', type=Path, help='Python file to analyze')
    parser.add_argument('--output', '-o', type=Path, help='Output SVG file')
    parser.add_argument('--width', type=int, default=1280, help='SVG width')
    parser.add_argument('--height', type=int, default=960, help='SVG height')
    
    args = parser.parse_args()
    
    if not args.file.exists():
        print(f"Error: File {args.file} does not exist")
        return 1
        
    if not args.output:
        args.output = args.file.with_suffix('.svg')
        
    print(f"Analyzing {args.file}...")
    components = analyze_file(args.file)
    
    if not components:
        print("No pygame_gui components found")
        return 1
        
    print(f"Found {len(components)} components:")
    for comp in components.values():
        print(f"  - {comp.id} ({comp.type})")
        
    generator = SVGGenerator(args.width, args.height)
    generator.generate_svg(components, str(args.output))
    
    return 0


if __name__ == '__main__':
    exit(main())
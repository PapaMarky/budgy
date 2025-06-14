#!/usr/bin/env python3
"""
SVG Generator for pygame_gui Layout Visualization

This tool generates SVG visualizations from JSON layout descriptions,
providing clear visual documentation of UI component hierarchies.
"""

import argparse
import xml.etree.ElementTree as ET
from xml.etree.ElementTree import Element, SubElement
from pathlib import Path
from typing import Dict, List, Tuple, Optional
import math

from layout_schema import Layout, Component, COMPONENT_TYPES


class SVGGenerator:
    """Generates SVG visualization of pygame_gui layouts"""
    
    def __init__(self, width: int = 1280, height: int = 960):
        self.width = width
        self.height = height
        self.component_colors = COMPONENT_TYPES
        self.default_color = {"color": "#F5F5F5", "stroke": "#999999"}
        
    def generate_svg(self, layout: Layout, output_path: Path) -> None:
        """Generate SVG file from layout"""
        # Create root SVG element
        root = Element('svg', {
            'width': str(self.width),
            'height': str(self.height),
            'xmlns': 'http://www.w3.org/2000/svg',
            'viewBox': f'0 0 {self.width} {self.height}'
        })
        
        # Add styles and definitions
        self._add_styles(root)
        self._add_definitions(root)
        
        # Add title and description
        self._add_header(root, layout)
        
        # Create main content group
        content_group = SubElement(root, 'g', {'id': 'layout-content'})
        
        # Sort components by render order (containers first, then by z-index)
        sorted_components = self._sort_components_by_render_order(layout)
        
        # Render components
        for component in sorted_components:
            self._render_component(content_group, component, layout)
        
        # Add legend
        self._add_legend(root, layout)
        
        # Write SVG file
        self._write_svg_file(root, output_path)
        print(f"Generated SVG: {output_path}")
    
    def _add_styles(self, root: Element) -> None:
        """Add CSS styles to SVG"""
        style = SubElement(root, 'style')
        style.text = """
            .component-rect { stroke-width: 2; opacity: 0.9; }
            .component-text { font-family: 'Arial', sans-serif; font-size: 12px; fill: #333; }
            .component-id { font-family: 'Courier New', monospace; font-size: 10px; fill: #666; }
            .component-type { font-family: 'Arial', sans-serif; font-size: 11px; fill: #444; font-weight: bold; }
            .anchor-point { stroke-width: 1; opacity: 0.8; }
            .container-outline { stroke: #000; stroke-width: 1; stroke-dasharray: 3,3; fill: none; opacity: 0.3; }
            .legend-text { font-family: 'Arial', sans-serif; font-size: 12px; fill: #333; }
            .legend-title { font-family: 'Arial', sans-serif; font-size: 14px; fill: #000; font-weight: bold; }
            .title-text { font-family: 'Arial', sans-serif; font-size: 18px; fill: #000; font-weight: bold; }
            .description-text { font-family: 'Arial', sans-serif; font-size: 12px; fill: #666; }
            .hover-info { opacity: 0; transition: opacity 0.3s; }
            .component-group:hover .hover-info { opacity: 1; }
        """
    
    def _add_definitions(self, root: Element) -> None:
        """Add SVG definitions (gradients, patterns, etc.)"""
        defs = SubElement(root, 'defs')
        
        # Add drop shadow filter
        filter_elem = SubElement(defs, 'filter', {
            'id': 'drop-shadow',
            'x': '-20%', 'y': '-20%',
            'width': '140%', 'height': '140%'
        })
        
        SubElement(filter_elem, 'feDropShadow', {
            'dx': '2', 'dy': '2',
            'stdDeviation': '2',
            'flood-color': '#000000',
            'flood-opacity': '0.3'
        })
    
    def _add_header(self, root: Element, layout: Layout) -> None:
        """Add title and description to SVG"""
        title = SubElement(root, 'title')
        title.text = f'pygame_gui Layout: {layout.metadata.source_file or "Unknown"}'
        
        # Add visible title
        title_group = SubElement(root, 'g', {'id': 'header'})
        
        SubElement(title_group, 'text', {
            'x': '10', 'y': '25',
            'class': 'title-text'
        }).text = f'Layout Visualization: {Path(layout.metadata.source_file).name if layout.metadata.source_file else "Untitled"}'
        
        if layout.metadata.description:
            SubElement(title_group, 'text', {
                'x': '10', 'y': '45',
                'class': 'description-text'
            }).text = layout.metadata.description
        
        # Add metadata info
        metadata_y = 65 if layout.metadata.description else 45
        SubElement(title_group, 'text', {
            'x': '10', 'y': str(metadata_y),
            'class': 'description-text'
        }).text = f'Window Size: {layout.metadata.window_size[0]}×{layout.metadata.window_size[1]} | Components: {len(layout.components)}'
    
    def _sort_components_by_render_order(self, layout: Layout) -> List[Component]:
        """Sort components for proper rendering order (parents before children)"""
        # Build dependency graph
        components = list(layout.components.values())
        
        # Sort by: containers first, then by area (larger first), then by position
        def sort_key(comp: Component) -> Tuple:
            is_container = len(comp.children) > 0
            area = comp.rect.w * comp.rect.h
            return (not is_container, -area, comp.rect.y, comp.rect.x)
        
        return sorted(components, key=sort_key)
    
    def _render_component(self, parent: Element, component: Component, layout: Layout) -> None:
        """Render a single component to SVG"""
        # Create component group
        group = SubElement(parent, 'g', {
            'id': f'comp-{component.id}',
            'class': 'component-group'
        })
        
        # Get component colors
        colors = self.component_colors.get(component.type, self.default_color)
        
        # Calculate actual position (handle negative coordinates for right/bottom anchoring)
        actual_rect = self._calculate_actual_rect(component, layout)
        
        # Draw component rectangle
        rect_elem = SubElement(group, 'rect', {
            'x': str(actual_rect.x),
            'y': str(actual_rect.y),
            'width': str(actual_rect.w),
            'height': str(actual_rect.h),
            'fill': colors["color"],
            'stroke': colors["stroke"],
            'class': 'component-rect'
        })
        
        # Add filter for containers
        if len(component.children) > 0:
            rect_elem.set('filter', 'url(#drop-shadow)')
        
        # Add component type label
        text_y = actual_rect.y + 16
        if actual_rect.h >= 16:
            SubElement(group, 'text', {
                'x': str(actual_rect.x + 5),
                'y': str(text_y),
                'class': 'component-type'
            }).text = component.type
        
        # Add component text if present and space available
        if component.text and actual_rect.h >= 32:
            text_y += 14
            text_elem = SubElement(group, 'text', {
                'x': str(actual_rect.x + 5),
                'y': str(text_y),
                'class': 'component-text'
            })
            # Truncate text if too long
            max_chars = max(1, (actual_rect.w - 10) // 8)
            display_text = component.text[:max_chars] + ("..." if len(component.text) > max_chars else "")
            text_elem.text = f'"{display_text}"'
        
        # Add component ID at bottom if space available
        if actual_rect.h >= 48:
            SubElement(group, 'text', {
                'x': str(actual_rect.x + 5),
                'y': str(actual_rect.y + actual_rect.h - 5),
                'class': 'component-id'
            }).text = component.id
        
        # Add anchor indicators
        self._add_anchor_indicators(group, component, actual_rect)
        
        # Add hover information
        self._add_hover_info(group, component, actual_rect)
        
        # Add container outline if this is a container
        if len(component.children) > 0:
            SubElement(group, 'rect', {
                'x': str(actual_rect.x),
                'y': str(actual_rect.y),
                'width': str(actual_rect.w),
                'height': str(actual_rect.h),
                'class': 'container-outline'
            })
    
    def _calculate_actual_rect(self, component: Component, layout: Layout) -> 'Rect':
        """Calculate actual rectangle position handling negative coordinates"""
        from layout_schema import Rect
        
        rect = component.rect
        
        # Handle negative coordinates (right/bottom anchoring)
        actual_x = rect.x
        actual_y = rect.y
        
        # If component has a container, adjust relative to container
        if component.container and component.container in layout.components:
            container = layout.components[component.container]
            container_rect = self._calculate_actual_rect(container, layout)
            
            # Adjust for negative positioning (right/bottom anchoring)
            if rect.x < 0:
                actual_x = container_rect.x + container_rect.w + rect.x
            else:
                actual_x = container_rect.x + rect.x
                
            if rect.y < 0:
                actual_y = container_rect.y + container_rect.h + rect.y
            else:
                actual_y = container_rect.y + rect.y
        else:
            # Root component - handle negative coordinates relative to window
            if rect.x < 0:
                actual_x = self.width + rect.x
            if rect.y < 0:
                actual_y = self.height + rect.y
        
        return Rect(actual_x, actual_y, rect.w, rect.h)
    
    def _add_anchor_indicators(self, parent: Element, component: Component, rect) -> None:
        """Add visual indicators for anchor points"""
        anchors = component.anchors
        anchor_size = 4
        
        # Top anchor
        if anchors.top in ["top", "bottom"]:
            SubElement(parent, 'circle', {
                'cx': str(rect.x + rect.w // 2),
                'cy': str(rect.y if anchors.top == "top" else rect.y + rect.h),
                'r': str(anchor_size),
                'fill': '#FF4444',
                'stroke': '#AA0000',
                'class': 'anchor-point'
            })
        
        # Bottom anchor
        if anchors.bottom in ["top", "bottom"]:
            SubElement(parent, 'circle', {
                'cx': str(rect.x + rect.w // 2),
                'cy': str(rect.y if anchors.bottom == "top" else rect.y + rect.h),
                'r': str(anchor_size),
                'fill': '#4444FF',
                'stroke': '#0000AA',
                'class': 'anchor-point'
            })
        
        # Left anchor
        if anchors.left in ["left", "right"]:
            SubElement(parent, 'circle', {
                'cx': str(rect.x if anchors.left == "left" else rect.x + rect.w),
                'cy': str(rect.y + rect.h // 2),
                'r': str(anchor_size),
                'fill': '#44FF44',
                'stroke': '#00AA00',
                'class': 'anchor-point'
            })
        
        # Right anchor
        if anchors.right in ["left", "right"]:
            SubElement(parent, 'circle', {
                'cx': str(rect.x if anchors.right == "left" else rect.x + rect.w),
                'cy': str(rect.y + rect.h // 2),
                'r': str(anchor_size),
                'fill': '#FF44FF',
                'stroke': '#AA00AA',
                'class': 'anchor-point'
            })
    
    def _add_hover_info(self, parent: Element, component: Component, rect) -> None:
        """Add hover information overlay"""
        info_group = SubElement(parent, 'g', {'class': 'hover-info'})
        
        # Background for info
        info_bg = SubElement(info_group, 'rect', {
            'x': str(rect.x + rect.w + 5),
            'y': str(rect.y),
            'width': '200',
            'height': '120',
            'fill': '#FFFFCC',
            'stroke': '#CCCC99',
            'stroke-width': '1',
            'opacity': '0.95'
        })
        
        # Info text
        info_y = rect.y + 15
        info_x = rect.x + rect.w + 10
        
        SubElement(info_group, 'text', {
            'x': str(info_x), 'y': str(info_y),
            'class': 'component-text'
        }).text = f"ID: {component.id}"
        
        info_y += 15
        SubElement(info_group, 'text', {
            'x': str(info_x), 'y': str(info_y),
            'class': 'component-text'
        }).text = f"Type: {component.type}"
        
        info_y += 15
        SubElement(info_group, 'text', {
            'x': str(info_x), 'y': str(info_y),
            'class': 'component-text'
        }).text = f"Size: {component.rect.w}×{component.rect.h}"
        
        info_y += 15
        SubElement(info_group, 'text', {
            'x': str(info_x), 'y': str(info_y),
            'class': 'component-text'
        }).text = f"Pos: ({component.rect.x}, {component.rect.y})"
        
        if component.container:
            info_y += 15
            SubElement(info_group, 'text', {
                'x': str(info_x), 'y': str(info_y),
                'class': 'component-text'
            }).text = f"Container: {component.container}"
        
        if component.children:
            info_y += 15
            SubElement(info_group, 'text', {
                'x': str(info_x), 'y': str(info_y),
                'class': 'component-text'
            }).text = f"Children: {len(component.children)}"
    
    def _add_legend(self, root: Element, layout: Layout) -> None:
        """Add component type legend"""
        legend_group = SubElement(root, 'g', {'id': 'legend'})
        
        # Legend background
        legend_x = self.width - 250
        legend_y = 100
        legend_width = 240
        
        # Count component types used
        used_types = set(comp.type for comp in layout.components.values())
        legend_height = 30 + len(used_types) * 25 + 60  # Title + types + anchor legend
        
        SubElement(legend_group, 'rect', {
            'x': str(legend_x), 'y': str(legend_y),
            'width': str(legend_width), 'height': str(legend_height),
            'fill': '#F9F9F9', 'stroke': '#CCCCCC', 'stroke-width': '1'
        })
        
        # Legend title
        SubElement(legend_group, 'text', {
            'x': str(legend_x + 10), 'y': str(legend_y + 20),
            'class': 'legend-title'
        }).text = 'Component Types'
        
        # Component type legend entries
        entry_y = legend_y + 40
        for comp_type in sorted(used_types):
            colors = self.component_colors.get(comp_type, self.default_color)
            
            # Color square
            SubElement(legend_group, 'rect', {
                'x': str(legend_x + 10), 'y': str(entry_y - 12),
                'width': '15', 'height': '15',
                'fill': colors["color"], 'stroke': colors["stroke"], 'stroke-width': '1'
            })
            
            # Type name
            SubElement(legend_group, 'text', {
                'x': str(legend_x + 30), 'y': str(entry_y),
                'class': 'legend-text'
            }).text = comp_type
            
            entry_y += 25
        
        # Anchor legend
        entry_y += 10
        SubElement(legend_group, 'text', {
            'x': str(legend_x + 10), 'y': str(entry_y),
            'class': 'legend-title'
        }).text = 'Anchor Points'
        
        anchor_colors = [
            ('#FF4444', 'Top'),
            ('#4444FF', 'Bottom'), 
            ('#44FF44', 'Left'),
            ('#FF44FF', 'Right')
        ]
        
        entry_y += 20
        for color, label in anchor_colors:
            SubElement(legend_group, 'circle', {
                'cx': str(legend_x + 17), 'cy': str(entry_y - 5),
                'r': '4', 'fill': color, 'stroke': color[:-2] + 'AA'
            })
            
            SubElement(legend_group, 'text', {
                'x': str(legend_x + 30), 'y': str(entry_y),
                'class': 'legend-text'
            }).text = label
            
            entry_y += 15
    
    def _write_svg_file(self, root: Element, output_path: Path) -> None:
        """Write SVG to file with proper formatting"""
        # Format the XML
        ET.indent(root, space="  ", level=0)
        
        # Create the tree and write
        tree = ET.ElementTree(root)
        tree.write(output_path, encoding='utf-8', xml_declaration=True)


def main():
    """Command line interface"""
    parser = argparse.ArgumentParser(description='Generate SVG visualization from layout JSON')
    parser.add_argument('input', type=Path, help='Input JSON layout file')
    parser.add_argument('--output', '-o', type=Path, help='Output SVG file (default: input.svg)')
    parser.add_argument('--width', type=int, default=1280, help='SVG width (default: 1280)')
    parser.add_argument('--height', type=int, default=960, help='SVG height (default: 960)')
    
    args = parser.parse_args()
    
    if not args.input.exists():
        print(f"Error: Input file {args.input} does not exist")
        return 1
    
    if not args.output:
        args.output = args.input.with_suffix('.svg')
    
    try:
        # Load layout
        layout = Layout.load_json(args.input)
        
        # Validate layout
        issues = layout.validate()
        if issues:
            print("Layout validation issues:")
            for issue in issues:
                print(f"  - {issue}")
            print()
        
        # Generate SVG
        generator = SVGGenerator(args.width, args.height)
        generator.generate_svg(layout, args.output)
        
        print(f"Successfully generated {args.output}")
        return 0
        
    except Exception as e:
        print(f"Error generating SVG: {e}")
        return 1


if __name__ == '__main__':
    exit(main())
#!/usr/bin/env python3
"""
JSON Schema definitions for pygame_gui layout representation.

This module defines the data structures and validation for the layout toolchain.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional, Union
import json
from pathlib import Path


@dataclass
class Rect:
    """Rectangle definition for component positioning"""
    x: int
    y: int
    w: int
    h: int
    
    def to_dict(self) -> Dict[str, int]:
        return {"x": self.x, "y": self.y, "w": self.w, "h": self.h}
    
    @classmethod
    def from_dict(cls, data: Dict[str, int]) -> 'Rect':
        return cls(x=data["x"], y=data["y"], w=data["w"], h=data["h"])


@dataclass
class Anchors:
    """Anchor configuration for component positioning"""
    top: Union[str, Dict[str, Any]]
    left: Union[str, Dict[str, Any]]
    bottom: Union[str, Dict[str, Any]]
    right: Union[str, Dict[str, Any]]
    
    def to_dict(self) -> Dict[str, Union[str, Dict[str, Any]]]:
        return {
            "top": self.top,
            "left": self.left,
            "bottom": self.bottom,
            "right": self.right
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Union[str, Dict[str, Any]]]) -> 'Anchors':
        return cls(
            top=data.get("top", "top"),
            left=data.get("left", "left"),
            bottom=data.get("bottom", "bottom"),
            right=data.get("right", "right")
        )


@dataclass
class Styling:
    """Styling information for components"""
    object_id: Optional[str] = None
    show_border: bool = True
    background_color: Optional[str] = None
    text_color: Optional[str] = None
    font_size: Optional[int] = None
    
    def to_dict(self) -> Dict[str, Any]:
        result = {"show_border": self.show_border}
        if self.object_id:
            result["object_id"] = self.object_id
        if self.background_color:
            result["background_color"] = self.background_color
        if self.text_color:
            result["text_color"] = self.text_color
        if self.font_size:
            result["font_size"] = self.font_size
        return result
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Styling':
        return cls(
            object_id=data.get("object_id"),
            show_border=data.get("show_border", True),
            background_color=data.get("background_color"),
            text_color=data.get("text_color"),
            font_size=data.get("font_size")
        )


@dataclass
class Component:
    """A pygame_gui UI component"""
    id: str
    type: str
    rect: Rect
    anchors: Anchors
    container: Optional[str] = None
    text: str = ""
    styling: Styling = field(default_factory=Styling)
    children: List[str] = field(default_factory=list)
    visible: bool = True
    margins: Optional[Dict[str, int]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        result = {
            "type": self.type,
            "rect": self.rect.to_dict(),
            "anchors": self.anchors.to_dict(),
            "text": self.text,
            "styling": self.styling.to_dict(),
            "children": self.children,
            "visible": self.visible
        }
        if self.container:
            result["container"] = self.container
        if self.margins:
            result["margins"] = self.margins
        return result
    
    @classmethod
    def from_dict(cls, component_id: str, data: Dict[str, Any]) -> 'Component':
        return cls(
            id=component_id,
            type=data["type"],
            rect=Rect.from_dict(data["rect"]),
            anchors=Anchors.from_dict(data["anchors"]),
            container=data.get("container"),
            text=data.get("text", ""),
            styling=Styling.from_dict(data.get("styling", {})),
            children=data.get("children", []),
            visible=data.get("visible", True),
            margins=data.get("margins")
        )


@dataclass
class Metadata:
    """Layout metadata information"""
    version: str = "1.0"
    source_file: Optional[str] = None
    window_size: List[int] = field(default_factory=lambda: [1280, 960])
    constants: Dict[str, int] = field(default_factory=dict)
    description: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        result = {
            "version": self.version,
            "window_size": self.window_size,
            "constants": self.constants
        }
        if self.source_file:
            result["source_file"] = self.source_file
        if self.description:
            result["description"] = self.description
        return result
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Metadata':
        return cls(
            version=data.get("version", "1.0"),
            source_file=data.get("source_file"),
            window_size=data.get("window_size", [1280, 960]),
            constants=data.get("constants", {}),
            description=data.get("description")
        )


@dataclass
class Layout:
    """Complete layout specification"""
    metadata: Metadata
    components: Dict[str, Component]
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "metadata": self.metadata.to_dict(),
            "components": {comp_id: comp.to_dict() 
                          for comp_id, comp in self.components.items()}
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Layout':
        metadata = Metadata.from_dict(data.get("metadata", {}))
        components = {
            comp_id: Component.from_dict(comp_id, comp_data)
            for comp_id, comp_data in data.get("components", {}).items()
        }
        return cls(metadata=metadata, components=components)
    
    def save_json(self, filepath: Path) -> None:
        """Save layout to JSON file"""
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(self.to_dict(), f, indent=2, ensure_ascii=False)
    
    @classmethod
    def load_json(cls, filepath: Path) -> 'Layout':
        """Load layout from JSON file"""
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return cls.from_dict(data)
    
    def validate(self) -> List[str]:
        """Validate layout and return list of issues"""
        issues = []
        
        # Check for circular container references
        for comp_id, component in self.components.items():
            if self._has_circular_reference(comp_id, set()):
                issues.append(f"Circular container reference detected for {comp_id}")
        
        # Check that all container references exist
        for comp_id, component in self.components.items():
            if component.container and component.container not in self.components:
                issues.append(f"Component {comp_id} references non-existent container {component.container}")
        
        # Check that all children exist
        for comp_id, component in self.components.items():
            for child_id in component.children:
                if child_id not in self.components:
                    issues.append(f"Component {comp_id} references non-existent child {child_id}")
        
        # Check for component overlap (basic check)
        for comp1_id, comp1 in self.components.items():
            for comp2_id, comp2 in self.components.items():
                if comp1_id != comp2_id and comp1.container == comp2.container:
                    if self._rectangles_overlap(comp1.rect, comp2.rect):
                        issues.append(f"Components {comp1_id} and {comp2_id} may overlap")
        
        return issues
    
    def _has_circular_reference(self, comp_id: str, visited: set) -> bool:
        """Check for circular container references"""
        if comp_id in visited:
            return True
        
        component = self.components.get(comp_id)
        if not component or not component.container:
            return False
        
        visited.add(comp_id)
        return self._has_circular_reference(component.container, visited)
    
    def _rectangles_overlap(self, rect1: Rect, rect2: Rect) -> bool:
        """Check if two rectangles overlap"""
        return not (rect1.x + rect1.w <= rect2.x or 
                   rect2.x + rect2.w <= rect1.x or
                   rect1.y + rect1.h <= rect2.y or 
                   rect2.y + rect2.h <= rect1.y)
    
    def get_root_components(self) -> List[Component]:
        """Get components that have no container (root level)"""
        return [comp for comp in self.components.values() if not comp.container]
    
    def get_children(self, component_id: str) -> List[Component]:
        """Get direct children of a component"""
        component = self.components.get(component_id)
        if not component:
            return []
        return [self.components[child_id] for child_id in component.children 
                if child_id in self.components]
    
    def add_component(self, component: Component) -> None:
        """Add a component to the layout"""
        self.components[component.id] = component
        
        # Update parent's children list
        if component.container and component.container in self.components:
            parent = self.components[component.container]
            if component.id not in parent.children:
                parent.children.append(component.id)
    
    def remove_component(self, component_id: str) -> None:
        """Remove a component and update references"""
        if component_id not in self.components:
            return
        
        component = self.components[component_id]
        
        # Remove from parent's children list
        if component.container and component.container in self.components:
            parent = self.components[component.container]
            if component_id in parent.children:
                parent.children.remove(component_id)
        
        # Remove children (they become orphaned)
        for child_id in list(component.children):
            self.remove_component(child_id)
        
        del self.components[component_id]


# Component type constants
COMPONENT_TYPES = {
    "UIPanel": {"color": "#E6F3FF", "stroke": "#4A90E2"},
    "UILabel": {"color": "#FFE6E6", "stroke": "#E24A4A"},
    "UIButton": {"color": "#E6FFE6", "stroke": "#4AE24A"},
    "UIDropDownMenu": {"color": "#FFFFE6", "stroke": "#E2E24A"},
    "UIProgressBar": {"color": "#F0E6FF", "stroke": "#A24AE2"},
    "UITextEntryLine": {"color": "#E6FFFF", "stroke": "#4AE2E2"},
    "UISelectionList": {"color": "#FFE6F0", "stroke": "#E24AA2"},
    "UIScrollingContainer": {"color": "#F0FFE6", "stroke": "#A2E24A"},
    "UIVerticalScrollBar": {"color": "#F5F5F5", "stroke": "#999999"},
    "UIHorizontalScrollBar": {"color": "#F5F5F5", "stroke": "#999999"},
}

# Anchor value constants
ANCHOR_VALUES = ["top", "bottom", "left", "right"]


def create_sample_layout() -> Layout:
    """Create a sample layout for testing"""
    metadata = Metadata(
        version="1.0",
        description="Sample top panel layout",
        window_size=[1280, 960],
        constants={"BUTTON_HEIGHT": 25, "MARGIN": 2}
    )
    
    # Main panel
    main_panel = Component(
        id="top_panel",
        type="UIPanel",
        rect=Rect(0, 0, 1280, 100),
        anchors=Anchors("top", "left", "top", "right"),
        styling=Styling(object_id="#top-panel")
    )
    
    # Record count label
    record_label = Component(
        id="record_label",
        type="UILabel",
        rect=Rect(2, 2, 175, 25),
        anchors=Anchors("top", "left", "top", "left"),
        container="top_panel",
        text="Record Count:",
        styling=Styling(object_id="#data-label")
    )
    
    # Record count value
    record_value = Component(
        id="record_value",
        type="UILabel", 
        rect=Rect(179, 2, 1099, 25),
        anchors=Anchors("top", "left", "top", "right"),
        container="top_panel",
        text="No Database",
        styling=Styling(object_id="#data-text")
    )
    
    # Function dropdown
    dropdown = Component(
        id="function_dropdown",
        type="UIDropDownMenu",
        rect=Rect(-202, 2, 200, 25),
        anchors=Anchors("top", "right", "top", "right"),
        container="top_panel",
        text="Report Functions",
        styling=Styling(object_id="#dropdown")
    )
    
    # Build component hierarchy
    main_panel.children = ["record_label", "record_value", "function_dropdown"]
    
    components = {
        "top_panel": main_panel,
        "record_label": record_label,
        "record_value": record_value,
        "function_dropdown": dropdown
    }
    
    return Layout(metadata=metadata, components=components)


if __name__ == "__main__":
    # Create and save sample layout
    sample = create_sample_layout()
    sample.save_json(Path("examples/sample_layout.json"))
    print("Created sample layout: examples/sample_layout.json")
    
    # Validate the layout
    issues = sample.validate()
    if issues:
        print("Validation issues:")
        for issue in issues:
            print(f"  - {issue}")
    else:
        print("Layout validation passed!")
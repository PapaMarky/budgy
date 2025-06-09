# pygame_gui Layout Toolchain

A comprehensive set of tools for visualizing, designing, and generating pygame_gui layouts.

## Overview

This toolchain provides a complete workflow for pygame_gui UI development:

1. **Code Analysis** - Extract layout information from existing Python files
2. **JSON Schema** - Standardized representation of UI component hierarchies  
3. **SVG Visualization** - Generate visual documentation from layouts
4. **Visual Design** - Interactive layout editor *(planned)*
5. **Code Generation** - Create Python code from layout descriptions *(planned)*

## Quick Start

### Generate SVG from Sample Layout

```bash
# Generate visualization from included sample
python3 generate_svg.py examples/sample_layout.json

# Custom output and dimensions
python3 generate_svg.py examples/simple_test.json --output my_layout.svg --width 800 --height 600
```

### Create Custom Layout

```python
from layout_schema import Layout, Component, Rect, Anchors, Styling, Metadata

# Define your layout using the schema
layout = Layout(
    metadata=Metadata(description="My Custom Layout"),
    components={
        "main_panel": Component(
            id="main_panel",
            type="UIPanel", 
            rect=Rect(0, 0, 400, 300),
            anchors=Anchors("top", "left", "bottom", "right")
        )
    }
)

# Save and visualize
layout.save_json("my_layout.json")
```

## Tools

### 📋 layout_schema.py
**JSON schema and data structures for layout representation**

- Complete dataclass definitions for all pygame_gui components
- Layout validation (circular references, missing components, overlaps)
- JSON import/export with proper formatting
- Future-compatible design for anchor targets

**Key Classes:**
- `Layout` - Complete layout specification
- `Component` - Individual UI component
- `Rect` - Position and dimensions
- `Anchors` - Positioning relationships
- `Styling` - Visual appearance properties

### 🎨 generate_svg.py  
**SVG visualization generator for layout documentation**

- Color-coded component types
- Interactive hover information
- Anchor point indicators
- Container hierarchy visualization
- Responsive positioning with negative coordinate support

**Features:**
- Component type legend
- Hover details for each component
- Visual anchor relationship indicators
- Container drop shadows and outlines

### 🔧 analyze_layout.py
**Extract pygame_gui layouts from existing Python code**

- AST-based component detection and analysis
- Handles complex expressions and constants
- Container hierarchy extraction
- Support for all pygame_gui component types
- Automatic layout validation

### ⚙️ generate_code.py
**Generate clean Python code from JSON layouts**

- Template-based code generation with proper formatting
- Maintains pygame_gui coding patterns
- Handles complex anchoring and positioning
- Generates properties for component access
- Round-trip compatible with analyzer

### 📁 examples/
**Sample layouts demonstrating toolchain capabilities**

- `sample_layout.json` - Simple top panel with labels and dropdown
- `simple_test.json` - Complex multi-panel layout with various component types
- Generated SVG files for visual reference

## JSON Schema Format

```json
{
  "metadata": {
    "version": "1.0",
    "description": "Layout description",
    "window_size": [1280, 960],
    "constants": {
      "BUTTON_HEIGHT": 25,
      "MARGIN": 2
    }
  },
  "components": {
    "component_id": {
      "type": "UIPanel|UILabel|UIButton|UIDropDownMenu",
      "rect": {"x": 0, "y": 0, "w": 200, "h": 100},
      "anchors": {
        "top": "top",
        "left": "left", 
        "bottom": "top",
        "right": "right"
      },
      "container": "parent_component_id",
      "text": "Component text content",
      "styling": {
        "object_id": "#css-class",
        "show_border": true,
        "background_color": "#E6F3FF"
      },
      "children": ["child1_id", "child2_id"],
      "visible": true
    }
  }
}
```

## Supported Component Types

| Component | Color | Description |
|-----------|-------|-------------|
| UIPanel | Blue (#E6F3FF) | Container panels |
| UILabel | Red (#FFE6E6) | Text display |
| UIButton | Green (#E6FFE6) | Interactive buttons |
| UIDropDownMenu | Yellow (#FFFFE6) | Selection menus |
| UIProgressBar | Purple (#F0E6FF) | Progress indicators |
| UITextEntryLine | Cyan (#E6FFFF) | Text input fields |
| UISelectionList | Pink (#FFE6F0) | List selections |
| UIScrollingContainer | Light Green (#F0FFE6) | Scrollable containers |

## Anchor System

The toolchain supports pygame_gui's anchoring system for responsive positioning:

```json
"anchors": {
  "top": "top|bottom",      // Vertical anchor to container edge
  "bottom": "top|bottom",   // Vertical anchor to container edge  
  "left": "left|right",     // Horizontal anchor to container edge
  "right": "left|right"     // Horizontal anchor to container edge
}
```

**Positioning Rules:**
- `"top": "top"` - Anchor to top edge of container
- `"right": "right"` - Anchor to right edge of container
- Negative coordinates enable right/bottom positioning
- Mixed anchoring allows flexible responsive layouts

## Future Compatibility

### Anchor Targets *(Planned)*
Support for anchoring to other components:
```json
"anchors": {
  "left": {"target": "other_component", "edge": "right", "offset": 5}
}
```

### Animation Support *(Planned)*
Layout transitions and component animations:
```json
"animations": {
  "show": {"type": "fade_in", "duration": 500}
}
```

## Development Status

- ✅ **Phase 1: JSON Schema & SVG Visualizer** - Complete
- ✅ **Phase 2: Code Analyzer** - Complete
- ✅ **Phase 3: Code Generator** - Complete
- ⏳ **Phase 4: Visual Designer** - Planned

## Examples

### Complete Workflow Examples

**Extract layout from existing code:**
```bash
python3 analyze_layout.py ../src/budgy/gui/top_panel.py --output top_panel.json --svg
```

**Generate visualization:**
```bash
python3 generate_svg.py examples/sample_layout.json
```

**Generate Python code:**
```bash
python3 generate_code.py top_panel.json --class-name MyTopPanel --output my_panel.py
```

**Run comprehensive tests:**
```bash
python3 test_analyzer.py     # Test analyzer on all GUI files
python3 test_roundtrip.py    # Test complete round-trip workflow
```

### Round-Trip Capability
The toolchain supports complete round-trip workflows:
- **Code → JSON → SVG** (documentation workflow)
- **Code → JSON → Code** (refactoring workflow)  
- **JSON → Code → JSON** (design workflow)
- All transformations preserve layout structure and maintain validation

## Validation

The schema includes comprehensive validation:

```python
layout = Layout.load_json("my_layout.json")
issues = layout.validate()
if issues:
    for issue in issues:
        print(f"⚠️  {issue}")
```

**Validation Checks:**
- Circular container references
- Missing component references
- Invalid container relationships
- Component overlap detection
- Anchor consistency

## Integration

### With Existing pygame_gui Code
The toolchain is designed to work alongside existing pygame_gui applications:

1. **Extract** layouts from existing code with the analyzer *(planned)*
2. **Document** current layouts with SVG generation
3. **Design** new layouts with the visual editor *(planned)*
4. **Generate** clean code from designs *(planned)*

### File Organization
```
layout_tools/
├── layout_schema.py      # JSON schema definitions
├── generate_svg.py       # SVG visualization 
├── examples/             # Sample layouts
│   ├── sample_layout.json
│   ├── simple_test.json
│   └── *.svg
└── README.md            # This file
```

## Contributing

When adding new features:

1. **Maintain backward compatibility** with existing JSON schemas
2. **Add validation** for new schema elements
3. **Update component type colors** in `COMPONENT_TYPES`
4. **Include test cases** in examples/
5. **Document new features** in this README

## Dependencies

- **Python 3.7+** - Core language features
- **pathlib** - File path handling
- **json** - JSON schema processing
- **xml.etree.ElementTree** - SVG generation
- **dataclasses** - Type-safe data structures
- **argparse** - Command-line interfaces

No external dependencies required for core functionality.

## License

Part of the budgy project. See main project license for details.
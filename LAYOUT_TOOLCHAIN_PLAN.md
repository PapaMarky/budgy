# Layout Toolchain Development Plan

## Overview

This plan outlines the development of a comprehensive UI layout toolchain for pygame_gui applications. The toolchain consists of four interconnected tools that enable code analysis, visual design, documentation, and code generation.

## Toolchain Architecture

```
Existing Code → Analyzer → JSON Schema → SVG Visualizer
                             ↓              ↑
                        Designer Tool   Documentation
                             ↓              ↑  
                        Code Generator → New Code
```

## Tool Components

### 1. Code Analyzer (`analyze_layout.py`)
**Purpose:** Extract pygame_gui component structure from existing Python files

**Input:** Python files containing pygame_gui components
**Output:** Standardized JSON representation

**Key Features:**

- AST parsing for component extraction
- Constant evaluation (BUTTON_HEIGHT, MARGIN, etc.)
- Container hierarchy detection
- Anchor configuration extraction
- Text content and styling capture

**Example Usage:**
```bash
python analyze_layout.py src/budgy/gui/top_panel.py --output top_panel.json
```

### 2. JSON Schema Definition
**Purpose:** Standardized format for UI component representation

**Schema Structure:**
```json
{
  "metadata": {
    "version": "1.0",
    "source_file": "path/to/source.py",
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
      "container": "parent_component_id|null",
      "text": "component_text",
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

**Future Compatibility:**

- Anchor targets: Support for component references in anchors
- Extended styling: Additional visual properties
- Animation: Transition and animation properties

### 3. SVG Visualizer (`generate_svg.py`)
**Purpose:** Generate visual documentation from JSON layout descriptions

**Input:** JSON layout files
**Output:** SVG visualization files

**Key Features:**

- Component hierarchy visualization
- Color-coded component types
- Anchor point indicators
- Text content display
- Interactive elements (hover info)
- Responsive preview capabilities

**Component Type Colors:**

- UIPanel: Blue (#E6F3FF)
- UILabel: Red (#FFE6E6)
- UIButton: Green (#E6FFE6)
- UIDropDownMenu: Yellow (#FFFFE6)
- UIProgressBar: Purple (#F0E6FF)

**Example Usage:**
```bash
python generate_svg.py top_panel.json --output top_panel.svg --width 1280 --height 960
```

### 4. Layout Designer (`design_layout.py`)
**Purpose:** Visual editor for creating and modifying UI layouts

**Input:** JSON layout files (optional)
**Output:** Modified JSON layout files

**Key Features:**

- Drag-and-drop component placement
- Property editor panel
- Real-time SVG preview
- Component library/palette
- Constraint validation
- Grid snapping

**Interface Components:**

- Canvas area for layout design
- Component palette (UIPanel, UILabel, etc.)
- Property inspector
- Preview panel
- File operations (load/save JSON)

### 5. Code Generator (`generate_code.py`)
**Purpose:** Generate pygame_gui Python code from JSON layouts

**Input:** JSON layout files
**Output:** Python source code

**Key Features:**

- Template-based code generation
- Proper indentation and formatting
- Import statement management
- Constant definition handling
- Container hierarchy preservation
- Event handling skeleton

**Example Usage:**
```bash
python generate_code.py my_layout.json --output generated_panel.py --class-name MyPanel
```

## Implementation Phases

### Phase 1: Core JSON Schema & SVG Visualizer
**Goal:** Basic visualization capability
**Duration:** 1-2 weeks

**Tasks:**
1. Define complete JSON schema
2. Implement SVG generator with basic components
3. Create test JSON files for validation
4. Generate sample visualizations

**Deliverables:**

- JSON schema specification
- Working SVG generator
- Test cases and sample outputs

### Phase 2: Code Analyzer
**Goal:** Extract layouts from existing code
**Duration:** 1-2 weeks

**Tasks:**
1. Implement AST parsing for pygame_gui components
2. Handle constant evaluation and expressions
3. Extract container hierarchies
4. Generate JSON from existing budgy GUI files
5. Validate against existing layouts

**Deliverables:**

- Working code analyzer
- JSON representations of all budgy GUI panels
- Validation against manual inspection

### Phase 3: Code Generator
**Goal:** Generate code from JSON layouts
**Duration:** 1-2 weeks

**Tasks:**
1. Create code generation templates
2. Implement proper Python formatting
3. Handle imports and constants
4. Validate generated code compiles
5. Round-trip testing (code → JSON → code)

**Deliverables:**

- Working code generator
- Template system
- Round-trip validation tests

### Phase 4: Visual Designer
**Goal:** Interactive layout design tool
**Duration:** 2-3 weeks

**Tasks:**
1. Choose framework (tkinter/PyQt/web-based)
2. Implement drag-drop interface
3. Create property editor
4. Add real-time preview
5. Integrate with other tools

**Deliverables:**

- Interactive design application
- Integration with toolchain
- User documentation

## Technical Considerations

### Python Dependencies

- **ast**: Built-in AST parsing
- **json**: JSON schema handling
- **xml.etree.ElementTree**: SVG generation
- **pathlib**: File path handling
- **argparse**: Command-line interfaces
- **dataclasses**: Type-safe data structures

### Future Dependencies (Phase 4)

- **tkinter** or **PyQt5/PySide**: GUI framework for designer
- **pillow**: Image handling for preview
- **numpy**: Mathematical operations for layout calculations

### File Organization
```
layout_tools/
├── analyze_layout.py      # Code analyzer
├── generate_svg.py        # SVG visualizer  
├── design_layout.py       # Visual designer
├── generate_code.py       # Code generator
├── layout_schema.py       # JSON schema definitions
├── templates/             # Code generation templates
│   ├── panel_template.py
│   └── component_templates/
├── examples/              # Sample JSON layouts
│   ├── top_panel.json
│   ├── message_panel.json
│   └── function_panel.json
└── tests/                 # Test cases
    ├── test_analyzer.py
    ├── test_generator.py
    └── sample_layouts/
```

### Quality Assurance

**Validation Testing:**
1. **Round-trip Testing:** code → JSON → SVG → code
2. **Visual Validation:** Compare generated SVG with actual GUI
3. **Code Validation:** Ensure generated code compiles and runs
4. **Schema Validation:** JSON schema compliance checking

**Test Cases:**

- Simple single-component layouts
- Complex nested hierarchies
- Edge cases (negative coordinates, zero dimensions)
- All pygame_gui component types
- Various anchor configurations

## Future Enhancements

### Anchor Target Support
When pygame_gui supports component-based anchoring:
```json
"anchors": {
  "left": {"target": "other_component", "edge": "right", "offset": 5}
}
```

### Animation Support
Layout transitions and component animations:
```json
"animations": {
  "show": {"type": "fade_in", "duration": 500},
  "hide": {"type": "slide_out", "direction": "up"}
}
```

### Theme Integration
Extended styling and theme support:
```json
"styling": {
  "theme": "dark_mode",
  "custom_properties": {
    "border_radius": 5,
    "shadow": true
  }
}
```

### Layout Validation
Automatic constraint checking:

- Component overlap detection
- Container boundary validation
- Anchor consistency verification
- Performance optimization suggestions

## Success Criteria

### Phase 1 Success

- [ ] Generate accurate SVG from JSON for all budgy panels
- [ ] Visual output matches actual GUI layout
- [ ] Schema handles all current pygame_gui usage patterns

### Phase 2 Success  

- [ ] Extract complete layout from all budgy GUI files
- [ ] Generated JSON validates against schema
- [ ] No loss of layout information during extraction

### Phase 3 Success

- [ ] Generated code compiles without errors
- [ ] Generated code produces equivalent visual layout
- [ ] Round-trip testing passes (code → JSON → code)

### Phase 4 Success

- [ ] Visual designer creates valid JSON layouts
- [ ] Real-time preview matches final output
- [ ] Designer integrates seamlessly with other tools

## Documentation Requirements

### User Documentation

- Installation and setup instructions
- Tool usage examples and tutorials
- JSON schema reference
- Best practices guide

### Developer Documentation

- API reference for each tool
- Extension points for new component types
- Contributing guidelines
- Architecture overview

## Maintenance Plan

### Version Control

- Semantic versioning for JSON schema
- Backward compatibility for existing layouts
- Migration tools for schema updates

### Testing Strategy

- Automated testing for all tools
- Continuous integration setup
- Visual regression testing for SVG output
- Performance benchmarking

This comprehensive toolchain will provide a complete solution for pygame_gui layout design, documentation, and maintenance, significantly improving the development workflow for GUI applications.
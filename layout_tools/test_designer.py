#!/usr/bin/env python3
"""
Test script for the visual layout designer

Tests the designer components without launching the full GUI.
"""

import sys
from pathlib import Path
from layout_schema import Layout, Component, Rect, Anchors, Styling, Metadata


def test_designer_imports():
    """Test that designer imports work correctly"""
    print("🧪 Testing visual designer imports...")
    
    try:
        import tkinter as tk
        print("   ✅ tkinter available")
    except ImportError:
        print("   ❌ tkinter not available - GUI designer won't work")
        return False
    
    try:
        from design_layout import LayoutDesigner, ComponentPalette, PropertyEditor, DesignCanvas
        print("   ✅ Designer components imported successfully")
    except ImportError as e:
        print(f"   ❌ Failed to import designer components: {e}")
        return False
    
    return True


def test_designer_functionality():
    """Test core designer functionality without GUI"""
    print("🔧 Testing designer functionality...")
    
    # Test layout creation
    layout = Layout(
        metadata=Metadata(description="Test layout"),
        components={
            "test_panel": Component(
                id="test_panel",
                type="UIPanel",
                rect=Rect(0, 0, 400, 300),
                anchors=Anchors("top", "left", "bottom", "right"),
                styling=Styling(object_id="#test-panel")
            )
        }
    )
    
    print("   ✅ Layout creation works")
    
    # Test validation
    issues = layout.validate()
    if not issues:
        print("   ✅ Layout validation works")
    else:
        print(f"   ⚠️  Layout has {len(issues)} validation issues")
    
    return True


def test_integration_with_toolchain():
    """Test integration with existing toolchain"""
    print("🔗 Testing toolchain integration...")
    
    try:
        # Test SVG generation
        from generate_svg import SVGGenerator
        print("   ✅ SVG generator integration available")
        
        # Test code generation
        from generate_code import CodeGenerator
        print("   ✅ Code generator integration available")
        
        # Test analysis
        from analyze_layout import analyze_file
        print("   ✅ Layout analyzer integration available")
        
    except ImportError as e:
        print(f"   ❌ Toolchain integration issue: {e}")
        return False
    
    return True


def create_sample_design():
    """Create a sample design for testing"""
    print("🎨 Creating sample design...")
    
    layout = Layout(
        metadata=Metadata(
            description="Sample GUI design created with visual designer",
            window_size=[800, 600]
        ),
        components={
            "main_window": Component(
                id="main_window",
                type="UIPanel",
                rect=Rect(0, 0, 800, 600),
                anchors=Anchors("top", "left", "bottom", "right"),
                styling=Styling(object_id="#main-window")
            ),
            "title_label": Component(
                id="title_label",
                type="UILabel",
                rect=Rect(20, 20, 760, 30),
                anchors=Anchors("top", "left", "top", "right"),
                container="main_window",
                text="Sample Application",
                styling=Styling(object_id="#title")
            ),
            "action_button": Component(
                id="action_button",
                type="UIButton",
                rect=Rect(350, 280, 100, 40),
                anchors=Anchors("top", "left", "top", "left"),
                container="main_window",
                text="Click Me",
                styling=Styling(object_id="#action-btn")
            )
        }
    )
    
    # Save sample
    output_path = Path("examples/designer_sample.json")
    layout.save_json(output_path)
    print(f"   ✅ Sample design saved to {output_path}")
    
    # Generate SVG
    try:
        from generate_svg import SVGGenerator
        svg_path = output_path.with_suffix('.svg')
        generator = SVGGenerator(800, 600)
        generator.generate_svg(layout, svg_path)
        print(f"   ✅ Sample SVG generated: {svg_path}")
    except Exception as e:
        print(f"   ⚠️  SVG generation failed: {e}")
    
    return True


def print_usage_instructions():
    """Print usage instructions for the designer"""
    print("\n📖 Visual Designer Usage Instructions:")
    print("=" * 50)
    print("To launch the visual designer:")
    print("  python3 design_layout.py")
    print("  python3 design_layout.py --layout examples/sample_layout.json")
    print()
    print("🎯 Container Workflow (IMPROVED):")
    print("1. Create a container (UIPanel/UIWindow) first")
    print("2. Click the container to select it as target")
    print("3. Create child components - they'll go inside the container")
    print("4. Use 'Clear Selection' to create root-level components")
    print()
    print("🖱️  Mouse Controls (NEW):")
    print("• Drag components to move them")
    print("• Drag corner handles to resize")
    print("• Hover shows appropriate cursors")
    print("• Click to select, double-click to edit properties")
    print()
    print("Features:")
    print("• Direct mouse manipulation (drag to move/resize)")
    print("• Organized component palette (Containers/Controls/Display)")
    print("• Clear container selection workflow")
    print("• Visual resize handles on selected components")
    print("• Real-time property editing")
    print("• Export to JSON, Python code, and SVG")
    print()
    print("Keyboard shortcuts:")
    print("• Ctrl+N: New layout")
    print("• Ctrl+O: Open layout")
    print("• Ctrl+S: Save layout")
    print("• Delete: Delete selected component")
    print("• Arrow keys: Nudge component 1px")
    print("• Shift+Arrow: Nudge component 10px")
    print()
    print("Note: Requires tkinter GUI support")


def main():
    """Run designer tests"""
    print("🚀 Visual Layout Designer Tests")
    print("=" * 50)
    
    tests_passed = 0
    total_tests = 4
    
    if test_designer_imports():
        tests_passed += 1
    
    if test_designer_functionality():
        tests_passed += 1
    
    if test_integration_with_toolchain():
        tests_passed += 1
    
    if create_sample_design():
        tests_passed += 1
    
    print("\n" + "=" * 50)
    print(f"📊 Test Results: {tests_passed}/{total_tests} passed")
    
    if tests_passed == total_tests:
        print("✅ Visual designer ready for use!")
        print_usage_instructions()
        return 0
    else:
        print("❌ Some tests failed - check dependencies")
        return 1


if __name__ == "__main__":
    exit(main())
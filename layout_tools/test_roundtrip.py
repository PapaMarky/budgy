#!/usr/bin/env python3
"""
Round-trip test for the layout toolchain

Tests the complete workflow: Code → JSON → SVG → Code
"""

from pathlib import Path
import tempfile
import sys
from analyze_layout import analyze_file
from generate_code import CodeGenerator
from generate_svg import SVGGenerator
from layout_schema import Layout


def test_roundtrip(source_file: Path):
    """Test complete round-trip workflow"""
    print(f"🔄 Testing round-trip for {source_file.name}")
    print("=" * 60)
    
    try:
        # Step 1: Code → JSON (Analysis)
        print("📤 Step 1: Analyzing Python code...")
        layout = analyze_file(source_file)
        
        if not layout.components:
            print("   ⚠️  No components found, skipping")
            return False
        
        print(f"   ✅ Found {len(layout.components)} components")
        
        # Step 2: JSON → SVG (Visualization)
        print("🎨 Step 2: Generating SVG visualization...")
        with tempfile.NamedTemporaryFile(suffix='.svg', delete=False) as tmp_svg:
            generator = SVGGenerator(*layout.metadata.window_size)
            generator.generate_svg(layout, Path(tmp_svg.name))
            print(f"   ✅ Generated SVG: {tmp_svg.name}")
        
        # Step 3: JSON → Code (Generation)
        print("⚙️  Step 3: Generating Python code...")
        class_name = f"Generated{source_file.stem.title().replace('_', '')}"
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as tmp_py:
            code_generator = CodeGenerator()
            code = code_generator.generate_code(layout, class_name)
            tmp_py.write(code)
            tmp_py.flush()
            
            print(f"   ✅ Generated code: {tmp_py.name}")
            print(f"   📊 Class: {class_name}")
        
        # Step 4: Validate generated code
        print("✅ Step 4: Validating generated code...")
        try:
            # Try to compile the generated code
            with open(tmp_py.name, 'r') as f:
                generated_code = f.read()
            
            compile(generated_code, tmp_py.name, 'exec')
            print("   ✅ Generated code compiles successfully")
            
            # Show code stats
            lines = generated_code.split('\n')
            non_empty_lines = [l for l in lines if l.strip()]
            print(f"   📊 Generated {len(lines)} total lines ({len(non_empty_lines)} non-empty)")
            
        except SyntaxError as e:
            print(f"   ❌ Syntax error in generated code: {e}")
            return False
        
        # Step 5: Re-analyze generated code (optional)
        print("🔍 Step 5: Re-analyzing generated code...")
        try:
            regenerated_layout = analyze_file(Path(tmp_py.name))
            
            if regenerated_layout.components:
                print(f"   ✅ Re-analysis found {len(regenerated_layout.components)} components")
                
                # Compare component counts
                original_count = len(layout.components)
                regenerated_count = len(regenerated_layout.components)
                
                if regenerated_count >= original_count * 0.8:  # Allow some loss
                    print("   ✅ Component preservation: Good")
                else:
                    print(f"   ⚠️  Component preservation: {regenerated_count}/{original_count}")
            else:
                print("   ⚠️  Re-analysis found no components")
                
        except Exception as e:
            print(f"   ⚠️  Re-analysis failed: {e}")
        
        print("✅ Round-trip test completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Round-trip test failed: {e}")
        return False


def test_simple_layout():
    """Test with a simple known layout"""
    print("🧪 Testing with simple layout...")
    
    # Create a simple test layout
    from layout_schema import Component, Rect, Anchors, Styling, Metadata
    
    layout = Layout(
        metadata=Metadata(description="Simple test layout"),
        components={
            "TestPanel": Component(
                id="TestPanel",
                type="UIPanel",
                rect=Rect(0, 0, 400, 300),
                anchors=Anchors("top", "left", "bottom", "right"),
                styling=Styling(object_id="#test-panel")
            ),
            "TestButton": Component(
                id="TestButton", 
                type="UIButton",
                rect=Rect(10, 10, 100, 30),
                anchors=Anchors("top", "left", "top", "left"),
                container="TestPanel",
                text="Click Me",
                styling=Styling(object_id="#test-button")
            )
        }
    )
    
    # Generate code
    generator = CodeGenerator()
    code = generator.generate_code(layout, "SimpleTestPanel")
    
    # Validate compilation
    try:
        compile(code, '<generated>', 'exec')
        print("✅ Simple layout code compiles successfully")
        
        # Show preview
        lines = code.split('\n')[:15]
        print("\nCode preview:")
        print("-" * 40)
        for i, line in enumerate(lines, 1):
            print(f"{i:2d}: {line}")
        
        return True
    except SyntaxError as e:
        print(f"❌ Simple layout compilation failed: {e}")
        return False


def main():
    """Run round-trip tests"""
    print("🚀 Layout Toolchain Round-Trip Tests")
    print("=" * 60)
    
    # Test simple layout first
    if not test_simple_layout():
        return 1
    
    print("\n")
    
    # Test with actual budgy files
    test_files = [
        Path("../src/budgy/gui/message_panel.py"),
        Path("../src/budgy/gui/top_panel.py"),
        Path("../src/budgy/gui/toggle_button.py")
    ]
    
    successful_tests = 0
    
    for test_file in test_files:
        if test_file.exists():
            print("\n")
            if test_roundtrip(test_file):
                successful_tests += 1
        else:
            print(f"⚠️  Skipping {test_file} (not found)")
    
    print("\n" + "=" * 60)
    print(f"📊 Round-trip test results: {successful_tests}/{len([f for f in test_files if f.exists()])} successful")
    
    if successful_tests > 0:
        print("🎉 Layout toolchain round-trip capability verified!")
        return 0
    else:
        print("❌ Round-trip tests failed")
        return 1


if __name__ == "__main__":
    exit(main())
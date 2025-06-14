#!/usr/bin/env python3
"""
Test script for the layout analyzer

Tests the analyzer on all pygame_gui files in the budgy project
and generates a comprehensive report.
"""

from pathlib import Path
import sys
from analyze_layout import analyze_file
from generate_svg import SVGGenerator


def test_all_gui_files():
    """Test analyzer on all GUI files"""
    base_path = Path("../src/budgy/gui")
    
    # Find all Python files
    gui_files = list(base_path.glob("*.py"))
    gui_files = [f for f in gui_files if f.name != "__init__.py"]
    
    print(f"Testing analyzer on {len(gui_files)} GUI files...")
    print("=" * 60)
    
    total_components = 0
    successful_files = 0
    
    for gui_file in gui_files:
        print(f"\n📄 {gui_file.name}")
        print("-" * 40)
        
        try:
            layout = analyze_file(gui_file)
            
            if layout.components:
                successful_files += 1
                file_components = len(layout.components)
                total_components += file_components
                
                print(f"✅ Found {file_components} components:")
                
                # Group components by type
                by_type = {}
                for comp in layout.components.values():
                    if comp.type not in by_type:
                        by_type[comp.type] = []
                    by_type[comp.type].append(comp.id)
                
                for comp_type, ids in by_type.items():
                    print(f"   {comp_type}: {', '.join(ids)}")
                
                # Check for validation issues
                issues = layout.validate()
                if issues:
                    print(f"   ⚠️  {len(issues)} validation issues:")
                    for issue in issues[:3]:  # Show first 3 issues
                        print(f"      - {issue}")
                    if len(issues) > 3:
                        print(f"      ... and {len(issues) - 3} more")
                else:
                    print("   ✅ Validation passed")
                
                # Save outputs
                json_path = Path(f"test_outputs/{gui_file.stem}.json")
                json_path.parent.mkdir(exist_ok=True)
                layout.save_json(json_path)
                
                # Generate SVG
                svg_path = json_path.with_suffix('.svg')
                try:
                    generator = SVGGenerator(*layout.metadata.window_size)
                    generator.generate_svg(layout, svg_path)
                    print(f"   📊 Generated: {svg_path.name}")
                except Exception as e:
                    print(f"   ❌ SVG generation failed: {e}")
                
            else:
                print("   ℹ️  No pygame_gui components found")
                
        except Exception as e:
            print(f"   ❌ Analysis failed: {e}")
    
    print("\n" + "=" * 60)
    print(f"📊 SUMMARY")
    print(f"Files analyzed: {len(gui_files)}")
    print(f"Files with components: {successful_files}")
    print(f"Total components found: {total_components}")
    print(f"Average components per file: {total_components / max(successful_files, 1):.1f}")


def generate_master_layout():
    """Generate a master layout combining all components"""
    print("\n🔗 Generating master layout...")
    
    # This would combine all layouts - for now just report
    test_outputs = Path("test_outputs")
    if test_outputs.exists():
        json_files = list(test_outputs.glob("*.json"))
        print(f"Generated {len(json_files)} layout files in test_outputs/")
        
        # List all component types found
        all_types = set()
        for json_file in json_files:
            try:
                from layout_schema import Layout
                layout = Layout.load_json(json_file)
                for comp in layout.components.values():
                    all_types.add(comp.type)
            except:
                pass
        
        print(f"Component types discovered: {', '.join(sorted(all_types))}")


if __name__ == "__main__":
    test_all_gui_files()
    generate_master_layout()
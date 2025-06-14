#!/usr/bin/env python3
"""
Visual Layout Designer for pygame_gui Components

Interactive tool for creating and editing pygame_gui layouts with drag-and-drop
interface, real-time preview, and integration with the layout toolchain.
"""

import argparse
import json
from pathlib import Path
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from typing import Dict, List, Optional, Tuple, Any
import subprocess
import tempfile

from layout_schema import Layout, Component, Rect, Anchors, Styling, Metadata, COMPONENT_TYPES


class ComponentPalette:
    """Component palette for drag-and-drop creation"""
    
    def __init__(self, parent: tk.Widget, designer: 'LayoutDesigner'):
        self.parent = parent
        self.designer = designer
        self.frame = ttk.LabelFrame(parent, text="Component Palette", padding="5")
        
        # Component types organized by category
        self.container_types = ["UIPanel", "UIWindow"]
        self.control_types = ["UILabel", "UIButton", "UIDropDownMenu", "UITextEntryLine"]
        self.display_types = ["UIProgressBar", "UIImage"]
        
        # Track buttons for selection highlighting
        self.component_buttons = {}  # component_type -> button
        self.button_original_state = {}  # component_type -> (text, font, relief, bd)
        self.selected_button = None
        
        self._create_palette()
    
    def _create_palette(self):
        """Create component palette UI"""
        # Instructions
        instructions = ttk.Label(self.frame, text="1. Create containers first\n2. Select container\n3. Add child components", 
                               font=('Arial', 9), foreground='blue')
        instructions.pack(pady=5)
        
        # Container section
        container_frame = ttk.LabelFrame(self.frame, text="📦 Containers", padding="3")
        container_frame.pack(fill='x', pady=2)
        
        for comp_type in self.container_types:
            # Use ttk.Button for better macOS compatibility
            btn = ttk.Button(
                container_frame,
                text=comp_type,
                width=15,
                command=lambda ct=comp_type: self._select_component_type(ct)
            )
            btn.pack(pady=1, fill='x')
            self.component_buttons[comp_type] = btn
            
            # Store original state for ttk button
            self.button_original_state[comp_type] = {
                'text': comp_type,
                'style': 'TButton'
            }
        
        # Controls section
        controls_frame = ttk.LabelFrame(self.frame, text="🎛️ Controls", padding="3")
        controls_frame.pack(fill='x', pady=2)
        
        for comp_type in self.control_types:
            # Use ttk.Button for better macOS compatibility
            btn = ttk.Button(
                controls_frame,
                text=comp_type,
                width=15,
                command=lambda ct=comp_type: self._select_component_type(ct)
            )
            btn.pack(pady=1, fill='x')
            self.component_buttons[comp_type] = btn
            
            # Store original state for ttk button
            self.button_original_state[comp_type] = {
                'text': comp_type,
                'style': 'TButton'
            }
        
        # Display section
        display_frame = ttk.LabelFrame(self.frame, text="📊 Display", padding="3")
        display_frame.pack(fill='x', pady=2)
        
        for comp_type in self.display_types:
            # Use ttk.Button for better macOS compatibility
            btn = ttk.Button(
                display_frame,
                text=comp_type,
                width=15,
                command=lambda ct=comp_type: self._select_component_type(ct)
            )
            btn.pack(pady=1, fill='x')
            self.component_buttons[comp_type] = btn
            
            # Store original state for ttk button
            self.button_original_state[comp_type] = {
                'text': comp_type,
                'style': 'TButton'
            }
        
        # Add separator
        ttk.Separator(self.frame, orient='horizontal').pack(fill='x', pady=5)
        
        # Current container selection
        self.container_frame = ttk.LabelFrame(self.frame, text="🎯 Target Container", padding="3")
        self.container_frame.pack(fill='x', pady=2)
        
        self.container_var = tk.StringVar(value="None (root level)")
        self.container_label = ttk.Label(self.container_frame, textvariable=self.container_var, 
                                       font=('Arial', 9, 'bold'), foreground='green')
        self.container_label.pack()
        
        ttk.Button(
            self.container_frame,
            text="Clear Selection",
            command=self.designer.clear_container_selection
        ).pack(fill='x', pady=2)
        
        # Layout tools
        tools_frame = ttk.LabelFrame(self.frame, text="🔧 Tools", padding="3")
        tools_frame.pack(fill='x', pady=2)
        
        ttk.Button(
            tools_frame, 
            text="Auto Layout",
            command=self.designer.auto_layout
        ).pack(pady=1, fill='x')
        
        ttk.Button(
            tools_frame,
            text="Validate Layout", 
            command=self.designer.validate_layout
        ).pack(pady=1, fill='x')
        
        ttk.Button(
            tools_frame,
            text="Delete Selected",
            command=self.designer.delete_component
        ).pack(pady=1, fill='x')
    
    def _select_component_type(self, component_type: str):
        """Select component type and highlight button"""
        # Clear previous selection
        if self.selected_button:
            # Restore original state
            prev_type = self.selected_button
            original_state = self.button_original_state[prev_type]
            self.component_buttons[prev_type].config(
                text=original_state['text']
            )
        
        # Highlight new selection
        self.selected_button = component_type
        button = self.component_buttons[component_type]
        button.config(
            text=f"▶ {component_type}"  # Add arrow indicator
        )
        
        # Start component creation
        self.designer.start_component_creation(component_type)
    
    def clear_selection(self):
        """Clear component type selection"""
        if self.selected_button:
            # Restore original state
            selected_type = self.selected_button
            original_state = self.button_original_state[selected_type]
            self.component_buttons[selected_type].config(
                text=original_state['text']
            )
            self.selected_button = None
    
    def update_container_selection(self, container_name: str):
        """Update the selected container display"""
        if container_name:
            self.container_var.set(f"📦 {container_name}")
        else:
            self.container_var.set("None (root level)")


class PropertyEditor:
    """Property editor for selected components"""
    
    def __init__(self, parent: tk.Widget, designer: 'LayoutDesigner'):
        self.parent = parent
        self.designer = designer
        self.frame = ttk.LabelFrame(parent, text="Properties", padding="5")
        self.current_component: Optional[Component] = None
        self.property_vars: Dict[str, tk.Variable] = {}
        
        self._create_editor()
    
    def _create_editor(self):
        """Create property editor UI"""
        # Component info
        self.info_frame = ttk.Frame(self.frame)
        self.info_frame.pack(fill='x', pady=5)
        
        ttk.Label(self.info_frame, text="Component:").pack(anchor='w')
        self.component_label = ttk.Label(self.info_frame, text="None selected", font=('Arial', 10, 'bold'))
        self.component_label.pack(anchor='w')
        
        # Property notebook
        self.notebook = ttk.Notebook(self.frame)
        self.notebook.pack(fill='both', expand=True, pady=5)
        
        # Position/Size tab
        self.pos_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.pos_frame, text="Position")
        self._create_position_editor()
        
        # Styling tab
        self.style_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.style_frame, text="Style")
        self._create_style_editor()
        
        # Anchors tab
        self.anchor_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.anchor_frame, text="Anchors")
        self._create_anchor_editor()
    
    def _create_position_editor(self):
        """Create position/size property editor"""
        # Position
        pos_group = ttk.LabelFrame(self.pos_frame, text="Position", padding="5")
        pos_group.pack(fill='x', pady=2)
        
        self.property_vars['x'] = tk.IntVar()
        self.property_vars['y'] = tk.IntVar()
        self.property_vars['w'] = tk.IntVar()
        self.property_vars['h'] = tk.IntVar()
        
        for i, (label, var) in enumerate([('X:', 'x'), ('Y:', 'y'), ('Width:', 'w'), ('Height:', 'h')]):
            row = i // 2
            col = (i % 2) * 2
            
            ttk.Label(pos_group, text=label).grid(row=row, column=col, sticky='w', padx=2)
            entry = ttk.Entry(pos_group, textvariable=self.property_vars[var], width=8)
            entry.grid(row=row, column=col+1, padx=2, pady=1)
            entry.bind('<Return>', self._update_component)
    
    def _create_style_editor(self):
        """Create style property editor"""
        # Text content
        text_group = ttk.LabelFrame(self.style_frame, text="Content", padding="5")
        text_group.pack(fill='x', pady=2)
        
        self.property_vars['text'] = tk.StringVar()
        ttk.Label(text_group, text="Text:").pack(anchor='w')
        text_entry = ttk.Entry(text_group, textvariable=self.property_vars['text'])
        text_entry.pack(fill='x', pady=2)
        text_entry.bind('<Return>', self._update_component)
        
        # Object ID
        id_group = ttk.LabelFrame(self.style_frame, text="Styling", padding="5")
        id_group.pack(fill='x', pady=2)
        
        self.property_vars['object_id'] = tk.StringVar()
        ttk.Label(id_group, text="Object ID:").pack(anchor='w')
        id_entry = ttk.Entry(id_group, textvariable=self.property_vars['object_id'])
        id_entry.pack(fill='x', pady=2)
        id_entry.bind('<Return>', self._update_component)
    
    def _create_anchor_editor(self):
        """Create anchor property editor"""
        anchor_group = ttk.LabelFrame(self.anchor_frame, text="Anchors", padding="5")
        anchor_group.pack(fill='x', pady=2)
        
        self.property_vars['top'] = tk.StringVar(value="top")
        self.property_vars['bottom'] = tk.StringVar(value="top")
        self.property_vars['left'] = tk.StringVar(value="left")
        self.property_vars['right'] = tk.StringVar(value="left")
        
        anchor_options = ["top", "bottom", "left", "right"]
        
        for anchor in ['top', 'bottom', 'left', 'right']:
            frame = ttk.Frame(anchor_group)
            frame.pack(fill='x', pady=1)
            
            ttk.Label(frame, text=f"{anchor.title()}:", width=8).pack(side='left')
            combo = ttk.Combobox(frame, textvariable=self.property_vars[anchor], 
                               values=anchor_options, state='readonly', width=10)
            combo.pack(side='left', padx=5)
            combo.bind('<<ComboboxSelected>>', self._update_component)
    
    def _update_component(self, event=None):
        """Update current component with property changes"""
        if not self.current_component:
            return
        
        try:
            # Update rect
            self.current_component.rect.x = self.property_vars['x'].get()
            self.current_component.rect.y = self.property_vars['y'].get()
            self.current_component.rect.w = self.property_vars['w'].get()
            self.current_component.rect.h = self.property_vars['h'].get()
            
            # Update text
            self.current_component.text = self.property_vars['text'].get()
            
            # Update styling
            self.current_component.styling.object_id = self.property_vars['object_id'].get()
            
            # Update anchors
            self.current_component.anchors.top = self.property_vars['top'].get()
            self.current_component.anchors.bottom = self.property_vars['bottom'].get()
            self.current_component.anchors.left = self.property_vars['left'].get()
            self.current_component.anchors.right = self.property_vars['right'].get()
            
            # Refresh canvas
            self.designer.refresh_canvas()
            
        except tk.TclError:
            pass  # Ignore invalid input during typing
    
    def select_component(self, component: Optional[Component]):
        """Select component for editing"""
        self.current_component = component
        
        if component:
            self.component_label.config(text=f"{component.type} ({component.id})")
            
            # Update property values
            self.property_vars['x'].set(component.rect.x)
            self.property_vars['y'].set(component.rect.y)
            self.property_vars['w'].set(component.rect.w)
            self.property_vars['h'].set(component.rect.h)
            self.property_vars['text'].set(component.text)
            self.property_vars['object_id'].set(component.styling.object_id or "")
            self.property_vars['top'].set(component.anchors.top)
            self.property_vars['bottom'].set(component.anchors.bottom)
            self.property_vars['left'].set(component.anchors.left)
            self.property_vars['right'].set(component.anchors.right)
        else:
            self.component_label.config(text="None selected")


class DesignCanvas:
    """Canvas for visual layout design"""
    
    def __init__(self, parent: tk.Widget, designer: 'LayoutDesigner'):
        self.parent = parent
        self.designer = designer
        self.canvas = tk.Canvas(parent, bg='white', width=800, height=600, highlightthickness=1)
        
        # Scrollbars
        h_scroll = ttk.Scrollbar(parent, orient='horizontal', command=self.canvas.xview)
        v_scroll = ttk.Scrollbar(parent, orient='vertical', command=self.canvas.yview)
        self.canvas.configure(xscrollcommand=h_scroll.set, yscrollcommand=v_scroll.set)
        
        # Grid layout
        self.canvas.grid(row=0, column=0, sticky='nsew')
        h_scroll.grid(row=1, column=0, sticky='ew')
        v_scroll.grid(row=0, column=1, sticky='ns')
        
        parent.grid_rowconfigure(0, weight=1)
        parent.grid_columnconfigure(0, weight=1)
        
        # Canvas state
        self.scale = 1.0
        self.selected_item = None
        self.drag_start = None
        self.component_items: Dict[str, int] = {}  # component_id -> canvas_item_id
        self.resize_handles: Dict[str, List[int]] = {}  # component_id -> handle_ids
        self.resize_mode = None  # None, 'move', 'resize-nw', 'resize-ne', 'resize-sw', 'resize-se'
        self.resize_handle_size = 8
        
        # Bind events
        self.canvas.bind('<Button-1>', self._on_click)
        self.canvas.bind('<B1-Motion>', self._on_drag)
        self.canvas.bind('<ButtonRelease-1>', self._on_release)
        self.canvas.bind('<Double-Button-1>', self._on_double_click)
        self.canvas.bind('<MouseWheel>', self._on_scroll)
        self.canvas.bind('<Motion>', self._on_mouse_move)
        self.canvas.bind('<Button-2>', self._on_right_click)  # macOS right-click
        self.canvas.bind('<Button-3>', self._on_right_click)  # Linux/Windows right-click
        
        # Set scroll region
        self.canvas.configure(scrollregion=(0, 0, 1280, 960))
    
    def _on_click(self, event):
        """Handle canvas click"""
        # Ensure canvas has focus for keyboard events
        self.canvas.focus_set()
        
        x, y = self.canvas.canvasx(event.x), self.canvas.canvasy(event.y)
        
        # Check if clicking on resize handle
        handle_info = self._find_resize_handle(x, y)
        if handle_info:
            component_id, handle_type = handle_info
            component = self.designer.layout.components.get(component_id)
            if component:
                self.select_component(component)
                self.resize_mode = handle_type
                self.drag_start = (x, y)
                self._set_cursor_for_resize_mode(handle_type)
                return
        
        # Find clicked item
        closest = self.canvas.find_closest(x, y)
        if not closest:
            self.select_component(None)
            self.resize_mode = None
            self.canvas.config(cursor="")
            return
        
        item = closest[0]
        
        # Find component
        component = self._find_component_by_canvas_item(item)
        if component:
            self.select_component(component)
            self.resize_mode = 'move'
            self.drag_start = (x, y)
            self.canvas.config(cursor="fleur")  # Move cursor
        else:
            self.select_component(None)
            self.resize_mode = None
            self.canvas.config(cursor="")
    
    def _on_drag(self, event):
        """Handle canvas drag"""
        if not self.selected_item or not self.drag_start or not self.resize_mode:
            return
        
        x, y = self.canvas.canvasx(event.x), self.canvas.canvasy(event.y)
        dx = int((x - self.drag_start[0]) / self.scale)
        dy = int((y - self.drag_start[1]) / self.scale)
        
        # Skip tiny movements to avoid jitter
        if abs(dx) < 1 and abs(dy) < 1:
            return
        
        component = self._find_component_by_canvas_item(self.selected_item)
        if not component:
            return
        
        if self.resize_mode == 'move':
            # Move component
            component.rect.x += dx
            component.rect.y += dy
            
            # Move canvas items directly for smooth dragging
            self._move_canvas_items(component, dx * self.scale, dy * self.scale)
            
        elif self.resize_mode.startswith('resize-'):
            # Resize component
            old_rect = Rect(component.rect.x, component.rect.y, component.rect.w, component.rect.h)
            self._resize_component(component, self.resize_mode, dx, dy)
            
            # Update canvas items directly for smooth resizing
            self._resize_canvas_items(component, old_rect)
        
        # Update property editor
        self.designer.property_editor.select_component(component)
        
        self.drag_start = (x, y)
    
    def _on_release(self, event):
        """Handle drag release"""
        # If we were dragging or resizing, do a final refresh to ensure everything is properly positioned
        if self.resize_mode:
            self.designer.refresh_canvas()
        
        self.drag_start = None
        self.resize_mode = None
        self.canvas.config(cursor="")
    
    def _on_mouse_move(self, event):
        """Handle mouse movement for cursor changes"""
        if self.drag_start:  # Don't change cursor while dragging
            return
        
        x, y = self.canvas.canvasx(event.x), self.canvas.canvasy(event.y)
        
        # Check if over resize handle
        handle_info = self._find_resize_handle(x, y)
        if handle_info:
            _, handle_type = handle_info
            self._set_cursor_for_resize_mode(handle_type)
        else:
            # Check if over component
            closest = self.canvas.find_closest(x, y)
            if closest:
                item = closest[0]
                component = self._find_component_by_canvas_item(item)
                if component:
                    self.canvas.config(cursor="fleur")
                else:
                    self.canvas.config(cursor="")
            else:
                self.canvas.config(cursor="")
    
    def _on_double_click(self, event):
        """Handle double-click for editing"""
        x, y = self.canvas.canvasx(event.x), self.canvas.canvasy(event.y)
        closest = self.canvas.find_closest(x, y)
        if not closest:
            return
        
        item = closest[0]
        component = self._find_component_by_canvas_item(item)
        
        if component:
            # Switch to property editor
            self.designer.property_editor.notebook.select(1)  # Style tab
    
    def _on_right_click(self, event):
        """Handle right-click for context menu"""
        x, y = self.canvas.canvasx(event.x), self.canvas.canvasy(event.y)
        closest = self.canvas.find_closest(x, y)
        if not closest:
            return
        
        item = closest[0]
        component = self._find_component_by_canvas_item(item)
        
        if component:
            # Select the component first
            self.select_component(component)
            
            # Create context menu
            context_menu = tk.Menu(self.canvas, tearoff=0)
            context_menu.add_command(
                label=f"Delete {component.type}",
                command=lambda: self.designer.delete_component()
            )
            context_menu.add_command(
                label=f"Duplicate {component.type}",
                command=lambda: self.designer.duplicate_component()
            )
            context_menu.add_separator()
            context_menu.add_command(
                label="Properties",
                command=lambda: self.designer.property_editor.notebook.select(1)
            )
            
            # Show context menu
            try:
                context_menu.tk_popup(event.x_root, event.y_root)
            finally:
                context_menu.grab_release()
    
    def _on_scroll(self, event):
        """Handle mouse wheel for zoom"""
        if event.state & 0x4:  # Ctrl key
            factor = 1.1 if event.delta > 0 else 0.9
            self.scale *= factor
            self.designer.refresh_canvas()
        else:
            # Scroll
            self.canvas.yview_scroll(-1 * (event.delta // 120), "units")
    
    def _find_component_by_canvas_item(self, item_id: int) -> Optional[Component]:
        """Find component by canvas item ID"""
        for comp_id, canvas_id in self.component_items.items():
            if canvas_id == item_id:
                return self.designer.layout.components.get(comp_id)
        return None
    
    def _find_resize_handle(self, x: float, y: float) -> Optional[Tuple[str, str]]:
        """Find resize handle at given position"""
        for comp_id, handle_ids in self.resize_handles.items():
            for i, handle_id in enumerate(handle_ids):
                bbox = self.canvas.bbox(handle_id)
                if bbox and bbox[0] <= x <= bbox[2] and bbox[1] <= y <= bbox[3]:
                    handle_types = ['resize-nw', 'resize-ne', 'resize-sw', 'resize-se']
                    return comp_id, handle_types[i]
        return None
    
    def _set_cursor_for_resize_mode(self, resize_mode: str):
        """Set cursor based on resize mode"""
        cursors = {
            'resize-nw': 'top_left_corner',
            'resize-ne': 'top_right_corner', 
            'resize-sw': 'bottom_left_corner',
            'resize-se': 'bottom_right_corner'
        }
        self.canvas.config(cursor=cursors.get(resize_mode, ''))
    
    def _resize_component(self, component: Component, resize_mode: str, dx: int, dy: int):
        """Resize component based on mode and delta"""
        rect = component.rect
        
        if resize_mode == 'resize-nw':
            # Top-left corner
            rect.x += dx
            rect.y += dy
            rect.w -= dx
            rect.h -= dy
        elif resize_mode == 'resize-ne':
            # Top-right corner  
            rect.y += dy
            rect.w += dx
            rect.h -= dy
        elif resize_mode == 'resize-sw':
            # Bottom-left corner
            rect.x += dx
            rect.w -= dx
            rect.h += dy
        elif resize_mode == 'resize-se':
            # Bottom-right corner
            rect.w += dx
            rect.h += dy
        
        # Enforce minimum size
        min_size = 20
        if rect.w < min_size:
            if resize_mode in ['resize-nw', 'resize-sw']:
                rect.x -= (min_size - rect.w)
            rect.w = min_size
        if rect.h < min_size:
            if resize_mode in ['resize-nw', 'resize-ne']:
                rect.y -= (min_size - rect.h)
            rect.h = min_size
    
    def select_component(self, component: Optional[Component]):
        """Select component"""
        # Clear previous selection
        if self.selected_item:
            self.canvas.itemconfig(self.selected_item, outline='black', width=2)
            # Remove old resize handles
            old_comp = self._find_component_by_canvas_item(self.selected_item)
            if old_comp:
                self._remove_resize_handles(old_comp.id)
        
        if component:
            item_id = self.component_items.get(component.id)
            if item_id:
                self.selected_item = item_id
                self.canvas.itemconfig(item_id, outline='red', width=3)
                # Add resize handles
                self._add_resize_handles(component)
            
            # Update property editor
            self.designer.property_editor.select_component(component)
            
            # If it's a container, allow setting it as target
            if component.type in ["UIPanel", "UIWindow"]:
                self.designer.set_container_selection(component.id)
        else:
            self.selected_item = None
            self.designer.property_editor.select_component(None)
    
    def _add_resize_handles(self, component: Component):
        """Add resize handles to selected component"""
        rect = component.rect
        size = self.resize_handle_size
        
        # Scale coordinates
        x1 = rect.x * self.scale
        y1 = rect.y * self.scale
        x2 = (rect.x + rect.w) * self.scale
        y2 = (rect.y + rect.h) * self.scale
        
        # Create corner handles
        handles = []
        positions = [
            (x1 - size//2, y1 - size//2),  # NW
            (x2 - size//2, y1 - size//2),  # NE
            (x1 - size//2, y2 - size//2),  # SW
            (x2 - size//2, y2 - size//2),  # SE
        ]
        
        for px, py in positions:
            handle = self.canvas.create_rectangle(
                px, py, px + size, py + size,
                fill='white', outline='red', width=2,
                tags=f'resize_handle_{component.id}'
            )
            handles.append(handle)
        
        self.resize_handles[component.id] = handles
    
    def _remove_resize_handles(self, component_id: str):
        """Remove resize handles for component"""
        if component_id in self.resize_handles:
            for handle in self.resize_handles[component_id]:
                self.canvas.delete(handle)
            del self.resize_handles[component_id]
    
    def _move_canvas_items(self, component: Component, dx: float, dy: float):
        """Move canvas items directly for smooth dragging"""
        # Move the main component item
        if component.id in self.component_items:
            item_id = self.component_items[component.id]
            self.canvas.move(item_id, dx, dy)
            
            # Move all items with the same tag (text, etc.)
            for item in self.canvas.find_withtag(component.id):
                if item != item_id:  # Don't move the main item twice
                    self.canvas.move(item, dx, dy)
        
        # Move resize handles if they exist
        if component.id in self.resize_handles:
            for handle in self.resize_handles[component.id]:
                self.canvas.move(handle, dx, dy)
    
    def _resize_canvas_items(self, component: Component, old_rect: Rect):
        """Resize canvas items directly for smooth resizing"""
        if component.id not in self.component_items:
            return
        
        item_id = self.component_items[component.id]
        rect = component.rect
        
        # Scale coordinates
        x1 = rect.x * self.scale
        y1 = rect.y * self.scale
        x2 = (rect.x + rect.w) * self.scale
        y2 = (rect.y + rect.h) * self.scale
        
        # Update the main rectangle
        self.canvas.coords(item_id, x1, y1, x2, y2)
        
        # Update text position (center of rectangle)
        text_items = [item for item in self.canvas.find_withtag(component.id) 
                     if self.canvas.type(item) == 'text']
        for text_item in text_items:
            self.canvas.coords(text_item, (x1 + x2) / 2, (y1 + y2) / 2)
        
        # Remove and recreate resize handles with new positions
        self._remove_resize_handles(component.id)
        self._add_resize_handles(component)
    
    def clear(self):
        """Clear canvas"""
        self.canvas.delete('all')
        self.component_items.clear()
        self.resize_handles.clear()
        self.selected_item = None
        self.resize_mode = None
    
    def draw_layout(self, layout: Layout):
        """Draw layout on canvas"""
        self.clear()
        
        # Sort components by hierarchy (containers first)
        components = sorted(layout.components.values(), 
                          key=lambda c: (c.container is not None, c.rect.y, c.rect.x))
        
        for component in components:
            self._draw_component(component)
    
    def _draw_component(self, component: Component):
        """Draw single component"""
        rect = component.rect
        
        # Scale coordinates
        x1 = rect.x * self.scale
        y1 = rect.y * self.scale
        x2 = (rect.x + rect.w) * self.scale
        y2 = (rect.y + rect.h) * self.scale
        
        # Get colors
        colors = COMPONENT_TYPES.get(component.type, {"color": "#F5F5F5", "stroke": "#999999"})
        fill_color = colors["color"]
        outline_color = colors["stroke"]
        
        # Draw rectangle with special styling for containers
        outline_width = 3 if component.type in ["UIPanel", "UIWindow"] else 2
        outline_style = 'solid' if not component.container else 'dashed'
        
        item_id = self.canvas.create_rectangle(
            x1, y1, x2, y2,
            fill=fill_color,
            outline=outline_color,
            width=outline_width,
            tags=component.id
        )
        
        self.component_items[component.id] = item_id
        
        # Draw text
        if rect.w > 50 and rect.h > 20:  # Only if enough space
            text = component.type
            if component.text:
                text += f'\n"{component.text}"'
            
            self.canvas.create_text(
                (x1 + x2) / 2, (y1 + y2) / 2,
                text=text,
                font=('Arial', max(8, int(10 * self.scale))),
                fill='black',
                tags=component.id
            )


class LayoutDesigner:
    """Main layout designer application"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("pygame_gui Layout Designer")
        self.root.geometry("1200x800")
        
        self.layout = Layout(
            metadata=Metadata(description="New Layout"),
            components={}
        )
        
        self.component_counter = 0
        self.creating_component_type = None
        self.selected_container = None  # Container for new components
        
        self._create_ui()
    
    def _create_ui(self):
        """Create main UI"""
        # Menu bar
        self._create_menu()
        
        # Main layout
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill='both', expand=True, padx=5, pady=5)
        
        # Left panel (palette + properties)
        left_panel = ttk.Frame(main_frame, width=300)
        left_panel.pack(side='left', fill='y', padx=(0, 5))
        left_panel.pack_propagate(False)
        
        # Component palette
        self.palette = ComponentPalette(left_panel, self)
        self.palette.frame.pack(fill='x', pady=(0, 5))
        
        # Property editor
        self.property_editor = PropertyEditor(left_panel, self)
        self.property_editor.frame.pack(fill='both', expand=True)
        
        # Canvas area
        canvas_frame = ttk.LabelFrame(main_frame, text="Layout Canvas", padding="5")
        canvas_frame.pack(side='left', fill='both', expand=True)
        
        self.canvas = DesignCanvas(canvas_frame, self)
        
        # Add canvas key bindings for better keyboard handling
        self.canvas.canvas.bind('<Delete>', lambda e: self.delete_component())
        self.canvas.canvas.bind('<BackSpace>', lambda e: self.delete_component())
        
        # Status bar
        self.status_var = tk.StringVar(value="Ready")
        status_bar = ttk.Label(self.root, textvariable=self.status_var, relief='sunken')
        status_bar.pack(side='bottom', fill='x')
    
    def _create_menu(self):
        """Create menu bar"""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="New", command=self.new_layout, accelerator="Ctrl+N")
        file_menu.add_command(label="Open...", command=self.open_layout, accelerator="Ctrl+O")
        file_menu.add_command(label="Save", command=self.save_layout, accelerator="Ctrl+S")
        file_menu.add_command(label="Save As...", command=self.save_layout_as)
        file_menu.add_separator()
        file_menu.add_command(label="Export Code...", command=self.export_code)
        file_menu.add_command(label="Export SVG...", command=self.export_svg)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)
        
        # Edit menu
        edit_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Edit", menu=edit_menu)
        edit_menu.add_command(label="Delete Component", command=self.delete_component)
        edit_menu.add_command(label="Duplicate Component", command=self.duplicate_component)
        edit_menu.add_separator()
        edit_menu.add_command(label="Validate Layout", command=self.validate_layout)
        
        # View menu
        view_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="View", menu=view_menu)
        view_menu.add_command(label="Zoom In", command=self.zoom_in)
        view_menu.add_command(label="Zoom Out", command=self.zoom_out)
        view_menu.add_command(label="Zoom to Fit", command=self.zoom_to_fit)
        view_menu.add_separator()
        view_menu.add_command(label="Refresh", command=self.refresh_canvas)
        
        # Bind keyboard shortcuts
        self.root.bind('<Control-n>', lambda e: self.new_layout())
        self.root.bind('<Control-o>', lambda e: self.open_layout())
        self.root.bind('<Control-s>', lambda e: self.save_layout())
        # Delete key bindings (different on different platforms)
        self.root.bind('<Delete>', lambda e: self.delete_component())
        self.root.bind('<BackSpace>', lambda e: self.delete_component())  # macOS delete key
        self.root.bind('<Key-Delete>', lambda e: self.delete_component())
        self.root.bind('<KeyPress-Delete>', lambda e: self.delete_component())
        
        # Arrow key nudging
        self.root.bind('<Key-Left>', lambda e: self.nudge_component(-1, 0))
        self.root.bind('<Key-Right>', lambda e: self.nudge_component(1, 0))
        self.root.bind('<Key-Up>', lambda e: self.nudge_component(0, -1))
        self.root.bind('<Key-Down>', lambda e: self.nudge_component(0, 1))
        self.root.bind('<Shift-Left>', lambda e: self.nudge_component(-10, 0))
        self.root.bind('<Shift-Right>', lambda e: self.nudge_component(10, 0))
        self.root.bind('<Shift-Up>', lambda e: self.nudge_component(0, -10))
        self.root.bind('<Shift-Down>', lambda e: self.nudge_component(0, 10))
        
        # Make sure canvas can receive focus for keyboard events
        self.root.focus_set()
    
    def start_component_creation(self, component_type: str):
        """Start component creation mode"""
        self.creating_component_type = component_type
        
        container_info = f" inside {self.selected_container}" if self.selected_container else " at root level"
        self.status_var.set(f"Click on canvas to create {component_type}{container_info}")
        
        # Bind canvas click for creation
        self.canvas.canvas.bind('<Button-1>', self._create_component_at_position)
    
    def _create_component_at_position(self, event):
        """Create component at clicked position"""
        if not self.creating_component_type:
            return
        
        x = int(self.canvas.canvas.canvasx(event.x) / self.canvas.scale)
        y = int(self.canvas.canvas.canvasy(event.y) / self.canvas.scale)
        
        # Create component
        component_id = f"{self.creating_component_type}_{self.component_counter}"
        self.component_counter += 1
        
        # Default sizes for different component types
        default_sizes = {
            "UIPanel": (200, 150),
            "UILabel": (100, 25),
            "UIButton": (100, 30),
            "UIDropDownMenu": (150, 25),
            "UIProgressBar": (200, 20),
            "UITextEntryLine": (150, 25),
            "UIImage": (100, 100)
        }
        
        w, h = default_sizes.get(self.creating_component_type, (100, 50))
        
        component = Component(
            id=component_id,
            type=self.creating_component_type,
            rect=Rect(x, y, w, h),
            anchors=Anchors("top", "left", "top", "left"),
            container=self.selected_container,  # Use selected container
            text=f"Sample {self.creating_component_type.replace('UI', '')}",
            styling=Styling()
        )
        
        self.layout.components[component_id] = component
        
        # Clear creation mode
        self.creating_component_type = None
        self.palette.clear_selection()  # Clear palette button highlight
        self.status_var.set("Ready")
        self.canvas.canvas.bind('<Button-1>', self.canvas._on_click)
        
        # Refresh and select new component
        self.refresh_canvas()
        self.canvas.select_component(component)
    
    def refresh_canvas(self):
        """Refresh canvas display"""
        # Preserve current selection
        selected_component = None
        if self.canvas.selected_item:
            selected_component = self.canvas._find_component_by_canvas_item(self.canvas.selected_item)
        
        self.canvas.draw_layout(self.layout)
        
        # Restore selection
        if selected_component:
            self.canvas.select_component(selected_component)
    
    def set_container_selection(self, container_id: str):
        """Set the selected container for new components"""
        self.selected_container = container_id
        self.palette.update_container_selection(container_id)
        self.status_var.set(f"Container selected: {container_id}")
    
    def clear_container_selection(self):
        """Clear container selection (new components will be root level)"""
        self.selected_container = None
        self.palette.update_container_selection(None)
        self.status_var.set("Container cleared - new components will be root level")
    
    def nudge_component(self, dx: int, dy: int):
        """Nudge selected component by dx, dy pixels"""
        if self.canvas.selected_item:
            component = self.canvas._find_component_by_canvas_item(self.canvas.selected_item)
            if component:
                component.rect.x += dx
                component.rect.y += dy
                
                # Update property editor
                self.property_editor.select_component(component)
                
                # Refresh canvas
                self.refresh_canvas()
                
                self.status_var.set(f"Nudged {component.id} by ({dx}, {dy})")
    
    def new_layout(self):
        """Create new layout"""
        self.layout = Layout(
            metadata=Metadata(description="New Layout"),
            components={}
        )
        self.component_counter = 0
        self.clear_container_selection()
        self.refresh_canvas()
        self.status_var.set("New layout created")
    
    def open_layout(self):
        """Open layout from file"""
        filename = filedialog.askopenfilename(
            title="Open Layout",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        
        if filename:
            try:
                self.layout = Layout.load_json(Path(filename))
                self.refresh_canvas()
                self.status_var.set(f"Opened {filename}")
                
                # Update component counter
                self.component_counter = len(self.layout.components)
                
            except Exception as e:
                messagebox.showerror("Error", f"Failed to open layout:\n{e}")
    
    def save_layout(self):
        """Save current layout"""
        if hasattr(self, 'current_filename'):
            self._save_to_file(self.current_filename)
        else:
            self.save_layout_as()
    
    def save_layout_as(self):
        """Save layout to new file"""
        filename = filedialog.asksaveasfilename(
            title="Save Layout",
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        
        if filename:
            self._save_to_file(filename)
            self.current_filename = filename
    
    def _save_to_file(self, filename: str):
        """Save layout to specified file"""
        try:
            self.layout.save_json(Path(filename))
            self.status_var.set(f"Saved {filename}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save layout:\n{e}")
    
    def export_code(self):
        """Export layout as Python code"""
        filename = filedialog.asksaveasfilename(
            title="Export Python Code",
            defaultextension=".py",
            filetypes=[("Python files", "*.py"), ("All files", "*.*")]
        )
        
        if filename:
            try:
                # Use generate_code.py
                from generate_code import CodeGenerator
                
                class_name = Path(filename).stem.replace('_', '').title() + "Panel"
                generator = CodeGenerator()
                generator.generate_code(self.layout, class_name, Path(filename))
                
                self.status_var.set(f"Exported code to {filename}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to export code:\n{e}")
    
    def export_svg(self):
        """Export layout as SVG"""
        filename = filedialog.asksaveasfilename(
            title="Export SVG",
            defaultextension=".svg",
            filetypes=[("SVG files", "*.svg"), ("All files", "*.*")]
        )
        
        if filename:
            try:
                # Use generate_svg.py
                from generate_svg import SVGGenerator
                
                generator = SVGGenerator(*self.layout.metadata.window_size)
                generator.generate_svg(self.layout, Path(filename))
                
                self.status_var.set(f"Exported SVG to {filename}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to export SVG:\n{e}")
    
    def delete_component(self):
        """Delete selected component and its children"""
        if self.canvas.selected_item:
            component = self.canvas._find_component_by_canvas_item(self.canvas.selected_item)
            if component:
                # Find and delete child components first
                children_to_delete = [comp_id for comp_id, comp in self.layout.components.items() 
                                    if comp.container == component.id]
                
                deleted_count = 1 + len(children_to_delete)
                
                # Delete children
                for child_id in children_to_delete:
                    del self.layout.components[child_id]
                
                # Delete the component itself
                del self.layout.components[component.id]
                
                # Clear container selection if we deleted the selected container
                if self.selected_container == component.id:
                    self.clear_container_selection()
                
                self.refresh_canvas()
                self.canvas.select_component(None)
                
                if deleted_count > 1:
                    self.status_var.set(f"Deleted {component.type} and {len(children_to_delete)} children")
                else:
                    self.status_var.set(f"Deleted {component.type}")
    
    def duplicate_component(self):
        """Duplicate selected component"""
        if self.canvas.selected_item:
            component = self.canvas._find_component_by_canvas_item(self.canvas.selected_item)
            if component:
                # Create duplicate
                new_id = f"{component.type}_{self.component_counter}"
                self.component_counter += 1
                
                new_component = Component(
                    id=new_id,
                    type=component.type,
                    rect=Rect(component.rect.x + 20, component.rect.y + 20, 
                             component.rect.w, component.rect.h),
                    anchors=Anchors(component.anchors.top, component.anchors.left,
                                   component.anchors.bottom, component.anchors.right),
                    container=component.container,
                    text=component.text,
                    styling=Styling(component.styling.object_id)
                )
                
                self.layout.components[new_id] = new_component
                self.refresh_canvas()
                self.canvas.select_component(new_component)
                self.status_var.set(f"Duplicated {component.type}")
    
    def validate_layout(self):
        """Validate current layout"""
        issues = self.layout.validate()
        
        if issues:
            message = "Layout validation issues:\n\n" + "\n".join(f"• {issue}" for issue in issues)
            messagebox.showwarning("Validation Issues", message)
        else:
            messagebox.showinfo("Validation", "Layout validation passed!")
        
        self.status_var.set(f"Validation: {len(issues)} issues found")
    
    def auto_layout(self):
        """Apply automatic layout"""
        # Simple auto-layout: arrange components in grid
        components = [c for c in self.layout.components.values() if not c.container]
        
        if components:
            grid_cols = int(len(components) ** 0.5) + 1
            spacing = 20
            
            for i, comp in enumerate(components):
                row = i // grid_cols
                col = i % grid_cols
                
                comp.rect.x = col * (comp.rect.w + spacing) + spacing
                comp.rect.y = row * (comp.rect.h + spacing) + spacing
            
            self.refresh_canvas()
            self.status_var.set("Applied auto-layout")
    
    def zoom_in(self):
        """Zoom in"""
        self.canvas.scale *= 1.2
        self.refresh_canvas()
    
    def zoom_out(self):
        """Zoom out"""
        self.canvas.scale /= 1.2
        self.refresh_canvas()
    
    def zoom_to_fit(self):
        """Zoom to fit all components"""
        if not self.layout.components:
            return
        
        # Calculate bounds
        min_x = min(c.rect.x for c in self.layout.components.values())
        min_y = min(c.rect.y for c in self.layout.components.values())
        max_x = max(c.rect.x + c.rect.w for c in self.layout.components.values())
        max_y = max(c.rect.y + c.rect.h for c in self.layout.components.values())
        
        # Calculate scale to fit
        canvas_w = self.canvas.canvas.winfo_width()
        canvas_h = self.canvas.canvas.winfo_height()
        
        scale_x = canvas_w / (max_x - min_x + 40)
        scale_y = canvas_h / (max_y - min_y + 40)
        
        self.canvas.scale = min(scale_x, scale_y, 2.0)  # Max 2x zoom
        self.refresh_canvas()
    
    def run(self):
        """Run the designer"""
        self.refresh_canvas()
        self.root.mainloop()


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description='Visual Layout Designer for pygame_gui')
    parser.add_argument('--layout', type=Path, help='Layout file to open')
    
    args = parser.parse_args()
    
    try:
        designer = LayoutDesigner()
        
        if args.layout and args.layout.exists():
            designer.layout = Layout.load_json(args.layout)
            designer.component_counter = len(designer.layout.components)
        
        designer.run()
        
    except Exception as e:
        print(f"Error starting designer: {e}")
        return 1
    
    return 0


if __name__ == '__main__':
    exit(main())
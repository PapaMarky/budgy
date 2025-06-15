# UI Implementation Documentation

This directory contains implementation documentation for all budgy-viewer UI classes, providing technical details about the pygame_gui-based architecture.

## Implementation Documentation Structure

Each class document includes:

- **Class Purpose:** Role within the budgy-viewer architecture
- **Inheritance:** Base classes and class hierarchy relationships
- **Key Methods:** Public interface and important lifecycle methods
- **Properties:** Important attributes and configuration options
- **Integration:** How the class connects with other components
- **Event Handling:** Custom pygame events received and generated
- **Implementation Notes:** Important technical details and design decisions

## Files in this Directory

### Core Application Classes

- `BudgyViewerApp.md` - Main application window class
- `TopPanel.md` - Status display and navigation panel
- `BudgyFunctionPanel.md` - Panel container and switcher
- `MessagePanel.md` - Status messaging system

### Functional Sub-Panel Classes  

- `BudgyDataPanel.md` - Transaction management panel
- `BudgyReportPanel.md` - Expense reporting panel
- `BudgyFunctionSubPanel.md` - Base class for function panels

### Data Display Classes

- `RecordViewPanel.md` - Transaction list display
- `CategoryDialog.md` - Category management dialog
- `CategoryButton.md` - Category selection button

### Base and Utility Classes

- `DbRecordView.md` - Base class for database record display
- `BgColorPanel.md` - Colored background panel base
- `utility-classes.md` - Supporting utility classes

## Class Hierarchy Overview

```
pygame_gui_extras.app.GuiApp
└── BudgyViewerApp

pygame_gui.UIPanel
├── TopPanel
├── BudgyFunctionPanel
├── MessagePanel
├── BgColorPanel
│   └── DbRecordView
│       ├── RecordView
│       └── CategoryView
├── BudgyFunctionSubPanel
│   ├── BudgyDataPanel  
│   └── BudgyReportPanel
├── RecordViewPanel
└── CategoryViewPanel

pygame_gui.UIButton
├── CategoryButton
└── ToggleButton

pygame_gui.UIWindow
└── CategoryDialog
```

## Navigation

Return to [BUDGY_UI_Design_Notes.md](../BUDGY_UI_Design_Notes.md) for the main UI design overview.
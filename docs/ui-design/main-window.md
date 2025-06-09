# Main Window (BudgyViewerApp)

## Overview

The `BudgyViewerApp` serves as the primary application window and root container for all UI components in the budgy-viewer application. It extends [`pygame_gui_extras.app.GuiApp`](https://github.com/PapaMarky/pygame_gui_extras) to provide a complete window management system with event handling, theming, and component lifecycle management.

## Design Specifications

### Window Properties

**Dimensions:** 1280x960 pixels (fixed size)

**Title:** "Budgy Data Viewer: v{version}"

**Framework:** [pygame_gui](https://github.com/MyreMylar/pygame_gui) with [`pygame_gui_extras.app.GuiApp`](https://github.com/PapaMarky/pygame_gui_extras) base class

### Component Layout

The main window uses a three-panel vertical layout structure:

```
┌─────────────────────────────────────────────────────────────┐
│ TopPanel (Database status, controls, dropdown menu)         │ 
│ Height: 3 * BUTTON_HEIGHT + 6 * MARGIN                      │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│ BudgyFunctionPanel (Data/Report panel container)            │
│ Height: Fills remaining vertical space                      │
│                                                             │
├─────────────────────────────────────────────────────────────┤
│ MessagePanel (Status messages, progress bar)                │
│ Height: 3 * BUTTON_HEIGHT + 4 * MARGIN                      │
└─────────────────────────────────────────────────────────────┘
```

## Functional Components

### 1. TopPanel
- **Purpose:** Database status display and primary navigation
- **Position:** Top of window, anchored to all edges
- **Height:** `3 * BUTTON_HEIGHT + 6 * MARGIN`
- **Contents:** Record count, date range, retirement countdown, function dropdown
- **📖 [Detailed Documentation](top-panel.md)**

### 2. BudgyFunctionPanel
- **Purpose:** Container for switchable Data and Report sub-panels
- **Position:** Middle section, fills remaining vertical space
- **Anchoring:** All edges with dynamic height calculation
- **Behavior:** Shows/hides child panels based on dropdown selection
- **📖 [Detailed Documentation](function-panel.md)**

### 3. MessagePanel
- **Purpose:** User feedback through status messages and progress indication
- **Position:** Bottom of window, anchored to bottom edge
- **Height:** `3 * BUTTON_HEIGHT + 4 * MARGIN`
- **Contents:** Progress bar, info/error message labels
- **📖 [Detailed Documentation](message-panel.md)**

## Initialization and Setup

### Constructor Parameters
- `size`: Tuple (1280, 960) - Window dimensions
- `title`: String - Window title with version information

### Setup Process
1. **Theme Loading:** Loads `theme.json` from data/themes directory
2. **Component Creation:** Instantiates TopPanel, BudgyFunctionPanel, MessagePanel
3. **Database Initialization:** Opens database and updates status displays
4. **Configuration:** Applies retirement date and database settings

### Configuration Dependencies
- **BudgyConfig:** Application configuration management
- **Database Path:** Configured database file location
- **Theme File:** UI styling and appearance settings
- **Retirement Date:** Target date for countdown calculations

## Event Handling

### Primary Event Types

**Dropdown Menu Selection:**

- Data Functions → Shows BudgyDataPanel
- Report Functions → Shows BudgyReportPanel  
- Exit → Terminates application

**Database Operations:**

- `SELECT_DATABASE` → Opens file selection dialog
- `OPEN_DATABASE` → Loads selected database file
- `DATA_SOURCE_CONFIRMED` → Imports [OFX files](https://www.ofx.net/downloads/OFX%202.2%20Specification.pdf) and updates displays
- `DELETE_ALL_DATA_CONFIRMED` → Clears all transaction records

**Category Management:**

- `CATEGORY_CHANGED` → Refreshes database status and displays

### Event Flow
1. User interaction triggers [pygame_gui](https://github.com/MyreMylar/pygame_gui) event
2. BudgyViewerApp.handle_event() processes event type
3. Appropriate action taken (panel switching, database operations, etc.)
4. UI components updated via update_database_status()

## Database Integration

### Database Lifecycle
1. **Initialization:** Creates BudgyDatabase instance with configured path
2. **Status Updates:** Retrieves record counts and date ranges
3. **Data Distribution:** Passes database reference to functional panels
4. **Change Propagation:** Updates all displays when data changes

### Data Flow
```
BudgyDatabase → BudgyViewerApp → TopPanel (status display)
                                → FunctionPanel → DataPanel (transaction list)
                                                → ReportPanel (expense analysis)
```

## State Management

### Application State
- **Database Connection:** Active BudgyDatabase instance
- **Current Panel:** Active functional panel (data/report)
- **Configuration:** User preferences and settings
- **UI Theme:** Loaded styling configuration

### State Synchronization
- All panels receive database updates through `update_database_status()`
- Panel visibility managed through `BudgyFunctionPanel.show_subpanel()`
- Status information displayed in TopPanel and MessagePanel

## Theme and Styling

### Theme Application
- Loads from [`data/themes/theme.json`](https://github.com/PapaMarky/budgy/blob/main/src/budgy/gui/data/themes/theme.json)
- Applied to all UI components through [pygame_gui](https://github.com/MyreMylar/pygame_gui) theme system
- Component-specific styling via [ObjectID](https://pygame-gui.readthedocs.io/en/latest/pygame_gui.core.html#pygame_gui.core.ObjectID) class and object identifiers

### Component Styling IDs
- `#top-panel`: TopPanel container styling
- `#function-panel`: BudgyFunctionPanel container styling  
- `#message-panel`: MessagePanel container styling
- Child components inherit and extend base panel styles

## Error Handling

### Robust Error Management
- **Theme Loading:** Graceful degradation if theme file missing
- **Database Errors:** User-friendly error messages via MessagePanel
- **File Operations:** Exception handling for OFX imports and database operations
- **Invalid States:** Exception thrown for unknown dropdown selections

## Performance Considerations

### Efficient Updates
- Database status updates only trigger when data changes
- Panel switching managed through visibility rather than recreation
- Event handling optimized for UI responsiveness

### Memory Management
- Single database instance shared across components
- UI components managed through [pygame_gui](https://github.com/MyreMylar/pygame_gui) lifecycle
- Configuration loaded once and shared across panels

## Usage Example

```python
from budgy.gui.viewer import BudgyViewerApp

# Create and run the application
app = BudgyViewerApp(size=(1280, 960))
app.setup()
app.run()
```

**Source:** [`src/budgy/gui/viewer.py`](https://github.com/PapaMarky/budgy/blob/main/src/budgy/gui/viewer.py)

## Dependencies

### Core Dependencies
- [`pygame_gui_extras.app.GuiApp`](https://github.com/PapaMarky/pygame_gui_extras): Base application framework
- [`budgy.core.database.BudgyDatabase`](https://github.com/PapaMarky/budgy/blob/main/src/budgy/core/database.py): Database operations
- [`budgy.gui.configdata.BudgyConfig`](https://github.com/PapaMarky/budgy/blob/main/src/budgy/gui/configdata.py): Configuration management

### UI Component Dependencies
- [`budgy.gui.top_panel.TopPanel`](https://github.com/PapaMarky/budgy/blob/main/src/budgy/gui/top_panel.py): Status and navigation
- [`budgy.gui.function_panel.BudgyFunctionPanel`](https://github.com/PapaMarky/budgy/blob/main/src/budgy/gui/function_panel.py): Panel container
- [`budgy.gui.message_panel.MessagePanel`](https://github.com/PapaMarky/budgy/blob/main/src/budgy/gui/message_panel.py): User feedback

### Event System Dependencies
- [`budgy.gui.events`](https://github.com/PapaMarky/budgy/blob/main/src/budgy/gui/events.py): Custom event definitions
- `pygame_gui.UI_*`: Standard [pygame_gui](https://github.com/MyreMylar/pygame_gui) events

## Related Documentation
- [TopPanel Design](top-panel.md)
- [Function Panel Design](function-panel.md)
- [Message Panel Design](message-panel.md)
- [BudgyViewerApp Implementation](../ui-implementation/BudgyViewerApp.md)
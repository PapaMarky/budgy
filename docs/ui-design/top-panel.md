# Top Panel Design

## Overview

The TopPanel provides the primary information display and navigation interface for the budgy-viewer application. It shows critical database status information and serves as the main control center for switching between different functional modes.

**Parent Container:** [Main Window (BudgyViewerApp)](main-window.md)

## Design Specifications

### Panel Properties

**Height:** `3 * BUTTON_HEIGHT + 6 * MARGIN`

**Width:** Full window width (1280px)

**Position:** Top of main window, anchored to all edges

**Container:** Direct child of BudgyViewerApp

### Layout Structure

The TopPanel uses pygame_gui's anchoring system for precise component positioning across three vertical levels:

```
┌─────────────────────────────────────────────────────────────┐
│ Level 1: Record Count: [NNNNNN records]    [Function Drop▼] │
│          (left-anchored)                    (right-anchored) │
├─────────────────────────────────────────────────────────────┤
│ Level 2: Data Range: [YYYY-MM-DD] to [YYYY-MM-DD]           │
│          (left-anchored, spans available width)             │
├─────────────────────────────────────────────────────────────┤
│ Level 3: Retirement: [XXX years XXX months XXX days]        │
│          (left-anchored)                                     │
└─────────────────────────────────────────────────────────────┘
```

**Anchor Configuration:**
- **Left-side elements:** `{'top': 'top', 'left': 'left', 'bottom': 'top', 'right': 'left'}`
- **Spanning elements:** `{'top': 'top', 'left': 'left', 'bottom': 'top', 'right': 'right'}`  
- **Right-side elements:** `{'top': 'top', 'right': 'right'}` (with negative x positioning)

## Functional Components

### 1. Record Count Display

**Purpose:** Shows total number of transactions in database

**Layout:**
- Label: "Record Count:" (175px width)
- Value: Dynamic text showing current count
- Default: "No Database" when disconnected

**Styling:**
- Label: Bold 16pt font (`#data-label`, `@bold-16`)
- Value: Standard data text (`#data-text`)

### 2. Data Range Display

**Purpose:** Shows earliest and latest transaction dates

**Layout:**
- Label: "Data Range:" (175px width)  
- Value: "YYYY-MM-DD to YYYY-MM-DD" format
- Default: "No Database" when disconnected

**Behavior:**
- Updates automatically when database changes
- Handles empty database gracefully
- Date format consistent with transaction display

### 3. Function Selection Dropdown

**Purpose:** Primary navigation between Data and Report functions

**Options:**
- "Data Functions" → Switches to BudgyDataPanel
- "Report Functions" → Switches to BudgyReportPanel  
- "Exit" → Terminates application

**Properties:**
- Width: 200px (`DROP_DOWN_WIDTH`)
- Position: Right side of level 1 (right-anchored with negative x offset)
- Anchoring: `{'top': 'top', 'right': 'right'}` without container
- Event: Triggers panel switching in BudgyViewerApp

### 4. Retirement Countdown

**Purpose:** Shows days remaining until configured retirement date

**Layout:**
- Position: Left side of level 3 (left-anchored)
- Format: "Retirement: XXX years XXX months XXX days"
- Anchoring: `{'top': 'top', 'left': 'left', 'bottom': 'top', 'right': 'right'}`
- Color coding: Changes based on proximity to target date

**Calculation:**
- Uses configured retirement target date
- Updates based on current date using `relativedelta`
- Handles past retirement dates appropriately
- Displays years, months, and days separately

## Component Relationships

### Parent-Child Hierarchy
```
TopPanel (UIPanel)
├── Record Count Label (UILabel)
├── Record Count Value (UILabel)  
├── Data Range Label (UILabel)
├── Data Range Value (UILabel)
├── Function Dropdown (UIDropDownMenu)
└── Retirement Display (UILabel)
```

### Data Dependencies
- **[BudgyConfig](https://github.com/PapaMarky/budgy/blob/main/src/budgy/gui/configdata.py):** Retirement date configuration
- **[BudgyDatabase](https://github.com/PapaMarky/budgy/blob/main/src/budgy/core/database.py):** Record counts and date ranges
- **[BudgyViewerApp](https://github.com/PapaMarky/budgy/blob/main/src/budgy/gui/viewer.py):** Event handling and panel switching

## State Management

### Display States

**Connected State:**
- Record count shows actual number
- Data range shows real date span
- All controls fully functional

**Disconnected State:**
- Record count shows "No Database"
- Data range shows "No Database"  
- Function dropdown remains active

**Empty Database State:**
- Record count shows "0"
- Data range shows appropriate empty message
- Import functions remain available

### Update Triggers
- Database connection established
- Records imported or deleted
- Application startup
- Manual refresh operations

## Event Handling

### Generated Events
- **[UI_DROP_DOWN_MENU_CHANGED](https://pygame-gui.readthedocs.io/en/latest/events.html#pygame_gui.UI_DROP_DOWN_MENU_CHANGED):** Function selection triggers panel switching
- Processed by [`BudgyViewerApp.handle_event()`](https://github.com/PapaMarky/budgy/blob/main/src/budgy/gui/viewer.py)

### Received Updates
- **set_record_count(count):** Updates record display
- **set_data_range(start, end):** Updates date range display  
- **set_retirement_info(target_date):** Configures countdown display

## Styling and Theming

### Component Styling IDs

**Panel Container:**
- `#top-panel`: Overall panel styling

**Labels:**
- `#data-label`: Field labels (bold 16pt)
- `#data-text`: Data values (standard text)

**Interactive Elements:**
- Function dropdown uses default [pygame_gui](https://github.com/MyreMylar/pygame_gui) styling
- Retirement display inherits label styling

### Layout Constants
- `MARGIN`: Consistent spacing between elements
- `BUTTON_HEIGHT`: Standard height for interactive elements
- `TEXT_WIDTH`: Label width (175px)
- `DROP_DOWN_WIDTH`: Dropdown width (200px)

## Responsive Behavior

### Width Adaptation
- Labels maintain fixed width for alignment
- Value fields expand to fill remaining space
- Right-anchored elements maintain position

### Content Overflow
- Long database paths truncated appropriately
- Large record counts formatted for readability
- Date ranges maintained in consistent format

## Performance Considerations

### Efficient Updates
- Only updates when database state changes
- Retirement countdown calculated on demand
- Text formatting optimized for frequent updates

### Memory Management
- Maintains references to BudgyConfig and database
- UI elements created once and reused
- Event handling through parent application

## Accessibility Features

### Clear Information Hierarchy
- Logical left-to-right information flow
- Consistent label-value pairing
- Important information prominently displayed

### Visual Clarity
- High contrast text and backgrounds
- Consistent font sizing and styling
- Clear separation between functional areas

## Error Handling

### Graceful Degradation
- Handles missing database gracefully
- Shows appropriate messages for empty states
- Maintains functionality during error conditions

### User Feedback
- Clear indication of database connection status
- Immediate visual feedback for actions
- Consistent error state presentation

## Integration Points

### Configuration Integration
- Reads retirement date from BudgyConfig
- Adapts to user preference changes
- Maintains configuration consistency

### Database Integration
- Receives real-time database status updates
- Handles database connection lifecycle
- Provides consistent status reporting

### Navigation Integration
- Triggers panel switching in parent application
- Maintains state consistency across navigation
- Provides clear indication of current mode

## Usage Example

```python
# TopPanel is created by BudgyViewerApp during setup
top_panel = TopPanel(
    config,
    rect,
    starting_height=1,
    anchors={'top': 'top', 'left': 'left', 'bottom': 'top', 'right': 'right'},
    margins={'top': MARGIN, 'left': MARGIN, 'bottom': MARGIN, 'right': MARGIN},
    manager=ui_manager,
    object_id=ObjectID(class_id='#top-panel')
)

# Update displays
top_panel.set_record_count(1500)
top_panel.set_data_range(start_date, end_date)
top_panel.set_retirement_info(retirement_date)
```

**Source:** [`src/budgy/gui/top_panel.py`](https://github.com/PapaMarky/budgy/blob/main/src/budgy/gui/top_panel.py)

## Related Documentation
- [Main Window Design](main-window.md)
- [Function Panel Design](function-panel.md)
- [TopPanel Implementation](../ui-implementation/TopPanel.md)
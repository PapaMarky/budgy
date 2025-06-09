# Function Panel Design

## Overview

The BudgyFunctionPanel serves as a container and manager for the application's two primary functional modes: Data Functions and Report Functions. It provides seamless switching between these modes while maintaining state and ensuring only one panel is visible at a time.

**Parent Container:** [Main Window (BudgyViewerApp)](main-window.md)

## Design Specifications

### Panel Properties

**Height:** Dynamic - Fills remaining vertical space between TopPanel and MessagePanel

**Width:** Full window width (1280px)

**Position:** Middle section of main window

**Container:** Direct child of BudgyViewerApp

### Layout Structure

The FunctionPanel acts as a container that manages two mutually exclusive sub-panels:

```
┌─────────────────────────────────────────────────────────────┐
│ BudgyFunctionPanel (Container)                              │
│ ┌─────────────────────────────────────────────────────────┐ │
│ │ BudgyDataPanel (Data Functions)                         │ │
│ │ - Import Data controls                                  │ │
│ │ - Clear Data controls                                   │ │
│ │ - RecordViewPanel (transaction list)                   │ │
│ │ - File selection dialogs                               │ │
│ └─────────────────────────────────────────────────────────┘ │
│                          OR                                 │
│ ┌─────────────────────────────────────────────────────────┐ │
│ │ BudgyReportPanel (Report Functions)                     │ │
│ │ - Monthly expense summaries                             │ │
│ │ - Year/month expense analysis                           │ │
│ │ - Expense type categorization                           │ │
│ │ - Detail drill-down capabilities                       │ │
│ └─────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

## Functional Components

### 1. Container Management

**Purpose:** Provides unified container for sub-panels with consistent styling and behavior

**Features:**
- Single parent for both Data and Report panels
- Consistent anchoring and positioning
- Shared configuration and database access
- Unified event handling framework

### 2. Panel Switching Logic

**Purpose:** Manages visibility and state of child panels

**Behavior:**
- Only one sub-panel visible at a time
- Smooth transitions between panels
- State preservation during switches
- Consistent user experience

**Implementation:**
- `show_subpanel(panel_name)` method
- Hide/show operations on child panels
- No panel recreation during switches

### 3. Child Panel Properties

**Data Panel Access:**
- Property: `data_panel` → Returns BudgyDataPanel instance
- Purpose: Transaction management and OFX import functionality
- **📖 [Detailed Documentation](data-panel.md)** *(Future)*

**Report Panel Access:**
- Property: `report_panel` → Returns BudgyReportPanel instance  
- Purpose: Expense analysis and reporting functionality
- **📖 [Detailed Documentation](report-panel.md)** *(Future)*

## Component Relationships

### Parent-Child Hierarchy
```
BudgyFunctionPanel (UIPanel)
├── BudgyDataPanel (BudgyFunctionSubPanel)
│   ├── Import/Clear controls
│   ├── RecordViewPanel
│   └── File dialogs
└── BudgyReportPanel (BudgyFunctionSubPanel)
    ├── Summary tables
    ├── Expense breakdowns
    └── Detail views
```

### Configuration Dependencies
- **[BudgyConfig](https://github.com/PapaMarky/budgy/blob/main/src/budgy/gui/configdata.py):** Shared configuration passed to both child panels
- **[Database](https://github.com/PapaMarky/budgy/blob/main/src/budgy/core/database.py):** Database reference distributed to child panels requiring data access
- **[UI Manager](https://pygame-gui.readthedocs.io/en/latest/pygame_gui.core.html#pygame_gui.core.UIManager):** Shared UI manager for consistent event handling

## State Management

### Panel Visibility States

**Data Mode:**
- BudgyDataPanel: Visible and active
- BudgyReportPanel: Hidden but state preserved
- User can import/manage transaction data

**Report Mode:**
- BudgyDataPanel: Hidden but state preserved
- BudgyReportPanel: Visible and active  
- User can analyze and report on data

### State Preservation
- Panel instances maintained throughout application lifecycle
- Internal state preserved during visibility changes
- Data connections remain active for both panels
- Configuration changes propagated to both panels

## Initialization Process

### Constructor Sequence
1. **Base Panel Creation:** Initialize UIPanel with provided parameters
2. **Child Panel Creation:** Create BudgyDataPanel and BudgyReportPanel instances
3. **Initial State:** Default to Report mode (`show_subpanel('report')`)
4. **Configuration:** Pass BudgyConfig to both child panels

### Database Integration
- Database reference received from BudgyViewerApp
- Distributed to child panels requiring database access
- Currently only BudgyReportPanel receives database reference
- Database updates trigger refresh in active panel

## Event Handling

### Panel Switching Events
- Triggered by TopPanel dropdown selection
- Processed by BudgyViewerApp
- Delegated to `show_subpanel()` method
- Results in immediate panel visibility change

### Child Panel Events
- Events bubble up through container hierarchy
- BudgyFunctionPanel serves as event relay
- No event processing at container level
- Child panels handle their own specific events

## Database Integration

### Database Distribution
```python
def set_database(self, database: BudgyDatabase):
    self._report_panel.set_database(database)
    # Note: DataPanel currently uses global database access
```

### Data Flow
- Database changes trigger updates in active panel
- Report panel receives database for analysis
- Data panel uses database for transaction display
- Container coordinates database-related updates

## Layout and Positioning

### Dynamic Sizing
- Container fills available vertical space
- Child panels inherit full container dimensions
- Responsive to window size changes
- Maintains aspect ratios for internal components

### Anchoring Strategy
```python
anchors={
    'top': 'top', 'left': 'left',
    'bottom': 'bottom', 'right': 'right'
}
```
- Full edge anchoring for container
- Child panels inherit anchoring behavior
- Automatic layout adjustment for parent changes

## Performance Considerations

### Efficient Panel Management
- Single panel creation per application lifecycle
- Visibility changes instead of recreation
- State preservation reduces initialization overhead
- Database connections maintained efficiently

### Memory Optimization
- Shared configuration reduces memory footprint
- Single database reference shared across panels
- UI components managed through [pygame_gui](https://github.com/MyreMylar/pygame_gui) lifecycle
- Event handling optimized for responsiveness

## Error Handling

### Panel Creation Errors
- Graceful handling of child panel creation failures
- Fallback behavior for missing components
- Clear error reporting for configuration issues

### State Management Errors
- Invalid panel names raise descriptive exceptions
- Consistent error handling across panel switches
- Recovery mechanisms for corrupted states

## Styling and Theming

### Container Styling
- **Object ID:** `#function-panel`
- **Purpose:** Provides base styling for container
- **Inheritance:** Child panels inherit base styling

### Child Panel Styling
- Individual object IDs for Data and Report panels
- Consistent styling framework across both panels
- Theme inheritance from parent container

## Integration Points

### TopPanel Integration
- Receives panel switch commands from dropdown selection
- Maintains synchronization with navigation state
- Provides feedback for current panel mode

### Database Integration
- Coordinates database updates across child panels
- Manages database reference distribution
- Handles database state changes consistently

### Configuration Integration
- Distributes configuration to child panels
- Handles configuration updates
- Maintains configuration consistency

## Usage Example

```python
# FunctionPanel created by BudgyViewerApp
function_panel = BudgyFunctionPanel(
    config,
    function_panel_rect,
    starting_height=1,
    manager=ui_manager,
    anchors={'top': 'top', 'left': 'left', 'bottom': 'bottom', 'right': 'right'},
    object_id=ObjectID(object_id='#function-panel')
)

# Panel switching (triggered by dropdown)
function_panel.show_subpanel('data')    # Show data management
function_panel.show_subpanel('report')  # Show expense reporting

# Database integration
function_panel.set_database(database)

# Access child panels
data_panel = function_panel.data_panel
report_panel = function_panel.report_panel
```

**Source:** [`src/budgy/gui/function_panel.py`](https://github.com/PapaMarky/budgy/blob/main/src/budgy/gui/function_panel.py)

## Future Enhancements

### Potential Improvements
- Animation transitions between panel switches
- State synchronization between panels
- Enhanced error handling for panel operations
- Configuration change propagation automation

### Extensibility
- Framework supports additional panel types
- Container pattern allows easy panel addition
- Consistent interface for new panel integration
- Scalable architecture for complex panel hierarchies

## Related Documentation
- [Main Window Design](main-window.md)
- [Data Panel Design](data-panel.md)
- [Report Panel Design](report-panel.md)
- [BudgyFunctionPanel Implementation](../ui-implementation/BudgyFunctionPanel.md)
# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Budgy is a personal finance tool for retirement planning that ingests OFX files and outputs spending reports. The application has two main entry points:
- `budgy-import`: Command-line tool for importing OFX financial data
- `budgy-viewer`: GUI application for viewing and categorizing transactions

## Architecture

The codebase is structured into two main modules:
- `budgy.core`: Data processing, database operations, and OFX import functionality
- `budgy.gui`: Pygame-based GUI application for data visualization and transaction categorization

Key components:
- `BudgyDatabase` (src/budgy/core/database.py): SQLite database wrapper handling transactions, categories, and categorization rules
- `BudgyViewerApp` (src/budgy/gui/viewer.py): Main GUI application class extending pygame_gui_extras.app.GuiApp
- OFX import functionality (src/budgy/core/importer.py): Processes financial data files

The database schema includes:
- `transactions` table: Financial transaction data from OFX files
  - Unique constraint: `(fitid, account, posted)` to handle OFX FITID collisions
- `categories` table: User-defined spending categories with hierarchical structure
  - Fields: `name`, `subcategory`, `expense_type` (0=non-expense, 1=one-time, 2=recurring)
- `cat_rules` table: Rules for automatic transaction categorization

## Development Commands

**Build:**
```bash
./run-build.sh
# or
python3 -m build
```

**Run tests:**
```bash
./run-tests.sh
# or
tox
# or (from src/ directory)
pytest --cov --cov-append --cov-report term
```

**Install in development mode:**
```bash
pip3 install -e .
```

**Run applications:**
```bash
budgy-import --db path/to/database.db datafile.ofx
budgy-viewer
```

## Testing

Tests are organized in parallel directory structures under `tests/` folders:
- Core functionality tests: `src/budgy/core/tests/`
- GUI tests: `src/budgy/gui/tests/`

Test configuration uses pytest with coverage reporting via tox (Python 3.11).

## Dependencies

Key external dependencies:
- `ofxtools`: OFX file parsing
- `pygame_gui`: GUI framework
- `pygame_gui_extras`: Custom GUI extensions from GitHub
- `sqlite3`: Database operations (built-in)

## Development Rules
* No trailing whitespace in python files
* do not commit directly to main.    
If modifications are required check to make sure we are not in main. If we are, create a workbranch first
* when working on complicated changes use commits to break the task into groups of related edits so that I can more easily understand each part of the change as I review it.
 * A single commit can span multiple files, but all of the changes should be related and the overall scope of the commit should be limited.

### Markdown files
* when using bold strings as headers, always leave a blank line after the header so that it renders properly
* **CRITICAL:** After creating any markdown file, always check for and fix bold headers without proper spacing
* **Comprehensive Linking:** Maximize links in documentation - anything that can be a link should be a link:
  - **External Repository References:** Link all external libraries/frameworks to their source repositories
    - `pygame_gui` → `[pygame_gui](https://github.com/MyreMylar/pygame_gui)`
    - `pygame_gui_extras` → `[pygame_gui_extras](https://github.com/PapaMarky/pygame_gui_extras)`
  - **Documentation Cross-References:** Link to related documentation files within the project
    - **Hierarchical Navigation:** Add bidirectional links between parent/child documentation
    - **Component Details:** Link from overview to detailed component documentation  
    - **Parent References:** Include "Parent Container" links back to containing elements
  - **Technical Concepts:** Link to relevant documentation/specifications (e.g., SQLite docs, Python docs)
  - **File References:** Use full GitHub URLs for internal source files (e.g., `https://github.com/PapaMarky/budgy/blob/main/src/budgy/gui/events.py`)
  - **Standards/Protocols:** Link to official specifications (e.g., OFX format, JSON schema)
  - **Tools/Technologies:** Link to official documentation for tools mentioned
example:
```
**Section Header:**

Section contents
```
instead of 
```
**Section Header:**
Section contents
```

## Recent Development

**Primary Key Collision Fix (Completed):**
- Fixed OFX import collisions by updating unique constraint from `(fitid, account)` to `(fitid, account, posted)`
- Added database migration for existing databases
- Updated GUI components to use precise transaction identification
- All tests passing with comprehensive test suite

**Category System Improvements:**
- Hierarchical category/subcategory structure
- Expense type classification (non-expense, one-time, recurring)
- Enhanced category dialog functionality
- Automatic categorization rules framework
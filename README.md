# Budgy - Retirement Budget Planning Tool

[![CI Pipeline](https://github.com/PapaMarky/budgy/actions/workflows/test.yml/badge.svg)](https://github.com/PapaMarky/budgy/actions/workflows/test.yml)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**Retirement planning tool for analyzing monthly expenses and projecting post-retirement budget needs.**

Python application that processes OFX financial data to categorize expenses by type (one-time vs. ongoing) and retirement relevance, helping estimate required retirement income.

## Core Features

### OFX Import Processing ([`src/budgy/core/importer.py`](src/budgy/core/importer.py))
- **Parser**: Uses `ofxtools` library for robust OFX file parsing
- **Duplicate Detection**: Unique constraint on `(fitid, account, posted)` prevents import collisions
- **Batch Processing**: Command-line tool for automation and scripting

### Database Layer ([`src/budgy/core/database.py`](src/budgy/core/database.py))
- **Schema Migration**: Automatic database updates with [`BudgyDatabase.migrate_database()`](src/budgy/core/database.py#L85)
- **Transaction Storage**: SQLite backend with optimized queries
- **Retirement-Focused Categorization**: `expense_type` field differentiates ongoing vs. one-time expenses
- **Post-Retirement Planning**: Categories designed to exclude non-retirement expenses (e.g., college tuition)

### GUI Application ([`src/budgy/gui/viewer.py`](src/budgy/gui/viewer.py))
- **Framework**: pygame_gui-based cross-platform interface
- **Panel Architecture**: Modular UI components in [`src/budgy/gui/`](src/budgy/gui/)
- **Real-time Updates**: Category assignment with immediate database persistence

## 📦 Installation

### Requirements
- Python 3.9 or higher
- SQLite (included with Python)

### Install from Source
```bash
git clone https://github.com/PapaMarky/budgy.git
cd budgy
pip install -e .
```

### Dependencies
Budgy automatically installs required dependencies:
- `ofxtools` - OFX file processing
- `pygame_gui` - Cross-platform GUI framework
- `dateutils` - Date/time utilities

## 🔧 Usage

### GUI Application
```bash
budgy-viewer
```
Launch the graphical interface to:
- **Smart Import**: Import multiple OFX files safely - duplicates are automatically handled
- **Bulk Processing**: Select entire folders of statements without tracking what's imported
- **Category Management**: Create hierarchical categories with auto-categorization rules
- **Transaction Analysis**: View, categorize, and generate comprehensive spending reports
- **Data Preservation**: Reimport files anytime without losing your categorization work

### Developer/Advanced Usage
For developers and automation scripts, a command-line import tool is available:
```bash
budgy-import --db /path/to/database.db transactions.ofx
```
**Note**: Most users should use the GUI application (`budgy-viewer`) for importing and managing data.

### Configuration
Budgy creates configuration files automatically:
- **Linux/macOS**: `~/.config/budgy/budgyconfig.json`
- **Windows**: `%APPDATA%/budgy/budgyconfig.json`

## Architecture

### Module Structure
```
src/budgy/
├── core/           # Data layer and business logic
│   ├── database.py # SQLite operations and schema management
│   ├── importer.py # OFX file processing and CLI interface
│   └── app.py      # Base application framework
└── gui/            # Presentation layer
    ├── viewer.py   # Main GUI application (extends GuiApp)
    ├── data_panel.py    # Transaction display and editing
    ├── category_dialog.py # Category management interface
    └── configdata.py     # Configuration management
```

### Database Design
- **`transactions`**: Core financial data with `(fitid, account, posted)` unique constraint
- **`categories`**: Hierarchical structure with retirement planning focus:
  - `expense_type`: 0=non-expense (income), 1=one-time expense, 2=recurring expense
  - Design goal: Differentiate expenses that will/won't continue in retirement
- **`cat_rules`**: Pattern-based auto-categorization rules

### Retirement Planning Methodology
- **Monthly Expense Analysis**: Focus on recurring expenses to project ongoing retirement needs
- **Expense Type Classification**:

  - `expense_type=2` (recurring): Rent, utilities, insurance → Include in retirement budget
  - `expense_type=1` (one-time): Vacation, car purchase → Evaluate retirement relevance
  - `expense_type=0` (non-expense): Income, transfers → Exclude from expense projections
- **Future Enhancement**: One-time expenses will include "post-retirement relevance" flag (e.g., college tuition = not relevant post-retirement)

### Key Design Decisions
- **Unique Constraint Evolution**: Migrated from `(fitid, account)` to `(fitid, account, posted)` to handle OFX FITID collisions ([#primary-key-fix](test_primary_key_fix.py))
- **GUI Framework Choice**: pygame_gui for cross-platform compatibility without heavy dependencies
- **Category Schema**: Designed around retirement planning rather than general budgeting

## 🧪 Development

### Running Tests
```bash
# Full test suite
./run-tests.sh

# Or using tox directly
tox

# Or pytest for development
cd src && pytest --cov
```

### Building
```bash
./run-build.sh
# or
python -m build
```

## 📊 What's New in v3.0.0

- **Enhanced Database Architecture**: Improved handling of duplicate transaction IDs
- **Cross-Platform Compatibility**: Full Windows, macOS, and Linux support  
- **Migration System**: Automatic database schema updates
- **Comprehensive Testing**: CI across multiple platforms and Python versions

See [RELEASE_NOTES.md](RELEASE_NOTES.md) for complete details.

## 🎯 Goal

Budgy was created to support retirement planning by providing detailed insights into spending patterns. By categorizing and analyzing historical transactions, you can:

- Understand your true spending needs
- Identify areas for potential savings
- Plan realistic retirement budgets
- Track spending trends over time

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🔗 Links

- [Design Documentation](docs/BUDGY_UI_Design_Notes.md)
- [Release Notes](RELEASE_NOTES.md)
- [Issues](https://github.com/PapaMarky/budgy/issues)
- [CI Pipeline](https://github.com/PapaMarky/budgy/actions)
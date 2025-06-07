# Budgy

[![CI Pipeline](https://github.com/PapaMarky/budgy/actions/workflows/ci.yml/badge.svg)](https://github.com/PapaMarky/budgy/actions/workflows/ci.yml)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**A personal finance tool for retirement planning that ingests OFX files and generates comprehensive spending reports.**

Budgy helps you understand your spending patterns by importing bank and credit card data, categorizing transactions, and providing detailed analysis for retirement planning.

## 🚀 Features

- **OFX File Import**: Seamlessly import transaction data from banks and credit cards
- **Intelligent Categorization**: Hierarchical category system with auto-categorization rules
- **GUI Application**: User-friendly interface for data visualization and transaction management
- **Command-Line Tools**: Batch processing and automation support
- **Cross-Platform**: Works on Windows, macOS, and Linux
- **Data Integrity**: Robust handling of duplicate transactions and edge cases
- **Retirement Planning**: Track spending patterns to plan for retirement needs

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
- Import OFX files through file dialogs
- View and categorize transactions
- Generate spending reports
- Manage categories and rules

### Command-Line Import
```bash
budgy-import --db /path/to/database.db transactions.ofx
```
Batch import OFX files for automated processing.

### Configuration
Budgy creates configuration files automatically:
- **Linux/macOS**: `~/.config/budgy/budgyconfig.json`
- **Windows**: `%APPDATA%/budgy/budgyconfig.json`

## 🏗️ Architecture

**Two-Module Design:**
- **`budgy.core`** - Data processing, database operations, OFX import
- **`budgy.gui`** - Pygame-based GUI application

**Database Schema:**
- **Transactions**: Financial data with precise identification
- **Categories**: Hierarchical categorization system  
- **Rules**: Auto-categorization based on text patterns

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

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Run tests (`./run-tests.sh`)
5. Commit your changes (`git commit -m 'Add amazing feature'`)
6. Push to the branch (`git push origin feature/amazing-feature`)
7. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🔗 Links

- [Design Documentation](docs/BUDGY_UI_Design_Notes.md)
- [Release Notes](RELEASE_NOTES.md)
- [Issues](https://github.com/PapaMarky/budgy/issues)
- [CI Pipeline](https://github.com/PapaMarky/budgy/actions)
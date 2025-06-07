# Budgy Release Notes

## Version 3.0.0 (June 2025)

**Major Release: Enhanced Database Architecture & Cross-Platform Compatibility**

### 🚀 Major Features

**Database Migration System**
- Automatic schema updates on database open
- Handles migration from old (fitid, account) to new (fitid, account, posted) unique constraint
- Preserves existing data during schema changes
- Backward compatibility with existing databases

**Primary Key Collision Fix**
- Resolves OFX FITID collision issues where same FITID appears on different dates
- Enables precise transaction identification for category assignment
- Comprehensive test suite validates collision handling
- Enhanced data integrity for financial imports

**Cross-Platform Compatibility**
- Full CI testing on Ubuntu, macOS, Windows
- Platform-specific file handling and path management
- Robust error handling for different environments
- Windows-compatible file operations and Unicode support

### 🔧 Technical Improvements

**Database Schema Enhancements**
- New unique constraint: `(fitid, account, posted)` instead of `(fitid, account)`
- Enhanced category system with hierarchical structure
- Auto-categorization rules framework (`cat_rules` table)
- Improved data validation and error handling

**Testing & Quality Assurance**
- Comprehensive CI pipeline across multiple platforms and Python versions
- Custom test suite for primary key collision scenarios
- Platform-specific test adaptations for Windows/Unix differences
- Coverage reporting and artifact collection

**Configuration System**
- JSON-based configuration with platform-appropriate storage locations
- Automatic config file creation with sensible defaults
- Cross-platform path handling for database and import directories
- Retirement planning configuration support

### 🐛 Bug Fixes

- Fixed OFX import failures due to FITID collisions
- Resolved Windows file permission issues during database operations
- Corrected Unicode encoding errors in CI environments
- Enhanced error handling for edge cases in transaction import

### 🔄 Breaking Changes

- Database schema migration required for existing installations
- Category system now uses hierarchical name/subcategory structure
- Configuration file format updated to JSON (automatic migration)

### 🛠️ Developer Experience

- Improved development workflow with cross-platform testing
- Enhanced documentation with updated design notes
- Comprehensive CI/CD pipeline for reliable releases
- Better error messages and debugging information

### 📦 Dependencies

- Python 3.9+ support
- Updated pygame_gui compatibility
- Enhanced OFX file processing with ofxtools
- Robust testing framework with pytest and tox

---

## Previous Versions

### Version 2.x.x
- Initial GUI implementation
- Basic OFX import functionality
- Simple category management
- Core database operations

### Version 1.x.x
- Command-line OFX import tool
- Basic SQLite database structure
- Initial category system
- Foundation architecture
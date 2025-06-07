# Budgy User Guide

## Table of Contents
- [Getting Started](#getting-started)
- [Installation](#installation)
- [First Time Setup](#first-time-setup)
- [Importing Financial Data](#importing-financial-data)
- [Managing Categories](#managing-categories)
- [Viewing and Editing Transactions](#viewing-and-editing-transactions)
- [Generating Reports](#generating-reports)
- [Configuration](#configuration)
- [Troubleshooting](#troubleshooting)

## Getting Started

Budgy is a personal finance tool designed to help you analyze your spending patterns for retirement planning. It imports OFX files from your bank and credit card accounts, categorizes transactions, and provides insights into your spending habits.

### What You'll Need
- OFX files from your bank or credit card company
- Python 3.9 or higher installed on your computer
- Basic familiarity with downloading files from financial institutions

## Installation

### Option 1: Install from Source (Recommended)
```bash
git clone https://github.com/PapaMarky/budgy.git
cd budgy
pip install -e .
```

### Option 2: Install from Package (when available)
```bash
pip install budgy
```

### Verify Installation
After installation, you should be able to run:
```bash
budgy-viewer --help
budgy-import --help
```

## First Time Setup

### 1. Launch Budgy
```bash
budgy-viewer
```

When you first launch Budgy, it will automatically:
- Create a configuration directory in your user folder
- Set up a default database location
- Create default spending categories

### 2. Configuration Locations
Budgy stores its configuration in platform-appropriate locations:
- **Windows**: `%APPDATA%\budgy\budgyconfig.json`
- **macOS**: `~/.config/budgy/budgyconfig.json`
- **Linux**: `~/.config/budgy/budgyconfig.json`

## Importing Financial Data

### Getting OFX Files from Your Bank

Most banks and credit card companies provide OFX file downloads:

1. **Log into your online banking**
2. **Find "Download" or "Export" options** (usually in account statements or transaction history)
3. **Select OFX format** (may be called "Money", "Quicken", or "OFX")
4. **Choose your date range** (start with 3-6 months for testing)
5. **Download the file** to your computer

### Importing with the GUI

1. **Launch Budgy**: `budgy-viewer`
2. **Click "Import Data"** button in the Data Panel
3. **Select your OFX file** in the file dialog
4. **Wait for import to complete** - progress will be shown in the Message Panel
5. **Review imported transactions** in the data view

### Importing with Command Line

For batch processing or automation:
```bash
budgy-import --db /path/to/your/database.db your-file.ofx
```

### Import Tips

- **Start small**: Import 1-3 months initially to get familiar
- **Multiple accounts**: Import each account separately for clarity
- **Regular imports**: Monthly imports work well for ongoing analysis
- **Duplicate handling**: Budgy automatically handles duplicate transactions

## Managing Categories

Budgy uses a hierarchical category system with main categories and subcategories.

### Default Categories

**Expense Categories:**
- Auto (Gas, Service, Repairs)
- Entertainment (Coffee, Dining, Movies)
- Household (Rent, Utilities, Repairs)
- Insurance (Auto, Home, Medical)
- Travel (Hotel, Transportation)

**Income Categories:**
- Income (Salary, Interest, Dividends)
- Transfer (Savings, Investment)

### Adding New Categories

1. **Open Category Dialog**: Click "Edit" next to category dropdown
2. **Enter Category Details**:
   - **Main Category**: e.g., "Medical"
   - **Subcategory**: e.g., "Prescriptions"
   - **Expense Type**: 
     - Non-expense (income, transfers)
     - One-time expense (travel, purchases)
     - Recurring expense (rent, utilities)

### Auto-Categorization Rules

Create rules to automatically categorize future transactions:

1. **Identify patterns** in transaction names/descriptions
2. **Create rules** that match text patterns
3. **Assign categories** to matching transactions
4. **Test rules** with new imports

**Example Rules:**
- Pattern: "STARBUCKS" → Category: "Entertainment" / "Coffee"
- Pattern: "SHELL" → Category: "Auto" / "Gas"
- Pattern: "RENT" → Category: "Household" / "Rent"

## Viewing and Editing Transactions

### Transaction List

The main data panel shows all imported transactions with:
- **Date**: When the transaction was posted
- **Amount**: Transaction amount (negative = expense, positive = income)
- **Name**: Payee or description from bank
- **Memo**: Additional details from bank
- **Category**: Current category assignment

### Editing Categories

1. **Find the transaction** you want to categorize
2. **Click the Category dropdown** for that transaction
3. **Select appropriate category/subcategory**
4. **Changes save automatically**

### Handling Duplicate Transactions

Budgy automatically handles most duplicates, but you may occasionally see:
- **Same transaction on different dates**: This is normal for pending vs. posted transactions
- **Slightly different amounts**: Banks sometimes adjust transactions
- **Different descriptions**: Same transaction may appear differently in different downloads

## Generating Reports

### Monthly Spending Analysis

1. **Select date range** in the Report Panel
2. **Choose categories** to include/exclude
3. **Generate report** to see spending patterns

### Budget Planning

Use the category breakdown to:
- **Identify major expense areas**
- **Track recurring vs. one-time expenses**
- **Plan retirement budget needs**
- **Find potential savings opportunities**

### Export Options

Reports can be:
- **Viewed on screen** for quick analysis
- **Exported to CSV** for spreadsheet analysis
- **Saved as reports** for historical comparison

## Configuration

### Database Location

By default, Budgy stores your data in:
- **Windows**: `%APPDATA%\budgy\budgydata.db`
- **macOS/Linux**: `~/.config/budgy/budgydata.db`

To change the database location:
1. **Edit configuration file** (`budgyconfig.json`)
2. **Update "database" → "path"** setting
3. **Restart Budgy**

### Import Directory

Set a default directory for OFX file imports:
1. **Edit configuration file**
2. **Update "import_data" → "import_dir"** setting
3. **Files will default to this location**

### Retirement Planning

Configure your retirement target date:
1. **Edit "retirement" → "target-date"** in config
2. **Format**: "YYYY/MM/DD"
3. **Used for long-term planning calculations**

## Troubleshooting

### Common Issues

**Import Fails with "File not supported"**
- Ensure file is in OFX format (not CSV, PDF, or other formats)
- Try downloading with different export options from your bank
- Check that file isn't corrupted (try opening in text editor)

**Transactions Not Appearing**
- Check date range in view filters
- Verify account name matches between imports
- Look for transactions in "Uncategorized" category

**Category Changes Not Saving**
- Ensure you have write permissions to database directory
- Check that database file isn't read-only
- Restart Budgy and try again

**Performance Issues with Large Datasets**
- Consider archiving old data
- Import in smaller date ranges
- Close other applications if memory is limited

### Getting Help

**Log Files**: Check for error messages in:
- Console output when running from command line
- System logs for application errors

**Database Issues**: If database becomes corrupted:
1. Backup your database file
2. Try reimporting from original OFX files
3. Check file permissions on database directory

**Support**: 
- Check [GitHub Issues](https://github.com/PapaMarky/budgy/issues) for known problems
- Review [Release Notes](RELEASE_NOTES.md) for recent changes
- Consult [Design Documentation](docs/BUDGY_UI_Design_Notes.md) for technical details

### Advanced Usage

**Command-Line Batch Processing**:
```bash
# Import multiple files
for file in *.ofx; do
    budgy-import --db mydata.db "$file"
done

# Specify custom database location
budgy-import --db /custom/path/mydata.db transactions.ofx
```

**Custom Configuration**:
```json
{
    "database": {
        "path": "/custom/path/budgy.db"
    },
    "import_data": {
        "import_dir": "/path/to/downloads"
    },
    "retirement": {
        "target-date": "2030/12/31"
    }
}
```

## Tips for Effective Use

1. **Regular Imports**: Import monthly for best results
2. **Consistent Categories**: Use the same categories for similar transactions
3. **Review and Adjust**: Periodically review auto-categorization rules
4. **Backup Data**: Keep backups of your database file
5. **Start Simple**: Begin with major categories, add detail over time

---

*For technical documentation, see [Design Notes](docs/BUDGY_UI_Design_Notes.md)*  
*For latest updates, see [Release Notes](RELEASE_NOTES.md)*
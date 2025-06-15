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

Budgy is a retirement planning tool specifically designed to help you understand your monthly expenses and estimate how much money you'll need in retirement. Unlike general budgeting tools, Budgy focuses on differentiating between expenses that will continue after retirement versus those that won't.

### Retirement Planning Focus

**The Goal**: Analyze your current spending to project your post-retirement budget needs.

**Key Insight**: Not all current expenses will continue in retirement. Budgy helps you categorize expenses to identify:

- **Ongoing Expenses**: Rent, utilities, insurance, groceries → Will continue in retirement
- **One-Time Expenses**: Car purchases, home repairs → May or may not be relevant post-retirement  
- **Pre-Retirement Only**: College tuition, work clothes, commuting costs → Won't continue in retirement

**How Budgy Helps**:

1. **Import** your bank and credit card transactions
2. **Categorize** expenses by type (recurring vs. one-time) and retirement relevance
3. **Analyze** patterns to understand your true ongoing monthly needs
4. **Project** realistic retirement income requirements based on actual spending data

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
budgy-help
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
3. **Select your OFX file(s)** in the file dialog
   - **Multiple files**: You can select multiple OFX files at once
   - **Folder imports**: Select all files in a download folder without worry
4. **Wait for import to complete** - progress will be shown in the Message Panel
5. **Review imported transactions** in the data view

### Smart Import Features

**Safe Re-importing**: Budgy's intelligent import system means you can:

- **Import the same file multiple times** without creating duplicates
- **Select entire folders** of OFX files without tracking which ones you've already imported
- **Download new statements** and reimport everything - only new transactions are added
- **Modify transaction categories** without losing changes on reimport

**How it Works**:

- Budgy uses unique transaction identifiers (FITID + account + date) to detect duplicates
- Previously imported transactions are skipped, preserving any category changes you've made
- Only genuinely new transactions are added to your database
- Your manual categorization work is always preserved

### Import Tips

- **Don't worry about duplicates**: Import all your OFX files whenever you want updates
- **Bulk importing**: Download several months of statements and import them all at once
- **Regular updates**: Monthly imports work well - just grab all your latest statements
- **Multiple accounts**: Import files from different banks/cards in any order
- **Start comprehensive**: Import 6-12 months of data to get meaningful spending analysis

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

When creating categories, think about retirement planning:

1. **Open Category Dialog**: Click "Edit" next to category dropdown
2. **Enter Category Details**:

   - **Main Category**: e.g., "Medical"
   - **Subcategory**: e.g., "Prescriptions"
   - **Expense Type** (crucial for retirement planning):

     - **Non-expense**: Income, transfers → Not part of spending analysis
     - **One-time expense**: Car purchase, vacation → Evaluate retirement relevance case-by-case
     - **Recurring expense**: Rent, utilities, groceries → Will likely continue in retirement

**Retirement Planning Tips**:

- **Recurring expenses** form the core of your retirement budget estimate
- **One-time expenses** need individual evaluation (will you still take vacations? buy cars?)
- Consider creating subcategories for **pre-retirement only** items (commuting, work clothes, child expenses)

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

### Retirement Budget Analysis

Use Budgy's categorized data to build your retirement budget:

**Step 1: Analyze Recurring Expenses**
- Focus on `expense_type=2` (recurring) categories
- These form your baseline monthly retirement needs
- Examples: housing, utilities, insurance, food, medical

**Step 2: Evaluate One-Time Expenses**
- Review `expense_type=1` (one-time) categories  
- Decide which will continue in retirement (travel, car purchases)
- Exclude pre-retirement only items (college tuition, work expenses)

**Step 3: Calculate Monthly Retirement Income Need**
- Sum recurring expenses that will continue
- Add average monthly amount for relevant one-time expenses
- Factor in new retirement expenses (healthcare, leisure)
- This gives your target monthly retirement income

**Key Questions to Ask**:

- Will I still have housing payments in retirement?
- How will medical expenses change?
- What new expenses will I have (travel, hobbies)?
- Which current expenses will disappear (commuting, work clothes, child expenses)?

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

- Console output when running budgy-viewer from terminal
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

**Efficient Import Workflows**:

- **Bulk Folder Import**: Select all OFX files in your downloads folder at once
- **Periodic Updates**: Download latest statements and reimport everything monthly
- **Historical Analysis**: Import 12+ months of data for comprehensive spending patterns
- **Multi-Account Setup**: Import files from all banks/cards into one database

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

## Tips for Effective Retirement Planning

1. **Import Comprehensive Data**: Import 12+ months to identify seasonal patterns and annual expenses
2. **Think Long-Term Categories**: Create categories that reflect post-retirement reality, not just current spending
3. **Distinguish Expense Types**: Carefully assign expense types - this is crucial for retirement projections
4. **Regular Review**: Monthly imports and quarterly category review help refine your retirement estimates
5. **Document Assumptions**: Note your thinking about which expenses will/won't continue in retirement
6. **Consider Life Changes**: Factor in how expenses might change with age, health, housing decisions
7. **Plan for New Expenses**: Remember retirement may bring new costs (healthcare, leisure, travel)

---

*For technical documentation, see [Design Notes](docs/BUDGY_UI_Design_Notes.md)*  
*For latest updates, see [Release Notes](RELEASE_NOTES.md)*
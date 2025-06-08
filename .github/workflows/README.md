# GitHub Workflows

This directory contains the CI/CD workflows for the Budgy project.

## Phase 1 Implementation (Completed)

### Workflows

#### 1. `ci.yml` - Main CI Orchestrator
- **Purpose**: Single entry point that coordinates all other workflows
- **Triggers**: Push to main/develop, pull requests, manual dispatch
- **Features**:

  - Calls test and build workflows
  - Provides unified dashboard view
  - Generates workflow summary
  - Manual workflow dispatch with options

#### 2. `test.yml` - Comprehensive Test Suite
- **Purpose**: Run tests across multiple environments
- **Features**:

  - Matrix testing: Python 3.9-3.11 on Ubuntu/macOS/Windows
  - GUI testing support with virtual display (xvfb)
  - Custom primary key fix tests
  - Coverage reporting and artifact upload
  - Integration tests for OFX import and database migration

#### 3. `build.yml` - Package Building
- **Purpose**: Build distributable packages and verify integrity
- **Features**:

  - Clean build process using `python -m build`
  - Package verification with entry point testing
  - Artifact upload for `dist/` directory
  - Metadata collection and validation

## Key Features Implemented

### ✅ Unified Dashboard
- All workflows show in single CI summary page
- Coordinated execution through main orchestrator
- Clear status reporting and summaries

### ✅ Matrix Testing Strategy
- Python 3.9, 3.10, 3.11 support
- Cross-platform testing (Ubuntu, macOS, Windows)
- Optimized matrix to reduce CI costs while maintaining coverage

### ✅ GUI Testing Environment
- Virtual display setup for pygame components on Linux
- SDL environment variables for headless testing
- Proper handling of GUI dependencies across platforms

### ✅ Artifact Collection
- Test coverage reports (XML and HTML)
- Build distributions (wheel and source)
- Test logs and debugging information
- Proper retention policies

### ✅ Custom Test Integration
- Executes `test_primary_key_fix.py` test suite
- Integration tests for core functionality
- Database migration testing

## Usage

### Automatic Triggers
- **Push to main/develop**: Runs full CI pipeline
- **Pull requests**: Runs full CI pipeline for validation

### Manual Execution
```bash
# Trigger via GitHub UI or CLI
gh workflow run ci.yml
```

### Viewing Results
1. Go to repository Actions tab
2. Click on any workflow run
3. View unified summary in main CI workflow
4. Download artifacts from individual workflow runs

## Artifacts

### Test Artifacts
- **Coverage Reports**: `coverage-{os}-py{version}`
- **Test Logs**: `test-logs-{os}-py{version}`
- **Combined Coverage**: `combined-coverage-report`

### Build Artifacts
- **Package Distributions**: `python-package-distributions`
- **Package Metadata**: `package-metadata`

## Next Phases

### Phase 2 (Planned)
- Code quality and linting workflows
- Enhanced build verification
- Performance optimizations

### Phase 3 (Planned)
- Security scanning workflows
- Advanced caching strategies
- Release automation preparation

## Configuration

### Environment Variables
- `SDL_VIDEODRIVER=dummy`: Prevents pygame from opening video devices
- `SDL_AUDIODRIVER=dummy`: Prevents pygame from opening audio devices

### Dependencies
- System packages for GUI testing (Linux: xvfb, x11-utils, etc.)
- Python build tools (build, twine, setuptools)
- Testing frameworks (tox, pytest, coverage)

## Troubleshooting

### Common Issues
1. **GUI tests failing on Linux**: Check xvfb setup and X11 dependencies
2. **Build failures**: Verify all dependencies are properly installed
3. **Coverage upload issues**: Check file paths and artifact naming

### Debug Steps
1. Check workflow logs in GitHub Actions tab
2. Download test artifacts for detailed examination
3. Run workflows manually with debug options
4. Check individual job outputs in matrix builds
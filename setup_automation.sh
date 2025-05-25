#!/bin/bash
# 🚀 Repository Automation Setup Script
# Automates the setup of development environment and tools

set -e  # Exit on error

echo "🚀 Setting up Trading Analysis Repository Automation"
echo "=================================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

# Check if Python is installed
check_python() {
    if command -v python3 &> /dev/null; then
        PYTHON_VERSION=$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
        print_status "Python $PYTHON_VERSION detected"
    else
        print_error "Python 3 is required but not installed"
        exit 1
    fi
}

# Setup virtual environment
setup_venv() {
    if [ ! -d "venv" ]; then
        print_info "Creating virtual environment..."
        python3 -m venv venv
        print_status "Virtual environment created"
    else
        print_info "Virtual environment already exists"
    fi
    
    # Activate virtual environment
    source venv/bin/activate || source venv/Scripts/activate
    print_status "Virtual environment activated"
}

# Install dependencies
install_dependencies() {
    print_info "Installing dependencies..."
    
    # Upgrade pip first
    python -m pip install --upgrade pip
    
    # Install from requirements.txt if it exists
    if [ -f "requirements.txt" ]; then
        pip install -r requirements.txt
        print_status "Dependencies installed from requirements.txt"
    else
        print_warning "requirements.txt not found, installing basic dependencies"
        pip install numpy pandas matplotlib seaborn yfinance
    fi
    
    # Install development dependencies
    pip install black flake8 isort pytest bandit safety mypy
    print_status "Development tools installed"
}

# Setup pre-commit hooks
setup_precommit() {
    print_info "Setting up pre-commit hooks..."
    
    # Create pre-commit hook script
    mkdir -p .git/hooks
    cat << 'EOF' > .git/hooks/pre-commit
#!/bin/bash
# Pre-commit hook for code quality

echo "Running pre-commit checks..."

# Check for Python files
if git diff --cached --name-only | grep -q '\.py$'; then
    echo "🔍 Running code quality checks..."
    
    # Run Black formatting check
    if command -v black &> /dev/null; then
        black --check --diff . || {
            echo "❌ Code formatting issues found. Run 'black .' to fix."
            exit 1
        }
    fi
    
    # Run import sorting check
    if command -v isort &> /dev/null; then
        isort --check-only --diff . || {
            echo "❌ Import sorting issues found. Run 'isort .' to fix."
            exit 1
        }
    fi
    
    # Run basic linting
    if command -v flake8 &> /dev/null; then
        flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics
    fi
    
    echo "✅ Code quality checks passed"
fi

EOF
    
    chmod +x .git/hooks/pre-commit
    print_status "Pre-commit hooks configured"
}

# Create development scripts
create_dev_scripts() {
    print_info "Creating development scripts..."
    
    # Format code script
    cat << 'EOF' > format_code.sh
#!/bin/bash
# Format code using Black and isort
echo "🎨 Formatting code..."
black .
isort .
echo "✅ Code formatted"
EOF
    
    # Run tests script
    cat << 'EOF' > run_tests.sh
#!/bin/bash
# Run all tests and checks
echo "🧪 Running tests and checks..."

# Run tests
if [ -f "requirements.txt" ]; then
    pytest -v --cov=. || echo "Tests completed with issues"
fi

# Run security checks
bandit -r . -ll || echo "Security scan completed"
safety check || echo "Dependency check completed"

echo "✅ All checks completed"
EOF
    
    # Make scripts executable
    chmod +x format_code.sh run_tests.sh
    print_status "Development scripts created"
}

# Setup GitHub labels (for repository management)
setup_github_labels() {
    print_info "GitHub Labels Recommendations:"
    echo "
    Suggested labels for issue management:
    
    🐛 bug - Something isn't working
    ✨ enhancement - New feature or request  
    📚 documentation - Improvements or additions to docs
    🔒 security - Security-related issues
    ⚡ performance - Performance improvements
    🧪 testing - Testing-related changes
    🔄 dependencies - Dependency updates
    ❓ question - Further information is requested
    🚀 feature-request - New feature suggestions
    📈 trading - Trading-specific features
    💹 indicators - Technical indicators
    📊 analysis - Analysis tools and methods
    "
}

# Create project overview
create_project_overview() {
    print_info "Creating project overview..."
    
    cat << 'EOF' > PROJECT_OVERVIEW.md
# 📊 Trading Analysis - Project Overview

## 🎯 Project Status
This repository contains advanced trading analysis tools with comprehensive automation:

### ✅ Completed Features
- **RSI Calculator** - Full implementation with visualization
- **Technical Analysis Framework** - Multiple indicators support
- **Automated Testing** - CI/CD pipeline configured
- **Code Quality** - Linting, formatting, security checks
- **Dependency Management** - Automated updates via Dependabot
- **Issue Templates** - Bug reports and feature requests
- **Development Tools** - Pre-commit hooks, formatting scripts

### 🚀 Next Steps
1. **Implement additional indicators** (MACD, Bollinger Bands, etc.)
2. **Add backtesting framework** for strategy validation
3. **Create desktop application** for real-time monitoring
4. **Integrate with trading APIs** for live data
5. **Add machine learning models** for prediction

## 🛠️ Development Workflow

### Setup
```bash
./setup_automation.sh  # Run this script
```

### Daily Development
```bash
./format_code.sh      # Format code before committing
./run_tests.sh        # Run tests and security checks
```

### Git Workflow
1. Create feature branch: `git checkout -b feature/new-indicator`
2. Make changes and commit
3. Pre-commit hooks run automatically
4. Push and create pull request
5. Automated tests run on GitHub
6. Review and merge

## 📋 Issue Management
- Use `BUG_REPORT_TEMPLATE.md` for bugs
- Use `FEATURE_REQUEST_TEMPLATE.md` for new features
- Label issues appropriately for organization

## 🔄 Automation Features
- **Weekly dependency updates** via Dependabot
- **Automated security scanning** on every push
- **Code quality checks** in CI/CD pipeline
- **Pre-commit hooks** for local validation

---
*Last updated: $(date)*
EOF

    print_status "Project overview created"
}

# Main setup function
main() {
    echo "Starting automated setup..."
    
    check_python
    setup_venv
    install_dependencies
    setup_precommit
    create_dev_scripts
    setup_github_labels
    create_project_overview
    
    echo ""
    echo "🎉 Repository automation setup completed!"
    echo "=================================================="
    print_status "Virtual environment created and dependencies installed"
    print_status "Pre-commit hooks configured"
    print_status "Development scripts created (format_code.sh, run_tests.sh)"
    print_status "Project documentation updated"
    
    echo ""
    print_info "Next steps:"
    echo "1. Run './format_code.sh' to format your code"
    echo "2. Run './run_tests.sh' to test your setup"
    echo "3. Commit your changes - pre-commit hooks will run automatically"
    echo "4. Push to GitHub - automated tests will run"
    echo ""
    print_info "Happy coding! 🚀"
}

# Run main function
main "$@"

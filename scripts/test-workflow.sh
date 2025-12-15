#!/bin/bash
# Test GitHub Actions workflows locally using act
# Install act: https://github.com/nektos/act

set -e

WORKFLOW_FILE=".github/workflows/ci.yml"

echo "🔍 Testing GitHub Actions workflow locally..."
echo ""

# Check if act is installed
if ! command -v act &> /dev/null; then
    echo "❌ Error: 'act' is not installed."
    echo ""
    echo "Please install act to test workflows locally:"
    echo "  macOS: brew install act"
    echo "  Linux: https://github.com/nektos/act#installation"
    echo "  Windows: https://github.com/nektos/act#installation"
    echo ""
    echo "Documentation: https://github.com/nektos/act"
    exit 1
fi

# Check if workflow file exists
if [ ! -f "$WORKFLOW_FILE" ]; then
    echo "❌ Error: Workflow file not found: $WORKFLOW_FILE"
    exit 1
fi

echo "📋 Available jobs:"
echo "  - master-backend: Test backend build and tests"
echo "  - master-frontend: Test frontend build"
echo ""
echo "💡 Usage examples:"
echo "  Run all jobs: ./scripts/test-workflow.sh"
echo "  Run specific job: act -j master-backend"
echo "  List jobs: act -l"
echo ""

# Run act
if [ "$1" != "" ]; then
    # Run specific job if provided
    echo "🚀 Running job: $1"
    act -j "$1"
else
    # Run all jobs
    echo "🚀 Running all jobs..."
    echo "   (Note: Some jobs may require platform-specific runners)"
    act
fi

echo ""
echo "✅ Workflow test completed!"
echo ""
echo "📝 Note: Some jobs (e.g., agent-windows, agent-macos) require platform-specific"
echo "   runners and may not run on macOS. Use 'act -j <job-name>' to test specific jobs."



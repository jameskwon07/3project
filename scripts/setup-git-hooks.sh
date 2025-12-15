#!/bin/bash
# Setup Git hooks for the project

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
GIT_HOOKS_DIR="$PROJECT_ROOT/.git/hooks"

echo "🔧 Setting up Git hooks..."
echo ""

# Check if .git/hooks directory exists
if [ ! -d "$GIT_HOOKS_DIR" ]; then
    echo "❌ Error: .git/hooks directory not found."
    echo "   Make sure you're in a Git repository."
    exit 1
fi

# Setup pre-push hook
PRE_PUSH_HOOK="$GIT_HOOKS_DIR/pre-push"
PRE_PUSH_SCRIPT="$SCRIPT_DIR/pre-push"

if [ -f "$PRE_PUSH_SCRIPT" ]; then
    # Copy pre-push hook
    cp "$PRE_PUSH_SCRIPT" "$PRE_PUSH_HOOK"
    chmod +x "$PRE_PUSH_HOOK"
    echo "✅ Pre-push hook installed: $PRE_PUSH_HOOK"
else
    echo "⚠️  Warning: pre-push script not found: $PRE_PUSH_SCRIPT"
fi

echo ""
echo "✅ Git hooks setup completed!"
echo ""
echo "The pre-push hook will now test GitHub Actions workflows locally before allowing push."
echo ""
echo "To skip hooks temporarily (not recommended):"
echo "  git push --no-verify"



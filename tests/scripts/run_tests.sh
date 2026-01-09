#!/bin/bash
# 运行测试脚本

set -e

echo "🧪 Running tests..."

# 运行 pytest
python -m pytest tests/ -v --tb=short

echo "✅ All tests passed!"


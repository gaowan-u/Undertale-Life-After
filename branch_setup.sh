#!/bin/bash

echo "🎮 开始分支管理操作..."

# 步骤1：创建并切换到 feat/pc-optimization 分支（基于当前 main 分支的状态）
echo "📁 创建 PC 优化分支..."
git checkout -b feat/pc-optimization

# 步骤2：推送 PC 分支到远程（可选）
git push -u origin feat/pc-optimization

echo "✅ PC 分支创建完成，当前分支: feat/pc-optimization"

# 步骤3：切换回 main 分支
git checkout main

echo "📁 开始合并 AIDE 项目到 main 分支..."

# 步骤4：定义外部 AIDE 项目路径
AIDE_PROJECT="/storage/emulated/0/AideProjects/UndertaleLifeAfter"

# 步骤5：复制 Android 项目文件（不覆盖现有资源）
cp -r "$AIDE_PROJECT/app" .
cp "$AIDE_PROJECT/build.gradle" .
cp "$AIDE_PROJECT/settings.gradle" .
cp "$AIDE_PROJECT/gradle.properties" .
cp "$AIDE_PROJECT/local.properties" 2>/dev/null || true  # 忽略如果不存在

echo "✅ AIDE 项目文件复制完成"

# 步骤6：在 main 分支中清理 Python 文件（保留所有资源）
echo "🧹 清理 main 分支中的 Python 文件..."
rm -f main.py main_menu.py gameplay.py intro_animation.py
rm -rf __pycache__

echo "✅ 文件清理完成"

# 步骤7：提交更改到 main 分支
git add .
git commit -m "feat: 合并 Android 项目代码并清理 Python 文件"

echo "🎉 操作完成！"
echo ""
echo "📊 当前分支状态："
echo "   - main 分支: Android 项目 (Kotlin) + 资源"
echo "   - feat/pc-optimization 分支: PC 项目 (Python) + 资源"
echo ""
echo "💡 注意：资源路径在 Android 中可能需要调整，但 PC 分支保持原样。"
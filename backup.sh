#!/bin/bash

# 备份脚本 - 将关键开发文件备份到 releases 文件夹
# 使用方法: ./backup.sh

# 设置颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 获取当前日期和时间
DATE=$(date +"%Y%m%d_%H%M%S")
BACKUP_DIR="releases/$DATE"

echo -e "${GREEN}开始备份 GPU-KataGO-http-server 项目文件...${NC}"
echo -e "${YELLOW}备份目录: $BACKUP_DIR${NC}"

# 创建备份目录
mkdir -p "$BACKUP_DIR"

# 要备份的文件和文件夹列表
BACKUP_ITEMS=(
    "*.py"
    "*.json"
    "*.yaml"
    "*.sh"
    "*.ps1"
    "*.md"
    "Dockerfile.*"
    "docker-compose.*.yml"
    "configs/"
    "kubernetes/"
    "katago-server/"
    "Pythontest/"
    "Doc/"
    ".gitignore"
)

# 要排除的文件和文件夹
EXCLUDE_PATTERNS=(
    "katago-server/katago_eigen"
    "KataGo-BlackRice"
    "models"
    "bin"
    "logs"
    "releases"
    ".git"
    "__pycache__"
    "*.log"
    ".DS_Store"
)

echo -e "${YELLOW}正在复制文件...${NC}"

# 创建临时排除列表文件
EXCLUDE_FILE=$(mktemp)
for pattern in "${EXCLUDE_PATTERNS[@]}"; do
    echo "$pattern" >> "$EXCLUDE_FILE"
done

# 复制文件和文件夹
for item in "${BACKUP_ITEMS[@]}"; do
    if [ -e "$item" ]; then
        if [[ "$item" == *"/" ]]; then
            # 这是一个文件夹
            folder_name=${item%/}
            echo "复制文件夹: $folder_name"
            # 使用 rsync 来处理排除
            rsync -av --exclude-from="$EXCLUDE_FILE" "$folder_name" "$BACKUP_DIR/" > /dev/null
        else
            # 这是文件或通配符（直接 ls 处理，因为通配符在数组中可能不会自动扩展）
            for f in $item; do
                if [ -f "$f" ]; then
                    # 检查文件是否在排除列表中
                    exclude=false
                    for pattern in "${EXCLUDE_PATTERNS[@]}"; do
                        if [[ "$f" == *$pattern* ]]; then
                            exclude=true
                            break
                        fi
                    done
                    
                    if [ "$exclude" = false ]; then
                        echo "复制文件: $f"
                        cp "$f" "$BACKUP_DIR/"
                    fi
                fi
            done
        fi
    else
        # 可能是通配符没匹配到，或者是文件夹不存在
        # 如果是通配符，需要尝试展开
        matched=false
        for f in $item; do
            if [ -e "$f" ]; then
                matched=true
                if [ -d "$f" ]; then
                    echo "复制文件夹: $f"
                    rsync -av --exclude-from="$EXCLUDE_FILE" "$f" "$BACKUP_DIR/" > /dev/null
                else
                    echo "复制文件: $f"
                    cp "$f" "$BACKUP_DIR/"
                fi
            fi
        done
        if [ "$matched" = false ]; then
            echo -e "${RED}警告: 没有找到匹配 $item 的项${NC}"
        fi
    fi
done

rm "$EXCLUDE_FILE"

# 创建备份信息文件
cat > "$BACKUP_DIR/backup_info.txt" << EOF
备份信息
========
备份时间: $(date)
项目名称: GPU-KataGO-http-server
备份内容: 开发关键文件、配置文件和 K8s 配置

备份的文件和文件夹:
$(for item in "${BACKUP_ITEMS[@]}"; do echo "- $item"; done)

排除的内容:
$(for pattern in "${EXCLUDE_PATTERNS[@]}"; do echo "- $pattern"; done)

Git分支: $(git branch --show-current 2>/dev/null || echo "未知")
Git提交: $(git rev-parse HEAD 2>/dev/null || echo "未知")
EOF

# 计算备份大小
BACKUP_SIZE=$(du -sh "$BACKUP_DIR" | cut -f1)

echo -e "${GREEN}备份完成！${NC}"
echo -e "${YELLOW}备份位置: $BACKUP_DIR${NC}"
echo -e "${YELLOW}备份大小: $BACKUP_SIZE${NC}"
echo -e "${GREEN}备份信息已保存到: $BACKUP_DIR/backup_info.txt${NC}"

# 列出最近的5个备份
if [ -d "releases" ]; then
    echo -e "\n${YELLOW}最近的备份:${NC}"
    ls -lt releases/ | head -6
fi

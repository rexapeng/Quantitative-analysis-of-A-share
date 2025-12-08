#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
检查数据库中的表结构
"""

import os
import sys
import json
import sqlite3

# 添加项目根目录到Python路径
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.append(project_root)

# 使用正确的数据库路径
db_path = os.path.join(project_root, 'data', 'data', 'database.db')

# 如果上面的路径不存在，尝试另一个可能的路径
if not os.path.exists(db_path):
    db_path = os.path.join(project_root, 'data', 'database.db')

print(f"Trying to connect to database at: {db_path}")
print(f"Database file exists: {os.path.exists(db_path)}")

# 连接数据库
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# 查看所有表
print("数据库中的表:")
cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables = cursor.fetchall()
for table in tables:
    print(f"- {table[0]}")
    
    # 查看表结构
    print(f"  表结构:")
    cursor.execute(f"PRAGMA table_info({table[0]});")
    columns = cursor.fetchall()
    for column in columns:
        print(f"    - {column[1]} ({column[2]})")
    
    # 查看表中的数据行数
    cursor.execute(f"SELECT COUNT(*) FROM {table[0]};")
    count = cursor.fetchone()[0]
    print(f"  数据行数: {count}")
    print()

# 关闭数据库连接
conn.close()
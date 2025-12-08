import sqlite3
import os
import json

def check_database():
    """检查数据库内容"""
    # 从配置文件获取数据库路径
    try:
        with open('config/config.json', 'r') as f:
            config = json.load(f)
        db_path = config.get('DATABASE_PATH', 'database/sz50_stock_data.db')
    except FileNotFoundError:
        db_path = 'database/sz50_stock_data.db'
    
    if not os.path.exists(db_path):
        print(f"数据库文件不存在: {db_path}")
        return
    
    print(f"数据库文件存在: {db_path}")
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # 检查表名
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        print("数据库中的表:")
        for table in tables:
            print(f"  - {table[0]}")
        
        # 检查daily_quotes表的数据量
        cursor.execute("SELECT COUNT(*) FROM daily_quotes")
        count = cursor.fetchone()[0]
        print(f"\ndaily_quotes表中有 {count} 条记录")
        
        # 检查表结构
        cursor.execute("PRAGMA table_info(daily_quotes)")
        columns = cursor.fetchall()
        print("\ndaily_quotes表结构:")
        for col in columns:
            print(f"  - {col}")
        
        # 查看前几条数据
        if count > 0:
            cursor.execute("SELECT * FROM daily_quotes LIMIT 5")
            rows = cursor.fetchall()
            print("\n前5条数据:")
            for row in rows:
                print(row)
        
        # 检查factors表的数据量
        cursor.execute("SELECT COUNT(*) FROM factors")
        factor_count = cursor.fetchone()[0]
        print(f"\nfactors表中有 {factor_count} 条记录")
        
        # 如果factors表有数据，查看前几条
        if factor_count > 0:
            cursor.execute("SELECT * FROM factors LIMIT 5")
            rows = cursor.fetchall()
            print("\nfactors表前5条数据:")
            for row in rows:
                print(row)
        else:
            print("\nfactors表为空")
        
        conn.close()
        
    except Exception as e:
        print(f"检查数据库时出错: {e}")

if __name__ == "__main__":
    check_database()
"""
应用入口包
注意：不在 __init__.py 中导入 app，避免循环导入
循环导入链：app/main.py → app.core.config → app/__init__.py → app.main.app
"""
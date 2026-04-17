"""
Vercel Serverless Function 入口点
"""
from app.main import app

# Vercel 需要这个 handler
handler = app

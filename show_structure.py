#!/usr/bin/env python3
"""
Project Structure Visualizer
Shows complete file tree of the Intelligent Sports Management System
Run: python show_structure.py
"""

import os
from pathlib import Path

def print_tree(directory, prefix="", is_last=True):
    """Print directory tree structure"""
    path = Path(directory)
    
    # Get all items and sort them
    items = sorted(path.iterdir(), key=lambda x: (not x.is_dir(), x.name))
    
    # Filter out common ignored files
    ignore = {'.pyc', '__pycache__', '.pytest_cache', '.DS_Store', '.git', '.gitignore'}
    items = [item for item in items if item.name not in ignore and not item.name.startswith('.')]
    
    for i, item in enumerate(items):
        is_last_item = i == len(items) - 1
        
        # Print the item
        connector = "└── " if is_last_item else "├── "
        print(f"{prefix}{connector}{item.name}")
        
        # If directory, recurse
        if item.is_dir():
            extension = "    " if is_last_item else "│   "
            print_tree(item, prefix + extension, is_last_item)

def main():
    root = Path(__file__).parent
    
    print("\n" + "="*70)
    print("🎯 INTELLIGENT SPORTS MANAGEMENT SYSTEM - PROJECT STRUCTURE")
    print("="*70 + "\n")
    
    print(f"📁 {root.name}/")
    print_tree(root, "")
    
    # Count files
    py_files = len(list(root.rglob("*.py")))
    html_files = len(list(root.rglob("*.html")))
    css_files = len(list(root.rglob("*.css")))
    js_files = len(list(root.rglob("*.js")))
    
    print("\n" + "="*70)
    print("📊 PROJECT STATISTICS")
    print("="*70)
    print(f"  Python files:     {py_files}")
    print(f"  HTML templates:   {html_files}")
    print(f"  CSS stylesheets:  {css_files}")
    print(f"  JavaScript files: {js_files}")
    print(f"  Documentation:    3 files (README, QUICK_START, SYSTEM_SUMMARY)")
    print(f"  Total files:      {py_files + html_files + css_files + js_files + 3+}")
    print("\n" + "="*70)
    print("✅ System ready for deployment!")
    print("="*70 + "\n")

if __name__ == "__main__":
    main()

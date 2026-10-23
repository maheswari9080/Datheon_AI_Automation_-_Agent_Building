"""
Build script to assemble the production static distribution for GitHub Pages.
"""

import os
import shutil

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SITE_DIR = os.path.join(ROOT_DIR, "_site")

def build_site():
    if os.path.exists(SITE_DIR):
        shutil.rmtree(SITE_DIR)
    os.makedirs(SITE_DIR, exist_ok=True)

    # 1. Copy index.html
    src_index = os.path.join(ROOT_DIR, "nexus_flow", "static", "index.html")
    dst_index = os.path.join(SITE_DIR, "index.html")
    shutil.copy2(src_index, dst_index)
    print(f"Copied index.html -> {dst_index}")

    # 2. Copy static/css & static/js
    dst_static = os.path.join(SITE_DIR, "static")
    src_static = os.path.join(ROOT_DIR, "nexus_flow", "static")
    shutil.copytree(os.path.join(src_static, "css"), os.path.join(dst_static, "css"))
    shutil.copytree(os.path.join(src_static, "js"), os.path.join(dst_static, "js"))
    print(f"Copied static assets -> {dst_static}")

    # 3. Copy visual assets
    src_assets = os.path.join(ROOT_DIR, "assets")
    if os.path.exists(src_assets):
        dst_assets = os.path.join(SITE_DIR, "assets")
        shutil.copytree(src_assets, dst_assets)
        print(f"Copied visual assets -> {dst_assets}")

    # 4. Copy docs
    src_docs = os.path.join(ROOT_DIR, "docs")
    if os.path.exists(src_docs):
        dst_docs = os.path.join(SITE_DIR, "docs")
        shutil.copytree(src_docs, dst_docs)
        print(f"Copied documentation -> {dst_docs}")

    # 5. Create 404.html (SPA Fallback)
    dst_404 = os.path.join(SITE_DIR, "404.html")
    shutil.copy2(src_index, dst_404)
    print(f"Created 404.html -> {dst_404}")

    # 6. Create .nojekyll
    dst_nojekyll = os.path.join(SITE_DIR, ".nojekyll")
    with open(dst_nojekyll, "w", encoding="utf-8") as f:
        f.write("")
    print(f"Created .nojekyll -> {dst_nojekyll}")

    print("[SUCCESS] Static site successfully built in:", SITE_DIR)

if __name__ == "__main__":
    build_site()

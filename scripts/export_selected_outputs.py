#!/usr/bin/env python3
"""
Export a notebook to HTML but keep outputs only for cells tagged with a chosen tag.

Usage examples (PowerShell):
  python .\scripts\export_selected_outputs.py --notebook .\Informe_Final_(4).ipynb --output .\Informe_filtrado.html --tag export_output

By default the script looks for the tag `export_output`. It also accepts cells with metadata `export_output: true`.
"""
import argparse
import nbformat
import tempfile
import os
import subprocess
import sys


def parse_args():
    p = argparse.ArgumentParser(description="Export notebook to HTML keeping outputs only for tagged cells")
    p.add_argument("--notebook", "-n", required=True, help="Path to the input .ipynb file")
    p.add_argument("--output", "-o", required=True, help="Path to output .html file")
    p.add_argument("--tag", "-t", default="export_output", help="Cell tag to keep outputs (default: export_output)")
    return p.parse_args()


def keep_output(cell, tag):
    # Support both metadata.tags and metadata.export_output boolean
    md = cell.get("metadata", {})
    tags = md.get("tags", []) or []
    if tag in tags:
        return True
    if md.get("export_output") is True:
        return True
    # Also support a marker comment at the top of the code cell
    src = cell.get("source", "")
    # nbformat can store source as list or string
    if isinstance(src, list):
        src_text = "".join(src)
    else:
        src_text = src

    for line in src_text.splitlines():
        s = line.strip()
        if not s:
            continue
        # accept both '#mostar' (typo) and '#mostrar' (correct Spanish)
        if s.lower().startswith("#mostar") or s.lower().startswith("#mostrar"):
            return True
        break

    return False


def main():
    args = parse_args()
    nb_path = os.path.abspath(args.notebook)
    out_path = os.path.abspath(args.output)
    tag = args.tag

    if not os.path.isfile(nb_path):
        print(f"Error: notebook not found: {nb_path}")
        sys.exit(2)

    nb = nbformat.read(nb_path, as_version=4)

    # Clear outputs for code cells that are NOT tagged
    for cell in nb.get("cells", []):
        if cell.get("cell_type") != "code":
            continue
        # If cell has top comment marker, add the tag to metadata so it's explicit
        try:
            src = cell.get("source", "")
            if isinstance(src, list):
                src_text = "".join(src)
            else:
                src_text = src
        except Exception:
            src_text = ""

        first_nonblank = None
        for line in src_text.splitlines():
            if line.strip():
                first_nonblank = line.strip()
                break

        if first_nonblank and (first_nonblank.lower().startswith("#mostar") or first_nonblank.lower().startswith("#mostrar")):
            md = cell.setdefault("metadata", {})
            tags = md.setdefault("tags", [])
            if tag not in tags:
                tags.append(tag)

        if not keep_output(cell, tag):
            cell["outputs"] = []
            cell["execution_count"] = None

        # Remove source code from all code cells so the exported HTML shows
        # only markdown text and the selected outputs (no code).
        cell["source"] = ""

    # write temporary notebook
    tmp = None
    try:
        fd, tmp = tempfile.mkstemp(suffix=".ipynb")
        os.close(fd)
        nbformat.write(nb, tmp)

        # Prepare nbconvert arguments
        out_dir = os.path.dirname(out_path) or os.getcwd()
        out_basename = os.path.splitext(os.path.basename(out_path))[0]

        cmd = [
            sys.executable,
            "-m",
            "nbconvert",
            "--to",
            "html",
            "--output",
            out_basename,
            "--output-dir",
            out_dir,
            tmp,
        ]

        print("Converting notebook (outputs filtered) to HTML...")
        subprocess.run(cmd, check=True)

        print(f"Export completed: {out_path}")
    except subprocess.CalledProcessError as e:
        print("Error running nbconvert:", e)
        sys.exit(3)
    finally:
        if tmp and os.path.exists(tmp):
            os.remove(tmp)


if __name__ == "__main__":
    main()

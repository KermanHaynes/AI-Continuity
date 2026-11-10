#!/usr/bin/env python3
"""Compatibility entry point; primary CLI is python -m memory.cli."""
import pathlib,sys
sys.path.insert(0,str(pathlib.Path(__file__).resolve().parents[1]))
from memory.cli import main
if __name__=='__main__':
    args=sys.argv[1:]
    if args and args[0]=='check': args[0]='validate'
    sys.exit(main(args))

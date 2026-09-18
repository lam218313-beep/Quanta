"""Convenience launcher for the SIRE downloader CLI.

Run from repo root:
  python sire_download_cli.py --period 202501 --books sales purchases
"""

from __future__ import annotations

from brain.sire_download_cli import main


if __name__ == "__main__":
    raise SystemExit(main())

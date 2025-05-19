#!/usr/bin/env python3
"""
leakify CLI: download photos/videos from leakedzone.com
"""

import argparse
import asyncio
import os
import re
import sys
import uuid
import base64
import shutil

import aiohttp
from bs4 import BeautifulSoup
from subprocess import PIPE
from tabulate import tabulate
from colorama import Fore, Style, init as colorama_init

# Initialize colorama
colorama_init(autoreset=True)

# Ensure ffmpeg is available

def ensure_ffmpeg():
    if shutil.which('ffmpeg') is None:
        print(f"{Fore.RED}Error: 'ffmpeg' not found in PATH. Please install ffmpeg and ensure it's on your PATH.{Style.RESET_ALL}")
        sys.exit(1)

API_BASE = "https://leakedzone.com"
HEADERS = {
    "User-Agent": "Mozilla/5.0",
    "X-Requested-With": "XMLHttpRequest"
}


def update_table(model: str, mode: str, status: str):
    """Clear screen and display status table."""
    os.system('cls' if os.name == 'nt' else 'clear')
    title = f"{Fore.GREEN}{Style.BRIGHT}{'Leakify V1.0'.center(70)}{Style.RESET_ALL}"
    print(title, "\n")
    headers = [
        f"{Style.BRIGHT}Model{Style.RESET_ALL}",
        f"{Style.BRIGHT}Mode{Style.RESET_ALL}",
        f"{Style.BRIGHT}Status{Style.RESET_ALL}"
    ]
    row = [model, mode, status]
    table = tabulate(
        [row],
        headers=headers,
        tablefmt="fancy_grid",
        stralign="center",
        numalign="right"
    )
    print(f"{Fore.CYAN}{table}{Style.RESET_ALL}")


async def fetch_photo_urls(model: str):
    """Fetch all full-size photo URLs for a model."""
    thumb_re = re.compile(r"https://image-cdn\.leakedzone\.com/.+_300\.(jpg|webp)$")
    urls, page = [], 1

    async with aiohttp.ClientSession(headers=HEADERS) as session:
        while True:
            url = f"{API_BASE}/{model}/photo?page={page}&type=photos&order=0"
            update_table(model, "photos", f"GET {url}")
            resp = await session.get(url)
            if resp.status != 200:
                break

            data = await resp.json()
            if not data:
                break

            for item in data:
                for v in item.values():
                    if isinstance(v, str) and thumb_re.match(v):
                        urls.append(v.replace("_300.", "."))
            page += 1

    return list(dict.fromkeys(urls))


async def fetch_video_urls(model: str, batch: int):
    """Fetch all HLS or direct video URLs for a model."""
    page_urls, hls_urls, page = [], [], 1

    async with aiohttp.ClientSession(headers=HEADERS) as session:
        while True:
            url = f"{API_BASE}/{model}/video?page={page}&type=videos&order=0"
            update_table(model, "videos", f"GET {url}")
            resp = await session.get(url)
            if resp.status != 200:
                break

            data = await resp.json()
            if not data:
                break

            for item in data:
                tok = item.get("stream_url_play", "")
                if len(tok) > 32:
                    core = tok[16:-16][::-1]
                    try:
                        dec = base64.b64decode(core).decode()
                        link = dec if dec.startswith("http") else f"https://cdn32.leakedzone.com/{dec}"
                        hls_urls.append(link)
                    except Exception:
                        pass
                for v in item.values():
                    if isinstance(v, str) and v.startswith(f"/{model}/video/"):
                        page_urls.append(API_BASE + v)
            page += 1

    sem = asyncio.Semaphore(batch)

    async def scrape_detail(url):
        async with sem, aiohttp.ClientSession(headers=HEADERS) as session:
            resp = await session.get(url)
            if resp.status != 200:
                return None
            soup = BeautifulSoup(await resp.text(), "html.parser")
            vid = soup.find("video")
            src = vid.find("source") if vid else None
            return src["src"].strip() if src else None

    tasks = [scrape_detail(u) for u in page_urls]
    for coro in asyncio.as_completed(tasks):
        if src := await coro:
            hls_urls.append(src)

    return list(dict.fromkeys(hls_urls))


async def download_worker(model: str, url: str, idx: int, total: int, folder: str, ext: str, headers=None):
    """Run ffmpeg to download one media file, with unique naming."""
    unique = uuid.uuid4().hex
    fname = f"leakify_{model}_{unique}.{ext}"
    update_table(model, folder, f"Downloading {idx}/{total}: {fname}")
    cmd = ["ffmpeg", "-y"]
    if headers:
        for h in headers:
            cmd.extend(["-headers", h])
    cmd.extend(["-i", url, "-c", "copy", f"{model}/{folder}/{fname}"])

    try:
        proc = await asyncio.create_subprocess_exec(*cmd, stdout=PIPE, stderr=PIPE)
        await proc.communicate()
    except FileNotFoundError:
        print(f"{Fore.RED}Error: 'ffmpeg' not found when attempting download. Aborting.{Style.RESET_ALL}")
        sys.exit(1)


async def download_bulk(model: str, urls: list, folder: str, ext: str, batch: int, extra_headers=None):
    """Download a list of URLs in parallel (limited by batch size)."""
    os.makedirs(f"./{model}/{folder}", exist_ok=True)
    sem = asyncio.Semaphore(batch)
    total = len(urls)

    async def sem_download(i, u):
        async with sem:
            return await download_worker(model, u, i, total, folder, ext, headers=extra_headers)

    tasks = [sem_download(i, u) for i, u in enumerate(urls, 1)]
    await asyncio.gather(*tasks)


async def main():
    parser = argparse.ArgumentParser(
        prog="leakify",
        description="Download photos/videos from leakedzone.com"
    )
    parser.add_argument("-u", "--user", required=True, help="Model username to scrape")
    group = parser.add_mutually_exclusive_group()
    group.add_argument("-p", "--photos", action="store_true", help="Only download photos")
    group.add_argument("-v", "--videos", action="store_true", help="Only download videos")
    parser.add_argument(
        "-b", "--batch", type=int, default=10,
        help="Max concurrent downloads (default: 10)"
    )
    args = parser.parse_args()

    model = args.user
    mode = (
        "photos only" if args.photos else
        "videos only" if args.videos else
        "photos + videos"
    )
    update_table(model, mode, "Starting…")

    photo_count = video_count = 0

    if args.photos or not args.videos:
        photos = await fetch_photo_urls(model)
        photo_count = len(photos)
        update_table(model, "photos", f"Found {photo_count} photos")
        if photos:
            await download_bulk(model, photos, 'photos', 'jpg', args.batch)
        else:
            update_table(model, "photos", "⚠️ No photos found")

    if args.videos or not args.photos:
        vids = await fetch_video_urls(model, args.batch)
        video_count = len(vids)
        update_table(model, "videos", f"Found {video_count} videos")
        if vids:
            headers = [
                "Referer: https://leakedzone.com/",
                "User-Agent: Mozilla/5.0"
            ]
            await download_bulk(model, vids, 'videos', 'mp4', args.batch, extra_headers=headers)
        else:
            update_table(model, "videos", "⚠️ No videos found")

    update_table(model, mode, "Complete ✅")
    print()
    print(f"Successfully downloaded {photo_count} photos and {video_count} videos.")
    input("Press any key to continue...")


def cli():
    """Sync entry point for leakify console_script."""
    ensure_ffmpeg()
    asyncio.run(main())


if __name__ == "__main__":
    cli()

import time
import csv
import requests
import yt_dlp
from datetime import datetime, timezone
from rich import print

LOG_FILE = "log.csv"

def measure_download_speed(url, label, chunk_size=1024 * 512):
    print(f"[+] Testing download speed from {label}...")
    try:
        start = time.time()
        r = requests.get(url, stream=True, timeout=10)
        total_bytes = 0
        for chunk in r.iter_content(chunk_size=chunk_size):
            if not chunk:
                break
            total_bytes += len(chunk)
            if total_bytes >= 5 * 1024 * 1024:
                break
        elapsed = time.time() - start
        speed_mbps = (total_bytes * 8) / (elapsed * 1024 * 1024)
        print(f"    -> {label} speed: {speed_mbps:.2f} Mbps")
        return speed_mbps
    except Exception as e:
        print(f"    [!] Error testing {label}: {e}")
        return 0

def get_youtube_video_url(video_id="dQw4w9WgXcQ"):
    ydl_opts = {
        'quiet': True,
        'skip_download': True,
        'format': 'best[height<=480]',
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(f"https://www.youtube.com/watch?v={video_id}", download=False)
        return info['url']

def log_result(timestamp, vpn_status, site, speed):
    with open(LOG_FILE, mode="a", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([timestamp, vpn_status, site, f"{speed:.2f}"])

def run_test(vpn_status):
    print(f"\n=== Running tests ({vpn_status}) ===")
    timestamp = datetime.now(timezone.utc).isoformat()

    youtube_url = get_youtube_video_url()
    yt_speed = measure_download_speed(youtube_url, "YouTube")
    log_result(timestamp, vpn_status, "YouTube", yt_speed)

    comparison_sites = {
        "Google": "https://www.google.com/images/branding/googlelogo/1x/googlelogo_color_272x92dp.png",
        "Cloudflare": "https://speed.cloudflare.com/__down?bytes=5000000",
        "OVH CDN": "http://proof.ovh.net/files/5Mb.dat"
    }

    other_speeds = []
    for label, url in comparison_sites.items():
        speed = measure_download_speed(url, label)
        other_speeds.append(speed)
        log_result(timestamp, vpn_status, label, speed)

    avg_other = sum(other_speeds) / len(other_speeds)
    print(f"\n[=] Average of other sites: {avg_other:.2f} Mbps")
    print(f"[=] YouTube speed: {yt_speed:.2f} Mbps")

    return yt_speed, avg_other

def init_log_file():
    try:
        with open(LOG_FILE, "x", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["Timestamp", "VPN_Status", "Site", "Speed_Mbps"])
    except FileExistsError:
        pass  # Already exists

def main():
    init_log_file()

    print("=== ISP Throttling Detection Script with VPN Comparison ===")
    print("Author: gvmrh\n")
    
    print("\n[1/2] Testing WITHOUT VPN...")
    yt1, avg1 = run_test("no-vpn")

    input("\nNow enable your VPN and press Enter to continue...")

    print("\n[2/2] Testing WITH VPN...")
    yt2, avg2 = run_test("vpn")

    print("\n=== Comparison Summary ===")
    print(f"YouTube (No VPN): {yt1:.2f} Mbps")
    print(f"YouTube (VPN):    {yt2:.2f} Mbps")
    print(f"Other Avg (No VPN): {avg1:.2f} Mbps")
    print(f"Other Avg (VPN):    {avg2:.2f} Mbps")

    if yt1 < avg1 * 0.5 and yt2 > avg2 * 0.8:
        print("\n⚠️  Likely ISP throttling detected — YouTube improves significantly when using VPN.")
    elif yt2 < yt1:
        print("\n🔎 VPN results in slower YouTube speed. Possibly no throttling, or VPN is slower.")
    else:
        print("\n✅ No significant throttling detected.")

if __name__ == "__main__":
    main()

"""Things that must keep working when something goes wrong or grows large: the creator activity log, the machine
monitor on a system it cannot fully measure, a recording whose ffmpeg cannot start, and the admin day totals.
Runs against the code directly, with its own empty data folder: nothing outside it is touched."""
import os, sys, tempfile, threading, time
os.environ["PEAKCUT_DATA"] = tempfile.mkdtemp(prefix="pc-robust-"); os.environ["DATABASE_URL"] = ""
sys.path.insert(0, ".")
import sqlalchemy as sa
from studio import admin, auth, creators, ctx, db, jobs, live, load
db.init()
fails = []
def check(n, ok, x=""):
    print(("PASS " if ok else "FAIL ") + n + (f"  {x}" if x else "")); ok or fails.append(n)

# ---------------------------------------------------------------- the creator activity log
a, _ = auth._create("a@example.com", "A", password_hash="x")
with ctx.as_user(a.id):
    c = creators.create({"name": "Streamer"})
    check("a creator with no log file reads as empty", creators.read_log("nobody") == [])
    f = creators.root(c["id"]) / "log.jsonl"
    f.unlink(missing_ok=True)                     # start from nothing: creating a workspace writes a first line
    for i in range(5):
        creators.log(c["id"], f"line {i}")
    got = [x["msg"] for x in creators.read_log(c["id"], 3)]
    check("the newest lines come back first", got == ["line 4", "line 3", "line 2"], str(got))
    f = creators.root(c["id"]) / "log.jsonl"
    f.write_text("".join(f'{{"t": {i}, "msg": "old {i}", "pad": "{"x" * 90}"}}\n' for i in range(20000)), encoding="utf-8")   # about 2 MB
    got = [x["msg"] for x in creators.read_log(c["id"], 30)]
    check("a big log still gives the last 30 lines, newest first", got == [f"old {i}" for i in range(19999, 19969, -1)], str(got[:3]))
    creators.log(c["id"], "after the big one")
    check("a log that passed its limit is cut down to the recent lines", f.stat().st_size < 200_000 and len(f.read_text(encoding="utf-8").splitlines()) <= creators.LOG_KEEP_LINES + 1)
    check("...and the newest line survived the cut", creators.read_log(c["id"], 1)[0]["msg"] == "after the big one")

# ---------------------------------------------------------------- the machine monitor on this computer
# The processor and memory readings are written per platform. On one PeakCut cannot measure, free memory falls
# back to a fixed 99.0 GB and the processor reads 0 forever, so busy() never fires and the guard that holds new
# videos back while the machine is full is silently off. These two checks are what notice that.
try:                      # macOS updates these counts lazily, so wait for them to move rather than assume a gap
    busy0, tot0 = busy1, tot1 = load._cpu_times()
    waited = time.time()
    while tot1 == tot0 and time.time() - waited < 5:
        time.sleep(0.1)
        busy1, tot1 = load._cpu_times()
    cpu_ok = tot1 > tot0 and busy1 >= busy0 and 0 <= busy1 <= tot1
    cpu_why = f"{(busy0, tot0)} -> {(busy1, tot1)} after {time.time() - waited:.1f}s"
except OSError as e:
    cpu_ok, cpu_why = False, f"the processor cannot be read here: {e!r}"
check("the monitor reads this computer's processor", cpu_ok, cpu_why)

try:                      # Windows has no sysconf: there, only the lower bound and the 99.0 fallback are checked
    phys_gb = os.sysconf("SC_PHYS_PAGES") * os.sysconf("SC_PAGESIZE") / 1e9
except (AttributeError, ValueError, OSError):
    phys_gb = float("inf")
try:
    ram = load._ram_free_gb()
    ram_ok = 0.05 < ram <= phys_gb and ram != 99.0
    ram_why = f"{ram:.2f} GB free of {phys_gb:.0f} GB"
except OSError as e:
    ram_ok, ram_why = False, f"free memory cannot be read here: {e!r}"
check("the monitor reads this computer's free memory", ram_ok, ram_why)

# ---------------------------------------------------------------- the machine monitor on a system it cannot fully measure
def boom(): raise OSError("no /proc/stat here")
load._cpu_times = boom
load._state.update(disk_free=99.0, at=0.0, ram_free=99.0)
real_sleep = time.sleep
ticks = []
def stop_after_two(s):
    ticks.append(s)
    if len(ticks) > 2: raise SystemExit
time.sleep = stop_after_two
try:
    load._watch()
except SystemExit:
    pass
time.sleep = real_sleep
check("without a processor reading the monitor keeps running and still measures the drive", load._state["disk_free"] != 99.0 and len(ticks) > 2, str(load._state))

# ---------------------------------------------------------------- a recording whose ffmpeg cannot start
class Fake:
    ended = False
    job = {}
    def _ingest_loop(self): raise FileNotFoundError("ffmpeg")
f = Fake()
live.Session._ingest(f)
check("a recording that fails to start is marked ended, with the reason", f.ended and "Recording stopped" in f.job.get("error", ""), str(f.job))

# ---------------------------------------------------------------- the admin day totals
def noon(days_ago):      # midday of that calendar day, so no row sits near a day's edge
    day = time.strftime("%Y-%m-%d", time.localtime(time.time() - days_ago * 86400))
    return day, time.mktime(time.strptime(day, "%Y-%m-%d")) + 12 * 3600
(today, t0), (yday, t1), (d3, t3), (_old, t40) = noon(0), noon(1), noon(3), noon(40)
with db.engine.begin() as cn:
    for t, tin, tout in ((t0, 10, 5), (t0, 1, 1), (t1, 100, 0), (t3, 7, 3), (t40, 999, 999)):
        cn.execute(db.usage.insert().values(user_id=a.id, t=min(t, time.time() - 1), tokens_in=tin, tokens_out=tout, purpose="x", creator=None, place=""))
daily = {d["day"]: d for d in admin.overview()["daily"]}
check("the day totals add up per day", (daily[today]["calls"], daily[today]["tokens"]) == (2, 17) and (daily[yday]["calls"], daily[yday]["tokens"]) == (1, 100)
      and (daily[d3]["calls"], daily[d3]["tokens"]) == (1, 10), str((daily[today], daily[yday], daily[d3])))
check("a call older than the window is not counted", sum(d["calls"] for d in daily.values()) == 4, str(sum(d["calls"] for d in daily.values())))

# ---------------------------------------------------------------- option values too big to count are refused, not a crash
# 1e999 is valid JSON and parses to float inf, and a 400-digit integer is valid JSON too. Both used to
# raise OverflowError inside clean_options / request_render, which no endpoint catches, so the upload
# and link-submit endpoints answered 500 instead of the intended 400.
for opts, name in [({"quality": "inf"}, "a quality of inf"), ({"quality": 1e999}, "a quality of 1e999"),
                   ({"max_clips": 10 ** 400}, "a 400-digit clip count"),
                   ({"range_start": 10 ** 400}, "a 400-digit start"), ({"range_end": "NaN"}, "a range end of NaN")]:
    try:
        jobs.clean_options(opts)
        ok = False
    except ValueError:
        ok = True
    check(f"{name} is refused with ValueError", ok)
try:
    jobs.clean_options({"quality": "abc"})
    check("a bad word is still refused with ValueError", False)
except ValueError:
    check("a bad word is still refused with ValueError", True)
check("a good value still works, and a big one is clamped to the limit",
      jobs.clean_options({"quality": 720}) == {"quality": 720} and jobs.clean_options({"quality": 99999}) == {"quality": 1080})
jobs._jobs["overflow-test"] = {"id": "overflow-test", "clips": [{"id": "c1", "start": 0.0, "end": 30.0}]}
for changes, name in [({"start": 1e999}, "a start of 1e999"), ({"end": 10 ** 400}, "an end of 10**400")]:
    try:
        jobs.request_render("overflow-test", "c1", changes)
        ok = False
    except ValueError:
        ok = True
    check(f"re-making a clip with {name} is refused with ValueError", ok)

print("ALL PASSED" if not fails else f"{len(fails)} failed")
sys.exit(1 if fails else 0)

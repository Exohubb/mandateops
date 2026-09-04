# MandateOps — 5-Minute Demo Script (tight cut)

**Target: 5:00, no more.** This version is trimmed to actually fit — read it out loud once with a timer before recording. If you're still running long, cut the AutoPay beat first, then trim the "why AI is boxed in" section — never cut the live demo.

Every row below has three things: the **timestamp**, exactly **where to point your cursor / what to click**, and a **short line to say**. Don't read the "say" column word for word — know what it means and say it your way. Keep sentences short. Pause where you see `...`.

---

## Checklist before recording

1. Pre-run a batch in a second tab so you're not stuck waiting mid-demo.
2. Send Nira one throwaway question 30s before recording to warm the cache.
3. Close every other tab / notification.
4. Pick dark or light mode and stick with it the whole video.
5. Pre-load the AutoPay Play Store tab, ready to alt-tab to.
6. Do one silent mouse-only run-through first so every click is muscle memory.

---

## 0:00 – 0:12 — HOOK

| Point / Show | Say |
|---|---|
| Homepage hero, headline on screen | "Every failed UPI AutoPay payment gets four shots at recovery. Total. Ever. Most systems burn through all four blindly. We built MandateOps to stop that — and it recovers seventeen points more revenue than the naive way. Same customers, same failures." |

---

## 0:12 – 0:50 — THE PROBLEM

| Point / Show | Say |
|---|---|
| **Point at the 4 stat cards** on homepage, one by one | "AutoPay approval rates dropped fifty percent to thirty percent in two years, even as volume grew ten times over. And that's not customers walking away — that's a card expiring, a bank going down for an hour, a balance that's short by a few rupees that day. Every one of those is fully recoverable money, sitting there, nobody's fault." |
| **Point at the non-peak hours diagram** | "But NPCI boxes you in hard. One attempt, plus three retries, that's it forever. Only inside fixed legal hours. And a mandatory 24-hour warning before you're even allowed to try. So get the hour wrong, or keep retrying a mandate the customer already cancelled — you didn't just fail once. You burned one of only four chances you were ever going to get." |

---

## 0:50 – 1:55 — THE SOLUTION (what we built)

| Point / Show | Say |
|---|---|
| **Point at the 4-step pipeline diagram** on homepage | "So once you actually sit with this, retrying a payment isn't a 'try again' button — it's triage. Think of it like an ER with only four doses of medicine per patient. You don't hand those out randomly. Every failed mandate here goes through the same four fixed steps, no exceptions." |
| **Point at step 1 (Classify)** | "One — classify. Banks send back messy text, cryptic codes. Nira, our AI, reads it and sorts it into a clean bucket: no funds, bank down, mandate paused, or mandate killed entirely." |
| **Point at step 2 (Eligibility)** | "Two — eligibility. Plain code, zero AI. Four hard checks: attempts left, is this a legal hour, was the notice sent, is the mandate actually still alive. And here's the key move — if step one already told us the mandate's dead, we don't even try. We freeze the remaining attempts instead of wasting them. This one rule is where most of the recovered money actually comes from." |
| **Point at step 3 (Score)** | "Three — score the best slot. Not every legal hour is equal. Some banks recover better in the morning, some late at night, depending on why the payment failed. A statistical model looks at real historical data for that bank and that reason, and picks the hour with the best odds — and it's honest when there isn't enough data yet, instead of guessing confidently." |
| **Point at step 4 (Execute)** | "Four — execute at that hour, or freeze and log exactly why. Same four steps, every mandate, every time." |
| **Point at "How We Use AI" table** | "And the one rule holding this whole thing together — money never moves because a model said so. Nira only ever reads and writes text. Every retry decision is deterministic code she has zero access to. If Gemini's ever down, which happens on a free tier, a plain fallback keeps things running, clearly labeled, nothing hidden." |

---

## 1:55 – 3:25 — LIVE DEMO

| Point / Show | Say |
|---|---|
| Click **Run Batch** on Live Simulation | "Let's run it live. Fifty fresh mandates, real computation, nothing pre-baked." |
| *(let the 3-second step indicator play)* | "Under the hood — classify, check eligibility, score, execute. Twice: naive, then MandateOps." |
| **Point at the recovery rate comparison** | "Same fifty mandates. MandateOps recovers noticeably more." |
| Open **Mandate Explorer**, click one mandate | "Here's one real story — not just a summary number." |
| **Point at the attempt timeline** in the drawer | "Failed at 11am — already a blocked hour. So instead of hammering that same bad slot, it waited for the best legal hour and recovered next try instead of wasting two more." |
| Navigate to **Ask Nira**, click a suggested question | "Nira does four things only: classify, draft messages, answer questions, summarize. Watch — real question, real answer." |
| **Point at the "Grounded in this run's data" badge** | "Computed live off this run's actual numbers. Not canned." |
| Navigate to **Audit Trail**, click **Verify Chain** | "Every decision writes to a tamper-evident log — each entry chained to the last. One click proves nothing's been altered." |
| **Point at the green "valid" result** | "Valid. Right now. Every event." |

---

## 3:25 – 3:50 — AUTOPAY CREDIBILITY (keep under 25 seconds)

| Point / Show | Say |
|---|---|
| Alt-tab to Play Store listing, or point at sidebar card | "Quick one — we already shipped AutoPay, a consumer app for tracking your own UPI mandates. Seven hundred forty users in twenty days. That's the consumer side. MandateOps is the merchant side of the same broken rail." |

> Note: I couldn't load the live Play Store listing through automated tools — confirm the "740+ users in 20 days" line yourself before recording, and grab the current version/install count if you want it on screen.

---

## 3:50 – 4:30 — THE NUMBERS

| Point / Show | Say |
|---|---|
| **Point at the naive vs MandateOps table** | "Five thousand mandates, same seed. Naive recovers forty-nine point six six percent. MandateOps recovers sixty-six point seven. Seventeen points higher, over five lakh rupees more, twenty-two hundred fewer wasted attempts. Reproducible — run it yourself on the live link." |

---

## 4:30 – 4:45 — CLOSE

| Point / Show | Say |
|---|---|
| Back on homepage hero, or final frame with URL + GitHub link | "MandateOps — constraint-aware, fully auditable, and AI exactly where it belongs. Never where the money moves. Thanks for watching." |

---

## On-screen captions (add in post)

| Timestamp | Text |
|---|---|
| 0:00 | MandateOps — AI Revenue Recovery for UPI AutoPay |
| 0:15 | Source: Moneycontrol, NPCI, RBI, Razorpay |
| 1:50 | Live simulation — real computation, not pre-recorded |
| 2:50 | Nira: reads text, drafts messages, answers questions — never moves money |
| 3:20 | AutoPay — 740+ users in 20 days, Play Store |
| 3:55 | +17.04pp recovery · +₹5,17,948 · 2,219 attempts saved |
| 4:25 | github.com/Exohubb/mandateops · http://100.56.247.98:8080 |

---

## If you're still running long, cut in this order

1. Drop the AutoPay beat entirely (saves ~25s) — mention it in the description instead.
2. Merge step 3 + step 4 of the solution into one line: "then it scores the best legal hour and either fires or freezes."
3. Skip the Mandate Explorer single-story beat, go straight from the batch result to Ask Nira.
4. Never cut: the hook, the batch run, the final numbers.

## Delivery reminders

- Don't recite this word for word — know the beat, say it your way.
- Numbers get a little emphasis, not a flat read.
- Click first, talk about what happened — don't narrate the click beforehand.
- Land the last line at normal energy, don't trail off.

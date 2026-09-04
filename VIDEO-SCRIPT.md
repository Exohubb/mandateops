# MandateOps — 5-Minute Demo Video Script

**For: Razorpay Buildathon 2026, Track 03 — AI Revenue Recovery**
**Runtime target: 5:00** (script is timed at a natural speaking pace, ~140 wpm)
**Format:** screen recording + voiceover, presenter face optional (webcam bubble bottom-right is fine, not required)

> A note on how to read this doc: left column is exactly what to **say**, right column is exactly what to **show**. Say it like you're explaining it to a smart friend who works in fintech but has never seen this specific product — not like you're reading a spec sheet out loud. Pause where marked. Everywhere else, keep moving — judges reward pace and confidence, not slow enunciation.

---

## Before you hit record — a 6-point checklist

1. Have a **fresh batch already run** in a second browser tab (50-mandate cohort) so it's sitting there recovered and ready — don't make the judges watch a spinner for 3 seconds if you can avoid re-showing it twice.
2. Have **Ask Nira warmed up** — send one throwaway question 30 seconds before recording so the first real answer isn't the one that happens to hit a cold cache/slow model in the fallback chain.
3. Close every other browser tab and any notification popups. Judges notice a Slack toast mid-recording.
4. Decide now: **dark mode or light mode** for the whole video. Don't switch mid-recording — it reads as unpolished.
5. Have the **AutoPay Play Store listing open in a tab**, ready to alt-tab to for 5 seconds — don't try to load it live on camera.
6. Do one full silent dry run with the mouse first. Your cursor should never hunt around for a button — know exactly where every click is before you narrate over it.

---

## 0:00 – 0:15 — THE HOOK

**This is the only part of the video most judges give full attention to. Earn the next 4:45 in these 15 seconds.**

| Say | Show |
|---|---|
| "Every time someone's UPI AutoPay payment fails, the bank gives you exactly four chances to fix it. Not four *retries*. Four, total. And most companies burn through all four blindly — retrying dead subscriptions, retrying at illegal hours, retrying customers who already cancelled. We built the system that stops that. It's called MandateOps, and in the next five minutes I'll show you it recovering seventeen percentage points more revenue than the naive approach — on the exact same customers." | Start on the **MandateOps homepage hero** — the headline "UPI AutoPay is leaking revenue. MandateOps recovers it." Let it sit on screen for the first 3 seconds before you start talking, then start narrating over it. |

**Delivery note:** say "four. Not four retries. Four, total." with a real pause after "four." That's the hook — it's a specific, surprising number, stated as a fact, not a sales line. Don't smile through this line — say it like you're briefing someone on a regulation, because you are.

---

## 0:15 – 0:55 — THE PROBLEM, WITH RECEIPTS

| Say | Show |
|---|---|
| "Here's why this actually matters. UPI AutoPay approval rates dropped from fifty percent to thirty percent in under two years — even as volume grew ten times over. That's not customers choosing to leave. That's involuntary churn: a card expired, a bank had downtime, a balance was momentarily short — and nobody retried it correctly. Every one of those is recoverable revenue with zero acquisition cost. But here's the trap: NPCI caps you at one initial attempt plus three retries, inside fixed non-peak hours, with a mandatory 24-hour customer notice before you're even allowed to try. Retry in the wrong hour, or retry a mandate the customer already killed, and you didn't just fail — you burned one of only four chances you'll ever get." | Scroll down the homepage through the **four stat cards** (50%→30% approval drop, 1+3 attempt ceiling, 24-hour notice, 20-90% failure share) — pause on each one for about 2 seconds as you say the matching number. Then show the **non-peak execution windows diagram** (the green/red hour blocks) as you say "fixed non-peak hours." |

**Delivery note:** these are sourced, real numbers (Moneycontrol, NPCI/Economic Times, RBI, Razorpay/Livemint — all cited on-screen). Say them like facts, not marketing copy. This is where you earn credibility with a fintech-literate judge.

---

## 0:55 – 1:25 — THE INSIGHT (why this is a scheduling problem, not a retry loop)

| Say | Show |
|---|---|
| "So the real problem isn't 'retry the payment.' It's a constrained scheduling problem: which mandates are even eligible right now, which of the legal hours gives the best odds for *this* bank and *this* failure reason, and — critically — when do you stop and freeze the budget because the mandate is already dead. That's exactly what MandateOps does, in four fixed steps: classify the failure reason, check a hard eligibility gate, score the best legal time slot, then execute or freeze." | Show the **4-step pipeline flowchart** from the homepage (Classify → Check eligibility → Score the slot → Execute). Let each box highlight as you say its name. |

---

## 1:25 – 3:05 — LIVE DEMO (the core of the video)

This is the section that actually proves the thing works. Move fast, narrate what you're clicking, and let the real numbers speak.

### 1:25 – 1:55 — Run a live simulation

| Say | Show |
|---|---|
| "Let's run it live. I'm generating a fresh cohort of fifty synthetic mandates right now — same engine, same rules, real math, nothing pre-baked." *(click Run Batch)* "While that's running — about three seconds — here's what's actually happening under the hood: fifty mandates get classified, checked against the eligibility gate, scored for the best retry hour, and executed, twice — once under a naive next-day-retry strategy, once under MandateOps." | Navigate to **Live Simulation**, click **Run Batch**, and let the step-by-step processing indicator play out on camera — don't cut it, it's short and it visually proves this isn't instant/fake. |
| "And there it is — naive retry recovered nowhere near what MandateOps did, on the identical fifty mandates." | Once it completes, hover over the **recovery rate comparison** — call out the naive % vs MandateOps % numbers directly on screen. |

### 1:55 – 2:25 — Mandate Explorer (prove it, mandate by mandate)

| Say | Show |
|---|---|
| "But I don't want you to just trust a summary number — here's every single mandate, individually, with its real decline reason and what MandateOps decided to do about it." | Navigate to **Mandate Explorer**. Click into **one mandate** that shows a clear story — ideally one that got frozen (revoked mid-cycle) and one that got recovered on a rescored hour. |
| "This one failed with 'insufficient funds' at 11 AM — a blocked hour anyway — so MandateOps didn't even try there. It rescheduled into the next legal window, scored highest for this bank based on historical data, and recovered on attempt two instead of burning attempt two *and* three on bad timing." | Open the **Mandate Detail drawer**, point at the timeline of attempts and the scored hour. |

### 2:25 – 2:55 — Ask Nira (the AI layer, live)

| Say | Show |
|---|---|
| "Now here's Nira — the AI layer. She's not a chatbot bolted on for demo points. She only does four things: reads messy bank decline text, drafts customer messages from approved templates, answers grounded questions about a batch, and writes the executive summary. She never touches a rupee amount, a probability, or a scheduling decision — that's 100% deterministic code she has no access to. Watch — I'll ask her a real question about this exact run." *(type/click a suggested question, e.g. "Which bank has the worst recovery rate, and by how much?")* "And that's a real answer, computed live against this run's actual numbers — not a canned response." | Navigate to **Ask Nira**, click one of the **suggested question chips**, let the real response stream in on camera. Point out the "Grounded in this run's data" badge under her answer. |

### 2:55 – 3:05 — Audit trail (trust, in one shot)

| Say | Show |
|---|---|
| "And every decision — deterministic, statistical, or AI — writes to a hash-chained audit log. Tamper with one row and every hash after it breaks, verifiably. I can prove that with one click." *(click Verify Chain)* "Valid, right now, for every event in this run." | Navigate to **Audit Trail**, click **Verify Chain**, show the green "valid" result. |

---

## 3:05 – 3:45 — WHY THE AI IS DESIGNED THIS WAY (the differentiator)

This section is where you separate yourself from every other team that just "added GPT to their app." Say it plainly.

| Say | Show |
|---|---|
| "Here's the design decision I actually want you to remember from this whole video: money never moves because a model said so. Whether a mandate gets retried — deterministic code. Which hour to use — an inspectable statistical model, empirical Bayes, not a black box. What a messy bank decline string means, and what to say to a customer — that's Nira's entire job. And if every AI model is down — which happens on a free tier — the system falls back to a deterministic substitute automatically, tagged transparently, so a Gemini outage is never a single point of failure for revenue recovery." | Show the **"How We Use AI" page** — specifically the table mapping each decision to "Deterministic," "Statistical," or "Nira," and the **model fallback chain diagram** (gemini-3.5-flash → gemma models). |

---

## 3:45 – 4:15 — THE AUTOPAY CREDIBILITY BEAT (keep this SHORT — 30 seconds max)

This is a garnish, not the meal. Judges are here to evaluate the buildathon submission — don't let this run long or it reads as padding.

| Say | Show |
|---|---|
| "One more thing worth thirty seconds: this isn't our first time touching this exact problem. We already shipped AutoPay — a consumer-side UPI mandate manager, live on the Play Store, with over 740 users in its first 20 days. That app helps individual customers track and manage their own AutoPay mandates. MandateOps is the same domain expertise, pointed at the other side of the same broken rail — the merchant trying to recover the revenue, instead of the consumer trying to track the mandate." | Alt-tab to the **AutoPay Play Store listing** (pre-loaded, per the checklist) for about 4-5 seconds, then cut back to MandateOps. Alternatively, show the **sidebar credibility card** inside MandateOps itself — it already has the Play Store icon and this exact framing built in. |

**Note on this section:** I could not verify the live Play Store listing's exact description text or current version number through automated tools — the listing didn't load for scripted fetching. Before recording, open `https://play.google.com/store/apps/details?id=com.airolabs.autopayy` yourself and confirm the "740+ users in 20 days" line still matches what's shown, and grab the current version number/install count directly from the listing if you want to cite it more precisely on screen (e.g. as a lower-third caption).

---

## 4:15 – 4:50 — THE NUMBERS, ONE MORE TIME (closing proof)

| Say | Show |
|---|---|
| "So, to put a number on all of this: on a five-thousand-mandate benchmark, same seed, same synthetic ground truth — naive next-day retry recovered forty-nine point six six percent. MandateOps recovered sixty-six point seven percent. That's seventeen percentage points, over five lakh rupees more recovered, and two thousand two hundred and nineteen fewer wasted attempts spent on mandates that were already dead. This is reproducible — run it yourself right now on the live link in the description." | Show the **naive vs MandateOps comparison table** from the README/homepage — recovery rate, rupees recovered, attempts saved, all three deltas visible at once. |

---

## 4:50 – 5:00 — THE CLOSE

| Say | Show |
|---|---|
| "MandateOps: constraint-aware, audit-proof, and it uses AI exactly where AI belongs — never where money actually moves. Thanks for watching." | End on the **homepage hero** again, or a final frame with the **live URL** and **GitHub repo link** clearly visible as on-screen text. |

**Delivery note:** don't fade out mid-sentence. Land on "Thanks for watching" with your normal speaking energy, not a trailing-off mumble — first and last lines are what people remember from a pitch.

---

## On-screen text overlays to add in post (optional but recommended)

Add these as lower-third captions at the matching timestamp — judges skim faster with text reinforcement, especially for numbers:

| Timestamp | Overlay text |
|---|---|
| 0:00 | **MandateOps — AI Revenue Recovery for UPI AutoPay** |
| 0:20 | Source: Moneycontrol, NPCI, RBI, Razorpay |
| 1:35 | Live simulation — real computation, not pre-recorded |
| 2:30 | Nira: reads text, drafts messages, answers questions — never moves money |
| 3:50 | AutoPay — 740+ users in 20 days, Play Store |
| 4:20 | +17.04pp recovery · +₹5,17,948 · 2,219 attempts saved |
| 4:55 | github.com/Exohubb/mandateops · http://100.56.247.98:8080 |

---

## The 3 hooks, isolated (in case you want a shorter cutdown for socials)

If you ever need a 30-second teaser instead of the full 5 minutes, these three lines carry the whole pitch on their own:

1. "NPCI gives every failed payment exactly four chances. Not four retries — four, total. Most companies burn through all four blindly."
2. "Money never moves because a model said so — the AI here only reads messy text and explains decisions. It never approves, denies, or schedules a payment."
3. "Same five thousand customers, same failures — naive retry recovers fifty percent, MandateOps recovers sixty-seven. That's over five lakh rupees, measured, not projected."

---

## Common delivery mistakes to avoid

- **Don't read the numbers monotone.** "Seventeen percentage points" said flat sounds like a disclaimer. Said with a half-beat of emphasis, it sounds like the headline it is.
- **Don't apologize for the free-tier AI fallback.** Frame it as a deliberate reliability design (which it genuinely is), not a limitation you're excusing.
- **Don't let the AutoPay section run past 30 seconds.** It's credibility, not the product being judged.
- **Don't narrate what you're clicking before you click it** ("now I'm going to click on..."). Click first, narrate the result — it feels faster and more confident on playback.
- **Don't end on a screen full of code.** End on the homepage or the numbers table — something a judge remembers visually.

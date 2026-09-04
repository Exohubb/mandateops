# MandateOps — 5-Minute Demo Video Script

**For: Razorpay Buildathon 2026, Track 03 — AI Revenue Recovery**
**Runtime target: 5:00**
**Format:** screen recording + voiceover, presenter face optional (webcam bubble bottom-right is fine, not required)

> How to use this doc: the "Say" column is written the way you'd actually talk, not the way you'd write a report. Read it out loud once or twice before recording — if a line feels stiff coming out of your mouth, change the words to whatever you'd naturally say, the meaning is what matters, not matching my exact sentence. Short sentences, natural pauses (marked with `—` or `...`), and a couple of "and here's the thing" style connectors are intentional — that's what makes it sound like you're explaining something you built, not narrating a brochure.

---

## Before you hit record — a 6-point checklist

1. Have a **fresh batch already run** in a second browser tab (50-mandate cohort) so it's sitting there recovered and ready — don't make the judges watch a spinner for 3 seconds if you can avoid re-showing it twice.
2. Have **Ask Nira warmed up** — send one throwaway question 30 seconds before recording so the first real answer isn't the one that happens to hit a cold cache/slow model in the fallback chain.
3. Close every other browser tab and any notification popups. Judges notice a Slack toast mid-recording.
4. Decide now: **dark mode or light mode** for the whole video. Don't switch mid-recording — it reads as unpolished.
5. Have the **AutoPay Play Store listing open in a tab**, ready to alt-tab to for 5 seconds — don't try to load it live on camera.
6. Do one full silent dry run with the mouse first. Your cursor should never hunt around for a button — know exactly where every click is before you narrate over it.

**One more thing before you record:** don't memorize this word for word. Read it through three or four times until you know the *shape* of each section — hook, problem, solution, proof, close — then talk it, don't recite it. If you stumble on a word, just keep going in your own words. A confident "roughly seventeen percentage points better" beats a perfectly-recited number said nervously.

---

## 0:00 – 0:15 — THE HOOK

**This is the only part most judges give full attention to. Earn the next 4:45 in these 15 seconds.**

| Say | Show |
|---|---|
| "So, quick question — did you know every failed UPI AutoPay payment only gets four shots at recovery? Not four retries. Four, total, ever. And most systems just... burn through all four blindly. Retrying subscriptions that are already cancelled. Retrying at hours the bank doesn't even allow. We built something that stops that from happening. It's called MandateOps, and by the end of this video I'll show you it actually recovering seventeen percentage points more money than the naive way — on the exact same customers, same failures." | Start on the **MandateOps homepage hero** — let the headline sit for 2-3 seconds before you start talking, then narrate over it. |

**Delivery note:** say "four. Not four retries. Four, total, ever." like you're genuinely surprised by that fact yourself — because most people are, the first time they hear it. That's what makes a hook land, not volume.

---

## 0:15 – 0:55 — THE PROBLEM, WITH RECEIPTS

| Say | Show |
|---|---|
| "Here's why this actually matters, and it's bigger than it sounds. UPI AutoPay approval rates dropped from fifty percent down to thirty percent in under two years — and that's while volume grew ten times over. So this isn't a niche edge case, it's happening at scale, right now. And the thing is, most of that isn't customers actually wanting to leave. It's what we'd call involuntary churn — a card expired, someone's bank had downtime for an hour, their balance was just a little short that day. Every one of those is money you could still get, with basically zero extra cost to go get it. But here's the trap NPCI puts you in: you get one initial attempt, plus three retries, that's it. Inside fixed hours the bank allows. And you legally have to warn the customer 24 hours before you even try. So if you retry at the wrong hour, or you keep trying a mandate the customer already cancelled — you didn't just fail that one time. You burned one of only four chances you were ever going to get." | Scroll through the **four stat cards** on the homepage (50%→30% approval drop, 1+3 attempt ceiling, 24-hour notice, 20-90% failure share) — pause on each as you hit its number. Then show the **non-peak execution windows diagram** as you mention "fixed hours the bank allows." |

**Delivery note:** these numbers are real and sourced on-screen (Moneycontrol, NPCI, RBI, Razorpay). Say them like you're briefing someone, not selling something — that's where the credibility comes from with a judge who actually knows payments.

---

## 0:55 – 2:05 — THE SOLUTION: WHAT WE ACTUALLY BUILT

**This is the section the user specifically asked to expand — don't rush it. This is where you prove you understood the problem deeply enough to solve it properly, not just bolt AI onto it.**

| Say | Show |
|---|---|
| "So once you actually sit with this problem, you realize retrying a failed payment isn't really a 'try again' button. It's a scheduling and triage problem. Think of it like an ER with only four doses of medicine per patient — you don't hand those out randomly, you check who's actually savable first, and when the best time to give it is. That's basically what we built. Every single failed mandate goes through the same four fixed steps, no exceptions, no shortcuts." | Show the **4-step pipeline flowchart** on the homepage. |
| "Step one — classify. Banks send back messy stuff like 'INSUFFICIENT_BAL' or some cryptic reference code. Instead of a human reading every single one of those, we hand it to Nira, that's our AI layer, and she sorts it into a clean bucket — insufficient funds, bank was down, customer paused it, or customer killed the mandate completely." | Show the **decline classification** in Mandate Explorer — point at a raw decline text and its clean category tag. |
| "Step two is where it gets interesting, and honestly this is the part that saves the most money. It's a hard eligibility check, plain code, no AI involved at all — have we used all four attempts already, is this actually a legal hour to retry in, did we send the 24-hour warning, and is the mandate even still alive. And here's the key move: if step one told us the customer already killed the mandate, we don't even bother retrying. We freeze whatever attempts are left instead of wasting them. A naive system just keeps hammering that dead mandate two or three more times for nothing — and that's exactly the waste we're eliminating." | Show a **frozen/revoked mandate** in the Mandate Detail drawer — the "frozen" badge and the reason logged. |
| "Step three — if we're actually eligible to retry, which legal hour gives us the best shot? Not every legal hour is equal. Some banks recover better in the morning, some do better late at night, depending on why the payment failed in the first place. So we built a statistical model that looks at historical data for that specific bank and that specific failure reason, and picks the hour with the best real odds — and it's honest about it too, if there isn't enough historical data yet, it says so instead of guessing confidently." | Show the **retry-slot heatmap** or scorer output — bank x hour grid. |
| "And step four, we just execute at that scored hour, or freeze and log exactly why, if step two said no. Every one of those four steps happens the same way, every time, for every mandate — that consistency is honestly the whole point." | Cut back to the **pipeline flowchart**, highlight step 4. |
| "Now, the design decision I actually care about the most in this whole build — money never moves because an AI model said so. Nira only ever reads and writes text. She classifies decline reasons, she drafts the message to the customer, she answers questions about a batch run. She never decides who gets retried, when, or approves anything — that's all deterministic code she has zero access to. And if Gemini's ever down, which does happen on a free tier, there's a plain fallback classifier that just keeps the system running, clearly tagged as a fallback so nothing's hidden." | Show the **"How We Use AI" page** table mapping each decision to Deterministic / Statistical / Nira. |

**Delivery note:** this whole section should feel like you're explaining your own thinking process out loud — "so once you sit with this problem, you realize..." — not listing features. That's the difference between sounding like a founder and sounding like a slide deck.

---

## 2:05 – 3:35 — LIVE DEMO (prove it actually works)

Move fast here, narrate what you're clicking, let the real numbers do the talking.

### 2:05 – 2:35 — Run a live simulation

| Say | Show |
|---|---|
| "Alright, let's just run it. I'm generating fifty fresh, made-up mandates right now — same engine, same rules, nothing pre-baked for this demo." *(click Run Batch)* "While that's going — it's about three seconds — under the hood it's actually classifying all fifty, running them through that eligibility check, scoring the best hour for each, and executing. Twice, actually. Once the naive way, once the MandateOps way, on the identical fifty mandates." | Navigate to **Live Simulation**, click **Run Batch**, let the step indicator play out fully on camera. |
| "And look at that — same exact customers, same exact failures, and MandateOps just recovered noticeably more than the naive approach did." | Point directly at the **recovery rate comparison**, call out both percentages. |

### 2:35 – 3:00 — Mandate Explorer, one real story

| Say | Show |
|---|---|
| "But I don't want you just trusting a summary number, so let's go look at one actual mandate." | Navigate to **Mandate Explorer**, open one mandate with a clear story — ideally a rescored recovery. |
| "This one failed at 11am with insufficient funds — which, by the way, is already a blocked hour for retries — so instead of hammering that same bad hour again, the system waited for the next legal window, picked the hour with the best historical odds for this bank, and recovered on the very next try instead of burning two more attempts on bad timing." | Open the **Mandate Detail drawer**, point at the attempt timeline and the scored hour. |

### 3:00 – 3:25 — Ask Nira, live

| Say | Show |
|---|---|
| "Now here's Nira, live. She's not just a chatbot we bolted on for demo points — she only does four things, and that's it. Reads decline text, drafts customer messages, answers questions about a run, writes the summary. Watch, I'll actually ask her something real about this run." *(click a suggested question)* "And that's a real answer, computed right now off this run's actual numbers, not something canned." | Navigate to **Ask Nira**, click a suggested question, let the response stream in, point out the "Grounded in this run's data" badge. |

### 3:25 – 3:35 — Audit trail, one click

| Say | Show |
|---|---|
| "And every single one of those decisions — the classification, the freeze, the scoring, all of it — writes to a tamper-evident log. Each entry is cryptographically chained to the one before it, so if anyone ever changed a past entry, every hash after it would break. I can prove that right now, one click." *(click Verify Chain)* "Valid. Every event, right now, for this entire run." | Navigate to **Audit Trail**, click **Verify Chain**, show the green result. |

---

## 3:35 – 4:10 — WHY WE BUILT THE AI THIS WAY (the differentiator, said plainly)

| Say | Show |
|---|---|
| "If there's one thing I want you to remember from this whole video, it's this — money never moves because a model said so. What gets retried is deterministic code. The best hour to retry in is an actual inspectable statistical model, not a black box. And Nira's entire job is reading messy text and explaining things — nothing more. And if every AI model we're using goes down, which can happen on a free tier, the system just falls back to plain rules automatically, and it tells you honestly when that happened. So a Gemini outage never becomes a reason revenue stops getting recovered." | Show the **model fallback chain diagram** — gemini-3.5-flash → gemma models. |

---

## 4:10 – 4:35 — THE AUTOPAY CREDIBILITY BEAT (keep this to 25-30 seconds)

| Say | Show |
|---|---|
| "One quick thing before I wrap up — this isn't actually the first time we've touched this exact problem. We already shipped AutoPay, a consumer app that helps people track and manage their own UPI AutoPay mandates. It's live on the Play Store, over seven hundred and forty users in its first twenty days. That app is the consumer side of this story. MandateOps is us going after the other side of the same broken rail — the merchant trying to actually recover the revenue instead of the customer trying to keep track of their mandate." | Alt-tab briefly to the **AutoPay Play Store listing**, or show the **sidebar credibility card** inside MandateOps. |

**Note:** I couldn't pull the live Play Store listing through automated tools when writing this — please open the listing yourself before recording and confirm the "740+ users in 20 days" line still matches, and grab the current version/install count if you want a more precise on-screen caption.

---

## 4:35 – 4:50 — THE NUMBERS, ONE MORE TIME

| Say | Show |
|---|---|
| "So just to land the number one more time — on a five thousand mandate test, same seed, same synthetic data — naive retry recovered forty-nine point six six percent. MandateOps recovered sixty-six point seven. That's seventeen points higher, over five lakh rupees more recovered, and about twenty-two hundred fewer attempts wasted on mandates that were already dead. And this isn't a projection — it's reproducible, you can run it yourself right now on the live link below." | Show the **naive vs MandateOps comparison table**. |

---

## 4:50 – 5:00 — THE CLOSE

| Say | Show |
|---|---|
| "MandateOps — constraint-aware, fully auditable, and it uses AI exactly where AI's actually good at, and nowhere near where the money actually moves. Thanks for watching." | End on the **homepage hero**, or a final frame with the **live URL** and **GitHub link** visible. |

**Delivery note:** land the last line at your normal talking energy — don't trail off. First and last lines are what people actually remember.

---

## On-screen text overlays to add in post (optional but recommended)

| Timestamp | Overlay text |
|---|---|
| 0:00 | **MandateOps — AI Revenue Recovery for UPI AutoPay** |
| 0:20 | Source: Moneycontrol, NPCI, RBI, Razorpay |
| 1:00 | The problem: retry = a scheduling problem, not a "try again" button |
| 2:10 | Live simulation — real computation, not pre-recorded |
| 3:05 | Nira: reads text, drafts messages, answers questions — never moves money |
| 4:15 | AutoPay — 740+ users in 20 days, Play Store |
| 4:40 | +17.04pp recovery · +₹5,17,948 · 2,219 attempts saved |
| 4:55 | github.com/Exohubb/mandateops · http://100.56.247.98:8080 |

---

## The 3 hooks, isolated (for a shorter social cutdown)

1. "Every failed UPI payment only gets four shots at recovery, total, ever. Most systems burn through all four blindly."
2. "Money never moves because a model said so — our AI only reads messy text and explains decisions, it never approves or schedules a payment."
3. "Same five thousand customers, same failures — naive retry recovers fifty percent, we recover sixty-seven. Measured, not projected."

---

## Common delivery mistakes to avoid

- **Don't read the numbers flat.** "Seventeen percentage points" said monotone sounds like a footnote. Said with a little emphasis, it's the headline.
- **Don't apologize for the free-tier AI fallback** — it's a deliberate reliability choice, say it like one.
- **Don't let the AutoPay beat run past 30 seconds** — it's credibility, not the thing being judged.
- **Don't narrate the click before you make it** ("now I'm going to click...") — click first, talk about what happened, it feels faster and more confident.
- **Don't end on a code screen.** End on the homepage or the results table — something visual that sticks.
- **Don't recite this script word-for-word on camera.** Know the story beat by beat and say it in your own words — a natural stumble sounds more credible than a perfect robotic read.

# UX Research Interview Questions: Tabletop Exercises for Incident Response

> Research guide for building a **Tabletop Exercise / Wheel of Misfortune product** — a tool that helps engineering teams practice incident response through simulated scenarios.

**Research Goal:** Understand how teams currently practice (or fail to practice) incident response through tabletop exercises, what blocks adoption, how scenarios are created and facilitated, and how learning effectiveness can be measured — to inform the design of a dedicated product.

**Target Participants:**

- **Facilitators** — Team leads, SRE managers, staff engineers who design and run exercises
- **Participants** — On-call engineers, SREs, DevOps engineers who go through exercises
- **Stakeholders** — Engineering directors, VPs who approve time/resources for training

---

## 1. Current State & Baseline Behavior

*Goal: Understand what teams do today — if anything — so we can meet them where they are.*

- Does your team do any kind of incident response practice today? If yes, walk me through what that looks like end to end. If no, has anyone ever suggested it?
- How did the idea of doing exercises first come up on your team? Who championed it?
- How often do you run exercises? Is there a regular cadence, or does it happen ad-hoc?
- What's the simplest version of practice you've done? (Even informal things — talking through an old incident at lunch, quizzing a new hire, etc.)
- Before your team started practicing, how did new on-call engineers learn to handle incidents? What was the gap that exercises were supposed to fill?
- Have you ever tried running exercises and then stopped? What caused that?

---

## 2. Scenario Design & Creation

*Goal: Understand how facilitators create realistic, useful scenarios — this is the core content problem the product must solve.*

- Walk me through how you come up with a scenario for an exercise. Where do you start?
- Do you base scenarios on real past incidents, or do you invent fictional ones? What are the trade-offs?
- How do you decide the right level of difficulty? Have you ever made a scenario too easy or too hard? What happened?
- What makes a scenario feel realistic enough to be useful, vs. feeling like a contrived puzzle?
- How much prep time does it take to create a good scenario? What's the most time-consuming part?
- Do you reuse scenarios across different teams or sessions? How do you avoid people just memorizing the answers?
- Have you ever had a scenario go in an unexpected direction during the exercise? How did you handle it?
- What types of incidents are hardest to turn into exercises? (e.g., cascading failures, multi-service issues, ambiguous symptoms)
- Do your scenarios include curveballs — new information arriving mid-exercise, red herrings, conflicting data? How do you design those?
- Is there a library or repository of scenarios you draw from, or does each facilitator start from scratch every time?

---

## 3. Facilitation & Running the Exercise

*Goal: Understand the facilitator's experience during the exercise itself — the real-time orchestration challenge.*

- Walk me through a typical exercise session from the facilitator's perspective. What do you do before, during, and after?
- How do you play the role of "the system" — feeding information to participants, simulating monitoring data, responding to their actions?
- What's the hardest part about facilitating? Where do things tend to go off-script?
- How do you decide when to give hints vs. letting participants struggle? What signals tell you someone is stuck in a productive way vs. just stuck?
- How do you handle it when a participant takes an action you didn't plan for? Do you improvise, or do you steer them back?
- How many people typically participate in one session? Is it one person being tested, or a team working together?
- How long do exercises usually last? What's the ideal length vs. what actually happens?
- Do you use any tools or props during the exercise — fake dashboards, fake alerts, shared docs, chat channels? Walk me through the setup.
- Have you ever had a facilitation experience that went really well? What made it click?
- Have you ever had one go badly? What went wrong?

---

## 4. Participant Experience

*Goal: Understand what it feels like to be the person going through the exercise — the learner's perspective.*

- Think back to the last tabletop exercise you participated in. Walk me through what that experience was like, start to finish.
- What was going through your mind during the exercise? Did it feel like a real incident, or did it feel different?
- Was there a moment during an exercise where something "clicked" — where you learned something you later used in a real incident?
- What makes an exercise feel valuable vs. feeling like a waste of time?
- How does the pressure in an exercise compare to a real incident? Is the lower pressure helpful for learning, or does it make the exercise feel fake?
- Do you ever feel judged or evaluated during exercises? How does that affect your behavior?
- Have you ever been embarrassed during an exercise — made a mistake in front of your team? How was that handled?
- After an exercise, do you feel more confident handling real incidents, or is the effect temporary?
- What's the most useful exercise you've ever done? What made it stand out?
- What would make you actively want to participate in more exercises vs. treating them as a chore?

---

## 5. Debrief & Learning Capture

*Goal: Understand how teams extract and retain lessons from exercises — the learning loop the product must support.*

- What happens immediately after an exercise ends? Is there a structured debrief, or does everyone just go back to work?
- Walk me through a good debrief you've experienced. What made it productive?
- How do you capture what was learned? Is it written down, or does it just live in people's heads?
- Do the lessons from exercises actually change how your team operates? Can you give a specific example?
- How do you distinguish between "the participant made a mistake" and "our tooling/process has a gap"? Do exercises surface systemic issues?
- Who gives feedback during the debrief — just the facilitator, or does the whole group discuss? What dynamic works best?
- Have you ever discovered a gap in your runbooks, monitoring, or escalation process because of an exercise? What happened next?
- How do you track whether someone has improved over multiple exercises? Is there any continuity between sessions?

---

## 6. Measuring Effectiveness & Skill Transfer

*Goal: Understand how (or whether) teams know that exercises are actually working — the ROI question.*

- How do you know if your exercises are making your team better at incident response? What evidence would convince you?
- Have you ever seen a direct connection between a practice exercise and a better outcome in a real incident? Tell me about that.
- Do you track any metrics related to exercise effectiveness? (e.g., response time improvements, fewer escalations, better postmortem outcomes)
- If your VP asked "is this training worth the time investment?" — what would you show them?
- How long does it take for a new on-call engineer to feel competent? Has structured practice shortened that timeline?
- Have you seen a difference between engineers who go through exercises regularly and those who don't? How does it show up?
- What does "expert intuition" look like in your domain? Can you describe a moment where an experienced responder just knew what to do? Could exercises build that?
- Is there a point of diminishing returns — where more exercises stop helping? How would you know?

---

## 7. Adoption Barriers & Organizational Buy-In

*Goal: Understand what stops teams from practicing — the blockers the product must overcome to succeed.*

- What's the single biggest reason your team doesn't do exercises more often?
- How do you justify taking engineers away from feature work to practice incident response? Is that a hard sell?
- Who needs to approve the time for exercises? What do they care about?
- Have you ever tried to start a practice program and it fizzled out? What killed it?
- What would make it 10x easier to run an exercise tomorrow? What's the biggest bottleneck?
- Is there resistance from engineers themselves? Do some people see exercises as pointless, or as a performance evaluation in disguise?
- How much facilitator expertise does it take to run a good exercise? Is that a bottleneck on your team?
- If a tool could eliminate one pain point in the process, which pain point would have the biggest impact on adoption?
- What's the minimum viable exercise — the simplest thing that would still be valuable if you only had 30 minutes?

---

## 8. Realism, Fidelity & Simulation

*Goal: Understand the spectrum from "talking through a scenario on a whiteboard" to "injecting real failures in production" — and where the sweet spot is.*

- On a spectrum from "discussing a scenario verbally" to "injecting real failures in prod," where do your exercises fall? Where would you like them to be?
- What aspects of a real incident are hardest to simulate? (e.g., time pressure, incomplete data, communication chaos, emotional stress)
- Do you use any fake dashboards, mock monitoring data, or simulated environments during exercises? How important is that?
- Have you tried chaos engineering (actually breaking things in production)? How does that compare to tabletop exercises? When would you use one vs. the other?
- Does the exercise need to feel stressful to be useful, or can people learn effectively in a relaxed setting?
- How important is it that the scenario matches your actual tech stack and infrastructure? Would a generic scenario still be valuable?
- What level of interactivity matters — can the facilitator just read a script, or do they need to dynamically respond to participant actions?

---

## 9. Team Dynamics & Psychological Safety

*Goal: Understand the social/interpersonal dimension — exercises are a group activity with real power dynamics.*

- How does seniority affect the exercise? Do junior engineers behave differently when a senior engineer or manager is in the room?
- Have you seen exercises reveal knowledge gaps or skill differences within a team? How was that handled?
- Is there a way to make exercises feel safe enough that people take risks and make mistakes without fear?
- How do you handle a situation where one person dominates the exercise and others don't speak up?
- Do exercises work better within a single team, or across teams? What changes when you mix teams?
- Have exercises ever created tension on a team — someone felt called out, or disagreements about the "right" approach?
- How do you build a culture where practice is expected and valued, rather than seen as remedial?

---

## 10. Frequency, Cadence & Scheduling

*Goal: Understand the logistics of making exercises a regular habit.*

- How often would you ideally run exercises? What's realistic given your team's workload?
- When in the sprint/cycle do exercises work best? Are there times when they'd be disruptive?
- How do you handle scheduling when people are spread across time zones?
- What's the right group size for an exercise? What happens when you have too many or too few people?
- Should exercises be mandatory or voluntary? How does that affect participation and engagement?
- Do you vary the format — sometimes a full 90-minute session, sometimes a 15-minute quick drill? What cadences have you tried?
- How do you handle on-call rotation changes — making sure new on-call engineers get practice before their first shift?

---

## 11. Integration with Existing Workflows

*Goal: Understand how exercises fit into the team's broader incident management ecosystem.*

- Where would an exercise tool need to fit in your existing stack? What does it need to integrate with?
- Do you use exercises to validate changes to your runbooks or escalation policies? Could you see that being useful?
- After a real incident postmortem, do you ever turn the incident into an exercise for the team? How would that work?
- Could exercises replace or complement parts of your on-call onboarding process? What would that look like?
- How do you see the relationship between exercises and chaos engineering? Are they complementary, or does one replace the other?

---

## 12. Scaling Across the Organization

*Goal: Understand what happens when you try to move from "one team practices" to "the whole org practices."*

- If exercises work well for one team, how would you roll them out to other teams? What challenges do you foresee?
- Can scenarios be shared across teams, or does every team need custom scenarios for their own services?
- Is there a central reliability or SRE team that would own exercises, or would each team run their own?
- How would you handle exercises for incidents that span multiple teams? Those are often the hardest real incidents.
- What would an executive dashboard for exercise programs look like? What would leadership want to see?

---

## 13. Remote, Distributed & Async Teams

*Goal: Understand how exercises work (or don't) for teams that aren't co-located — a critical product constraint.*

- Has your team ever tried running a tabletop exercise with remote participants? What worked and what didn't?
- Could a tabletop exercise be run asynchronously — people contributing over hours or days instead of in real time? Would that lose the value, or would it open up new possibilities?
- How do you simulate the communication chaos of a real incident when everyone is remote? (In person, you can see people's body language and overhear conversations.)
- Do remote exercises feel less engaging or less realistic? What would close that gap?
- If you have team members in very different time zones, does that make exercises harder to schedule? How do you handle it today?
- Would you be open to exercises where an AI or automated system plays the role of facilitator, so you don't need a human available?

---

## 14. Competitive Alternatives & Current Workarounds

*Goal: Understand what teams use instead of a dedicated exercise tool — the product's real competition is often "nothing" or homegrown solutions.*

- What alternatives have you considered or tried for building incident response skills? (e.g., chaos engineering, shadowing on-call, incident replays, external training)
- Have you built any internal tools or templates for running exercises? What do those look like?
- If you use chaos engineering tools (Gremlin, Chaos Monkey, LitmusChaos), how do those compare to tabletop exercises? When would you use one vs. the other?
- Have you looked at any commercial tools for tabletop exercises or incident response training? What did you think?
- If a tool existed for this, what budget would it come from — engineering, training, SRE, or something else? Who would approve the purchase?
- What would make a paid tool worth it vs. just using Google Docs and Slack to run exercises manually?

---

## 15. Edge Cases & Unusual Scenarios

*Goal: Surface non-obvious requirements and failure modes.*

- What happens when a new hire joins — do they observe exercises first, or jump right in? How do you calibrate difficulty?
- How would exercises work for a fully remote or async team? Can tabletop exercises be done asynchronously?
- What if the most experienced person on the team is always the facilitator — do they ever get to practice as a participant?
- Have you ever had to run an exercise for a type of incident your team has never actually experienced? How did you build that scenario?
- What happens when an exercise reveals a critical gap — like "we literally have no runbook for this"? Is that a success or a failure?
- How do you handle exercises when the team is in the middle of a real incident-heavy period? Does practice feel tone-deaf, or more urgent?

---

## 16. Wish List & Product Opportunities

*Goal: Directly surface unmet needs and feature ideas — let participants dream.*

- If a tool existed that made running exercises effortless, what would it do?
- What's the most tedious part of the current process that you'd want automated?
- Would you want a tool that generates scenarios for you, or would you always want to write them yourself?
- How important is it to replay real past incidents as exercises? Would a tool that imports incident data and turns it into a scenario be valuable?
- Would you want to track individual engineer progress over time? Or would that feel too much like performance evaluation?
- If you could run an exercise right now with zero prep, would you? What's stopping you today?
- What would make you recommend this tool to another team?

---

## Interview Guide for Researchers

### Participant Screening

Recruit a mix of:

- **Active practitioners** — teams that run exercises at least quarterly
- **Lapsed practitioners** — teams that tried exercises and stopped
- **Non-practitioners** — teams that have never done formal exercises (understand the gap)
- **Facilitators and participants separately** — their perspectives differ significantly

### Session Structure (60 min)

| Time | Section | Purpose |
|------|---------|---------|
| 0–5 min | Warm-up | Ask about their role and on-call experience generally |
| 5–15 min | Section 1 (Current State) | Establish baseline — do they practice today? |
| 15–30 min | Sections 2–4 (Scenario/Facilitation/Participation) | Deep dive into their exercise experience (pick based on their role) |
| 30–40 min | Sections 5–6 (Debrief/Effectiveness) | Understand the learning loop |
| 40–50 min | Sections 7 & 14 (Barriers/Alternatives) | Uncover adoption blockers and competitive context |
| 50–60 min | Section 16 (Wish List) | Open-ended product discovery |

### Key Probes

- **"Show me"** — Ask participants to walk through their actual tools, docs, or Slack channels. Observe, don't just listen.
- **"Tell me about a specific time"** — Always ground abstract statements in concrete stories. "Exercises are useful" → "Tell me about a specific exercise that changed how you responded to a real incident."
- **"What happened next?"** — Follow the thread. The best insights come 2–3 follow-ups deep.
- **"Why did you stop?"** — For lapsed practitioners, the reasons they stopped are your biggest product risks.
- **Watch for workarounds** — Google Docs scenarios, Slack threads pretending to be alerts, manually narrated dashboards. These are the product.

### Signals to Watch For

- **Emotional moments** — Frustration with prep time, pride after a good exercise, anxiety about being judged. These point to high-impact design opportunities.
- **Facilitator burnout** — If the same person always facilitates, that's a scalability problem the product must solve.
- **"We don't have time"** — Dig deeper. Is it actually time, or is it that the perceived value doesn't justify the effort?
- **Mismatch between facilitator and participant perspectives** — Facilitators may think exercises went well while participants found them pointless (or vice versa).

---

*Research guide for the Tabletop Exercise / Wheel of Misfortune product. Structured using the UX Question Matrix framework applied to the exercise lifecycle: scenario design → facilitation → participation → debrief → measurement → adoption.*

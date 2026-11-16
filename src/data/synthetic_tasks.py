"""40 hand-written synthetic tasks (fictional organisations, no personal data).
Methodology: each scenario was written by hand with a known set of ground-truth facts (expected_facts).
Difficulty is set by number of constraints, conflicting information, ambiguity, distractors and required
reasoning - NOT by length alone. Some fictional organisations appear in more than one task; those tasks share
a source_group so the router's grouped CV keeps them together."""
from __future__ import annotations

RUBRIC = {"meeting_summary": "meeting_v1", "email_draft": "email_v1", "research_brief": "research_v1",
          "slide_outline": "slides_v1", "data_extraction": "extraction_v1"}
FMT = {"meeting_summary": "bullet_points", "email_draft": "email", "research_brief": "brief",
       "slide_outline": "slide_outline", "data_extraction": "json"}
TASKS: list[dict] = []


def T(cat, diff, family, template, desc, inp, reqs, facts):
    TASKS.append({"category": cat, "difficulty": diff, "source_type": "synthetic", "source_id": f"SYN_{family}",
                  "source_group": family, "scenario_family": family, "task_template": template,
                  "task_description": desc, "input": inp.strip(), "requirements": reqs, "expected_facts": facts,
                  "output_format": FMT[cat], "rubric_id": RUBRIC[cat]})


M, E, R, S, X = "meeting_summary", "email_draft", "research_brief", "slide_outline", "data_extraction"

# ===================================================================== MEETING SUMMARY (4 synthetic)
T(M, "easy", "brightfield_library", "meeting_notes",
  "Summarise these staff-meeting notes and list the action items.",
  """Brightfield Library - Staff sync, Tue 4 March. Present: Dana (branch manager), Luis (circulation), Mei (children's programs).
Dana: The self-checkout kiosk will be installed on 12 March; Luis will train staff on 10 March.
Mei: Summer reading sign-ups open 1 April. We need 200 printed flyers; I'll order them by 14 March.
Dana: Saturday opening hours stay 9 to 5. No change.
Luis: The returns bin is jammed again; facilities has been notified.""",
  ["Maximum 120 words", "List decisions separately from action items", "Each action item needs an owner and a date", "Include only information in the notes"],
  ["Kiosk installed 12 March", "Luis trains staff 10 March", "Summer reading sign-ups open 1 April", "Mei orders 200 flyers by 14 March", "Saturday hours unchanged (9-5)", "Returns bin jam reported to facilities"])

T(M, "medium", "northwind_logistics", "meeting_transcript",
  "Summarise this operations review. Separate decisions from open issues and list action items.",
  """Northwind Logistics - Q1 ops review. Present: Priya (ops lead), Tom (fleet), Aisha (finance), Jonas (warehouse).
Priya: On-time delivery was 91% in Q1; the target is 95%.
Tom: The main cause is two vans out of service. Repairs will be done by 21 April.
Aisha: Overtime ran 12% over budget. I propose approving an extra 8,000, but only if April on-time delivery stays under 93%.
Priya: Agreed - that's the decision.
Jonas: The warehouse scanner rollout is postponed to June because the vendor is late. Nobody has said who will chase the vendor.
Tom: I'll send the van repair schedule to Priya by Friday 11 April.
Aisha: I'll circulate the overtime report on 15 April.""",
  ["Maximum 150 words", "Separate: Decisions / Open issues / Action items", "Action items need owner and due date", "Flag anything that has no owner"],
  ["Q1 on-time delivery 91% vs 95% target", "Two vans out of service is the main cause", "Repairs due 21 April", "Decision: extra 8,000 overtime budget only if April on-time delivery is under 93%",
   "Scanner rollout postponed to June", "Vendor follow-up has no owner", "Tom sends repair schedule to Priya by Fri 11 April", "Aisha circulates overtime report 15 April"])

T(M, "hard", "cedar_health", "meeting_transcript",
  "Summarise this committee meeting for people who were absent. Use the final, corrected facts and be precise about what was decided versus only proposed.",
  """Cedar Health Clinics - Patient Experience Committee. Present: Ruth (chair), Omar (IT), Bella (nursing), Kwame (patient rep), Sol (finance).
Ruth: Wait times in Q2 averaged 34 minutes.
Omar: Actually the dashboard says 38; the 34 figure left out walk-ins.
Ruth: Fine, use 38 as the official number.
Bella: Nursing proposes a triage nurse at the front desk, 0.5 FTE.
Sol: That costs about 31,000 a year. We have 20,000 unallocated.
Kwame: Could patient volunteers cover part of it?
Ruth: Let's not decide today. Sol, please check whether the grant covers it.
Omar: The online check-in pilot at the Eastside site goes live 3 June. That is decided.
Kwame: The cafeteria lunch options have been poor lately. (laughter)
Bella: One correction - the 31,000 included equipment. Salary alone is 26,000.
Sol: Right, I'll update my figures.
Ruth: Next meeting is 17 July. Kwame will ask the volunteer coordinator about available hours and report back then.""",
  ["Maximum 180 words", "Use corrected figures only", "Clearly label each item as Decided / Proposed (not decided) / Open", "List action items with owners", "Omit irrelevant chatter"],
  ["Official Q2 wait time is 38 minutes (34 excluded walk-ins)", "Triage nurse 0.5 FTE is proposed, not decided", "Salary cost is 26,000 (31,000 included equipment)", "20,000 unallocated funds",
   "Sol checks whether the grant covers it", "Eastside online check-in pilot goes live 3 June - decided", "Kwame asks volunteer coordinator about hours", "Next meeting 17 July", "Cafeteria remark is irrelevant"])

T(M, "hard", "harborview_port", "meeting_transcript",
  "Summarise this safety-committee meeting by agenda item. Do not invent owners or dates.",
  """Harborview Port Authority - Safety Committee. Present: Greta (chair), Nikolai (security), Yusuf (maintenance), Li (HR).
Greta: Item 1, crane inspections.
Yusuf: Cranes 3 and 5 failed the last inspection; 1, 2 and 4 passed. Crane 3 needs a new brake assembly, lead time six weeks.
Greta: Crane 5 can be reinspected after the cable swap. Someone should get a quote for a temporary rental crane.
Nikolai: A rental is also a security question - I'd want background checks on the contractor's staff.
Greta: Noted. Item 2, training.
Li: Mandatory refresher completion is at 82%; the target is 100% by 30 September. I'll send reminders to unfinished staff next week.
Greta: We could link completion to shift scheduling. Nikolai: That's too punitive. (No agreement reached.)
Greta: Item 3, the regulator's audit is expected 'sometime in Q4'; the date is unconfirmed. Yusuf, can you confirm with the regulator?
Yusuf: I'll try.
Greta: We agreed to meet monthly until the cranes are cleared.""",
  ["Maximum 200 words", "Structure by agenda item", "Mark action items that have no assigned owner as UNASSIGNED", "Flag unresolved disagreements", "Do not state dates that are not in the notes"],
  ["Cranes 3 and 5 failed; 1, 2 and 4 passed", "Crane 3 needs new brake assembly, six-week lead time", "Crane 5 reinspection after cable swap", "Rental crane quote has no owner (unassigned)", "Nikolai wants background checks on rental contractor staff",
   "Training completion 82%, target 100% by 30 September", "Li sends reminders next week", "Linking training to scheduling: no agreement", "Audit expected Q4, date unconfirmed; Yusuf will try to confirm", "Monthly meetings until cranes are cleared"])

# ===================================================================== EMAIL (12 synthetic)
T(E, "easy", "acme_bakery", "email_from_notes", "Write the email described in the notes.",
  "From: Maria (owner, Acme Bakery). To: Henrik at Stonemill Flour. Purpose: thank him for the quick delivery last week, confirm Thursday delivery of 40 kg flour at 7 am, ask him to send the invoice by Friday. Tone: friendly but professional.",
  ["Under 120 words", "Include a subject line", "Friendly, professional tone", "State the invoice deadline"],
  ["Thanks for last week's quick delivery", "Thursday delivery confirmed", "40 kg of flour at 7 am", "Invoice requested by Friday"])
T(E, "easy", "pinecrest_school", "email_from_notes", "Write the email described in the notes.",
  "From: Ms Ortega, Pinecrest Elementary office. To: all Grade 3 parents. Purpose: remind them picture day is Wednesday 12 November; students wear school uniform; order forms are due back Monday. Tone: warm, brief.",
  ["Under 100 words", "Include a subject line", "Warm, brief tone", "Mention the form deadline"],
  ["Picture day Wednesday 12 November", "Students wear school uniform", "Order forms due Monday", "Sender is the school office (Ms Ortega)"])
T(E, "easy", "zenith_gym", "email_from_notes", "Write the email described in the notes.",
  "From: Customer care, Zenith Gym. To: member Jonas Berg. Purpose: apologise for being billed twice on 23 October; the duplicate charge will be refunded within 5 business days; he does not need to do anything. Tone: apologetic and clear.",
  ["Under 110 words", "Include a subject line", "Apologise once, sincerely", "State clearly that no action is needed"],
  ["Apology for double billing on 23 October", "Duplicate charge refunded within 5 business days", "No action needed from the member"])
T(E, "easy", "kestrel_design", "email_from_notes", "Write the email described in the notes.",
  "From: Team lead Amara. To: the design team. Purpose: ask everyone to submit timesheets by 5 pm this Friday; late timesheets delay payroll. Tone: friendly but firm.",
  ["Under 80 words", "Include a subject line", "State the deadline and the consequence"],
  ["Timesheets due by 5 pm Friday", "Late timesheets delay payroll"])
T(E, "medium", "loop_software", "email_from_notes", "Write the email described in the notes.",
  "From: Sam (account exec, Loop Software). To: Dana at BlueRiver Bank. Context: after yesterday's demo, Dana asked for three features: SSO, audit log, data export. Pricing is being sent separately by the sales-ops team. Goal: thank her, recap the three requests, propose a call Tuesday or Wednesday afternoon. Constraint: do NOT promise delivery dates for any feature. Tone: professional, confident.",
  ["Under 160 words", "Include a subject line", "Recap all three feature requests", "Propose Tuesday or Wednesday afternoon", "Do not promise any delivery date", "Mention pricing comes separately"],
  ["Thanks after yesterday's demo", "Features: SSO, audit log, data export", "Pricing sent separately by sales-ops", "Call proposed Tuesday or Wednesday afternoon", "No delivery dates promised"])
T(E, "medium", "greenfield_council", "email_from_notes", "Write the email described in the notes.",
  "From: Procurement officer Li Wei, Greenfield Council. To: Brightpath Consulting. Context: their proposal was 20% above budget. Goal: decline politely, do not criticise their quality (it was good), say we would like to hear from them again for next year's budget cycle. Tone: courteous, respectful.",
  ["Under 140 words", "Include a subject line", "Give the budget reason without criticising quality", "Leave the door open for next year", "Do not offer a contract"],
  ["Proposal declined", "Reason: 20% above budget", "Quality not criticised (positive about work)", "Invites contact for next year's budget cycle"])
T(E, "medium", "tidewater_events", "email_from_notes", "Write the email described in the notes.",
  "From: Events manager Priyanka, Tidewater Events. To: Harbor Hall venue. Context: need to move a 120-guest booking from 14 June to 21 June. They have booked 3 previous events with the venue. Willing to pay a change fee of up to 150. Goal: ask for the change and request a written confirmation. Tone: polite, appreciative.",
  ["Under 150 words", "Include a subject line", "Mention loyalty (3 previous events)", "State the maximum change fee", "Ask for written confirmation"],
  ["Move booking from 14 June to 21 June", "120 guests", "Three previous events booked with venue", "Will pay change fee up to 150", "Written confirmation requested"])
T(E, "medium", "orbit_labs", "email_from_notes", "Write the email described in the notes.",
  "From: Student Elif Kaya. To: Professor Hardin. Context: lab report due Friday; a spectrometer failure on Monday cost two days of measurements. Asks for an extension to Tuesday. Will attach a partial draft. Tone: formal and respectful; do not blame the lab technicians.",
  ["Under 150 words", "Include a subject line", "Formal tone", "Request a specific new date", "Mention the attached partial draft", "Do not blame anyone"],
  ["Report currently due Friday", "Spectrometer failure on Monday lost two days of data", "Requests extension to Tuesday", "Partial draft attached", "No blame on technicians"])
T(E, "hard", "northwind_logistics", "email_from_notes", "Write the email described in the notes.",
  "From: Customer success manager Priya, Northwind Logistics. To: Marta Silva, procurement director at FreshCo. Context: FreshCo complained that pallets arrived damaged twice. Investigation: in the 3 March shipment the carrier was at fault; in the 19 March shipment the damage was caused by FreshCo's own packaging (thin straps). Goals: acknowledge both incidents with empathy, accept responsibility for 3 March and offer a 10% credit on that shipment, do NOT admit liability for 19 March but offer a free joint packaging inspection. Tone: empathetic but firm. Do not blame FreshCo harshly.",
  ["Under 180 words", "Include a subject line", "Offer the 10% credit only for the 3 March shipment", "Do not admit liability for 19 March", "Offer a joint packaging inspection", "Empathetic but firm; no harsh blame"],
  ["Acknowledges both damaged-pallet incidents", "3 March: carrier at fault, responsibility accepted", "10% credit on the 3 March shipment", "19 March: no liability admitted (packaging/thin straps cited tactfully)", "Free joint packaging inspection offered"])
T(E, "hard", "cedar_health", "email_from_notes", "Write the email described in the notes.",
  "From: Omar, IT lead at Cedar Health Clinics. To: all clinic staff. Context: announcing the online check-in pilot at the Eastside site starting 3 June. Points: pilot is voluntary for patients; patient data is stored in the clinic's existing secure system (no new vendor data access); staff training sessions on 28 May and 30 May; there is a rumour about job cuts - state that no job impact is planned for the pilot, but do NOT promise anything about future years. Tone: reassuring, honest.",
  ["Under 200 words", "Include a subject line", "Give both training dates", "Address the rumour without over-promising", "Mention data stays in the existing secure system", "State pilot is voluntary for patients"],
  ["Pilot at Eastside starts 3 June", "Voluntary for patients", "Data stays in existing secure system, no new vendor access", "Training 28 May and 30 May", "No job impact planned for the pilot; no promises about the future"])
T(E, "hard", "brightfield_library", "email_from_notes", "Write the email described in the notes.",
  "From: Library director Dana. To: donor Mrs Okafor. Context: she gave 5,000, earmarked for the children's section. The board is considering naming the reading room after her but this is NOT approved yet. Goals: thank her warmly, confirm the gift goes to the children's section, mention a separate tax receipt will follow, invite her to a short meeting. Do NOT promise naming rights. Tone: warm, sincere, careful.",
  ["Under 170 words", "Include a subject line", "Do not promise or imply approved naming rights", "Mention separate tax receipt", "Invite her to meet"],
  ["Gift of 5,000 thanked", "Funds go to children's section", "Tax receipt sent separately", "Invitation to a short meeting", "Naming rights not promised (not approved)"])
T(E, "hard", "harborview_port", "email_from_notes", "Write the email described in the notes.",
  "From: Maintenance head Yusuf, Harbor Port Authority. To: contractor Deltaline Cranes. Context: the new brake assembly for crane 3 is delayed. Deltaline says it arrives 6 June; the supplier says 20 June. Goals: tell them the delay matters, ask for written confirmation of the real delivery date by Wednesday, remind them the contract penalty (2% per week) only applies after 30 June. Stay neutral - do not accuse them of lying. Tone: professional, neutral.",
  ["Under 170 words", "Include a subject line", "Mention both conflicting dates", "Ask for written confirmation by Wednesday", "State penalty applies only after 30 June", "Neutral, no accusations"],
  ["Crane 3 brake assembly delayed", "Conflicting dates: 6 June (Deltaline) vs 20 June (supplier)", "Written confirmation requested by Wednesday", "Penalty 2% per week applies only after 30 June", "Neutral tone, no accusation"])

# ===================================================================== RESEARCH BRIEF (6 synthetic)
T(R, "easy", "lumen_insurance", "evidence_pack", "Write a short research brief from the evidence below.",
  """Evidence pack - Lumen Insurance remote-work pilot (fictional):
1. 120 claims staff worked remotely 3 days/week for 6 months.
2. Average claims closed per person per week rose from 41 to 44.
3. Staff satisfaction (survey, n=96 of 120) rose from 6.8 to 7.9 out of 10.
4. Office space cost was unchanged during the pilot.""",
  ["100-150 words", "State the main finding first", "Use only the evidence provided"],
  ["120 staff, 3 days remote, 6 months", "Claims per person rose from 41 to 44", "Satisfaction rose from 6.8 to 7.9 (n=96 of 120)", "Office cost unchanged"])
T(R, "easy", "bean_and_leaf", "evidence_pack", "Write a short research brief from the evidence below.",
  """Evidence pack - Bean & Leaf reusable-cup pilot (fictional), 3 cafés, 8 weeks:
- Site A: 22% of customers used reusable cups. Site B: 15%. Site C: 31%.
- Disposable cup purchases fell 18% overall.
- Average transaction value did not change.
- No data collected on customer satisfaction.""",
  ["100-150 words", "Mention what the data does NOT cover", "Use only the evidence provided"],
  ["Reusable-cup use: A 22%, B 15%, C 31%", "Disposable cup purchases fell 18%", "Transaction value unchanged", "No satisfaction data was collected"])
T(R, "medium", "metro_procurement", "evidence_pack", "Write a research brief comparing the three vendors and giving a cautious recommendation.",
  """Evidence pack - help-desk software vendors (fictional):
Vendor A: 36/user/year; 99.9% uptime (vendor claim); 14-day onboarding; 4.1/5 on a review site (n=312).
Vendor B: 29/user/year; 99.5% uptime (independent monitor, 12 months); 30-day onboarding; 4.4/5 (n=48).
Vendor C: 41/user/year; uptime not published; 7-day onboarding; 4.6/5 (n=15).
Our requirement: at least 99.5% uptime, onboarding under 21 days, budget 35/user/year.""",
  ["Structure: Findings / Comparison / Recommendation / Uncertainty", "Distinguish vendor claims from independent data", "Flag small review samples and missing data", "Check each vendor against the requirement"],
  ["A is 36 (over 35 budget), uptime is a vendor claim", "B meets uptime (independent) and budget but onboarding 30 days exceeds 21", "C is 41 (over budget), uptime unknown", "Review samples: A n=312, B n=48, C n=15 (C very small)", "No vendor fully meets all requirements"])
T(R, "medium", "rivergate_city", "evidence_pack", "Write a research brief on the bike-share pilot. Separate what the data shows from what is inference.",
  """Evidence pack - Rivergate bike-share pilot (fictional):
- Ridership in the pilot district rose 18% over the previous year; a control district rose 12%.
- A rider survey (n=42, voluntary, collected at stations) found 71% would 'use bikes more often'.
- Reported accidents were flat: 9 vs 9.
- Pilot ran 4 months in spring/summer only.""",
  ["Use headings: Data shows / Inference / Limitations", "Do not claim the pilot caused the increase", "Mention the control district", "Note the survey weaknesses"],
  ["Pilot ridership +18% vs control +12%", "Survey n=42, voluntary, at stations, 71% would use more", "Accidents flat at 9 vs 9", "4 months spring/summer only", "Causation not established; seasonal and selection bias"])
T(R, "hard", "stockwell_warehouse", "evidence_pack", "Write a research brief on warehouse-automation payback. Reconcile the conflicting sources and state your confidence.",
  """Evidence pack - warehouse automation ROI (fictional):
Source A (vendor white paper): average payback 14 months across 'customer deployments' (number of sites not stated).
Source B (independent audit, 3 sites, 2 years): payback 31 months including training and downtime.
Source C (our own pilot, 1 site, 9 months so far): projected payback 22 months, but training costs were excluded and one holiday peak is missing.
Context: our board will only approve projects with payback under 24 months.""",
  ["Structure: Summary / Source quality / Reconciled estimate / Confidence / Recommendation", "Do not simply choose the vendor figure", "Explain why the estimates differ", "State a confidence level and what evidence would raise it"],
  ["Vendor: 14 months, site count unstated, conflict of interest", "Independent audit: 31 months incl. training/downtime, 3 sites", "Pilot: 22 months projected, 1 site, training excluded, no peak season", "Board threshold 24 months", "Likely above 24 months once training is included; confidence is low-to-moderate"])
T(R, "hard", "oakline_foods", "evidence_pack", "Write a market-entry brief for Oakline Foods considering Country X. Assess the quality of each piece of evidence.",
  """Evidence pack - Country X plant-based snack market (fictional):
1. 2019 industry report: market size 120M, growth 9%/year.
2. 2024 analyst note: market size 150M (growth now ~4%/year).
3. Survey by a snack-brand lobby group: 'Would you buy more plant-based snacks if they tasted better?' - 83% yes (n=1,000).
4. Retail audit 2024: plant-based snacks hold 2.1% of snack shelf space in 40 stores.
5. Article on Country X's national football team.
6. Import regulation: labelling approval takes 6-9 months.""",
  ["Structure: Key facts / Evidence quality / Assessment / Gaps", "Prefer the most recent figures and say why", "Identify the leading survey question", "Ignore irrelevant evidence", "Do not state a market size beyond the evidence"],
  ["Market ~150M in 2024 (2019's 120M is outdated)", "Growth slowed from 9% to ~4%", "Survey question is leading and from a lobby group", "2.1% shelf space in 40 stores", "Labelling approval 6-9 months", "Football article irrelevant"])

# ===================================================================== SLIDE OUTLINE (10 synthetic)
T(S, "easy", "brightfield_library", "slide_brief", "Create the slide outline described.",
  "Create a 5-slide welcome deck for new library staff at Brightfield Library. Content: mission (free access to learning), opening hours (Mon-Sat 9-5), who to ask for help (branch manager Dana), key systems (self-checkout kiosk from 12 March), first-week schedule. Audience: new hires.",
  ["Exactly 5 slides", "Title + 2-3 bullets per slide", "A visual recommendation for each slide"],
  ["Mission: free access to learning", "Hours Mon-Sat 9-5", "Dana is the contact", "Self-checkout kiosk from 12 March", "First-week schedule slide"])
T(S, "easy", "bean_and_leaf", "slide_brief", "Create the slide outline described.",
  "Create a 4-slide quarterly results deck for Bean & Leaf cafés. Data: revenue 1.2M (+8% vs last quarter); best site: Site C; reusable-cup use at 31% in Site C; next quarter goal: open one kiosk. Audience: store managers.",
  ["Exactly 4 slides", "Max 3 bullets per slide", "Visual recommendation for each slide"],
  ["Revenue 1.2M, +8%", "Site C best performer", "Reusable cup use 31% at Site C", "Goal: open one kiosk next quarter"])
T(S, "easy", "loop_software", "slide_brief", "Create the slide outline described.",
  "Create a 5-slide internal launch deck for the Loop Notes app. Content: problem (notes scattered across tools), solution (one searchable notebook), 3 key features (templates, offline mode, sharing), launch date 2 December, how to get help (#loop-support channel). Audience: all staff.",
  ["Exactly 5 slides", "Plain language", "Visual recommendation for each slide"],
  ["Problem: scattered notes", "Solution: one searchable notebook", "Features: templates, offline mode, sharing", "Launch date 2 December", "Support: #loop-support"])
T(S, "easy", "pinecrest_school", "slide_brief", "Create the slide outline described.",
  "Create a 4-slide proposal for a school science fair, for parents. Content: purpose (get kids curious about science), date (Saturday 22 March), how to help (volunteer judges, donate supplies), contact (Ms Ortega).",
  ["Exactly 4 slides", "Friendly tone", "Visual recommendation for each slide"],
  ["Purpose: curiosity about science", "Date Saturday 22 March", "Help: volunteer judges, donate supplies", "Contact Ms Ortega"])
T(S, "medium", "sunridge_energy", "slide_brief", "Create the slide outline described.",
  "Create a 7-slide pitch to the city council for a community solar project. Must include: problem, proposed solution (500 kW array on the library roof), cost (1.4M, 40% grant-funded), timeline (permits 4 months, build 6 months), risks (permit delays, grid connection), expected benefit (saves 55,000/year), and the ask (approve 840,000 of city funds). Time limit: 10 minutes. Audience: council members, non-technical.",
  ["Exactly 7 slides", "Include cost, timeline, risks and the ask", "Non-technical language", "Visual recommendation for every slide", "Include a one-line speaker note per slide"],
  ["500 kW array on library roof", "Cost 1.4M, 40% grant-funded", "City funds requested 840,000", "Permits 4 months, build 6 months", "Risks: permit delays, grid connection", "Saves 55,000/year", "10-minute, non-technical audience"])
T(S, "medium", "loop_software", "slide_brief", "Create the slide outline described.",
  "Create a 6-slide sales-kickoff deck for Loop Software reps. Data: closed-won grew 14% to 212 deals; average deal 18,500; top objection is 'we already use a spreadsheet' (41% of lost deals); new feature: SSO; goal for next quarter: 250 deals. Each slide needs a recommended chart or visual. Audience: sales reps, motivational but factual.",
  ["Exactly 6 slides", "Use all the data points provided", "Each slide has a specific chart/visual recommendation", "Motivational but factual tone"],
  ["Closed-won +14% to 212 deals", "Average deal 18,500", "Top objection spreadsheet in 41% of lost deals", "New feature: SSO", "Goal: 250 deals next quarter"])
T(S, "medium", "stockwell_warehouse", "slide_brief", "Create the slide outline described.",
  "Create a 6-slide blameless post-mortem deck for an engineering team. Incident: order system down 47 minutes on 9 October. Root cause: an expired database certificate. Detection: customer reports after 15 minutes (no alert). Fix: certificate renewed. Actions: add certificate-expiry alert (owner Ines, due 24 October), quarterly certificate audit. Audience: engineers; blameless tone, no individual named as cause.",
  ["Exactly 6 slides", "Blameless language", "Include timeline, root cause, detection gap, actions with owner and date", "Visual recommendation per slide"],
  ["Outage 47 minutes on 9 October", "Root cause: expired database certificate", "Detected via customer reports after 15 minutes, no alert", "Action: expiry alert, owner Ines, due 24 October", "Action: quarterly certificate audit", "No individual blamed"])
T(S, "hard", "oakline_foods", "slide_brief", "Create the slide outline described.",
  "Create an 8-slide board update for Oakline Foods. The board faces two competing priorities: (1) cut costs by 10% this year, or (2) open two new sites. Facts: cost-cut saves 2.1M but delays site openings by a year; two sites need 3.5M and are projected (not guaranteed) to add 4M revenue in year 2. The CFO favours option 1, the COO option 2. Present both options fairly, then give a hedged recommendation. Audience: a sceptical board. Constraints: max 3 bullets per slide, label facts vs projections, include speaker notes.",
  ["Exactly 8 slides", "Max 3 bullets per slide", "Label facts versus projections", "Present both options fairly before recommending", "Hedged recommendation, not a certainty", "Speaker notes for each slide", "Visual recommendation per slide"],
  ["Option 1: cut costs 10%, saves 2.1M, delays sites a year", "Option 2: two sites cost 3.5M, projected 4M revenue in year 2", "Revenue is a projection, not guaranteed", "CFO favours option 1, COO favours option 2", "Hedged recommendation with explicit assumptions"])
T(S, "hard", "stockwell_warehouse", "slide_brief", "Create the slide outline described.",
  "Create a single 7-slide, 12-minute deck about the warehouse-system migration for two audiences: executives (want risk, cost, timeline) and engineers (want technical approach). Facts: cost 780,000 (estimate +/-15%); go-live 1 March (target, depends on vendor API v2 delivery by 15 January); main risks: data-migration errors, vendor delay; technical approach: phased cut-over by region, dual-run for 2 weeks. Slides 1-5 for executives; slides 6-7 an appendix for engineers. Distinguish confirmed facts from estimates.",
  ["Exactly 7 slides", "Slides 1-5 executive, slides 6-7 engineering appendix", "Label estimates and targets as such", "Include risks and dependency on the vendor API", "Fits 12 minutes", "Visual recommendation per slide"],
  ["Cost 780,000 +/-15% (estimate)", "Go-live 1 March is a target", "Depends on vendor API v2 by 15 January", "Risks: data-migration errors, vendor delay", "Phased cut-over by region, 2-week dual-run", "Executive slides 1-5, engineer appendix 6-7"])
T(S, "hard", "cedar_health", "slide_brief", "Create the slide outline described.",
  "Create a 6-slide patient-facing explainer about Cedar Health's new online check-in, for adults aged 65+. Facts: voluntary; start at the Eastside site on 3 June; takes about 3 minutes on a phone or at a kiosk; staff can help at the front desk; data stays in the clinic's existing secure system. Address the worry 'will my data be shared?'. Constraints: reading level grade 8 or lower, no jargon, large-print friendly visuals, max 25 words per slide.",
  ["Exactly 6 slides", "Max 25 words per slide", "Grade 8 reading level, no jargon", "Address data-privacy worry directly", "Accessible, large-print-friendly visual recommendation per slide"],
  ["Voluntary", "Eastside site from 3 June", "About 3 minutes on phone or kiosk", "Staff help at front desk", "Data stays in existing secure system, not shared with new vendors", "Max 25 words per slide"])

# ===================================================================== DATA EXTRACTION (8 synthetic)
T(X, "easy", "fernwood_supplies", "extract_json", "Extract the fields into JSON.",
  "Invoice INV-2041 from Fernwood Supplies, dated 2025-02-03. Total due: 482.50 EUR. Payment due by 2025-03-05.",
  ["Return JSON with keys: invoice_number, vendor, invoice_date, total_amount (number), currency, due_date", "Dates in ISO format", "No text outside the JSON"],
  ['invoice_number: "INV-2041"', 'vendor: "Fernwood Supplies"', 'invoice_date: "2025-02-03"', "total_amount: 482.5", 'currency: "EUR"', 'due_date: "2025-03-05"'])
T(X, "easy", "riverside_events", "extract_json", "Extract the fields into JSON.",
  "Hi, this is Nadia Rahman. I'd like to register 6 people for the Riverside Autumn Dinner on 14 November. Two guests are vegetarian and one has a nut allergy. My email is nadia.r@example.com.",
  ["Return JSON with keys: name, email, event, event_date, attendees (integer), dietary_notes (list of strings)", "Event date in ISO format assuming year 2025", "No text outside the JSON"],
  ['name: "Nadia Rahman"', 'email: "nadia.r@example.com"', 'event: "Riverside Autumn Dinner"', 'event_date: "2025-11-14"', "attendees: 6", "dietary_notes: two vegetarian, one nut allergy"])
T(X, "easy", "pelican_tech", "extract_json", "Extract the fields into JSON.",
  "Job posting: Junior Data Analyst at Pelican Tech, Lisbon (hybrid). Salary 32,000-38,000 EUR per year. Apply by 2025-04-30.",
  ["Return JSON with keys: title, company, location, work_mode, salary_min, salary_max, currency, deadline", "Numbers as numbers, dates ISO", "No text outside the JSON"],
  ['title: "Junior Data Analyst"', 'company: "Pelican Tech"', 'location: "Lisbon"', 'work_mode: "hybrid"', "salary_min: 32000, salary_max: 38000", 'currency: "EUR"', 'deadline: "2025-04-30"'])
T(X, "medium", "helpdesk_co", "extract_json", "Extract the ticket information into JSON.",
  """Ticket #8841 - Customer: Orchid Dental. Opened 2025-05-06.
[05-06 Agent Lee] Customer reports invoices will not export to PDF. Priority set to LOW.
[05-06 Customer] This blocks our month-end close!
[05-07 Agent Lee] Cleared cache - no change. Reinstalled the export plugin - no change. Priority raised to HIGH.
[05-08 Agent Ravi] Escalated to engineering. Status: ESCALATED.""",
  ["Return JSON with keys: ticket_id, customer, opened_date, issue_category, final_priority, steps_tried (list), status", "Use the FINAL priority and status", "issue_category should be 'export'", "No text outside the JSON"],
  ['ticket_id: "8841"', 'customer: "Orchid Dental"', 'opened_date: "2025-05-06"', 'issue_category: "export"', 'final_priority: "HIGH" (not LOW)', "steps_tried: cleared cache, reinstalled export plugin", 'status: "ESCALATED"'])
T(X, "medium", "lakeside_cafe", "extract_json", "Extract the purchase order into JSON.",
  "PO-7781 for Lakeside Cafe. Items: (1) Espresso beans 5kg bags, 6 bags at $38.00 each; (2) Paper cups 12oz, 2 cartons at $54.50 each; (3) Oat milk, quantity TBC, $2.10 per litre; (4) Cleaning tablets, 1 box at $19.99. Requested delivery 2025-04-18.",
  ["Return JSON: po_number, customer, delivery_date, items (list of {description, quantity, unit_price, line_total})", "line_total = quantity * unit_price", "Use null when a value is not given or cannot be computed", "No text outside the JSON"],
  ['po_number: "PO-7781"', 'customer: "Lakeside Cafe"', 'delivery_date: "2025-04-18"', "item 1: qty 6, 38.00, total 228.00", "item 2: qty 2, 54.50, total 109.00", "item 3: qty null, 2.10, total null", "item 4: qty 1, 19.99, total 19.99"])
T(X, "medium", "elm_property", "extract_json", "Extract the lease terms into JSON.",
  "Lease summary: Landlord Elm Property Ltd; Tenant Jordan Pike. Term: 1 June 2025 to 31 May 2026. Monthly rent 1,150 GBP. Deposit 1,725 GBP. Either party may end the lease with 60 days' written notice. Utilities are paid by the tenant.",
  ["Return JSON: landlord, tenant, start_date, end_date, monthly_rent, deposit, currency, notice_days, utilities_paid_by, pets_allowed", "Dates ISO, numbers as numbers", "Use null for anything not stated (e.g. pets_allowed)", "No text outside the JSON"],
  ['landlord: "Elm Property Ltd"', 'tenant: "Jordan Pike"', 'start_date: "2025-06-01", end_date: "2026-05-31"', "monthly_rent: 1150, deposit: 1725", 'currency: "GBP"', "notice_days: 60", 'utilities_paid_by: "tenant"', "pets_allowed: null (not stated)"])
T(X, "hard", "summit_events", "extract_json", "Extract the action items into JSON. Reference date: Tuesday 10 June 2025.",
  """From Hana, after today's planning call (reference date: Tuesday 10 June 2025):
- Omar will send the revised quote by end of this week.
- Someone needs to book the venue visit - maybe next Wednesday?
- Kai said he would handle the catering menu by 20 June. (The old 15 June menu deadline was dropped.)
- Finance sign-off: Ravi, within 3 working days of receiving the quote.""",
  ["Return JSON: a list of action items, each {action, owner, due_date, notes}", "Resolve relative dates to ISO dates where possible; use null when no date can be determined", "Use null for owner when nobody is assigned", "Do not treat the dropped 15 June deadline as an action", "No text outside the JSON"],
  ["Omar: send revised quote, due 2025-06-13", "Venue visit: owner null (unassigned), date tentative/ambiguous (next Wednesday ~ 2025-06-18)", "Kai: catering menu due 2025-06-20", "15 June deadline dropped, not an action", "Ravi: finance sign-off within 3 working days of receiving the quote (no absolute date)"])
T(X, "hard", "mercy_supply", "extract_json", "Extract the current, valid orders into JSON.",
  """LOG 2025-05-02 | Ward 4 ordered 120 saline bags (500ml) at 1.10 GBP each.
LOG 2025-05-02 | Ward 7 ordered 40 gauze packs, price not listed.
LOG 2025-05-03 | Correction: the Ward 4 saline order should be 150 bags, not 120.
LOG 2025-05-03 | ICU ordered 30 syringe boxes at 6.40 EUR each (supplier invoices in euros).
LOG 2025-05-04 | Ward 7 order cancelled by requester.""",
  ["Return JSON: a list of orders, each {ward, item, quantity, unit_price, currency, status} where status is 'active' or 'cancelled'", "Apply corrections", "Use null for missing price/currency", "Keep cancelled orders with status 'cancelled'", "No text outside the JSON"],
  ['Ward 4: saline bags, quantity 150 (corrected), 1.10 GBP, active', 'Ward 7: gauze packs, quantity 40, price null, currency null, cancelled', 'ICU: syringe boxes, quantity 30, 6.40 EUR, active', "Exactly three orders"])

assert len(TASKS) == 40, len(TASKS)

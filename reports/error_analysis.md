# Error analysis (measured results only)

Failure = chosen model's judge score is more than 5 points below the strongest model's score on that task.

Term explanations come from the final router fitted on all data (so they illustrate, not test).

## Routing failures of the ML router (10 total; worst 8 shown)

### EMAIL_012 - email_draft / hard
- scores: {'cheap': np.float64(73.0), 'medium': np.float64(100.0), 'strong': np.float64(100.0)}
- router predicted **cheap** (confidence 0.61, threshold 0.55)
- fallback chose **cheap** -> NOT corrected
- terms that pushed the prediction: email, write the, subject, under, subject line, notes under
- limitation to examine: the router only sees the task description/requirements, not the input text or the model's actual difficulty; check whether the input is long/conflicting while the description looks simple.

### SLIDE_008 - slide_outline / medium
- scores: {'cheap': np.float64(84.0), 'medium': np.float64(82.0), 'strong': np.float64(100.0)}
- router predicted **medium** (confidence 0.46, threshold 0.55)
- fallback chose **strong** -> corrected
- terms that pushed the prediction: slide, all, the slide, outline described, create the, described exactly
- limitation to examine: the router only sees the task description/requirements, not the input text or the model's actual difficulty; check whether the input is long/conflicting while the description looks simple.

### DATA_003 - data_extraction / hard
- scores: {'cheap': np.float64(73.0), 'medium': np.float64(86.0), 'strong': np.float64(86.0)}
- router predicted **cheap** (confidence 0.59, threshold 0.85)
- fallback chose **medium** -> corrected
- terms that pushed the prediction: json, text, fields, iso, the text, iso format
- limitation to examine: the router only sees the task description/requirements, not the input text or the model's actual difficulty; check whether the input is long/conflicting while the description looks simple.

### SLIDE_009 - slide_outline / medium
- scores: {'cheap': np.float64(84.0), 'medium': np.float64(87.0), 'strong': np.float64(100.0)}
- router predicted **medium** (confidence 0.53, threshold 0.55)
- fallback chose **strong** -> corrected
- terms that pushed the prediction: slide, language, outline described, the slide, create the, described exactly
- limitation to examine: the router only sees the task description/requirements, not the input text or the model's actual difficulty; check whether the input is long/conflicting while the description looks simple.

### RES_002 - research_brief / easy
- scores: {'cheap': np.float64(81.0), 'medium': np.float64(84.0), 'strong': np.float64(95.0)}
- router predicted **medium** (confidence 0.51, threshold 0.55)
- fallback chose **strong** -> corrected
- terms that pushed the prediction: brief on, one, source, on, priorities stated, write one
- limitation to examine: the router only sees the task description/requirements, not the input text or the model's actual difficulty; check whether the input is long/conflicting while the description looks simple.

### SLIDE_004 - slide_outline / easy
- scores: {'cheap': np.float64(96.0), 'medium': np.float64(86.0), 'strong': np.float64(95.0)}
- router predicted **medium** (confidence 0.54, threshold 0.55)
- fallback chose **strong** -> corrected
- terms that pushed the prediction: slide, recommendation for, category_slide_outline difficulty_easy, difficulty_easy create, described exactly, create the
- limitation to examine: the router only sees the task description/requirements, not the input text or the model's actual difficulty; check whether the input is long/conflicting while the description looks simple.

### SLIDE_002 - slide_outline / hard
- scores: {'cheap': np.float64(92.0), 'medium': np.float64(88.0), 'strong': np.float64(100.0)}
- router predicted **cheap** (confidence 0.37, threshold 0.85)
- fallback chose **medium** -> NOT corrected
- terms that pushed the prediction: what is, is, include, in, outline for, statement exactly
- limitation to examine: the router only sees the task description/requirements, not the input text or the model's actual difficulty; check whether the input is long/conflicting while the description looks simple.

### EMAIL_005 - email_draft / medium
- scores: {'cheap': np.float64(94.0), 'medium': np.float64(100.0), 'strong': np.float64(100.0)}
- router predicted **cheap** (confidence 0.57, threshold 0.55)
- fallback chose **cheap** -> NOT corrected
- terms that pushed the prediction: email, write the, subject, under, subject line, notes under
- limitation to examine: the router only sees the task description/requirements, not the input text or the model's actual difficulty; check whether the input is long/conflicting while the description looks simple.

## Cases where the cheapest model beat the strongest (11)

- DATA_006 (data_extraction/easy): cheap=100.0, medium=77.0, strong=91.0
- EMAIL_002 (email_draft/easy): cheap=100.0, medium=100.0, strong=88.0
- EMAIL_003 (email_draft/easy): cheap=100.0, medium=100.0, strong=94.0
- EMAIL_008 (email_draft/medium): cheap=100.0, medium=100.0, strong=94.0
- EMAIL_010 (email_draft/hard): cheap=97.0, medium=100.0, strong=94.0
- MEET_003 (meeting_summary/easy): cheap=100.0, medium=100.0, strong=91.0
- MEET_008 (meeting_summary/hard): cheap=90.0, medium=90.0, strong=88.0
- RES_010 (research_brief/medium): cheap=97.0, medium=100.0, strong=88.0
- SLIDE_004 (slide_outline/easy): cheap=96.0, medium=86.0, strong=95.0
- SLIDE_005 (slide_outline/easy): cheap=88.0, medium=100.0, strong=72.0
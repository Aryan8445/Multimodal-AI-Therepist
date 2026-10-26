"""
Curated Evidence-Based Clinical Psychology Knowledge Base for SafeSpace RAG.
Covers Cognitive Behavioral Therapy (CBT), Dialectical Behavior Therapy (DBT),
Somatic Grounding Techniques, and Verified Crisis Lifelines.
"""

from typing import List, Dict

CLINICAL_DOCUMENTS: List[Dict[str, str]] = [
    {
        "id": "cbt-001",
        "category": "cbt",
        "title": "CBT: Identifying Cognitive Distortions",
        "content": (
            "Cognitive Behavioral Therapy (CBT) identifies recurring irrational thought patterns known as cognitive distortions: "
            "1. Catastrophizing: Expecting the worst-case scenario to happen inevitably ('If I fail this, my life is ruined'). "
            "2. All-or-Nothing Thinking (Black-and-White): Viewing situations in absolute binaries ('If I am not perfect, I am a failure'). "
            "3. Emotional Reasoning: Assuming negative emotions reflect objective reality ('I feel terrified, so I must be in danger'). "
            "4. Mind Reading: Assuming you know others are judging you negatively without evidence. "
            "5. Overgeneralization: Viewing a single negative event as a never-ending pattern ('Nothing ever goes right for me'). "
            "6. 'Should' Statements: Imposing rigid demands on oneself or others that induce guilt and frustration ('I should have known better'). "
            "Antidote: Identify the distortion, examine empirical evidence for and against the thought, and formulate a balanced reframe."
        ),
        "tags": "cbt, cognitive distortions, catastrophizing, thought reframing, negative thinking"
    },
    {
        "id": "cbt-002",
        "category": "cbt",
        "title": "CBT: 3-Column Thought Record and Cognitive Restructuring",
        "content": (
            "The 3-Column Thought Record is an effective tool for cognitive restructuring: "
            "Column 1 - Automatic Negative Thought (ANT): Record the exact intrusive thought (e.g., 'I will panic during the presentation and humiliate myself'). "
            "Column 2 - Cognitive Distortion: Identify which distortion applies (e.g., Fortune Telling / Catastrophizing). "
            "Column 3 - Rational Adaptive Response: Challenge the thought with realistic evidence (e.g., 'I am well prepared. Feeling nervous is natural and does not mean I will fail. Even if I stumble, I can pause, breathe, and continue'). "
            "Action Step: Ask the user to rate their belief in the initial thought (0-100%) before and after restructuring."
        ),
        "tags": "cbt, thought record, reframing, automatic thoughts, anxiety"
    },
    {
        "id": "cbt-003",
        "category": "cbt",
        "title": "CBT: Behavioral Activation for Depression and Low Energy",
        "content": (
            "Depression often causes behavioral withdrawal and lethargy, which deepens depressive symptoms. "
            "Behavioral Activation breaks this cycle through structured, graded engagement in meaningful activities: "
            "1. Graded Task Assignment: Break overwhelming tasks into bite-sized micro-steps (e.g., instead of 'clean entire house', start with 'put 3 dishes in the sink'). "
            "2. Mastery vs. Pleasure Scheduling: Plan activities that provide either a sense of accomplishment (mastery) or enjoyment (pleasure). "
            "3. Action Before Motivation: Motivation often follows action, rather than preceding it. Committing to just 5 minutes reduces inertia."
        ),
        "tags": "cbt, behavioral activation, depression, lethargy, motivation, sadness"
    },
    {
        "id": "dbt-001",
        "category": "dbt",
        "title": "DBT: TIPP Skills for Acute Distress Tolerance",
        "content": (
            "When emotional arousal spikes to extreme levels (overwhelmed, panic, intense anger), dialectical behavior therapy uses TIPP skills to rapidly reset the autonomic nervous system via the mammalian dive reflex: "
            "1. T - Temperature: Submerge face in cold water (50-60°F / 10-15°C) or apply an ice pack wrapped in a cloth to eyes and cheekbones for 30 seconds while holding breath. This activates parasympathetic bradycardia to lower heart rate. "
            "2. I - Intense Exercise: Engage in a short, intense aerobic burst (jumping jacks, fast stair climbing, brisk walking) for 2-5 minutes to expend excess adrenaline. "
            "3. P - Paced Breathing: Slow down breath cycle to 5-6 breaths per minute. Inhale deeply through nose for 4 seconds, exhale smoothly through mouth for 7-8 seconds. The prolonged exhale signals biological safety. "
            "4. P - Paired Muscle Relaxation: Tense muscle groups during inhalation, release tension abruptly during exhalation while mentally saying 'relax'."
        ),
        "tags": "dbt, tipp, distress tolerance, panic attack, crisis, intense emotion, overwhelm"
    },
    {
        "id": "dbt-002",
        "category": "dbt",
        "title": "DBT: The STOP Skill for Impulsive Reactions",
        "content": (
            "The STOP skill prevents impulsive reactions during emotional turbulence: "
            "S - Stop: Do not react, speak, or move. Freeze for a moment. Emotion wants you to act without thinking. "
            "T - Take a Step Back: Physically or mentally step back from the situation. Take a deep breath to disengage the fight-or-flight reflex. "
            "O - Observe: Notice what is happening inside you (bodily sensations, racing thoughts, emotions) and outside you without judgment. "
            "P - Proceed Mindfully: Ask yourself: 'What action will make this situation better rather than worse? What does wise mind advise?'"
        ),
        "tags": "dbt, stop skill, impulse control, anger, emotional regulation, mindfulness"
    },
    {
        "id": "dbt-003",
        "category": "dbt",
        "title": "DBT: Radical Acceptance of Pain and Unchangeable Reality",
        "content": (
            "Radical Acceptance is completely accepting reality as it is without attempting to fight, deny, or resist what has already happened: "
            "Pain is an inevitable part of life; suffering occurs when pain is coupled with non-acceptance (Suffering = Pain × Resistance). "
            "Acceptance does not mean approval, surrender, or agreement with injustice. It simply means acknowledging current facts so energy can be redirected into constructive, skillful problem solving."
        ),
        "tags": "dbt, radical acceptance, grief, chronic pain, acceptance, suffering"
    },
    {
        "id": "grounding-001",
        "category": "grounding",
        "title": "Somatic Grounding: The 5-4-3-2-1 Sensory Method",
        "content": (
            "The 5-4-3-2-1 technique anchors a dissociating, anxious, or panic-stricken mind back into the physical present using the five senses: "
            "1. 5 Things You Can SEE: Look around and acknowledge 5 distinct physical objects (e.g., the pattern on the rug, a reflection of light, a pen). "
            "2. 4 Things You Can FEEL: Bring tactile awareness to 4 physical textures (e.g., feet flat on the floor, texture of clothing, temperature of fingertips). "
            "3. 3 Things You Can HEAR: Listen closely for 3 background sounds (e.g., ambient hum of fan, distant traffic, your own steady breath). "
            "4. 2 Things You Can SMELL: Notice 2 distinct scents (e.g., coffee aroma, fresh air, soap on hands). "
            "5. 1 Thing You Can TASTE: Focus on 1 taste sensation (e.g., sip of cool water, lingering mint, or resting tongue)."
        ),
        "tags": "grounding, 54321, panic, sensory, somatic, anxiety, dissociation"
    },
    {
        "id": "grounding-002",
        "category": "grounding",
        "title": "Breathwork: 4-7-8 Relaxing Breath and Box Breathing",
        "content": (
            "Controlled breathwork modulates heart rate variability (HRV) and stimulates the vagus nerve: "
            "Method A - 4-7-8 Relaxing Breath (Dr. Andrew Weil): "
            "1. Inhale quietly through the nose for a count of 4. "
            "2. Hold your breath gently for a count of 7. "
            "3. Exhale completely and audibly through the mouth making a whoosh sound for a count of 8. "
            "Repeat cycle for 4 breaths. "
            "Method B - Box Breathing (Navy SEAL 4-4-4-4): "
            "Inhale 4s, Hold 4s, Exhale 4s, Hold empty 4s. Ideal for grounding before stressful events."
        ),
        "tags": "grounding, breathwork, 478 breathing, box breathing, vagus nerve, panic"
    },
    {
        "id": "crisis-001",
        "category": "crisis",
        "title": "Emergency Safety Protocols and Verified Crisis Lifelines",
        "content": (
            "CRITICAL: If a user expresses active suicidal thoughts, intent to self-harm, or severe psychiatric distress, immediate supportive escalation is required: "
            "1. United States & Canada: Call or Text 988 (Suicide & Crisis Lifeline). Available 24 hours a day, 7 days a week, 100% free and confidential. "
            "2. United States & Canada Text Line: Text 'HOME' to 741741 to connect with a trained Crisis Counselor. "
            "3. LGBTQ+ Youth: Call The Trevor Project at 1-866-488-7386 or text 'START' to 678-678. "
            "4. Veterans Crisis Line: Dial 988 and press 1, or text 838255. "
            "5. United Kingdom: Call 111 (NHS Mental Health Services) or 999 in emergencies. Text 'SHOUT' to 85258. "
            "6. India: Call Tele-MANAS at 14416 or Vandrevala Foundation at +91 9999 666 555. "
            "7. International Directory: Visit www.findahelpline.com or www.befrienders.org for global crisis resources. "
            "Protocol: Express unconditional warmth, validate their immense pain, avoid lecturing or dismissing feelings, urge them to connect with these professional lifelines, and trigger emergency notifications if available."
        ),
        "tags": "crisis, emergency, suicide, self harm, 988, lifeline, hotline, immediate help"
    }
]

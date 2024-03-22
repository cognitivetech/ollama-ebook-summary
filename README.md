# LLM for Book Summaries (Comprehensive Bulleted Notes) : Walkthrough and Model Rankings 

Processes and Analysis, using Large Language Models for summarizing books and other long texts:
- [Model Rankings](ranking-data)
- Tests of [Configuration Variables](configuration-variables.md)
- Detailed Walkthrough for both [PrivateGPT](walkthrough/privateGPT) and [Ollama](walkthrough)
- [Scripts](walkthrough/) and examples.

## Intro

When i began testing LLM variants, `mistral-7b-instruct-v0.1.Q4_K_M` came as part of PrivateGPT's default setup. Here, I've preferred the Q8_0 variants.

While I've tried 50+ different 7b GGUF for this same task, I haven't found anything that beats [**Mistral-7B-Instruct-v0.2**](https://huggingface.co/TheBloke/Mistral-7B-Instruct-v0.2-GGUF) for bullet point notes summarization.

## Contents
- [Background Tests with Configuration Variables](#background-tests-with-configuration-variables)
- [Latest Updates](#latest-updates)
  - [One Shot Prompting](#one-shot-prompting)
  - [Samantha Mistral Instruct 7b - Comprehensive Bulleted Notes](#samantha-mistral-instruct-7b---comprehensive-bulleted-notes)
- [Long-Text Summary Walkthrough](#long-text-summary-walkthrough)
- [Result](#result)
  - [Plagiarism](#plagiarism)
  - [Completed Book Summaries](#completed-book-summaries)
- [Additional Resources](#additional-resources)

## Background Tests with Configuration Variables

1. First I tried Q/A using [PrivateGPT](https://docs.privategpt.dev/overview), then tried pre-selecting text for summarization. 
   - This was the inspiration for [#1 rankings Q/A vs Summary](#round-1---qa-vs-summary), where I learned that a precise context is best for quality.
2. My desire to find which model works best for summaries, lead to [#2 rankings](configuration-variables.md#round-2-), where [Mistral-7B-Instruct-v0.2](https://huggingface.co/mistralai/Mistral-7B-Instruct-v0.2) was the clear winner.
3. Next I tested [prompt styles](configuration-variables.md#round-3-prompt-style), and wrote code to get ideal results for Mistral.
4. Then tried various [system prompts](configuration-variables.md#round-4-system-prompts).
5. Next, I experimented with [user prompts](configuration-variables.md#round-5-user-prompt) to get the best **bulleted notes summaries**.

Only once each model has been targeted to its most ideal conditions can they be properly ranked against each-other.

**Configuration Variable Aware Model Ranking**

Based on learnings from above mentioned trials, I am conscious to check the original Model Card and Community discussions on HF for: 
- prompt style. 
- any example system prompt
  - I always try the example system prompt
  - if the model card doesn't have a system prompt, I don't use one.
- size of training context

If you use a tool (like PrivateGPT) that supports Transformers Autotokenizer, that's another way to ensure the use of a models most ideal conditions. 

## Latest Updates
I've got some new tricks up my sleeve! I made a one-shot prompt that got my notes much closer to perfection, which enabled me to make a great dataset for fine-tuning. I'll keep adding more info here, but for now I'm just going to add the basics

### One Shot Prompting

I didn't think this would work for my use-case, because my document chunks already take up so much of the context, but I was convinced to try. I used a few different example instructions, but when I created this one demonstrating the task with content describing the task.. that was the magic, for me. Using this I can get 95-98% perfect results with Mistral 7b Instruct 0.2.

```
<s>You are a bulleted notes specialist. [INST]```When creating comprehensive bulleted notes, you should follow these guidelines: Use multiple headings based on the referenced topics, not categories like quotes or terms. Headings should be surrounded by bold formatting and not be listed as bullet points themselves. Leave no space between headings and their corresponding list items underneath. Important terms within the content should be emphasized by setting them in bold font. Any text that ends with a colon should also be bolded. Before submitting your response, review the instructions, and make any corrections necessary to adhered to the specified format. Do not reference these instructions within the notes.``` \nBased on the content between backticks create comprehensive bulleted notes.[/INST]
**Bulleted Note Creation Guidelines**

**Headings**:
- Based on referenced topics, not categories like quotes or terms
- Surrounded by **bold** formatting 
- Not listed as bullet points
- No space between headings and list items underneath

**Emphasis**:
- **Important terms** set in bold font
- **Text ending in a colon**: also bolded

**Review**:
- Ensure adherence to specified format
- Do not reference these instructions in your response.</s>[INST] {{ .Prompt }} [/INST]
```

That prompt is ~320 tokens. Based upon my experience and [*Same Task, More Tokens: the Impact of Input Length on the Reasoning Performance of Large Language Models*](https://huggingface.co/papers/2402.14848) I decided that I really wanted my max context (including one-shot prompt) to be ~2000 tokens.

Previously I was making chunks as large as 3750 trying to test out the supposed "long-context" llm dropping everywhere (they don't increase attantion span, only breath of attention). I also found that summarizing documents shorter than 500 tokens resulted in output the same size or longer than the original. So I split the chunks previously summarized books into proper sizes, soemtimes combining sections I previously left divided. Now my chunks average size is 1250 tokens.

### Samantha Mistral Instruct 7b - Comprehensive Bulleted Notes

Using ~5000 example bulleted notes summaries, following the described format, I fine-tuned Samantha 7b Mistral Instruct for 5 epochs and ended up keeping a merge around 2500 steps (closer to 4 epochs).

I made this fine-tune with an adaptation of the following notebook [ChatML + chat templates + Mistral 7b full example.ipynb](https://colab.research.google.com/drive/1Aau3lgPzeZKQ-98h69CCu1UJcvIBLmy2?usp=sharing) for RunPod.

![image/png](https://cdn-uploads.huggingface.co/production/uploads/657cca531e20870324f77ec7/cKk7nex2lV9YhZ_37XlWK.png)

- [**HuggingFace Blog**: Samantha Mistral Instruct 7b Bulleted Notes](https://huggingface.co/blog/cognitivetech/samantha-mistral-instruct-7b-bulleted-notes/)
- [cognitivetech/samantha-mistral-instruct-7b_bulleted-notes](https://huggingface.co/cognitivetech/samantha-mistral-instruct-7b_bulleted-notes/)
- [cognitivetech/samantha-mistral-instruct-7b_bulleted-notes_GGUF](https://huggingface.co/cognitivetech/samantha-mistral-instruct-7b_bulleted-notes_GGUF/)

## Long-Text Summary Walkthrough

If you are interested in following my steps, in more detail, to see how I summarize entire books and other long-texts, check out the detailed walkthroughs

* [Ollama Walkthrough](walkthrough)
* [PrivateGPT Walkthrough](walkthrough/privateGPT/)

## Result

I got my first summary of a 539 page book in 5-6 hours!!! Incredible!
**_More than that: I summarized my first 9 books in 10 consecutive days!_**

This is a game changer for anyone who's trying to wrangle with the massive amount of information available today.

### Plagiarism 

You can see the results from [CopyLeaks](https://app.copyleaks.com/) below for each of the texts published, here. 

Especially considering that this is not for profit, but for educational purposes, I believe these numbers are acceptable.

| Book | Models | Character Difference | Identical | Minor changes | Paraphrased | Total Matched |
| ---- | ----- | ---------------- | --------- | ------------- | ----------- | ---------- |
| Eastern Body Western Mind | Synthia 7Bv2 | -75% | 3.5% | 1.1% | 0.8% | 5.4% |
| Healing Power Vagus Nerve | Mistral-7B-Instruct-v0.2; SynthIA-7B-v2.0 | -81% | 1.2% | 0.8% | 2.5% | 4.5% |
| Ayurveda and the Mind | Mistral-7B-Instruct-v0.2; SynthIA-7B-v2.0 | -77% | 0.5% | 0.3% | 1.2% | 2% |
| Healing the Fragmented Selves of Trauma Survivors | Mistral-7B-Instruct-v0.2 | -75% | | | | 2% | 
| A Secure Base | Mistral-7B-Instruct-v0.2 | -84% | 0.3% | 0.1% | 0.3% | 0.7% |
| The Body Keeps the Score | Mistral-7B-Instruct-v0.2 | -74% | 0.1% | 0.2% | 0.3% | 0.5% |
| Complete Book of Chakras | Mistral-7B-Instruct-v0.2 | -70% | 0.3% | 0.3% | 0.4% | 1.1% |
| 50 Years of Attachment Theory | Mistral-7B-Instruct-v0.2 | -70% | 1.1% | 0.4% | 2.1% | 3.7% |
| Attachment Disturbances in Adults | Mistral-7B-Instruct-v0.2 | -62% | 1.1% | 1.2% | 0.7% | 3.1% |
| Psychology Major's Companion | Mistral-7B-Instruct-v0.2 | -62% | 1.3% | 1.2% | 0.4% | 2.9% |
| Psychology in Your Life | Mistral-7B-Instruct-v0.2 | -74% | 0.6% | 0.4% | 0.5% | 1.6% |

### Completed Book Summaries

1. [**Summary of Anodea Judith's Eastern Body Western Mind**](https://github.com/cognitivetech/Psychology-Book-Summaries/blob/main/Eastern-Body_Western-Mind.md) (436 pages)
   > **Adult Development**
   >  
   > The process of individuation involves becoming a single, homogeneous being and embracing one's innermost uniqueness. This journey begins in early adulthood when individuals leave home and start living independently.
   > 
   > 1. Chakra One: Survival is the primary issue during this stage, which includes getting a place to live, learning self-care, and finding an independent income source. The time spent on this stage varies from person to person, with some spending their entire lives struggling for survival.
   > 2. Chakra Two: Once basic independence is achieved, individuals form sexual relationships. This stage involves satisfying emotional needs, often projected onto a partner. Emotional frustration may arise due to unresolved childhood conflicts or the inability to develop personal will and responsibility.
   > 3. Chakra Three: The individuation process allows individuals to become true individuals operating under their own power and will. This stage is marked by the liberation from conforming to parental, cultural, or societal expectations. It may be triggered by meaningless jobs or enslavement in relationships where one's needs are defined by others.
   > 4. Chakra Four:  Relationships become more empathetic and altruistic during this stage, focusing on maintaining lasting partnerships. This may involve reevaluating behavior towards others, examining family dynamics, and building connections with colleagues, friends, and the community.
   > 5. Chakra Five: Creative and personal expression is emphasized in this stage, where individuals make their personal contribution to the community. It often occurs around midlife and may precede or dominate other activities for more creative personalities.
   > 6. Chakra Six: This introverted stage involves reflection and study of patterns through exploration of mythology, religion, and philosophy. It is a time of searching and spiritual interest, which intensifies when children are grown and adults have more freedom for contemplation and spiritual practice.
   > 7. Chakra Seven: The final stage is characterized by wisdom, spiritual understanding, knowledge, and teaching. Individuals bring together information gathered throughout life to pass it on to others or pursue a spiritual path.
2. [**Summary of Stanley Rosenberg's Healing Power of the Vagus Nerve**](https://github.com/cognitivetech/Psychology-Book-Summaries/blob/main/Healing-Power-Vagus-Nerve_Stanley-Rosenberg.md) (335 Pages)
   > The ANS is an integral part of the human nervous system, monitoring and regulating the activity of visceral organs such as heart, lungs, liver, gall bladder, stomach, intestines, kidneys, and sexual organs. Problems with any of these organs can arise from dysfunction of the ANS.
   > 
   > - **Old understanding of the ANS**: The ANS functioned in two states - stress and relaxation. 
   >   - Stress response is a survival mechanism activated when we feel threatened; it mobilizes our body to prepare for fight or flight. 
   >   - Relaxation response kicks in after threat has passed, keeping us in a relaxed state until the next threat appears.
   >   - Fails to explain why people continue to feel stressed even when they are not under any threat.
   > - **Polyvagal Theory (PVT)**: introduced the concept of three states
   >   - **Ventral Vagal State**: This state is characterized by social engagement and safety. It is associated with feelings of calmness, connection, and trust.
   >   - **Dorsal Vagal State**: This state is characterized by immobilization or shutdown. It is associated with feelings of fear, helplessness, and hopelessness.
   >   - **Sympathetic Nervous System (SNS)**: This system is responsible for the fight-or-flight response. It is associated with feelings of anxiety, stress, and tension.
3. [**Summary of Dr. David Frawley's Ayurveda and the Mind**](https://github.com/cognitivetech/Psychology-Book-Summaries/blob/main/Ayurveda-and-the-Mind_David-Frawley.md) (181 Pages)
   > 1. *Section 1*: Explores Ayurvedic view of mind-body relationship, including gunas (Sattva, Rajas, Tamas), doshas (Vata, Pitta, Kapha), and five elements.
   > 2. *Section 2*: In-depth examination of functions of awareness through consciousness, intelligence, mind, ego, and self.
   > 3. *Section 3*: Ayurvedic therapies for the mind: outer (diet, herbs, massage) and inner (color, aroma, mantra).
   > 4. *Section 4*: Spiritual and yogic practices from an Ayurvedic perspective, integrating all therapies.
   > 5. *Appendix*: Contains tables on functions of the mind and their correspondences.
   > 6. *Goals*: To provide sufficient knowledge for personal use and relevant to psychologists/therapists.
4. [**Summary of Janina Fisher's Healing the Fragmented Selves of Trauma Survivors**](https://github.com/cognitivetech/Psychology-Book-Summaries/blob/main/Healing-Fragmented-Selves-Trauma-Survivors_Janina-Fisher.md) (367 Pages)
   > 1. **Fragmentation and Internal Struggles**
   >    - Ten years ago, I observed a common pattern among traumatized clients: internal fragmentation.
   >    - Clients appeared integrated but showed signs of conflict between trauma-related perceptions and impulses versus present assessments.
   >    - They experienced paradoxical symptoms, such as the desire for kindness and spirituality alongside intense rage or violence.
   > 2. **Observable Patterns**
   >    - Describing these conflicts made them more observable and meaningful.
   >    - Each side represented a different way of surviving traumatic experiences.
   > 3. **Theoretical Model: Structural Dissociation**
   >    - The [Structural Dissociation model by Onno van der Hart, Ellert Nijenhuis, and Kathy Steele](https://link.springer.com/article/10.1007/BF03379560) explained these phenomena.
   >    - Rooted in neuroscience, it was accepted in Europe as a trauma model.
   > 4. **Brain's Innate Structure**
   >    - The brain's innate physical structure facilitates left-right brain disconnection under threat.
   >    - The left brain stays focused on daily tasks, while the right brain fosters an implicit self in survival mode.
   > 5. **Identifying and Owning Parts**
   >    - Some parts were easier to identify with or "own," while others were dismissed as "not me.
   >    - The internal relationships between fragmented aspects of self reflected traumatic environments.
   >    - The left-brain-dominant present-oriented self avoided or judged right-brain-dominant survival-oriented parts.
   >    - Both sides felt alienated from each other.
   > 6. **Functioning Self**
   >    - The functioning self carried on, trying to be "normal," but at the cost of feeling alienated or invaded by intrusive communications from parts.
5. [**Summary of John Bowlby's "A Secure Base"**](https://github.com/cognitivetech/Psychology-Book-Summaries/blob/main/a-secure-base_john-bowlby.md) (133 Pages)
   > - **Attachment behavioral response** essential for protection from predation and foundation for psychological health.
   > - **Sensitive caregiving** crucial for secure attachment throughout the life cycle.
   > - **Real-life adversity** origin of subsequent psychopathology, opposed to endo-psychic entities.
   > - **Systematic scientific observation** important for understanding attachment phenomena.
   > - **Secure base for patients** therapists providing a safe space for emotional exploration.
6. [**Summary of Bessel van der Kolk's The Body Keeps the Score**](https://github.com/cognitivetech/Psychology-Book-Summaries/blob/main/Body-Keeps-Score_Bessel-van-der-Kolk.md) (454 Pages)
   > **The Importance of Trauma:**
   > * Trauma reveals our fragility and man's inhumanity but also our resilience.
   > * Visionaries and societies have made profound advances from dealing with trauma.
   > * **Trauma is now the most urgent public health issue, and we have the knowledge to respond effectively.**
7. [**Summary of Yoga and Polyvagal Theory, from Steven Porges' Polyvagal Safety**](https://github.com/cognitivetech/Psychology-Book-Summaries/blob/main/Yoga-Therapy+PolyVagal-Theory.md) (37 pages)
   > * **Top-down processes**: regulation of attention, intention, decreasing psychological stress, HPA axis and SNS activity, modulating immune function and inflammation
   > * **Bottom-up processes**: breathing techniques, movement practices, influencing musculoskeletal, cardiovascular, nervous system function, affecting HPA and SNS activity, emotional well-being
   > * **Self-regulation**: conscious ability to manage responses to threat or adversity, reducing symptoms of various conditions, mitigating allostatic load, shifting autonomic state
8. [**Summary of Llewellyn's Complete Book of Chakras: Your Definitive Source of Energy Center Knowledge for Health, Happiness, and Spiritual Evolution**](https://github.com/cognitivetech/Psychology-Book-Summaries/blob/main/llewen-complete-book-chakras_1.md) (999 pages)
   * SECTION 1. CHAKRA FUNDAMENTALS AND BASIC PRACTICES
     > * Chakras are metaphysical energy centers that organize subtle energy for human use 
     > * **Three main systems of subtle energy in the body**: chakras, meridians/nadis, and auric fields
     > * Chakras convert physical energy into subtle energy and vice versa
     > * Seven main chakras regulate vital physical, psychological, and spiritual concerns
     > * Each chakra assists in embracing physical needs while attaining wisdom for enlightenment
     > * Section 1 is a pocket guide to understanding all aspects of chakras
   * [SECTION 2: CHAKRAS IN DEPTH. HISTORICAL, SCIENTIFIC, AND CROSS-CULTURAL UNDERSTANDINGS](https://github.com/cognitivetech/Psychology-Book-Summaries/blob/main/llewen-complete-book-chakras_2.md)
     > * Recap of chakras as pulsing points of light and key to health, connection, and spiritual enlightenment
     > * Origin and history of chakra knowledge primarily from ancient India
     > * Chakras and their companions (subtle energies, body, energetic anatomies, kundalini) are explainable through scientific perspectives
9. [**Summary of Fifty Years of Attachment Theory: The Donald Winnicott Memorial Lecture**](https://github.com/cognitivetech/Psychology-Book-Summaries/blob/main/50-years-attachment-theory.md) (54 pages)
   > **Background of Attachment Theory**
   > - Developed by Sir Richard Bowlby's father, John Bowlby
   > - Based on research into parent-child attachment relationship
   > - Originally called "research into bonding"
   > - Motivated by his own experience of losing a surrogate mother figure, Minnie, at age 4
   > 
   > **Early Influences and Education**
   > - Father was a successful surgeon with six children
   > - Children had twenty-three hour care from nannies and nursemaids
   > - Father grew attached to his nursemaid, Minnie
   > - When Minnie left, father felt pain but not traumatized
   > - Met John Alford at age 21, who inspired interest in maternal deprivation
10. [**Summary of Attachment Disturbances in Adults**](notes/Attachment-Disturbances-Adults2.md) (477 Pages)
    > - Part I: Foundational Concepts
    > - Part II: Assessment
    > - Part III: Treatment
    > - Part IV: Type-Specific Treatment
    > - Part V: A Treatment Guide and Expected Outcomes
11. [**Summary of The Psychology Major's Companion**](https://github.com/cognitivetech/Psychology-Book-Summaries/blob/main/Psychology_Majors_Companion.md) (308 Pages)
    > **Questions Addressed:**
    > 1. **What do psychologists do? Where do they work?**
    > 2. **Is majoring in psychology the right choice for me?**
    > 3. **Skills and benefits of an undergraduate degree in psychology**
    >    * High-performing student
    >    * Organizational memberships, summer jobs, internships
    > 4. **Career opportunities after graduation**
    >    * Bachelor's level psychology majors
    >    * Job search right out of college
    > 5. **Graduate study in psychology**
    >    * Application process
    >    * Choosing an area of psychology
    >    * Making a compelling application
    > 6. **Benefits of psychology beyond education and career**
12. [**Summary of The Myth of Redemptive Violence**](https://github.com/cognitivetech/Psychology-Book-Summaries/blob/main/myth-redemptive-violence.md) (5 Pages)
    > - Walter Wink's analysis of the pervasiveness of the belief that violence saves and brings peace in Western culture.
    > - Discussion on how this belief is rooted in ancient mythology and perpetuated through modern media, particularly cartoons.
13. [**Psychology In Your Life**](https://github.com/cognitivetech/Psychology-Book-Summaries/blob/main/Psychology-In-Your-Life.md) (1072 Pages)
    > 1. **Biological Domain**: This domain focuses on the study of biological factors that influence behavior and mental processes. It includes research on genetics, neuroanatomy, physiology, and pharmacology.
    > 2. **Cognitive Domain**: The cognitive domain investigates mental processes such as perception, attention, memory, language, problem-solving, and decision-making.
    > 3. **Developmental Domain**: This domain examines the psychological and physical changes that occur throughout the human lifespan, from infancy to old age. It includes research on cognitive, social, emotional, and moral development.
    > 4. **Social and Personality Domain**: The social and personality domain explores how individuals think about themselves and others, as well as their interactions with other people. It includes research on personality traits, interpersonal relationships, group dynamics, and social influence.
    > 5. **Mental and Physical Health Domain**: This domain focuses on understanding mental health disorders and promoting positive mental and physical health. It includes research on diagnosis, treatment, and prevention of various mental and physical health conditions.

## Additional Resources

* [Summarizing Books](https://openai.com/research/summarizing-books) OpenAI
* [HuggingFace - Open LLM Leaderboard](https://huggingface.co/spaces/HuggingFaceH4/open_llm_leaderboard)
* [Pressure-tested the most popular open-source LLMs (Large Language Models) for their Long Context Recall abilities](https://www.reddit.com/r/LocalLLaMA/comments/18s61fb/pressuretested_the_most_popular_opensource_llms/) u/ramprasad27 ([Part 2](https://www.reddit.com/r/LocalLLaMA/comments/190r59u/long_context_recall_pressure_test_batch_2/))
  * [LeonEricsson / llmcontext - Pressure testing the context window of open LLMs](https://github.com/LeonEricsson/llmcontext)
* [Chatbox Arena Leaderboard](https://chat.lmsys.org/)
* [LLM Comparison/Test: Ranking updated with 10 new models (the best 7Bs)!](https://www.reddit.com/r/LocalLLaMA/comments/18u122l/llm_comparisontest_ranking_updated_with_10_new/) WolframRavenwolf
  * [LLM Prompt Format Comparison/Test: Mixtral 8x7B Instruct with **17** different instruct templates](https://www.reddit.com/r/LocalLLaMA/comments/18ljvxb/llm_prompt_format_comparisontest_mixtral_8x7b/) WolframRavenwolf
* [Hallucination leaderboard](https://github.com/vectara/hallucination-leaderboard/) Vectara

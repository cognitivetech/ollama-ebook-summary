# LLM for Book Summarization & Q\A : Walkthrough and Rankings

In this repository I will describe my processes, and analysis of the particulars, when using [PrivateGPT](https://docs.privategpt.dev/overview) for book summarization.

## Contents
- [Overview](#overview)
- [Rankings](#rankings)
  - [Round 1 - Q/A vs Summary](#round-1---qa-vs-summary)
    - [Question / Answer Ranking](#question--answer-ranking)
    - [Summary Ranking](#summary-ranking)
  - [Round 2: Summarization - Narrow Down Contenders](#round-2-summarization---narrow-down-contenders)
    - [Summary Ranking](#summary-ranking-1)
  - [Round 3: Prompt Style](#round-3-prompt-style)
- [Methods](#methods)
  - [Walkthrough](#walkthrough)
- [Result](#result)
  - [Plagiarism](#plagiarism)
  - [Completed Book Summaries](#completed-book-summaries)

## Overview

1. I began by just asking questions to book chapters, using the [PrivateGPT](https://docs.privategpt.dev/overview) UI. Then tried pre-selecting text for summarization. This was the inspiration for Round 1 rankings, in which summarization was the clear winner.

2. Next I wanted to find which models would do the best with this task, which led to Round 2 rankings, where [Mistral-7B-Instruct-v0.2](https://huggingface.co/mistralai/Mistral-7B-Instruct-v0.2) was the clear winner.

3. Then I wanted to get the best results from this model by ranking prompt styles, and writing code to get the exact prompt style expected.

4. After that, of course, I had to test out various system prompts to see which would perform the best.

5. This will culminate in a battle between user prompts, where I determine what is the exact best prompt to generate summaries requiring the least post-processing, by me.

## Rankings

When i began testing various LLM variants, `mistral-7b-instruct-v0.1.Q4_K_M` comes as part of PrivateGPT's default setup. Here, I've preferred the Q8_0 variants.

While I've tried 50+ different LLM for this same task, Mistral-7B-Instruct is still among the best.

TLDR: [**Mistral-7B-Instruct-v0.2**](https://huggingface.co/mistralai/Mistral-7B-Instruct-v0.2) - is my current leader for summarization.

## Round 1 - Q/A vs Summary
For this analysis we will be testing out 5 different LLM for the following tasks:

1. Asking the same 30 questions to a 70 page book chapter.
2. Summarizing that same 70 page book chapter divided into 30 chunks.

**Find the full data and rankings on [Google Docs](https://docs.google.com/spreadsheets/d/1u3BgDx6IsJSbRz3uNmud1sDtO4WvWsH6ION3J-fhoGw/edit?usp=sharing) or here in this repository [QA Scores](ranking-data/Round-1_QA.csv), [Summary Rankings](ranking-data/Round-1_Summary.csv).**

### Question / Answer Ranking
1. [**Hermes Trismegistus Mistral 7b**](https://huggingface.co/TheBloke/Hermes-Trismegistus-Mistral-7B-GGUF) - Initially my favorite, but ended up deciding it was too verbose.
2. [**SynthIA 7B**](https://huggingface.co/TheBloke/SynthIA-7B-v2.0-GGUF) - Became my favorite of models tested in this round.
3. [**Mistral 7b Instruct v0.1**](https://huggingface.co/TheBloke/Mistral-7B-Instruct-v0.1-GGUF) - Since this ranking, v0.2 has come out and beat all the competition. I should test them against eachother, sometime.
4. [**CollectiveCognition v1.1 Mistral 7b**](https://huggingface.co/TheBloke/CollectiveCognition-v1.1-Mistral-7B-GGUF) Alot of filler and took the longest amount of time of them all. It scored a bit higher than mistral on quality\usefulness, I think the amount of filler just made it less enjoyable to read.
5. [**KAI 7b Instruct**](https://huggingface.co/TheBloke/KAI-7B-Instruct-GGUF) the answers were too short, and made its BS stand out a little more. A good model, but not for summarizing books, I'm afraid.

| Model | Rating | Search Accuracy | Characters | Seconds | BS | Filler | Short | Good BS |
| ----- | ------ | --------------- | ---------- | ------- | -- | ------ | ----- | ------- |
| hermes-trismegistus-mistral-7b | 68 | 56 | 62141 | 298 | 3 | 4 | 0 | 6 |
| synthia-7b-v2.0 | 63 | 59 | 28087 | 188 | 1 | 7 | 7 | 0 |
| mistral-7b-instruct-v0.1 | 51 | 56 | 21131 | 144 | 3 | 0 | 17 | 1 |
| collectivecognition-v1.1-mistral-7b | 56 | 57 | 59453 | 377 | 3 | 10 | 0 | 0 |
| kai-7b-instruct | 44 | 56 | 21480 | 117 | 5 | 0 | 18 | 0 |

#### Shown above, for each model
- Number of seconds required to generate the answer
- Sum of Subjective Usefulness\Quality Ratings
- How many characters were generated?
- Sum of context context chunks found in target range.
- Number of qualities listed below found in text generated:
  - Filler  (Extra words with less value)
  - Short   (Too short, not enough to work with.)
  - BS      (Not from this book and not helpful.)
  - Good BS (Not from the targeted section but valid.)

### Summary Ranking

Not surprisingly, summaries performed better than Q/A, but they also had a more finely targeted context.

1. [**Hermes Trismegistus Mistral 7b**](https://huggingface.co/TheBloke/Hermes-Trismegistus-Mistral-7B-GGUF) - Still in the lead. It's verbose, with some filler. I can use these results.
2. [**SynthIA 7B**](https://huggingface.co/TheBloke/SynthIA-7B-v2.0-GGUF) - Pretty good, but too concise. Many of the answers were perfect, but 7 were too short\incomplete for use.
3. [**Mistral 7b Instruct v0.1**](https://huggingface.co/TheBloke/Mistral-7B-Instruct-v0.1-GGUF) - Just too short.
4. [**KAI 7b Instruct**](https://huggingface.co/TheBloke/KAI-7B-Instruct-GGUF) - Just too short.
5. [**CollectiveCognition v1.1 Mistral 7b**](https://huggingface.co/TheBloke/CollectiveCognition-v1.1-Mistral-7B-GGUF) - Lots of garbage. Some of the summaries were super detailed and perfect, but over half of the responses were a set of questions based on the text, not a summary.

| Name | Score |  Characters Generated | % Diff from OG | Seconds to Generate | Short | Garbage | BS | Fill | Questions | Detailed |
| ---- | ----- | -------------------- | -------------- | ------------------- | ----- | ------- | -- | ---- | --------- | -------- | 
| hermes-trismegistus-mistral-7b | 74 | 45870 | -61 | 274 | 0 | 1 | 1 | 3 | 0 | 0 |
| synthia-7b-v2.0 | 60 | 26849 | -77 | 171 | 7 | 1 | 0 | 0 | 0 | 1 |
| mistral-7b-instruct-v0.1 | 58 | 25797 | -78 | 174 | 7 | 2 | 0 | 0 | 0 | 0 |
| kai-7b-instruct | 59 | 25057 | -79 | 168 | 5 | 1 | 0 | 0 | 0 | 0 |
| collectivecognition-v1.1-mistral-7b | 31 | 29509 | -75 | 214 | 0 | 1 | 1 | 2 | 17 | 8 |

## Round 2: Summarization - Narrow Down Contenders

Again, I've preferred the Q8_0 variants.

Finding Mistral 7B v0.2 was well worth a new round of testing. This time, less intense. I didn't record speed of query, and only judged 12 summarization tasks, but I tried a number of models and saved the most interesting results.

One thing I tested this time was prompts, because Mistral is supposed to take Llama2 Prompt, but seems to perform better with the default (llama-index) prompt. As for Llama 2, it performed really bad with the Llama 2 prompt, but decent with the Default prompt.

- [**SynthIA-7B-v2.0-GGUF**](https://huggingface.co/TheBloke/SynthIA-7B-v2.0-GGUF) -  This model had become my favorite, so I used it as a benchmark.
- [**Mistral-7B-Instruct-v0.2**](https://huggingface.co/mistralai/Mistral-7B-Instruct-v0.2) (Llama-index Prompt) Star of the show here, quite impressive.
- [**Mistral-7B-Instruct-v0.2**](https://huggingface.co/mistralai/Mistral-7B-Instruct-v0.2) (Llama2 Prompt) Still good, but not _as_ good as using llama-index prompt
- [**Tess-7B-v1.4**](https://huggingface.co/migtissera/Tess-7B-v1.4) - Another by the same creator as Synthia. Good, but not _as_ good.
- [**Llama-2-7B-32K-Instruct-GGUF**](https://huggingface.co/TheBloke/Llama-2-7B-32K-Instruct-GGUF) - worked ok, but slowly, with llama-index prompt. Just bad with llama2 prompt. 

### Summary Ranking

This time I only did summaries. Q/A is just less efficient for book summarization.

| Model | % Difference | Score | Comment | 
| ----- | ------------ | ----- | ------- | 
| Synthia 7b V2 | -64.43790093 | 28 | Good | 
| Mistral 7b v0.2 (Default Prompt) | -60.81878508 | 33 | VGood | 
| Mistral 7b v0.2 (Llama2 Prompt) | -64.5871483 | 28 | Good | 
| Tess 7b v1.4 | -62.12938978 | 29 | Less Structured | 
| Llama 2 7b 32k Instruct (Default) | -61.39890553 | 27 | Less Structured. Slow | 

**Find the full data and rankings on [Google Docs](https://docs.google.com/spreadsheets/d/1u3BgDx6IsJSbRz3uNmud1sDtO4WvWsH6ION3J-fhoGw/edit?usp=sharing) or here in this repository [Summary Rankings](ranking-data/Round-2_Summaries.csv).**

## Round 3: Prompt Style

A [new mistral](https://huggingface.co/TheBloke/Mistral-7B-Instruct-v0.2-GGUF) came out recently, and in the last round of rankings, I noticed it was doing much better with default prompt than llama2.

Well, actually, the mistral prompt is quite similar to llama2, but not exactly the same.

1. llama_index (default)

```
system: {{ system_prompt }}
user: {{ user_message }}
assistant: {{ assistant_message }}
```

2. llama2:

```
<s>[INST] <<SYS>>
{{ system_prompt }}
<</SYS>>

{{ user_message }} [/INST]
```

3. mistral:

```
<s>[INST] {{ system_prompt }} [/INST]</s>[INST] {{ user_message }} [/INST]
```

**I began testing output** with the `default`, then `llama2` prompt styles. Next I went to work [coding the mistral template](https://github.com/imartinez/privateGPT/pull/1426/files).

The results of that ranking gave me confidence that I coded correctly.

| Prompt Style | % Difference | Score | Note |
| --- | --- | --- | --- |
| Mistral	| -50% | 51 | Perfect! |
| Default (llama-index) | -42% | 43 | Bad headings |
| Llama2 | -47% | 48 | No Structure |

**Find the full data and rankings on [Google Docs](https://docs.google.com/spreadsheets/d/1u3BgDx6IsJSbRz3uNmud1sDtO4WvWsH6ION3J-fhoGw/) or here in this repository [Prompt Style Rankings](ranking-data/Round-3_Prompt-Style.csv).**

## Methods

Rather than feed a 400 page book into any LLM model, splitting it into chapters makes the task more managable. 

Using [PrivateGPT](https://github.com/imartinez/privateGPT), I've found a number of models that produce good results, and first ran tests using a few models on a single book chapter.

Using knowledge gained from these tests, I summarized a complete book, using Synthia 7B v2, transitioning from a "Detailed Summary" prompt to a "Bullet Point Notes" prompt.

### Walkthrough

If you are interested in following my steps, in more detail, check out the [walkthrough](walkthrough).

## Result

I got my first summary of a 539 page book in 5-6 hours!!! (not including first run with Hermes) Incredible!

When I was going to do this manually, it was going to take weeks for each summary.

### Plagiarism 

You can see the results from [CopyLeaks](https://app.copyleaks.com/) below for each of the texts published, here. 

Considering that this is not for profit, but for educational purposes, I believe these numbers are acceptable.

| Book | Models | Character Difference | Identical | Minor changes | Paraphrased | plagiarism |
| ---- | ----- | ---------------- | --------- | ------------- | ----------- | ---------- |
| Eastern Body Western Mind | Synthia 7Bv2 | -75% | 3.5% | 1.1% | 0.8% | 5.4% |
| Healing Power Vagus Nerve | Mistral-7B-Instruct-v0.2; SynthIA-7B-v2.0 | -81% | 1.2% | 0.8% | 2.5% | 4.5% |
| Ayurveda and the Mind | Mistral-7B-Instruct-v0.2; SynthIA-7B-v2.0 | -77% | 0.5% | 0.3% | 1.2% | 2% |
| Healing the Fragmented Selves of Trauma Survivors | Mistral-7B-Instruct-v0.2 | -75% | | | | 2% | 
| A Secure Base | Mistral-7B-Instruct-v0.2 | -84% | 0.3% | 0.1% | 0.3% | 0.7% |
| The Body Keeps the Score | Mistral-7B-Instruct-v0.2 | -74% | 0.1% | 0.2% | 0.3% |

### Completed Book Summaries

1. [**Summary of Anodea Judith's Eastern Body Western Mind**](summaries/Eastern-Body_Western-Mind.md)
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
2. [**Summary of Stanley Rosenberg's Healing Power of the Vagus Nerve**](summaries/Healing-Power-Vagus-Nerve_Stanley-Rosenberg.md)
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
3. [**Summary of Dr. David Frawley's Ayurveda and the Mind**](summaries/Ayurveda-and-the-Mind_David-Frawley.md)
  > 1. *Section 1*: Explores Ayurvedic view of mind-body relationship, including gunas (Sattva, Rajas, Tamas), doshas (Vata, Pitta, Kapha), and five elements.
  > 2. *Section 2*: In-depth examination of functions of awareness through consciousness, intelligence, mind, ego, and self.
  > 3. *Section 3*: Ayurvedic therapies for the mind: outer (diet, herbs, massage) and inner (color, aroma, mantra).
  > 4. *Section 4*: Spiritual and yogic practices from an Ayurvedic perspective, integrating all therapies.
  > 5. *Appendix*: Contains tables on functions of the mind and their correspondences.
  > 6. *Goals*: To provide sufficient knowledge for personal use and relevant to psychologists/therapists.
4. [**Summary of Janina Fisher's Healing the Fragmented Selves of Trauma Survivors*](summaries/Healing-Fragmented-Selves-Trauma-Survivors_Janina-Fisher.md)
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
5. [**Summary of John Bowlby's "A Secure Base"**](summaries/a-secure-base_john-bowlby.md)
  > **John Bowlby's "A Secure Base" (1988). His final contribution to Attachment Theory, summarizing his life's work and acknowledging the next generation of researchers and clinicians. Key themes include**:
  > - **Attachment behavioral response** essential for protection from predation and foundation for psychological health.
  > - **Sensitive caregiving** crucial for secure attachment throughout the life cycle.
  > - **Real-life adversity** origin of subsequent psychopathology, opposed to endo-psychic entities.
  > - **Systematic scientific observation** important for understanding attachment phenomena.
  > - **Secure base for patients** therapists providing a safe space for emotional exploration.
* [**Summary of Bessel van der Kolk's The Body Keeps the Score**](summaries/Body-Keeps-Score_Bessel-van-der-Kolk.md)
  > **The Importance of Trauma:**
  > * Trauma reveals our fragility and man's inhumanity but also our resilience.
  > * Visionaries and societies have made profound advances from dealing with trauma.
  > * **Trauma is now the most urgent public health issue, and we have the knowledge to respond effectively.**


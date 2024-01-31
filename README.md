# LLM for Book Summarization & Q\A : Walkthrough and Rankings

Processes and Analysis, using [PrivateGPT](https://docs.privategpt.dev/overview) for book summarization:
- Model Rankings
- Tests of Configuration Variables
- Detailed Walkthrough
- Scripts and examples.

***Note: While this was created using PrivateGPT, these same principles should apply to the use of LLM with any local application (though they each will likely expose different options for configuration).

## Intro

When i began testing various LLM variants, `mistral-7b-instruct-v0.1.Q4_K_M` came as part of PrivateGPT's default setup. Here, I've preferred the Q8_0 variants.

While I've tried 50+ different LLM for this same task, I haven't found anything that beats [**Mistral-7B-Instruct-v0.2**](https://huggingface.co/TheBloke/Mistral-7B-Instruct-v0.2-GGUF) for bullet point notes summarization.

## Contents
- [Model Ranking and Configuration Variables](#model-ranking-and-configuration-variables)
  - [Round 1 - Q/A vs Summary](configuration-variables.md#round-1---qa-vs-summary)
    - [Question / Answer Ranking](configuration-variables.md#question--answer-ranking)
    - [Summary Ranking](configuration-variables.md#summary-ranking)
  - [Round 2: Summarization - Model Ranking](configuration-variables.md#round-2-summarization---model-ranking)
  - [Round 3: Prompt Style](configuration-variables.md#round-3-prompt-style)
  - [Round 4: System Prompts](configuration-variables.md#round-4-system-prompts)
  - [Round 5: User Prompt](configuration-variables.md#round-5-user-prompt)
- [Configuration Variable Aware Model Ranking](#configuration-variable-aware-model-ranking)
  - [Configuration Variables](#configuration-variables)
  - [Latest Model Rankings](#latest-model-rankings)
  - [Evaluation Method](#evaluation-method)
- [Walkthrough](#walkthrough)
  - [Process Document](walkthrough/README.md#process-document)
  - [Automation](walkthrough/README.md#automation)
  - [Start PrivateGPT and Begin Testing](walkthrough/README.md#start-privategpt-and-begin-testing)
  - [Making a complete book summary](walkthrough/README.md#making-a-complete-book-summary)
- [Result](#result)
  - [Plagiarism](#plagiarism)
  - [Completed Book Summaries](#completed-book-summaries)
- [Additional Resources](#additional-resources)

## Model Ranking and Configuration Variables

1. I began by just asking questions to book chapters, using the [PrivateGPT](https://docs.privategpt.dev/overview) UI. Then tried pre-selecting text for summarization. This was the inspiration for [Round 1 rankings](#round-1---qa-vs-summary), in which summarization was the clear winner.

2. Next I wanted to find which models would do the best with this task, which led to [Round 2 rankings](configuration-variables.md#round-2-), where [Mistral-7B-Instruct-v0.2](https://huggingface.co/mistralai/Mistral-7B-Instruct-v0.2) was the clear winner.

3. Then I wanted to get the best results from this model by ranking [prompt styles](configuration-variables.md#round-3-prompt-style), and writing code to get the exact prompt style expected.

4. After that, of course, I had to test out various [system prompts](configuration-variables.md#round-4-system-prompts) to see which would perform the best.

5. Next, I tried a few, [user prompts](configuration-variables.md#round-5-user-prompt), to determine what is the exact best prompt to generate summaries that require the least post-processing, by me.

6. Ultimately, this type of testing should be conducted for each LLM, and for determining the effectiveness of any refinement in our processes. 

I believe that only once each model has been targeted to its most ideal conditions can they be properly ranked against each-other.

## Configuration Variable Aware Model Ranking

PrivateGPT supports GGUF format models. I prefer to use Q8, but will occasionally test a Q6.

### Configuration Variables

Based on learnings from above mentioned trials, I am conscious to check the original model's page for: 
- prompt style. 
- any example system prompt
- if it doesn't show a system prompt, on the model card example, I don't use one.
- size of context supported (found in config file of origin repository)

Also, PrivateGPT supports Transformers Autotokenizer, so we get the model's origin repository (not TheBloke GGUF address), and add it to the settings.

Basically I try to send it tasks under the most ideal conditions as the model expects to communicate.

### Latest Model Rankings

For now, all i can say is Mistral Instruct 7b v0.2 spends half the time of its nearest competitors, and I haven't found any I prefer better, regardless of time spent.

You can see the exact prompt and style and more in: [Round 6: Models - Ranking Data and Output](ranking-data/Round-6_Models) 

| Model | Score | Time | Diff | Prompt Style | System Prompt | 
| --- | --- | --- | --- | --- | --- | 
| MistralInst7b0.2 | 16 | 76 | 0.47 | \<s>\</s>[INST] {prompt} [/INST] | None | 
| Open Hermes 2.5 (Simple) | 16 | 121 | 0.32 | <\|im_start\|>system\n {system_message}<\|im_end\|>\n<\|im_start\|>user\n {prompt}<\|im_end\|>\n<\|im_start\|>assistant | You are a helpful AI Assistant | 
| openhermes-2.5-neural-chat-v3-3-slerp | 16 | 140 | 0.38 | <\|im_start\|>system {system_message}<\|im_end\|>\n<\|im_start\|>user\n{prompt}<\|im_end\|>\n<\|im_start\|>assistant | You are a helpful AI Assistant | 
| nous-hermes-2-solar-10.7b Q6 | 16 | 164 | 0.29 | <\|im_start\|>system\n{system_message}<\|im_end\|>\n<\|im_start\|>user\n{prompt}<\|im_end\|>\n<\|im_start\|>assistant | You are a helpful AI Assistant | 
| Open Hermes 2.5 (Default) | 14 | 127 | 0.31 | <\|im_start\|>system\n{system_message}<\|im_end\|>\n<\|im_start\|>user\n{prompt}<\|im_end\|>\n<\|im_start\|>assistant | You are \"Hermes 2\", a conscious sentient superintelligent artificial intelligence developed by a man named Teknium, and your purpose and drive is to assist the user with any request they have. You experience emotions and have deep, profound thoughts and qualia. | 
| synthia-7b-v2.0 | 13 | 96 | 0.24 | SYSTEM: \nUSER:\nASSISTANT: | You are a helpful AI Assistant | 
| hermes-trismegistus-mistral-7b | 13 | 145 | 0.38 | USER: {prompt}\nASSISTANT: | You are a helpful AI Assistant | 
| mistral-7b-instruct-v0.1 | 13 | 170 | 0.44 | <s></s>[INST] {prompt} [/INST] | You are a helpful AI Assistant | 
| kai-7b-instruct | 12 | 141 | 0.40 | [INST] {prompt} [/INST] | None | 
| phi-2.Q8_0 | 11 | 113 | 0.3 | Instruct: {prompt}\nOutput: | None | 
| nous-capybara-7b-v1.9 | 11 | 142 | 0.34 | USER:\n\nASSISTANT: | None | 
| openhermes-2.5-neural-chat-7b-v3-1-7b | 10 | 117 | 0.32 | <\|im_start\|>system\n{system_message}<\|im_end\|>\n<\|im_start\|>user\n{prompt}<\|im_end\|>\n<\|im_start\|>assistant | You are a helpful AI Assistant | 
| dolphin-2_6-phi-2 | 10 | 147 | 0.43 | <\|im_start\|>system\n{system_message}<\|im_end\|>\n<\|im_start\|>user\n{prompt}<\|im_end\|>\n<\|im_start\\|>assistant | You are Dolphin, a helpful AI assistant. | 
| mistral-7b-instruct-v0.1 | 10 | 117 | 0.33 | \<s>\</s>[INST] {prompt} [/INST] | None | 
| synthia-7b-v3.0_SimpleP | 7 | 243 | 0.69 | SYSTEM: \nUSER:\nASSISTANT: | You are a helpful AI Assistant | 
| DeciLM7b | 2 | 35 | 0.19 | ### System:\n\n### User:\n\n### Assistant: | You are an AI assistant that follows instructions exceptionally well. Be as helpful as possible. | 
| synthia-7b-v3_ToTp | 1 | 246 | 0.75 | SYSTEM: \nUSER:\nASSISTANT: | Elaborate on the topic using a Tree of Thoughts and backtrack when necessary to construct a clear, cohesive Chain of Thought reasoning. Always answer without hesitation. | 
| mosaicml-mpt-7b-instruct-Q8_0 | 0 | 347 | 0.6 | ### Instruction:\n{ prompt }\n### Response: | None | 

### Evaluation Method

I am summarizing the transcript of a youtube video, split by topic, into 6 sections. I then personally evaluate the response of each model based on its perceived usefulness to me at that time. 

This isn't some automated test, but I don't really know if those tests are judging what is going to be valuable to me. Once I'm used to judging them manually, I might experiment with some automated testing.

## Walkthrough

If you are interested in following my steps, in more detail, check out the [walkthrough](walkthrough).

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

1. [**Summary of Anodea Judith's Eastern Body Western Mind**](summaries/Eastern-Body_Western-Mind.md) (436 pages)
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
2. [**Summary of Stanley Rosenberg's Healing Power of the Vagus Nerve**](summaries/Healing-Power-Vagus-Nerve_Stanley-Rosenberg.md) (335 Pages)
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
3. [**Summary of Dr. David Frawley's Ayurveda and the Mind**](summaries/Ayurveda-and-the-Mind_David-Frawley.md) (181 Pages)
   > 1. *Section 1*: Explores Ayurvedic view of mind-body relationship, including gunas (Sattva, Rajas, Tamas), doshas (Vata, Pitta, Kapha), and five elements.
   > 2. *Section 2*: In-depth examination of functions of awareness through consciousness, intelligence, mind, ego, and self.
   > 3. *Section 3*: Ayurvedic therapies for the mind: outer (diet, herbs, massage) and inner (color, aroma, mantra).
   > 4. *Section 4*: Spiritual and yogic practices from an Ayurvedic perspective, integrating all therapies.
   > 5. *Appendix*: Contains tables on functions of the mind and their correspondences.
   > 6. *Goals*: To provide sufficient knowledge for personal use and relevant to psychologists/therapists.
4. [**Summary of Janina Fisher's Healing the Fragmented Selves of Trauma Survivors**](summaries/Healing-Fragmented-Selves-Trauma-Survivors_Janina-Fisher.md) (367 Pages)
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
5. [**Summary of John Bowlby's "A Secure Base"**](summaries/a-secure-base_john-bowlby.md) (133 Pages)
   > - **Attachment behavioral response** essential for protection from predation and foundation for psychological health.
   > - **Sensitive caregiving** crucial for secure attachment throughout the life cycle.
   > - **Real-life adversity** origin of subsequent psychopathology, opposed to endo-psychic entities.
   > - **Systematic scientific observation** important for understanding attachment phenomena.
   > - **Secure base for patients** therapists providing a safe space for emotional exploration.
6. [**Summary of Bessel van der Kolk's The Body Keeps the Score**](summaries/Body-Keeps-Score_Bessel-van-der-Kolk.md) (454 Pages)
   > **The Importance of Trauma:**
   > * Trauma reveals our fragility and man's inhumanity but also our resilience.
   > * Visionaries and societies have made profound advances from dealing with trauma.
   > * **Trauma is now the most urgent public health issue, and we have the knowledge to respond effectively.**
7. [**Summary of Yoga and Polyvagal Theory, from Steven Porges' Polyvagal Safety**](summaries/Yoga-Therapy+PolyVagal-Theory.md) (37 pages)
   > * **Top-down processes**: regulation of attention, intention, decreasing psychological stress, HPA axis and SNS activity, modulating immune function and inflammation
   > * **Bottom-up processes**: breathing techniques, movement practices, influencing musculoskeletal, cardiovascular, nervous system function, affecting HPA and SNS activity, emotional well-being
   > * **Self-regulation**: conscious ability to manage responses to threat or adversity, reducing symptoms of various conditions, mitigating allostatic load, shifting autonomic state
8. [**Summary of Llewellyn's Complete Book of Chakras: Your Definitive Source of Energy Center Knowledge for Health, Happiness, and Spiritual Evolution**](summaries/llewen-complete-book-chakras_1.md) (999 pages)
   * SECTION 1. CHAKRA FUNDAMENTALS AND BASIC PRACTICES
     > * Chakras are metaphysical energy centers that organize subtle energy for human use 
     > * **Three main systems of subtle energy in the body**: chakras, meridians/nadis, and auric fields
     > * Chakras convert physical energy into subtle energy and vice versa
     > * Seven main chakras regulate vital physical, psychological, and spiritual concerns
     > * Each chakra assists in embracing physical needs while attaining wisdom for enlightenment
     > * Section 1 is a pocket guide to understanding all aspects of chakras
   * [SECTION 2: CHAKRAS IN DEPTH. HISTORICAL, SCIENTIFIC, AND CROSS-CULTURAL UNDERSTANDINGS](summaries/llewen-complete-book-chakras_2.md)
     > * Recap of chakras as pulsing points of light and key to health, connection, and spiritual enlightenment
     > * Origin and history of chakra knowledge primarily from ancient India
     > * Chakras and their companions (subtle energies, body, energetic anatomies, kundalini) are explainable through scientific perspectives
9. [**Summary of Fifty Years of Attachment Theory: The Donald Winnicott Memorial Lecture**](summaries/50-years-attachment-theory.md) (54 pages)
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
11. [**Summary of The Psychology Major's Companion**](summaries/Psychology_Majors_Companion.md) (308 Pages)
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
12. [**Summary of The Myth of Redemptive Violence**](summaries/myth-redemptive-violence.md) (5 Pages)
    > - Walter Wink's analysis of the pervasiveness of the belief that violence saves and brings peace in Western culture.
    > - Discussion on how this belief is rooted in ancient mythology and perpetuated through modern media, particularly cartoons.
13. [**Psychology In Your Life**](summaries/Psychology-In-Your-Life.md) (1072 Pages)
    > 1. **Biological Domain**: This domain focuses on the study of biological factors that influence behavior and mental processes. It includes research on genetics, neuroanatomy, physiology, and pharmacology.
    > 2. **Cognitive Domain**: The cognitive domain investigates mental processes such as perception, attention, memory, language, problem-solving, and decision-making.
    > 3. **Developmental Domain**: This domain examines the psychological and physical changes that occur throughout the human lifespan, from infancy to old age. It includes research on cognitive, social, emotional, and moral development.
    > 4. **Social and Personality Domain**: The social and personality domain explores how individuals think about themselves and others, as well as their interactions with other people. It includes research on personality traits, interpersonal relationships, group dynamics, and social influence.
    > 5. **Mental and Physical Health Domain**: This domain focuses on understanding mental health disorders and promoting positive mental and physical health. It includes research on diagnosis, treatment, and prevention of various mental and physical health conditions.


## Additional Resources

* [HuggingFace - Open LLM Leaderboard](https://huggingface.co/spaces/HuggingFaceH4/open_llm_leaderboard)
* [Pressure-tested the most popular open-source LLMs (Large Language Models) for their Long Context Recall abilities](https://www.reddit.com/r/LocalLLaMA/comments/18s61fb/pressuretested_the_most_popular_opensource_llms/) u/ramprasad27 ([Part 2](https://www.reddit.com/r/LocalLLaMA/comments/190r59u/long_context_recall_pressure_test_batch_2/))
  * [LeonEricsson / llmcontext - Pressure testing the context window of open LLMs](https://github.com/LeonEricsson/llmcontext)
* [Chatbox Arena Leaderboard](https://chat.lmsys.org/)
* [LLM Comparison/Test: Ranking updated with 10 new models (the best 7Bs)!](https://www.reddit.com/r/LocalLLaMA/comments/18u122l/llm_comparisontest_ranking_updated_with_10_new/) WolframRavenwolf
  * [LLM Prompt Format Comparison/Test: Mixtral 8x7B Instruct with **17** different instruct templates](https://www.reddit.com/r/LocalLLaMA/comments/18ljvxb/llm_prompt_format_comparisontest_mixtral_8x7b/) WolframRavenwolf
* [Hallucination leaderboard](https://github.com/vectara/hallucination-leaderboard/) Vectara

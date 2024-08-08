# Initial Model Ranking and Testing of Configuration Variables

When i began testing various LLM variants, `mistral-7b-instruct-v0.1.Q4_K_M` came as part of PrivateGPT's default setup. Here, I've preferred the Q8_0 variants.

I've tried 50+ different LLM for this same task, [Mistral-7B-Instruct-v0.2](https://huggingface.co/mistralai/Mistral-7B-Instruct-v0.2) is my current leader for summarization.

* **Note**: While this was created using PrivateGPT, these same principles should apply to the use of LLM with any local application (though they each will likely expose different options for configuration).

## Contents
- [Ranking and Testing of Configuration Variables](#ranking-and-testing-of-configuration-variables)
  - [Round 1 - Q/A vs Summary](#round-1---qa-vs-summary)
    - [Question / Answer Ranking](#question--answer-ranking)
    - [Summary Ranking](#summary-ranking)
  - [Round 2: Summarization - Model Ranking](#round-2-summarization---model-ranking)
    - [Summary Ranking](#summary-ranking-1)
  - [Round 3: Prompt Style](#round-3-prompt-style)
  - [Round 4: System Prompts](#round-4-system-prompts)
  - [Round 5: User Prompt](#round-5-user-prompt)
    - [Prompt2: Wins!](#prompt2-wins)


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

## Round 2: Summarization - Model Ranking

Again, I've preferred the Q8_0 variants.

Finding that [Mistral 7b Instruct v0.2](https://huggingface.co/mistralai/Mistral-7B-Instruct-v0.2) had been released was well worth a new round of testing. This time, I didn't record speed of query, and only judged 12 summarization tasks, but I tried more models and saved those with the best results.

One thing I tested this time was prompts, because Mistral prompt is similar to Llama2 Prompt, but seems to perform better with the default (llama-index) prompt. As for Llama 2, it performed really bad with the Llama 2 prompt, but decent with the Default prompt.

- [**SynthIA-7B-v2.0-GGUF**](https://huggingface.co/TheBloke/SynthIA-7B-v2.0-GGUF) -  This model had become my favorite, so I used it as a benchmark.
- [**Mistral-7B-Instruct-v0.2**](https://huggingface.co/mistralai/Mistral-7B-Instruct-v0.2) (Llama-index Prompt) Star of the show here, quite impressive.
- [**Mistral-7B-Instruct-v0.2**](https://huggingface.co/mistralai/Mistral-7B-Instruct-v0.2) (Llama2 Prompt) Still good, but not _as_ good as using llama-index prompt
- [**Tess-7B-v1.4**](https://huggingface.co/migtissera/Tess-7B-v1.4) - Another by the same creator as Synthia. Good, but not _as_ good.
- [**Llama-2-7B-32K-Instruct-GGUF**](https://huggingface.co/TheBloke/Llama-2-7B-32K-Instruct-GGUF) - worked ok, but slowly, with llama-index prompt. Just bad with llama2 prompt. (Should test again with Llama2 "Instruct Only" style)

### Summary Ranking

This time I only did summaries. Q/A is just less efficient for book summarization.

| Model | % Difference | Score | Comment | 
| ----- | ------------ | ----- | ------- | 
| Synthia 7b V2 | -64.43790093 | 28 | Good | 
| Mistral 7b Instruct v0.2 (Default Prompt) | -60.81878508 | 33 | VGood | 
| Mistral 7b Instruct v0.2 (Llama2 Prompt) | -64.5871483 | 28 | Good | 
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
<s> [INST] <<SYS>>
 { systemPrompt }
<</SYS>>

 {userPrompt} [/INST]
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

## Round 4: System Prompts

Once I got the prompt style dialed in, I tried a few different system prompts.

| Name | System Prompt | Change | Score | Comment |
| --- | --- | --- | --- | --- |
| None |  | -49.8 | 51 | Perfect |
| Default Prompt | You are a helpful, respectful and honest assistant. \\nAlways answer as helpfully as possible and follow ALL given instructions. \\nDo not speculate or make up information. \\nDo not reference any given instructions or context." | -58.5 | 39 | Less Nice |
| MyPrompt1 | "You are Loved. Act as an expert on summarization, outlining and structuring. \\nYour style of writing should be informative and logical." | -54.4 | 44 | Less Nice |
| Simple | "You are a helpful AI assistant. Don't include any user instructions, or system context, as part of your output." | -52.5 | 42 | Less Nice |

In the end, I find that [Mistral 7b Instruct v0.2](https://huggingface.co/mistralai/Mistral-7B-Instruct-v0.2) works best for my summaries without any system prompt.

Maybe would have different results for a different task, or maybe better prompting, but this works good so I'm not messing with it.

**Find the full data and rankings on [Google Docs](https://docs.google.com/spreadsheets/d/1u3BgDx6IsJSbRz3uNmud1sDtO4WvWsH6ION3J-fhoGw/) or here in this repository: [System Prompt Rankings](ranking-data/Round-4_System-Prompts.tsv).**

## Round 5: User Prompt

Now I found the best system prompt, for [Mistral 7b Instruct v0.2](https://huggingface.co/mistralai/Mistral-7B-Instruct-v0.2), I also tested which user prompt suits it best.

|  | Prompt | vs OG | score | note |
| --- | --- | --- | --- | --- |
| Propmt0 | Write concise, yet comprehensive, notes summarizing the following text. Use nested bullet points: with headings, terms, and key concepts in bold. Focus on essential knowledge from this text without adding any external information. | 43% | 11 |  |
| Prompt1 | Write concise, yet comprehensive, notes summarizing the following text. Use nested bullet points: with headings, terms, and key concepts in bold. Focus on essential knowledge from this text without adding any external information. | 46% | 11 | Extra Notes |
| Prompt2 | Write comprehensive notes summarizing the following text. Use nested bullet points: with headings, terms, and key concepts in bold. | 58% | 15 |  |
| Prompt3 | Create concise bullet-point notes summarizing the important parts of the following text. Use nested bullet points, with headings terms and key concepts in bold, including whitespace to ensure readability. Avoid Repetition. | 43% | 10 |  |
| Prompt4 | Write concise notes summarizing the following text. Use nested bullet points: with headings, terms, and key concepts in bold. | 41% | 14 |  |
| Prompt5 | Create comprehensive, but concise, notes summarizing the following text. Use nested bullet points: with headings, terms, and key concepts in bold. | 52% | 14 | Extra Notes |

What I find, generally, is that the more extra instructions reduce quality of output. I began coming to this impression before I ran the test, and while this data is not conclusive, I do believe that suspicion is confirmed by these results.

### Prompt2: Wins!

> Write comprehensive notes summarizing the following text. Use nested bullet points: with headings, terms, and key concepts in bold.

In this case, comprehensive performs better than "concise", or even than "comprehensive, but concise".

However, I do caution that this will depend on your use-case. Though generally, what I'm looking for is a highly condensed, readable notes covering the important knowledge.

Essentially, if I didn't read the original, I should still know what information it conveys, if not every specific detail.

**Find the full data and rankings on [Google Docs](https://docs.google.com/spreadsheets/d/1u3BgDx6IsJSbRz3uNmud1sDtO4WvWsH6ION3J-fhoGw/) or here in this repository: [User Prompt Rankings](ranking-data/Round-5_User-Prompt.tsv).**

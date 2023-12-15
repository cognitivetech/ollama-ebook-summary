# LLM for Book Summarization & Q\A : Walkthrough and Rankings

In this repository I will describe my methods for book summarization using [PrivateGPT](https://docs.privategpt.dev/overview), including a comparison of 6 different models using these methods.

I've searched quite a bit on this topic, and there doesn't seem to be any guide written describing how to use LLM for book summarization, and felt that i could fill a gap by documenting my efforts.

## Contents
- [Contents](#contents)
- [Rankings](#rankings)
  - [Question / Answer Ranking](#question--answer-ranking)
  - [Summary Ranking](#summary-ranking)
- [Overview](#overview)
- [Result](#result)
- [Check out my first complete book summary](#check-out-my-first-complete-book-summary)
- [Walkthrough](#walkthrough)

## Rankings

`mistral-7b-instruct-v0.1.Q4_K_M` comes as part of PrivateGPT's default setup. Here, I've preferred the 8_0 variants.

While I've tried 50+ different LLM for this same task, Mistral-7B-Instruct is still among the best.

For this analysis we will be testing out 5 different LLM for the following tasks:

1. Asking the same 30 questions to a 70 page book chapter.
2. Summarizing that same 70 page book chapter divided into 30 chunks.

#### Find the full data and rankings on [Google Docs](https://docs.google.com/spreadsheets/d/1u3BgDx6IsJSbRz3uNmud1sDtO4WvWsH6ION3J-fhoGw/edit?usp=sharing) or here in this repository [QA Scores](Rankings-QA.csv), [Summary Rankings](Rankings-Summary.csv).

### Question / Answer Ranking
1. [**Hermes Trismegistus Mistral 7b**](https://huggingface.co/TheBloke/Hermes-Trismegistus-Mistral-7B-GGUF) is my overall choice. It's verbose, with some filler, and its a good bullshitter. I can use these results.
2. [**SynthIA 7B**](https://huggingface.co/TheBloke/SynthIA-7B-v2.0-GGUF) is very impressive. I think if you want a little less filler, go here. Some of it was just a little too short and not on target enough for my taste.
3. [**Mistral 7b Instruct v0.1**](https://huggingface.co/TheBloke/Mistral-7B-Instruct-v0.1-GGUF) is an excellent model and surprised its not higher on this list. Only real complaint is the answers are just too short.
4. [**CollectiveCognition v1.1 Mistral 7b**](https://huggingface.co/TheBloke/CollectiveCognition-v1.1-Mistral-7B-GGUF) is quite good. However there is a lot of filler and took the longest amount of time of them all. It scored a bit higher than mistral on quality\usefulness, I think the amount of filler just made it less enjoyable to read.
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


## Method

Rather than feed a 400 page book into any LLM model, splitting it into chapters makes the task more managable. Using [PrivateGPT](https://github.com/imartinez/privateGPT), I've found a number of models that produce good results, and first ran tests with a few models on a single book chapter.

Then I used that information to summarize a complete book, making one run with Hermes Trismegistus Mistral 7B, with a "detailed summary" prompt, and a second run with Synthia 7B v2, using a "Bullet Point" prompt.

## Result

I my first summary of a 539 page book in 5-6 hours!!! (not including first run with Hermes) Incredible!

A few of the api calls didn't go through, but I had my first run with a summary prompt prompting to back up this run. I will say, bullet-point notes are a lot easier to read while editing. 

Some of that run of api calls didn't go perfectly. When necessary I found a missing section in my original summary, and ran it through the bullet point prompting, so I wasn't missing any sections, but could maintain readability.

When I was going to do this manually, it would have taken me over a month.

One thing I was worried about too is plagarism. With the final text containing around 25% of the characters as original, was this going to take me far beyond "fair use" into plagarism land?

![](https://i.imgur.com/xqWNToN.png)

According to [CopyLeaks](https://app.copyleaks.com/) it says my text is only 5.4% plagiarized!!! Considering that this is not for profit, but for educational purposes, I'm going to call that a victory.

## Check out my first complete book summary

* [**Summary of Anodea Judith's Eastern Body Western Mind**](Eastern-Body_Western-Mind_Synthia.md)
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

## Walkthrough

If you are interested in following my steps, in more detail, check out the [walkthrough](walkthrough).
# LLM for Book Summarization & Q\A : Walkthrough and Rankings

In this repository I will describe my methods for book summarization using [PrivateGPT](https://docs.privategpt.dev/overview), including a comparison of 6 different models using these methods.

I've searched quite a bit on this topic, and there doesn't seem to be any guide written describing how to use LLM for book summarization, and felt that i could fill a gap, by documenting my efforts.

## Contents

- [Rankings](#rankings)
  - [Question / Answer Ranking](#question--answer-ranking)
  - [Summary Rankings](#summary-ranking)
- [Guide](#guide)
  - [Disclaimer](#disclaimer)
  - [Background](#background)
  - [Walkthrough](#walkthrough)

## Rankings

`mistral-7b-instruct-v0.1.Q4_K_M` comes as part of PrivateGPT's default setup. Here, I've preferred the 8_0 variants.

While I've tried 50+ different LLM for this same task, Mistral-7B-Instruct is still among the best.

For this analysis we will be testing out 5 different LLM for the following tasks:

1. Asking the same 30 questions to a 70 page book chapter.
2. Summarizing that same 70 page book chapter divided into 30 chunks.

#### Find the full data and rankings on [Google Docs](https://docs.google.com/spreadsheets/d/1u3BgDx6IsJSbRz3uNmud1sDtO4WvWsH6ION3J-fhoGw/edit?usp=sharing) or here in this repository [QA Scores](Scores-QA.csv), [Summary Scores](Scores-Summary.csv).

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

## Guide
### Disclaimer

These models are not deterministic, and may provide unpredictable results.

If you are running privateGPT from the UX, these same queries will take longer because of the chat history is included in the context.

### Background
#### System
If you have a good CPU, some of these models will work using Q4_K_M or Q5_K_M variants. But can take a few minutes per query.

I'm running this project at home using an RTX 3060. Each answer typically takes a minute or less from the GUI.

#### Overview

Rather than feed a 400 page book into any LLM model, splitting it into chapters makes the task more managable. Using [PrivateGPT](https://github.com/imartinez/privateGPT), I've found a number of models that produce good results when asking questions on a 60 page book-chapter.

In this project, I'll prepare a whole chapter for query\summarization, and then use a shell script to submit the same queries to the models selected for comparison.

#### Backend
Roughly speaking, PrivateGPT splits your document into chunks which are "tagged" and stored in a database. 

Based upon your query, the LLM searches through those chunks to find the most relevant content, and elaborates upon that. 

One way we'll be judging the models is by how much of its response comes from targeted pages.

I've edited PrivateGPT source:
- to use 4 chuncks, per query, vs 2 which is default.
- to generate up to 512 tokens per query, vs 256 which is default

#### Objective
Our results will show the difference between asking questions to a database, vs to specific sections of text. Each has its strengths, and different models will likely show strengths in one vs the other.

I want to learn the personality of these models which have stood out among the rest, and find out which are best suited to which tasks.

### Walkthrough
#### Step One - Chapterize Book

https://github.com/torakiki/sejda

Great thing about Sejda is that its open source, and has a free web version avaialable. And you don't have to read my hacky code :D

https://www.sejda.com/split-pdf-by-outline

#### Step Two - Prepare book for query and summarization.

I'm using [Calibre](https://calibre-ebook.com/) and [VS Code](https://code.visualstudio.com/).

`ebook-convert file.pdf file.txt`

For this demonstration I'm using a chapter from a book that comparing the chakra system with western psychology: Eastern Body, Western Mind: Psychology and the Chakra System, by Anodea Judith.

Now I've pulled into VSCode, the text version of the chapter and am selecting sections I want summarized. I compressing them to a single line by selecting sections and using regex search replace to change new lines into a space (`\n` -> ` ` ).

All in all I've split a 73 page, 30k token, book chapter into 31 chunks of text, leaving an average of 850 tokens per query.

I've also written 30 questions, one for each sub-heading within the chapter.

#### Step Three - Prepare data for automation.

I will make two different type of JSON objects, depending on the type of query.

##### Question
Note I have set Include Sources, as well as Use Context so the questions are asked to the document already ingested, and we learn which sources were used.

```json
{
  "include_sources": true,
  "prompt": "What are the basic issues of the fourth chakra",
  "stream": false,
  "use_context": true
}
```
##### Summary
I've also made a file that breaks the entire chapter into 31 json objects just like shown below.

```json
{
  "include_sources": false, "prompt": "Write a paragraph based on the following: Finding the Balance in Love FOURTH CHAKRA AT A GLANCE ELEMENT Air NAME Anahata (unstruck) PURPOSES Love Balance ISSUES Love Balance Self-love Relationship Intimacy Anima/animus Devotion Reaching out and taking in COLOR Green LOCATION Chest, heart, cardiac plexus IDENTITY Social ORIENTATION Self-acceptance Acceptance of others DEMON Grief DEVELOPMENTAL STAGE 4 to 7 years DEVELOPMENTAL TASKS Forming peer and family relationships Developing persona BASIC RIGHTS To love and be loved BALANCED CHARACTERISTICS Compassionate Loving Empathetic Self-loving Altruistic Peaceful, balanced Good immune system TRAUMAS AND ABUSES Rejection, abandonment, loss Shaming, constant criticism Abuses to any other chakras, especially lower chakras Unacknowledged grief, including parents’ grief Divorce, death of loved one Loveless, cold environment Conditional love Sexual or physical abuse Betrayal DEFICIENCY Antisocial, withdrawn, cold Critical, judgmental, intolerant of self or others Loneliness, isolation Depression Fear of intimacy, fear of relationships Lack of empathy Narcissism EXCESS Codependency Poor boundaries Demanding Clinging Jealousy Overly sacri cing PHYSICAL MALFUNCTIONS Disorders of the heart, lungs, thymus, breasts, arms Shortness of breath Sunken chest Circulation problems Asthma Immune system de ciency Tension between shoulder blades, pain in chest HEALING PRACTICES Breathing exercises, pranayama Work with arms, reaching out, taking in Journaling, self-discovery Psychotherapy Examine assumptions about relationships Emotional release of grief Forgiveness when appropriate Inner child work Codependency work Self-acceptance Anima-animus integration AFFIRMATIONS I am worthy of love. I am loving to myself and others. There is an in nite supply of love. I live in balance with others.", "stream": false, "use_context": false
}
```

#### Step Four - Write Shell Script

I've minified those json objects [so they are on one line each](script/q.json), and will now submit them to my models for testing and analysis.
 
##### Questions
```bash
cat q.json | while read line
do
  echo $line | jq .
  curl -d "$line" -H 'Content-Type: application/json' http://0.0.0.0:8001/v1/completions | jq .
done
```

##### Summaries

```bash
cat sum.json | while read line
do
  echo $line | jq .
  curl -d "$line" -H 'Content-Type: application/json' http://0.0.0.0:8001/v1/completions | jq .
done
```

#### Step Five - Start PrivateGPT and Begin Testing

`PGPT_PROFILES=local make run`

In another window I run my [script](script):

`./bash.sh`

##### mistral-7b-instruct-v0.1.Q8_0.gguf 

Our first answer complete in two seconds!

```json
{
  "id": "60831830-121f-46e4-858c-941acde05aa6",
  "object": "completion",
  "created": 1702201732,
  "model": "private-gpt",
  "choices": [
    {
      "finish_reason": "stop",
      "delta": null,
      "message": {
        "role": "assistant",
        "content": " The basic issues of the fourth chakra include balance, love, self-reflection, self-acceptance, relationship, intimacy, anima/animus, eros/thanatos, grief, and compassion."
      },
      "sources": [
        {
          "object": "context.chunk",
          "score": 0.8444509774575022,
          "document": {
            "object": "ingest.document",
            "doc_id": "73b15bfe-b786-422f-8a44-41b3a1840fa5",
            "doc_metadata": {
              "window": "Like\nthe green, growing plants, which push toward the heavens from\ntheir roots in the earth, we, too, reach outward in two directions—\nanchoring the manifesting current deep in our bodies and expanding\nthe liberating current as we reach beyond ourselves.  In the heart\nchakra, these currents come to perfect balance in the center of our\nbeing.  From that sacred center—the heart of the system—we enter\nthe mystery of love.\n The basic issues that we encounter in the heart chakra deal with\nbalance, love, and relationship .  Through balance we \u0000nd a center\nfrom which we can love, through love we form relationships, and\nthrough relationships we have the opportunity to transform the self-\ncentered ego of the lower chakras into awareness of the larger realm\nin which we are embedded.",
              "original_text": "The basic issues that we encounter in the heart chakra deal with\nbalance, love, and relationship . ",
              "page_label": "10",
              "file_name": "10-Chakra Four.pdf",
              "doc_id": "73b15bfe-b786-422f-8a44-41b3a1840fa5"
            }
          },
          "text": "Like\nthe green, growing plants, which push toward the heavens from\ntheir roots in the earth, we, too, reach outward in two directions—\nanchoring the manifesting current deep in our bodies and expanding\nthe liberating current as we reach beyond ourselves.  In the heart\nchakra, these currents come to perfect balance in the center of our\nbeing.  From that sacred center—the heart of the system—we enter\nthe mystery of love.\n The basic issues that we encounter in the heart chakra deal with\nbalance, love, and relationship .  Through balance we \u0000nd a center\nfrom which we can love, through love we form relationships, and\nthrough relationships we have the opportunity to transform the self-\ncentered ego of the lower chakras into awareness of the larger realm\nin which we are embedded.",
          "previous_texts": null,
          "next_texts": null
        },
        {
          "object": "context.chunk",
          "score": 0.8391257615891241,
          "document": {
            "object": "ingest.document",
            "doc_id": "b89370a0-1eb4-4e97-ac38-26955ac90a54",
            "doc_metadata": {
              "window": "Without\nlove, there is no binding force to hold our world together.  Without\nlove, there is no integration but instead dis-integration.  Without\nlove, our Rainbow Bridge collapses in the middle and we fall into\nthe chasm of separation below.\n        UNFOLDING THE PETALS\nBASIC ISSUES OF THE FOURTH CHAKRA\nLove\nBalance\nSelf-Re\u0000ection\nSelf-Acceptance\nRelationship\nIntimacy\nAnima/Animus\nEros/Thanatos\nGrief\nCompassion",
              "original_text": "UNFOLDING THE PETALS\nBASIC ISSUES OF THE FOURTH CHAKRA\nLove\nBalance\nSelf-Re\u0000ection\nSelf-Acceptance\nRelationship\nIntimacy\nAnima/Animus\nEros/Thanatos\nGrief\nCompassion",
              "page_label": "9",
              "file_name": "10-Chakra Four.pdf",
              "doc_id": "b89370a0-1eb4-4e97-ac38-26955ac90a54"
            }
          },
          "text": "Without\nlove, there is no binding force to hold our world together.  Without\nlove, there is no integration but instead dis-integration.  Without\nlove, our Rainbow Bridge collapses in the middle and we fall into\nthe chasm of separation below.\n        UNFOLDING THE PETALS\nBASIC ISSUES OF THE FOURTH CHAKRA\nLove\nBalance\nSelf-Re\u0000ection\nSelf-Acceptance\nRelationship\nIntimacy\nAnima/Animus\nEros/Thanatos\nGrief\nCompassion",
          "previous_texts": null,
          "next_texts": null
        },
        {
          "object": "context.chunk",
          "score": 0.8240340522107765,
          "document": {
            "object": "ingest.document",
            "doc_id": "90849b7f-26aa-40f7-afd7-3e583591fc47",
            "doc_metadata": {
              "window": "A child enters school, chooses friends, and tries out these behavior\nprograms in the world outsid e the family.  The child learn s whether\nshe is well-liked or rejected, and thus her social identity gets added\non to her ego identity as a new basis for self-esteem.  It is interesting\nthat the most common time for imaginary playmates occurs between\nages four and six, as if this were a practice realm  for real\nrelationships.\n Since relationships are the formative ground for fourth chakra\ndevelopment, it is important to ask some basic questions.  Do\nrelationships in the family depend on aggressive \u0000ghting for one’s\nrights?  Do they depend on giving up oneself to avoid punishment or\nrejection? ",
              "original_text": "Since relationships are the formative ground for fourth chakra\ndevelopment, it is important to ask some basic questions. ",
              "page_label": "36",
              "file_name": "10-Chakra Four.pdf",
              "doc_id": "90849b7f-26aa-40f7-afd7-3e583591fc47"
            }
          },
          "text": "A child enters school, chooses friends, and tries out these behavior\nprograms in the world outsid e the family.  The child learn s whether\nshe is well-liked or rejected, and thus her social identity gets added\non to her ego identity as a new basis for self-esteem.  It is interesting\nthat the most common time for imaginary playmates occurs between\nages four and six, as if this were a practice realm  for real\nrelationships.\n Since relationships are the formative ground for fourth chakra\ndevelopment, it is important to ask some basic questions.  Do\nrelationships in the family depend on aggressive \u0000ghting for one’s\nrights?  Do they depend on giving up oneself to avoid punishment or\nrejection? ",
          "previous_texts": null,
          "next_texts": null
        },
        {
          "object": "context.chunk",
          "score": 0.8224758550171385,
          "document": {
            "object": "ingest.document",
            "doc_id": "cab96e6d-d081-4b21-bff3-d514d83cfeab",
            "doc_metadata": {
              "window": "within ourselv es and others.  We do not know what real love looks\nlike or how to create it.\n The following suggestions only scratch the surface of this vast\nsubject, but give you a place to begin.\n THE TASK OF SELF-ACCEPTANCE\nIn order to love, there has to be someone home inside.  As we open\nup to the more universal elements of love, it is easy to forget to\nhonor each other’s individua lity. ",
              "original_text": "The following suggestions only scratch the surface of this vast\nsubject, but give you a place to begin.\n",
              "page_label": "62",
              "file_name": "10-Chakra Four.pdf",
              "doc_id": "cab96e6d-d081-4b21-bff3-d514d83cfeab"
            }
          },
          "text": "within ourselv es and others.  We do not know what real love looks\nlike or how to create it.\n The following suggestions only scratch the surface of this vast\nsubject, but give you a place to begin.\n THE TASK OF SELF-ACCEPTANCE\nIn order to love, there has to be someone home inside.  As we open\nup to the more universal elements of love, it is easy to forget to\nhonor each other’s individua lity. ",
          "previous_texts": null,
          "next_texts": null
        }
      ],
      "index": 0
    }
  ]
}
```

# How to use LLM \ GPT for book summarization

In this repository I will describe my methods for book summarization using [PrivateGPT](https://docs.privategpt.dev/overview), including a comparison of 6 different models using these methods.

### Models
In order of generally how well I expect them to do.

- mistral-7b-instruct-v0.1.Q8_0.gguf 
- hermes-trismegistus-mistral-7b.Q8_0.gguf 
- collectivecognition-v1.1-mistral-7b.Q8_0.gguf 
- kai-7b-instruct.Q8_0.gguf 
- synthia-7b-v2.0.Q8_0.gguf
- llama-2-7b-32k-instruct.Q8_0.gguf 

`mistral-7b-instruct-v0.1.Q4_K_M` comes as part of PrivateGPT's default setup. Small enough to run on a CPU, and really good quality, considering. However, that won't be strong enough to make a task like this efficient. 

While I've tried 50+ different LLM for this same task, I'm not sure I've found any that fit my RTX 3060 that do better than Mistral-7B-Instruct at a similar speed.

### System
If you have a good CPU, some of these models will work using Q4_K_M or Q5_K_M variants. But can take a few minutes per query.

I'm running this project at home using an RTX 3060. Each question typically takes a minute or less.

### Method
I've searched quite a bit on this topic, and there doesn't seem to be any guide written describing how to use LLM for book summarization. I've found tools and determined methods to do this, and felt like i could fill a gap, by documenting my efforts and making a comparison of different models using this method.

### Overview

Rather than feed a 400 page book into any LLM model, splitting it into chapters makes the task more managable. Using PrivateGPT, I've found a number of models that producing good results, when asking questions to a 60 page book-chapter.

In this project, I'll prepare a whole chapter for query\summarization, and then use a shell script to submit the same queries to 6 models I've selected for comparison.

### Process

Roughly speaking, PrivateGPT splits your document into chunks which are "tagged" and stored in a database. 

Based upon your query, the LLM searches through those chunks to find the most relevant content, and elaborates upon that. 

One way we'll be judging the models is by how much of its response comes from targeted pages.

I've edited PrivateGPT source:
- to use 4 chuncks, per query, vs 2 which is default.
- to generate up to 512 tokens per query, vs 256 which is default

Some sections aren't easy to formulate a question for, and i decided to also chunk the chapter manually and have summaries prepared based on the specific context I'm targeting.

### Objective

Our results will show the difference between asking questions to a database, vs to specific sections of text. Each has its strengths, and different models will likely show strengths in one vs the other.

I want to learn the personality of these models which have stood out among the rest, and find out which are best suited to which tasks.

## Process

Here is the process I've undertaken, to perform this analsys.

### Step One - Chapterize Book

Well, I was using a hacky script to pull page ranges of bookmarks from PDF, and then use pdftk with that information.. but I lost that script in the shuffle, and then found this neat tool, Sejda.

https://github.com/torakiki/sejda

Great thing about Sejda is that its open source, and has a free web version avaialable. And you don't have to read\run my hacky code :D

https://www.sejda.com/split-pdf-by-outline

### Step Two - Prepare book for query and summarization.

I'm using Calibre and VS Code.

`ebook-convert file.pdf file.txt`

For this demonstration I'm using a chapter from a book making a synthesis of the chakra system with western psychology: Eastern Body, Western Mind: Psychology and the Chakra System, by Anodea Judith.

Now I've pulled into VSCode, the text version of the chapter and am selecting sections I want summarized, adn compressing them to one line by selecting sections of text using regex search replace, changing two new lines into a space (`\n` -> ` ` ).

I've also written questions for each sub-heading within the chapter.

In all I've split a 73 page, 30k token, book chapter into 35 lines of text, and written 30 questions. Leaving an average of 850 tokens per query.

This is going to be a lot of data for comparison, so perhaps we'll only compare a sub-seection of results... but ultimately I am demonstrating the level of precision used for this task.

### Step Three - Prepare data for automation.

I will make two different type of JSON objects, depending on the type of query.

### Question

Note I have set Include Sources, as well as Use Context so the questions are asked to the document already ingested, and we learn which sources were used.

```json
{
  "include_sources": true,
  "prompt": "What are the basic issues of the fourth chakra",
  "stream": false,
  "use_context": true
}
```

### Step Four - Write Shell Script

I've minified those json objects so they are on one line each, and will now submit them to my models for testing and analysis.

### Questions
```bash
cat q.json | while read line
do
  echo $line | jq .
  curl -d "$line" -H 'Content-Type: application/json' http://0.0.0.0:8001/v1/completions | jq .
done
```

### Summaries

```bash
cat sum.json | while read line
do
  echo $line | jq .
  curl -d "$line" -H 'Content-Type: application/json' http://0.0.0.0:8001/v1/completions | jq .
done
```

### Step Five - Start PrivateGPT and Begin Testing

Lets begin with the default Mistral 7b Instruct, which I think performs the best overall. Some seem to give better results in certain circumstances, but don't produce consistent results.

Any I've found that seem to perform better, also seem to hallucinate more often. Perhaps as creativity increases, accuracy is impacted.

### mistral-7b-instruct-v0.1.Q8_0.gguf 

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

### Step Six - Prepare for Consumption and Analysis.

I'll save you the nitty gritty of it, but be assured this is the longest part of the process.

## Analysis

To Be Continued....
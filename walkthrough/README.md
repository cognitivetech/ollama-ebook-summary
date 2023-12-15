# Walkthrough
- [Disclaimer](#disclaimer)
- [System](#system)
- [Step One - Chapterize Book](#step-one---chapterize-book)
- [Step Two - Prepare book for query and summarization.](#step-two---prepare-book-for-query-and-summarization)
- [Step Three - Prepare data for automation.](#step-three---prepare-data-for-automation)
- [Step Four - Write Shell Script](#step-four---write-shell-script)
- [Step Five - Start PrivateGPT and Begin Testing](#step-five---start-privategpt-and-begin-testing)
- [Making my first complete book summary](#making-my-first-complete-book-summary)
- [Prompting](#prompting)

## Disclaimer

These models are not deterministic, and may provide unpredictable results.

If you are running privateGPT from the UX, these same queries will take longer because of the chat history is included in the context.

## System
If you have a good CPU, some of these models will work using Q4_K_M or Q5_K_M variants. But can take a few minutes per query.

I'm running this project at home using an RTX 3060 12GB. Each answer typically takes a minute or less from the GUI.

## Step One - Chapterize Book

https://github.com/torakiki/sejda

Great thing about Sejda is that its open source, and has a free web version avaialable. And you don't have to read my hacky code :D

https://www.sejda.com/split-pdf-by-outline

## Step Two - Prepare book for query and summarization.

I'm using [Calibre](https://calibre-ebook.com/) and [VS Code](https://code.visualstudio.com/).

`ebook-convert file.epub file.txt --enable-heuristics --disable-markup-chapter-headings --disable-delete-blank-paragraphs  --disable-unwrap-lines`

The above command performs much better on the `epub` vs `pdf` for producing a clean output preserving formating and not adding tons of line-breaks. 

All the same, I'm still building up an array of regex commands to run in a sed script, because that won't always be an option.

Check this link, you might do better than me, even.

https://manual.calibre-ebook.com/conversion.html#heuristic-processing

### For this demonstration 

I'm using a chapter from a book that comparing the chakra system with western psychology: [Eastern body, Western mind : psychology and the chakra system as a path to the self](https://www.amazon.com/Eastern-Body-Western-Mind-Psychology/dp/1587612259/?&tag=cognitivetech-20), by Anodea Judith.

Now I've pulled into VSCode, the text version of the chapter and am selecting sections I want summarized. I compressing them to a single line by selecting sections and using the "join lines" function, that I've mapped to a convenient key combo.

All in all I've split a 73 page, 30k token, book chapter into 31 chunks of text, leaving an average of 850 tokens per query.

I've also written 30 questions, one for each sub-heading within the chapter.

## Step Three - Prepare data for automation.

I will make two different type of JSON objects, depending on the type of query.

#### Question
Note I have set Include Sources, as well as Use Context so the questions are asked to the document already ingested, and we learn which sources were used.

```json
{
  "include_sources": true,
  "prompt": "What are the basic issues of the fourth chakra",
  "stream": false,
  "use_context": true
}
```
#### Summary
I've also made a file that breaks the entire chapter into 31 json objects just like shown below.

```json
{
  "include_sources": false, "prompt": "Write a paragraph based on the following: Finding the Balance in Love FOURTH CHAKRA AT A GLANCE ELEMENT Air NAME Anahata (unstruck) PURPOSES Love Balance ISSUES Love Balance Self-love Relationship Intimacy Anima/animus Devotion Reaching out and taking in COLOR Green LOCATION Chest, heart, cardiac plexus IDENTITY Social ORIENTATION Self-acceptance Acceptance of others DEMON Grief DEVELOPMENTAL STAGE 4 to 7 years DEVELOPMENTAL TASKS Forming peer and family relationships Developing persona BASIC RIGHTS To love and be loved BALANCED CHARACTERISTICS Compassionate Loving Empathetic Self-loving Altruistic Peaceful, balanced Good immune system TRAUMAS AND ABUSES Rejection, abandonment, loss Shaming, constant criticism Abuses to any other chakras, especially lower chakras Unacknowledged grief, including parents’ grief Divorce, death of loved one Loveless, cold environment Conditional love Sexual or physical abuse Betrayal DEFICIENCY Antisocial, withdrawn, cold Critical, judgmental, intolerant of self or others Loneliness, isolation Depression Fear of intimacy, fear of relationships Lack of empathy Narcissism EXCESS Codependency Poor boundaries Demanding Clinging Jealousy Overly sacri cing PHYSICAL MALFUNCTIONS Disorders of the heart, lungs, thymus, breasts, arms Shortness of breath Sunken chest Circulation problems Asthma Immune system de ciency Tension between shoulder blades, pain in chest HEALING PRACTICES Breathing exercises, pranayama Work with arms, reaching out, taking in Journaling, self-discovery Psychotherapy Examine assumptions about relationships Emotional release of grief Forgiveness when appropriate Inner child work Codependency work Self-acceptance Anima-animus integration AFFIRMATIONS I am worthy of love. I am loving to myself and others. There is an in nite supply of love. I live in balance with others.", "stream": false, "use_context": false
}
```

## Step Four - Write Shell Script

I've minified those json objects [so they are on one line each](script/q.json), and will now submit them to my models for testing and analysis.
 
#### Questions
```bash
cat q.json | while read line
do
  echo $line | jq .
  curl -d "$line" -H 'Content-Type: application/json' http://0.0.0.0:8001/v1/completions | jq .
done
```

#### Summaries

```bash
cat sum.json | while read line
do
  echo $line | jq .
  curl -d "$line" -H 'Content-Type: application/json' http://0.0.0.0:8001/v1/completions | jq .
done
```

## Step Five - Start PrivateGPT and Begin Testing

`PGPT_PROFILES=local make run`

In another window I run my [script](script):

`./bash.sh`

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

## Making my first complete book summary

Using above methods I learned how each model responds and began to do my first complete summary.

I chopped a 535 page book, into 199 sections, most less than 10000 characters, and surrounded those sections in JSON objects.

Initially I thought I would prefer [Hermes Trismegistus Mistral 7b](https://huggingface.co/TheBloke/Hermes-Trismegistus-Mistral-7B-GGUF), because it made the most verbose output giving me something to work with. 

Ultimately, I decided to use [SynthIA 7B](https://huggingface.co/TheBloke/SynthIA-7B-v2.0-GGUF) because it is _less_ verbose, but still quite detailed. I also noticed that it always created less output than given, compared to Hermes Trismegistus, that will sometimes generate more content than given.

I would like to create summaries that contain 20% or less textual volume vs the original.

I also decided to be more particular about how sections are grouped, but I try to not group less than 3500 characters, preferring 7000-9000 characters per selection.

### Prompting

My first round of testing used a quite naive instruction: `Generate a detailed summary of the following: `, with whatever is the llama2 default system prompt.

After I split the book, a second time, into more intentional selections, I decided to try out a new prompt.

#### System Prompt

PrivateGPT just exposed the ability to change its system prompt, so now I'm using this:

```yaml
You are Loved. Act as an expert on summarization, outlining and structuring. 
Your style of writing should be informative and logical.
```
#### Instructions 

```yaml
Create bullet-point notes summarizing the important parts of the following text. Vocabulary terms and key concepts should be marked in bold. Focus only on essential information, without adding any extra thoughts. TEXT: ```{content}```
```

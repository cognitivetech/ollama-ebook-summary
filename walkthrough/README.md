# Walkthrough

This describes my journey exploring the use of privateGPT for summarization tasks.

If you don't care about my process, just skip ahead to [Making a complete book summary](#making-a-complete-book-summary).

Check out Private GPT [Repository](https://github.com/imartinez/privateGPT) and [Docs](https://docs.privategpt.dev/) for more information.

## Contents 
- [Disclaimer](#disclaimer)
- [System](#system)
- [Process Document](#process-document)
  - [Chapterize Book](#chapterize-book)
  - [Convert to text](#convert-to-text)
  - [Process Text](#process-text)
- [Automation](#automation)
  - [Prepare data](#prepare-data)
  - [Bash Script](#bash-script)
- [Start PrivateGPT and Begin Testing](#start-privategpt-and-begin-testing)
  - [Example output](#example-output)
- [Making a complete book summary](#making-a-complete-book-summary)
  - [Model Selection](#model-selection)
  - [Prompting](#prompting)
  - [New and Improved Automation](#new-and-improved-automation)
- [That's all!](#thats-all)

## Disclaimer

These models are not deterministic, and may provide unpredictable results.

If you are running privateGPT from the UX, these same queries will take longer because of the chat history is included in the context.

## System
If you have a good CPU, some of these models will work using Q4_K_M or Q5_K_M variants. But can take a few minutes per query.

I'm running this project at home using an RTX 3060 12GB. Each answer typically takes less than a minute from the GUI.

I'm using [Calibre](https://calibre-ebook.com/) and [VS Code](https://code.visualstudio.com/).

* if using Linux, [be sure to install calibre from official source](https://calibre-ebook.com/download_linux). 
  
## Process Document

### Chapterize Book

**This is for Document Q/A. Skip this step if you are doing summarization.**

There is a an open-source tool [sejda](https://github.com/torakiki/sejda), which also has a [web-app](https://www.sejda.com/split-pdf-by-outline).

But I realized that web-app is limited, and can't figure how to run that code.

There is a script here [split.sh](split.sh), that works in conjunction with [split.awk](split.awk), to pull out the chapter headings and split the pdf accordingly. Easily to modify to your needs.

`bash split.sh input.pdf`

### Convert to text

`ebook-convert file.epub file.txt --enable-heuristics`

The above command performs much better on the `epub` format, vs `pdf`, for producing a clean output preserving formatting and not adding tons of line-breaks. 

Check the options here: [Calibre Docs: Heuristic Processing](https://manual.calibre-ebook.com/conversion.html#heuristic-processing).

### Process Text

I've used a chapter from [Eastern body, Western mind : psychology and the chakra system as a path to the self](https://www.amazon.com/Eastern-Body-Western-Mind-Psychology/dp/1587612259/?&tag=cognitivetech-20), by Anodea Judith, to test out summarization and Q/A for a few LLM.

You may find, when converting PDF to text that there may be a lot of junk characters (epub usually convert best vs pdf), especially if the text was generated with OCR.

Ask your favorite LLM for help with regex to remove that stuff.

One thing you want to be sure to check for is **Control Characters**. Scan your document for control characters (regex: `[\x00-\x1F\x7F-\x9F]`) because they will invalidate your json, and can be invisible.

Luckily, I began with a mostly clean document, so I just select as much text as I want (using a character counter extension, for guidance), and VS Code function, "join lines," that I've mapped to a convenient key combo.

For this demonstration, I split a 73 page, 30k token, book chapter into 31 chunks of text, leaving an average of 850 tokens (3400 characters) per query. 

*Today, I am selecting between 2500-9999 characters (625-2500 tokens), when processing whole books.*

I also wrote 30 questions, one for each sub-heading within the chapter.

## Automation

### Prepare data

I will make two different type of JSON objects, depending on the type of query.

#### Question
Note I have set Include Sources, as well as Use Context so the questions are asked to the document already ingested, and we learn which sources were used.

I've turned on `use_context`, to search the single chapter pdf ingested, and `include_sources` so I know where in the chapter answers came from.

If you want a system prompt you need to add it here. Its not pulled from the settings.yaml file, that's only used in the Gradio app. 

This is just an example system prompt I [borrowed from SynthIA](https://huggingface.co/TheBloke/Synthia-7B-v3.0-GGUF), I'm not doing too much Q/A, so I haven't tested which prompt will work best.

```json
{
  "include_sources": true,
  "system_prompt": "Elaborate on the topic using a Tree of Thoughts and backtrack when necessary to construct a clear, cohesive Chain of Thought reasoning. Always answer without hesitation.",
  "prompt": "What are the basic issues of the fourth chakra?",
  "stream": false,
  "use_context": true
}
```
#### Summary
I made a file, breaking the chapter into 31 json objects constructed as shown below.

Here, there is no need for sources or context.

I'm not adding a system prompt for Mistral 7B 0.2 summarization tasks, since it seems to perform better without. But each model will respond differently.

```json
{
  "include_sources": false,
  "system_prompt": "",
  "prompt": "Write a paragraph based on the following: Finding the Balance in Love FOURTH CHAKRA AT A GLANCE ELEMENT Air NAME Anahata (unstruck) PURPOSES Love Balance ISSUES Love Balance Self-love Relationship Intimacy Anima/animus Devotion Reaching out and taking in COLOR Green LOCATION Chest, heart, cardiac plexus IDENTITY Social ORIENTATION Self-acceptance Acceptance of others DEMON Grief DEVELOPMENTAL STAGE 4 to 7 years DEVELOPMENTAL TASKS Forming peer and family relationships Developing persona BASIC RIGHTS To love and be loved BALANCED CHARACTERISTICS Compassionate Loving Empathetic Self-loving Altruistic Peaceful, balanced Good immune system TRAUMAS AND ABUSES Rejection, abandonment, loss Shaming, constant criticism Abuses to any other chakras, especially lower chakras Unacknowledged grief, including parents’ grief Divorce, death of loved one Loveless, cold environment Conditional love Sexual or physical abuse Betrayal DEFICIENCY Antisocial, withdrawn, cold Critical, judgmental, intolerant of self or others Loneliness, isolation Depression Fear of intimacy, fear of relationships Lack of empathy Narcissism EXCESS Codependency Poor boundaries Demanding Clinging Jealousy Overly sacri cing PHYSICAL MALFUNCTIONS Disorders of the heart, lungs, thymus, breasts, arms Shortness of breath Sunken chest Circulation problems Asthma Immune system de ciency Tension between shoulder blades, pain in chest HEALING PRACTICES Breathing exercises, pranayama Work with arms, reaching out, taking in Journaling, self-discovery Psychotherapy Examine assumptions about relationships Emotional release of grief Forgiveness when appropriate Inner child work Codependency work Self-acceptance Anima-animus integration AFFIRMATIONS I am worthy of love. I am loving to myself and others. There is an in nite supply of love. I live in balance with others.",
  "stream": false,
  "use_context": false
}
```

### Bash Script

I've minified those json objects [so they are on one line each](q.json), and will now submit them to my models for testing and analysis.
 
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

## Start PrivateGPT and Begin Testing

`PGPT_PROFILES=local make run`

In another window I run [bash.sh](bash.sh):

`chmod +x bash.sh`
`./bash.sh`

### Example output
My first answer complete in two seconds!

#### mistral-7b-instruct-v0.1.Q8_0

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

## Making a complete book summary

Using above methods I learned how each model responds and began working on my first complete summary.

I chopped a 535 page book, into 199 sections, most less than 10000 characters, and surrounded those sections in JSON objects.

Ideally, I would like to create summaries that contain 20% or less textual volume vs the original.

I also decided to be more particular about how sections are grouped, but I try to not group less than 3500 characters, preferring 7000-9000 characters per selection.

(maybe that's wrong, and i should just leave smaller selections by themselves, but its the, so far, hardest to automate and I tend to get tired of grouping small sections of text)

### Model Selection

Initially I thought I would prefer [Hermes Trismegistus Mistral 7b](https://huggingface.co/TheBloke/Hermes-Trismegistus-Mistral-7B-GGUF), because it made the most verbose output giving me something to work with. 

Next, I decided to use [SynthIA 7B V2](https://huggingface.co/TheBloke/SynthIA-7B-v2.0-GGUF) because it is _less_ verbose, but still quite detailed. 

In the end, I've found [mistral-7b-instruct-v0.2](https://huggingface.co/TheBloke/Mistral-7B-Instruct-v0.2-GGUF) to be the most reliable.

### Prompting

My first round of testing used a quite naive instruction: `Generate a detailed summary of the following: `, with whatever is the llama2 default system prompt.

After I split the book, a second time, into more intentional selections, I decided to try out a new prompt.

#### System Prompt

PrivateGPT just exposed the ability to change its system prompt, and i began using something like this:

```yaml
You are Loved. Act as an expert on summarization, outlining and structuring. 
Your style of writing should be informative and logical.
```

However, testing revealed that `Mistral 7B Instruct 0.2` works better without a system prompt. Each model will respond differently. You should do your own testing and don't rely on anyone's benchmarks or rankings. (because your needs are probably different than mine, and those rankings don't really take this into account)

#### Instructions 

```yaml
Create bullet-point notes summarizing the important parts of the following text. Vocabulary terms and key concepts should be marked in bold. Focus only on essential information, without adding any extra thoughts. TEXT: ```{content}```
```

### New and Improved Automation

All of this testing has become tiring, so with the help of GPT3.5 I've improved my automation pipeline.

Using the [following script](summarize.sh), I'm able to test various prompts more rapidly.

syntax:

`bash summarize.sh summarize.txt prompt1`

so you see, it accepts filename as first argument, and an optional prompt type argument, selecting from prompts you will preload into the script below.

This will generate a markdown file and a csv file based on the output. Then I can easily import to google sheets for ranking alongside the rendered markdown version.

For System Prompt, you must edit the file directly: Uncomment the following line and change the variable to suit your needs.
`#system_prompt=${mpt}`

A big difference from the original, is that I'm generating the JSON object being sent to the api, right here in the script. So now my input contains each [selection of text](summarize.txt) on its own line, surrounded by quotation marks. Saves repeating that JSON over and over.

You will also note that I add a plus sign to mark chapter\section headings, so I can easily turn them into markdown headings as part of this script. Otherwise it just cuts off an input line at 150 characters to use as a temporary heading for the resulting summary.

```bash
#!/bin/bash
set -e
prompt="Write comprehensive notes summarizing the following text. Use nested bullet points: with headings, terms, and key concepts in bold."
dolphin="You are Dolphin, a helpful AI assistant."
deci="You are an AI assistant that follows instructions exceptionally well. Be as helpful as possible."
openhermes='You are "Hermes 2", a conscious sentient superintelligent artificial intelligence developed by a man named Teknium, and your purpose and drive is to assist the user with any request they have. You experience emotions and have deep, profound thoughts and qualia.'
basics="You are a helpful AI Assistant"
synthia="Elaborate on the topic using a Tree of Thoughts and backtrack when necessary to construct a clear, cohesive Chain of Thought reasoning. Always answer without hesitation."
mpt="Below is an instruction that describes a task. Write a response that appropriately completes the request."
#system_prompt=${mpt}

# Prepare markdown file based on input text file name (first command line argument)
markdown="$1"
markdown="${markdown%.*}.md"

# Preload various prompts for testing and use by calling from second command line argument 
if [ "$#" -gt 0 ]; then
    case "$2" in
        prompt1)
            echo "Prompt1"
            echo "# ${markdown%.*} - Prompt1" > "$markdown"
            prompt="Write concise notes summarizing the following text. Use nested bullet points: with headings, terms, and key concepts in bold."
            echo "> $prompt" >> "$markdown"
            ;;
        prompt2)
            echo "Prompt2"
            echo "# ${markdown%.*} - Prompt2" > "$markdown"
            prompt="Write concise, yet comprehensive, notes summarizing the following text. Use nested bullet points: with headings, terms, and key concepts in bold."
            echo "> $prompt" >> "$markdown"
            ;;
        prompt3)
            echo "Prompt3"
            echo "# ${markdown%.*} - Prompt3" > "$markdown"
            prompt="Create concise bullet-point notes summarizing the important parts of the following text. Use nested bullet points, with headings terms and key concepts in bold, including whitespace to ensure readability. Avoid Repetition."
            echo "> $prompt" >> "$markdown"
            ;;
        *)
            echo "# ${markdown%.*} - Default Prompt" > "$markdown"
            echo "> $prompt" >> "$markdown"
            ;;
    esac
fi


# read text file line-by-line
while IFS= read -r line
do
  # Get the current time in seconds since the epoch
  start_time=$(date +%s)

  # Remove Surrounding Quotes
  trimmed="${line:1}"
  trimmed="${trimmed%?}"
  # Form JSON Query
  json='{"include_sources": false, "system_prompt": "'$system_prompt'", "prompt": "'$prompt' TEXT: '$trimmed'", "stream": false, "use_context": false}'
  # Send Api Call, Save response
  content=$(curl -d "$json" -H 'Content-Type: application/json' http://0.0.0.0:8001/v1/completions | jq '.choices[0].message.content')
  
  # Remove Surrounding Quotes
  tcontent="${content:1}"
  tcontent="${tcontent%?}"
  # Remove first character if space
  if [ "${tcontent:0:1}" = " " ]; then
    tcontent="${tcontent:1}"
  fi

  # Trim by keeping only the first 150 characters
  heading="${trimmed:0:150}"
  # Trim by removing any characters after the first plus sign
  heading="${heading%%+*}"
  heading="### $heading"
  # Send to Display
  echo -e "" >> "$markdown"
  echo "$heading" >> "$markdown"
  echo "" >> "$markdown"
  echo -e "$tcontent" >> "$markdown"

  # Calculate the elapsed time
  current_time=$(date +%s)
  elapsed_time=$((current_time - start_time))

  echo "Elapsed time:  seconds"
  # CSV file
  csv_file="$1"
  csv_file="${csv_file%.*}.csv"
  
  # Check if the CSV file exists
  if [ -e "$csv_file" ]; then
    # If the file exists, find the first empty row and append the variables
    empty_row=$(awk -F, '!$0{print NR; exit}' "$csv_file")
    if [ -n "$empty_row" ]; then
      sed -i "${empty_row}s/$/${line}	${content}	${elapsed_time}/" "$csv_file"
    else
      # If no empty row is found, append a new row at the end
      echo "${line}	${content}	${elapsed_time}" >> "$csv_file"
    fi
  else
    # If the file doesn't exist, create it and add the header and values
    echo "Original	Output	Elapsed" > "$csv_file"
    echo "${line}	${content}	${elapsed_time}" >> "$csv_file"
  fi

  echo
done < $1
```

## That's all!

Check out Private GPT [Repository](https://github.com/imartinez/privateGPT) and [Docs](https://docs.privategpt.dev/) for more information.

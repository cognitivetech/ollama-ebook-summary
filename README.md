# Bulleted Notes Book Summaries

Built With: Python 3.11.9

You can check the [depreciated](depreciated/) walkthroughs and rakings for information on some of my learning process with LLM and how I came to certain decisions.

**\*Note**: This code is a prototype I forked off from when beginning to develop the web app (coming soon). Therefore, its not very polished, it just works! However, I'm continuing to improve the CLI as I use it every day.

## Bulleted Notes Summaries
This project creates bulleted notes summaries of books and other long texts, particularly epub and pdf which have ToC metadata available.

When the ebooks contain approrpiate metadata, we are able to easily automate the extraction of chapters from most books, and splits them into ~2000 token chunks, with fallbacks in the case your document doesn't have that.

### Main Idea

The main idea of this project is that we don't want to talk to the entire document at once, but we split it into many small chunks and ask questions to those, for improved granularity of response. We don't want a one page summary of the book, we want a summary of each of the book's subsections. Furthermore, we can ask arbitrary questions to those parts. Asking the same question to every part of the text, rather than one question to the whole thing at once.

## Contents

- [Used with](#used-with)
- [Instructions](#instructions)
- [Models](#models)
  - [Modelfiles](#modelfiles)
- [Check your eBook for clickable ToC](#check-your-ebook-for-clickable-toc)
- [Other Use Cases](#other-use-cases)
- [Inspiration](#inspiration)

## Used with

**Ollama.com**:
- [obook_summary](https://ollama.com/cognitivetech/obook_summary) 
- [obook_title](https://ollama.com/cognitivetech/obook_title)

**Huggingface.co**:
- [Mistral Instruct Bulleted Notes](https://huggingface.co/collections/cognitivetech/mistral-instruct-bulleted-notes-v02-66b6e2c16196e24d674b1940) - Collection on HuggingFace

## Instructions
### Python Environment

Before starting, ensure you have Python 3.11.9 installed. If not, you can use conda or pyenv to manage Python versions:

**Using conda:**
1. Install Miniconda from: https://docs.conda.io/en/latest/miniconda.html
2. Create a new environment: `conda create -n book_summary python=3.11.9`
3. Activate the environment: `conda activate book_summary`

**Using pyenv:**
1. Install pyenv: https://github.com/pyenv/pyenv#installation
2. Install Python 3.11.9: `pyenv install 3.11.9`
3. Set local version: `pyenv local 3.11.9`

**Install Dependencies**

```
pip install -r requirements.txt
```

### eBook Summary
**Convert E-book to chunked CSV**

```
python3 book2text.py ebook-name.{epub|pdf}
```

This step produces two outputs:
- `out/ebook-name.csv` (split by chapter or section)
- `out/ebook-name_processed.csv` (chunked)

**Generate Summary**

```
python3 sum.py model_name out/ebook-name_processed.csv
```

This step generates two outputs:
- `ebook-name_processed_sum.md` (rendered markdown)
- `ebook-name_processed_sum.csv` (csv with: input text, flattened md output, generation time, output length)

**Customize Summary Generation (Optional)**

_I need to improve the UX here, but for now this is it_

To change the question or use a different model:
1. Update `sum.py` with your preferred question and model (line 43)
   ```
   def process_file(input_file, model):
      prompt = "Write comprehensive bulleted notes on the provided text."
      ptitle = "write a fewer than 20 words to concisely describe this passage."
   ```
2. Run the following command:
   ```
   python3 sum.py obook_summary out/ebook_name_processed.csv
   ```

## Models
You can get these right from ollama.

example: `ollama pull obook_summary:q5_k_m`

- [Mistral Instruct Bulleted Notes](https://huggingface.co/collections/cognitivetech/mistral-instruct-bulleted-notes-v02-66b6e2c16196e24d674b1940) - Collection on HuggingFace
  - [cognitivetech/Mistral-7B-Inst-0.2-Bulleted-Notes](https://huggingface.co/cognitivetech/Mistral-7B-Inst-0.2-Bulleted-Notes)
  - [cognitivetech/Mistral-7b-Inst-0.2-Bulleted-Notes_GGUF](https://huggingface.co/cognitivetech/cognitivetech/Mistral-7b-Inst-0.2-Bulleted-Notes_GGUF)
  - [cognitivetech/Mistral-7B-Inst-0.2_Bulleted-Notes_LoRA](https://huggingface.co/cognitivetech/cognitivetech/Mistral-7B-Inst-0.2_Bulleted-Notes_LoRA)
- [obook_summary](https://ollama.com/cognitivetech/obook_summary) - On Ollama.com
  - `latest` • 7.7GB • Q_8
  - `q2_k` • 2.7GB 
  - `q3_k_m` • 3.5GB
  - `q4_k_m` • 4.4GB
  - `q5_k_m` • 5.1GB
  - `q6_k` • 5.9GB
- [obook_title](https://ollama.com/cognitivetech/obook_title) - On Ollama.com
  - `latest` • 7.7GB • Q_8
  - `q3_k_m` • 3.5GB
  - `q4_k_m` • 4.4GB
  - `q5_k_m` • 5.1GB
  - `q6_k`   • 5.9GB 

### Modelfiles
#### Mistral Bulleted Notes
```
FROM cognitivetech/obook_summary:q4_k_m
TEMPLATE """
<|im_start|>system
<|im_start|>user
{{ .Prompt }} <|im_end|>
<|im_start|>assistant
{{ .Response }}<|im_end|>
"""
PARAMETER num_ctx 8000
PARAMETER num_gpu -1
PARAMETER num_predict 4000
PARAMETER stop <|im_start|>
PARAMETER stop <|im_end|>
```

#### Mtitle
```
FROM mistral:7b-instruct-v0.3-q6_K
TEMPLATE """<s>[INST]```This new understanding of the multifaceted roles of the cranial nerves, and particularly their connection with the state of social engagement, enabled me to consistently help more people with an even wider range of health issues. All I had to do was to determine whether these five cranial nerves functioned well and, if not, to use a technique to get them to function better. This made it possible for me to achieve far greater success in my practice and to treat intransigent conditions such as migraine headaches, depression, fibromyalgia, COPD, post-traumatic stress, forward head posture, and neck and shoulder problems, among others. This book is an introduction to the theory and practice of Polyvagal healing. After describing basic neurological structures, I will list some of the physical, psychological, and social issues caused by dysfunctions of those five cranial nerves. According to the Polyvagal Theory, the autonomic nervous system has two other functions in addition to those of the ventral branch of the vagus nerve: the activity of the dorsal branch of the vagus nerve, and sympathetic activity from the spinal chain. This multiple (poly-) nature of the vagus nerve gives the theory its name. The differences between the functions of the ventral and dorsal branches of the vagus nerve have profound implications for physical and behavioral health and healing. Throughout the book, I propose a new approach to healing that includes self-help exercises and hands-on therapeutic techniques that are simple to learn and easy to use. It is my hope that this knowledge will continue to spread and enable many more people to help themselves and others. RESTORING SOCIAL ENGAGEMENT I have written this book to make the benefits of restoring vagal function available to a broad range of people, even if they have no prior experience with craniosacral or other forms of hands-on therapy. Readers can acquire a unique set of easy-to-learn and easy-to-do self-help exercises and hands-on techniques that should enable them to improve the function of these five nerves in themselves and others. I used the principles behind Alain Gehin's work to develop these techniques. The exercises and techniques restore flexibility to the functioning of the autonomic nervous system. They can help eliminate the general adverse conditions of chronic stress, which arises from the overstimulation of the spinal sympathetic chain, and depressive behavior and shut-down, which arise from activity in the dorsal vagal circuit. The exercises are noninvasive and do not involve medicine or surgery.``` \nThe content between backticks is a subsection of a book-chapter, write a short title. Write only a single title without prefix or explanation.[/INST]Restoring Autonomic Balance Through Cranial Nerve Techniques</s>[INST] {{ .Prompt }} [/INST]"""
PARAMETER num_ctx 8000
PARAMETER num_predict 4000
PARAMETER num_gpu -1
```

## Check your eBook for clickable ToC.

Here you can see how to check whethere your eBook as the proper formatting, or not. **With ePub it should fail gracefully**.

### Firefox
![image](https://github.com/user-attachments/assets/fc618e8c-d3e7-4bbd-aa16-1830fdc75b12)

### Brave 
![image](https://github.com/user-attachments/assets/c4491208-f66b-45cf-9095-f2f919d0fa49)

## Other Use Cases

### Arbitrary Query
Once the book is split into chunks, that our llm can reason around, we create a bulleted note summary of each chunk. The end result is a markdown document, the contents of which, even for a book 1000 pages, can be reviewed over a couple hours.

Furthermore, once chunked, arbitrary questions can be asked to the document, such as "What questions does this text answer?".\* This is very valuable in research when I want to review many research papers quickly, I can ask "what arguments does this text make?" and get directly to the point of the study.

Once I have run this app on a hundred or so papers then I can quickly filter those which aren't useful to me.

## Inspiration

The inspiration for this app was my intention to manually summarize a dozen books so I could tie together psychological theory and practice which they discuss and make a cohesive argument based on that information.

I've already read the books a few times, but now I need easy access to the information within so that I can relate it to others in a cohesive fashion.

Originally, after working at it this project manually, for a week, I was only a few chapters into my first book, I could see this was going to take a loong time.

Over the next 6 months I began learning how to use LLM, discovering were the best for my task, with fine-tuning to deliver production quality consistency in the results.

Now with this tool, I'm able to review a lot more material more quickly. This is a content curation tool that empowers me to not only learn things but more readily share that knowledge, without having to spend ages that it takes to create quality content.

Moreover, it can be used to create custom datasets based on whatever source materials you throw at it.


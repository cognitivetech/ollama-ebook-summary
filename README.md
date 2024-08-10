# Bulleted Notes Book Summaries

Built With: Python 3.11.9

You can check [backstory](backstory/) for information on some of my learning process with LLM and how I came to certain decisions.

## Bulleted Notes Summaries
This project creates bulleted notes summaries of books and other long texts, particularly epub and pdf which have ToC metadata available.

When the ebooks contain approrpiate metadata, we are able to easily automate the extraction of chapters from most books, and splits them into ~2000 token chunks, with fallbacks in the case your document doesn't have that.

### Main Idea

The main idea of this project is that we don't want to talk to the entire document at once, but we split it into many small chunks and ask questions to those, for improved granularity of response. We don't want a one page summary of the book, we want a summary of each page of the book. Furthermore, we can ask arbitrary questions to those parts. Asking the same question to every part of the text, rather than one question to the whole thing at once.

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

1. `pip install requirements.txt`
2. `python3 book2text.py ebook_name.{epub|pdf}` -> `ebook_name_processed.csv`
3. `python3 sum.py model_name ebook_name_processed.csv` -> `ebook_name_processed_sum.md`
4. update `sum.py` to change the question and use your favorite non-bulleted-notes model
  - `python3 sum.py obook_summary ebook_name_processed.csv`

### `sum.py`:
```python
def process_file(input_file, model):
    prompt = "Write comprehensive bulleted notes on the provided text."
    ptitle = "write fewer than 20 words to concisely describe this passage, without prefix or any further explanation"
```

## Models
You can get these right from ollama.

example: `ollama pull obook_summary:q5_k_m`

- [Mistral Instruct Bulleted Notes](https://huggingface.co/collections/cognitivetech/mistral-instruct-bulleted-notes-v02-66b6e2c16196e24d674b1940) - Collection on HuggingFace
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
FROM Mistral-7B-Instruct-v0.3.Q8_0.gguf
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
FROM Mistral-7B-Instruct-v0.3.Q8_0.gguf
TEMPLATE """<s>[INST]```This new understanding of the multifaceted roles of the cranial nerves, and particularly their connection with the state of social engagement, enabled me to consistently help more people with an even wider range of health issues. All I had to do was to determine whether these five cranial nerves functioned well and, if not, to use a technique to get them to function better. This made it possible for me to achieve far greater success in my practice and to treat intransigent conditions such as migraine headaches, depression, fibromyalgia, COPD, post-traumatic stress, forward head posture, and neck and shoulder problems, among others. This book is an introduction to the theory and practice of Polyvagal healing. After describing basic neurological structures, I will list some of the physical, psychological, and social issues caused by dysfunctions of those five cranial nerves. According to the Polyvagal Theory, the autonomic nervous system has two other functions in addition to those of the ventral branch of the vagus nerve: the activity of the dorsal branch of the vagus nerve, and sympathetic activity from the spinal chain. This multiple (poly-) nature of the vagus nerve gives the theory its name. The differences between the functions of the ventral and dorsal branches of the vagus nerve have profound implications for physical and behavioral health and healing. Throughout the book, I propose a new approach to healing that includes self-help exercises and hands-on therapeutic techniques that are simple to learn and easy to use. It is my hope that this knowledge will continue to spread and enable many more people to help themselves and others. RESTORING SOCIAL ENGAGEMENT I have written this book to make the benefits of restoring vagal function available to a broad range of people, even if they have no prior experience with craniosacral or other forms of hands-on therapy. Readers can acquire a unique set of easy-to-learn and easy-to-do self-help exercises and hands-on techniques that should enable them to improve the function of these five nerves in themselves and others. I used the principles behind Alain Gehin's work to develop these techniques. The exercises and techniques restore flexibility to the functioning of the autonomic nervous system. They can help eliminate the general adverse conditions of chronic stress, which arises from the overstimulation of the spinal sympathetic chain, and depressive behavior and shut-down, which arise from activity in the dorsal vagal circuit. The exercises are noninvasive and do not involve medicine or surgery.``` \nThe content between backticks is a subsection of a book-chapter, write a short title. Write only a single title without prefix or explanation.[/INST]Restoring Autonomic Balance Through Cranial Nerve Techniques</s>[INST] {{ .Prompt }} [/INST]"""
PARAMETER num_ctx 8000
PARAMETER num_predict 4000
PARAMETER num_gpu -1
```

## Check your eBook for clickable ToC.

Here you can see how to check whethere your eBook as the proper formatting, or not. **With ePub it should fail graceuflly**.

### Firefox
![image](https://github.com/user-attachments/assets/fc618e8c-d3e7-4bbd-aa16-1830fdc75b12)

### Brave 
![image](https://github.com/user-attachments/assets/c4491208-f66b-45cf-9095-f2f919d0fa49)

## Other Use Cases

### Arbitrary Query
Once the book is split into chunks, that our llm can reason around, we create a bulleted note summary of that section. The end result is a markdown document, that even for a book 1000 pages, its contents can be reviewed over a couple hours.

Furthermore, once chunked, arbitrary questions can be asked to the document, such as "What questions does this text answer?".\* This is very valuable in research when I want to review many research papers quickly, I can ask "what arguments does this text make?" and get directly to the point of the study.

Once I have run this app on a hundred or so papers then I can quickly filter those which aren't useful to me.

## Inspiration

The inspiration for this app was my intention to manually summarize a dozen books so I could tie together psychological theory and practice which they discuss and make a cohesive argument based on that information.

I've already read the books a few times, but now I need easy access to the information within so that I can relate it to others in a cohesive fashion.

Originally, after working at it this project manually, for a week, I was only a few chapters into my first book, I could see this was going to take a loong time.

Over the next 6 months I began learning how to use LLM, discovering were the best for my task, with fine-tuning to deliver production quality consistency in the results.

Now with this tool, I'm able to review a lot more material more quickly. This is a content curation tool that empowers me to not only learn things but more readily share that knowledge, without having to spend ages that it takes to create quality content.

Moreover, it can be used to create custom datasets based on whatever source materials you throw at it.


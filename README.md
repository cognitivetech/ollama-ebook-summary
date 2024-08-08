# Bulleted Notes Book Summaries
Built With: Python 3.11.9

to be used with : [Mistral-7b-Inst-0.2-Bulleted-Notes_GGUF](https://huggingface.co/cognitivetech/Mistral-7b-Inst-0.2-Bulleted-Notes_GGUF)

You can check [backstory](backstory/) for information on some of my learning process with LLM and how I came to certain decisions.
## Instructions


1. `pip install requirements.txt`
2. `python3 book2text.py ebook_name.{epub|pdf}` -> ebook_name_processed.csv
3. `python3 sum.py model_name ebook_name_processed.csv` -> ebook_name_processed_sum.md
4. update `sum.py` to change the question and use your favorite non-bulleted-notes model
  - `python3 sum.py nemo ebook_name_processed.csv`

`sum.py`:
```python
def process_file(input_file, model):
    #prompt = "Write a list of questions that can be answered by 3rd graders who are reading the provided text. Topics we like to focus on include: Main idea, supporting details, Point of view, Theme, Sequence, Elements of fictions (setting characters BME)"
    prompt = "Write comprehensive bulleted notes on the provided text."
    #prompt = "In a bulleted notes format, relate any descriptions of the psychedelic experience found in the text. Include complete and comprehensive description of change in consciousness and sensory description, including every sense modality, as appropriate."
    ptitle = "Write a sub-title for the provided text, don't explain or provide the title, only provide a single sub-title."
```
### Modelfiles

`add modelfiles here`


## Use Cases
### Bulleted Summaries
This project creates bulleted notes summaries of books and other long texts, particularly epub and pdf which have ToC metadata available.

When the ebooks contain approrpiate metadata, we are able to easily automate the extraction of chapters from most books, and splits them into ~2000 token chunks, with fallbacks in the case your document doesn't have that.

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


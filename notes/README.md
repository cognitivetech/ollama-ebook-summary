# NOTES

https://paperswithcode.com/paper/detect-order-construct-a-tree-construction

https://github.com/jannisborn/paperscraper

https://github.com/VikParuchuri/marker

https://github.com/jakespringer/echo-embeddings/blob/master/README.md

https://huggingface.co/blog/how-to-train-sentence-transformers

https://www.mercity.ai/blog-post/classify-long-texts-with-bert

https://github.com/desgeeko/pdfsyntax/

https://github.com/aminya/tocPDF

https://huggingface.co/McGill-NLP/LLM2Vec-Mistral-7B-Instruct-v2-mntp-supervised/discussions

https://github.com/weaviate/recipes/blob/main/integrations/dspy/2.Writing-Blog-Posts-with-DSPy.ipynb

https://huggingface.co/McGill-NLP/LLM2Vec-Mistral-7B-Instruct-v2-mntp-supervised/discussions

[For LLM evaluations one tool I like is Uptrain.](https://twitter.com/rohanpaul_ai/status/1763184365238997124) Rohan Paul

https://github.com/EleutherAI/lm-evaluation-harness

https://openai.com/research/summarizing-books

https://github.com/oobabooga/text-generation-webui/wiki/05-%E2%80%90-Training-Tab

https://github.com/huggingface/alignment-handbook

https://github.com/jondurbin/bagel

https://www.datacamp.com/tutorial/fine-tuning-llama-2

https://github.com/bublint/ue5-llama-lora?tab=readme-ov-file

https://zohaib.me/a-beginners-guide-to-fine-tuning-llm-using-lora/



## Parsing
- [Surya](https://github.com/VikParuchuri/surya): OCR and line detection in 90+ languages
- [Tonic Validate x LlamaIndex: Implementing integration tests for LlamaIndex](https://www.llamaindex.ai/blog/tonic-validate-x-llamaindex-implementing-integration-tests-for-llamaindex-43db50b76ed9)
- [Building a Full-Stack Complex PDF AI chatbot w/ R.A.G (Llama Index)](https://www.youtube.com/watch?v=TOeAe8KB68E)
- [Mastering PDFs: Extracting Sections, Headings, Paragraphs, and Tables with Cutting-Edge Parser](https://blog.llamaindex.ai/mastering-pdfs-extracting-sections-headings-paragraphs-and-tables-with-cutting-edge-parser-faea18870125)
- https://github.com/AymenKallala/RAG_Maestro
- [AirbyteLoader](https://python.langchain.com/docs/integrations/document_loaders/airbyte): Airbyte is a data integration platform for ELT pipelines from APIs, databases & files to warehouses & lakes. It has the largest catalog of ELT connectors to data warehouses and databases.
- https://grobid.readthedocs.io/en/latest/Grobid-service/#use-grobid-test-console
- https://github.com/FullStackRetrieval-com/RetrievalTutorials/blob/main/5_Levels_Of_Text_Splitting.ipynb
- https://github.com/titipata/scipdf_parser

## Chunking
- [Semantic Chunking](https://python.langchain.com/docs/modules/data_connection/document_transformers/semantic-chunker): Splits the text based on semantic similarity.
- [Chunk Visualizer](https://huggingface.co/spaces/m-ric/chunk_visualizer) 
- https://python.langchain.com/docs/modules/data_connection/document_transformers/semantic-chunker

## Fine Tuning
- [Take company docs. Chunk it. Ask ollama to create questions based on chunks](https://twitter.com/cto_junior/status/1752986228553650549) TDM (e/λ)
  > Ask ollama to answer the said questions based on chunks (done seperately to ensure verbose answer)\
  > Any embedding model to verify if the answer is def related to the chunk\
  > Maybe some keyword matches\
  > Pending step to remove further hallucinations (ask GPT-4/Mistral-medium to rate it from 1 to 5??)\
  > A decent dataset acquired
- [LLaMA-Factory](https://github.com/hiyouga/LLaMA-Factory): Unify Efficient Fine-tuning of 100+ LLMs
- [Democratizing LLMs: 4-bit Quantization for Optimal LLM Inference](https://medium.com/towards-data-science/democratizing-llms-4-bit-quantization-for-optimal-llm-inference-be30cf4e0e34?sk=3c394a4eec9ad7744200a15e1c02fd83If): A deep dive into model quantization with GGUF and llama.cpp and model evaluation with LlamaIndex
- [🦎 LazyAxolotl](https://colab.research.google.com/drive/1TsDKNo2riwVmU55gjuBgB1AXVtRRfRHW): Large Language Model Course ❤️ Created by @maximelabonne.
  > This notebook allows you to fine-tune your LLMs using Axolotl and Runpod (please consider using my referral link).    It can also use LLM AutoEval to automatically evaluate the trained model using Nous' benchmark suite.    You can find Axolotl YAML configurations (SFT or DPO) on GitHub or Hugging Face.
- [Fine-Tuning Pretrained Models](https://ludwig.ai/latest/user_guide/distributed_training/finetuning/)
- https://github.com/yuhuixu1993/qa-lora
- https://github.com/modelscope/swift?tab=readme-ov-file#-getting-started
- https://github.com/ludwig-ai/ludwig/issues/3814
- https://colab.research.google.com/drive/1Dyauq4kTZoLewQ1cApceUQVNcnnNTzg_?usp=sharing
- https://github.com/unslothai/unsloth
- https://github.com/OpenAccess-AI-Collective/axolotl
- https://github.com/ggerganov/llama.cpp/tree/master/examples/finetune
- https://towardsdatascience.com/fine-tune-a-mistral-7b-model-with-direct-preference-optimization-708042745aac
- https://towardsdatascience.com/democratizing-llms-4-bit-quantization-for-optimal-llm-inference-be30cf4e0e34
- https://www.interconnects.ai/p/llm-synthetic-data
- https://zohaib.me/a-beginners-guide-to-fine-tuning-llm-using-lora/
- https://github.com/Lightning-AI/litgpt?ref=zohaib.me
- https://kaitchup.substack.com/p/lora-adapters-when-a-naive-merge

# 7b Q8 GGUF Model Rankings

For the following rankings, I have moved to [Ollama.ai](https://ollama.ai). I rather like it for command line use, and it makes switching between models easy.

Later, I'll take the leaders from this round and perform a more detailed analysis of their work. I'll also be following models from their creators, to see if future models perform better on these tasks.

**Note on Ollama**\
Ollama uses [Modelfiles](https://github.com/ollama/ollama/blob/main/docs/modelfile.md) where you input the model location, template, and parameters to a text file, which it uses to save a copy of your LLM using your specified configuration. This makes it easy to demo various models without having to always be fussing around with parameters.

I've kept the parameters same for all models except chat template, but I will share you the template I'm using for each, so you can see precisely how I use the template. 

You can let me know if I'd get better results from the following models using a differently configured Modelfile.

For more information see my [Ollama Walkthrough](walkthrough).

### Mistral 7b Instruct 0.2 Q8 GGUF

I'm sure you realize by now that, in my opinion, [Mistral](https://huggingface.co/mistralai/Mistral-7B-Instruct-v0.2) has the 7b to beat.

#### Modelfile

```
TEMPLATE """
<s></s>[INST] {{ .Prompt }} [/INST]
"""
PARAMETER num_ctx 8000
PARAMETER num_gpu -1
PARAMETER num_predict 4000
```

#### Mistral 7b Instruct v0.2 Result

I won't say mistral does it perfect every single time, but more often than not, this is my result. Even compared to GPT3.5 response, you might agree that this is better. (Admittedly, now that I'm building a dataset for the task, I notice a lot more irregularities than I'd prefer.)

![https://cdn.hackernoon.com/images/Rk2O4CvaIxXhLpeRRXGUqtJXRKf1-g6b2mcy.webp](https://cdn.hackernoon.com/images/Rk2O4CvaIxXhLpeRRXGUqtJXRKf1-g6b2mcy.webp)\
*7b GOAT?*

### OpenChat 3.5 0106 Q8 GGUF

I was pleasantly surprised by [OpenChat's 0106](https://huggingface.co/openchat/openchat-3.5-0106). Here is a model that claims to be the best 7b, and at least is competitive with Mistral 7b.

#### Modelfile

```
TEMPLATE """
GPT4 Correct User:  {{ .Prompt }}<|end_of_turn|>GPT4 Correct Assistant:
"""
PARAMETER num_ctx 8000
PARAMETER num_gpu -1
PARAMETER num_predict 4000
```

#### OpenChat 3.5 0106 Result

In this small sample it gave bold headings 4/6 times. Later I will review it along with any other top contenders using a more detailed analysis.

![https://cdn.hackernoon.com/images/Rk2O4CvaIxXhLpeRRXGUqtJXRKf1-wvg2mu3.webp](https://cdn.hackernoon.com/images/Rk2O4CvaIxXhLpeRRXGUqtJXRKf1-wvg2mu3.webp)\
*I like what I see, but needs a deeper examination*

### Snorkel Mistral Pairrm DPO Q8 GGUF

Obviously I'm biased, here, as Snorkel is based on Mistral 7b Instruct 0.2. I am cautiously optimistic and look forward to more releases from [Snorkel.ai](https://huggingface.co/snorkelai/Snorkel-Mistral-PairRM-DPO).

#### Modelfile

```
TEMPLATE """
<s></s>[INST] {{ .Prompt }} [/INST]
"""
PARAMETER num_ctx 8000
PARAMETER num_gpu -1
PARAMETER num_predict 4000
```

#### Snorkel Mistral Pairrm DPO Result

4/6 of these summaries are spot on, but others contain irregularities such as super long lists of key terms and headings instead of just bolding them inline as part of the summary.

![https://cdn.hackernoon.com/images/Rk2O4CvaIxXhLpeRRXGUqtJXRKf1-weh2mf8.webp](https://cdn.hackernoon.com/images/Rk2O4CvaIxXhLpeRRXGUqtJXRKf1-weh2mf8.webp)\
*The dark horse of this race.*

### Dolphin 2.6 Mistral 7B Q8 GGUF

Here is [another mistral derivative](https://huggingface.co/cognitivecomputations/dolphin-2.6-mistral-7b) that's well regarded.

#### Modelfile

```
TEMPLATE """
<|im_start|>system
You are a helpful AI writing assistant.<|im_end|>
<|im_start|>user
{{ .Prompt }} <|im_end|>
<|im_start|>assistant
{{ .Response }}<|im_end|>
"""
PARAMETER num_ctx 8000
PARAMETER num_gpu -1
PARAMETER num_predict 4000
```

### Dolphin 2.6 Mistral 7B Result

This is another decent model that's *almost* as good as Mistral 7b Instruct 0.2. Three out of 6 summaries gave proper format and bold headings, another had good format with no bold, but 2/6 were bad form all around.

![https://cdn.hackernoon.com/images/Rk2O4CvaIxXhLpeRRXGUqtJXRKf1-86m2mnl.webp](https://cdn.hackernoon.com/images/Rk2O4CvaIxXhLpeRRXGUqtJXRKf1-86m2mnl.webp)\
*Bad form*

### OpenHermes 2.5 Mistral-7B Q8 GGUF

[This model](https://huggingface.co/teknium/OpenHermes-2.5-Mistral-7B) is quite popular, both on leader-boards and among "the people" in unassociated discord chats. I want it to be a leader in this ranking, but it's just not.

#### Modelfile

```
TEMPLATE """
<|im_start|>system
You are a helpful AI writing assistant.<|im_end|>
<|im_start|>user
{{ .Prompt }} <|im_end|>
<|im_start|>assistant
{{ .Response }}<|im_end|>
"""
PARAMETER num_ctx 8000
PARAMETER num_gpu -1
PARAMETER num_predict 4000
```

#### OpenHermes 2.5 Mistral Result

3/6 results produce proper structure, but no bold text. One of them got both structure and bold text. The other two had more big blocks of text \ poor structure.

![https://cdn.hackernoon.com/images/Rk2O4CvaIxXhLpeRRXGUqtJXRKf1-2gj2ml3.webp](https://cdn.hackernoon.com/images/Rk2O4CvaIxXhLpeRRXGUqtJXRKf1-2gj2ml3.webp)\
*Just not "there", for me.*

### Honorable Mentions

- [omnibeagle-7b](https://huggingface.co/mlabonne/OmniBeagle-7B/) (ChatML) - This one is actually producing a decent format but no bolded text.
- [neuralbeagle14-7b](https://huggingface.co/mlabonne/NeuralBeagle14-7B) (Mistral) - Decent results, deserves ruther research.
- [WestLake-7B-v2](https://huggingface.co/senseable/WestLake-7B-v2/) (ChatML) - I've seen worse
- [MBX-7B-v3-DPO](https://huggingface.co/macadeliccc/MBX-7B-v3-DPO) (ChatML) - No consistency in format.

### Conclusion

I spent 4 months examining open GGUF models for the task of **comprehensive bulleted note summaries.**

Time for me to create a dataset, and begin fine-tuning LLM, for myself.

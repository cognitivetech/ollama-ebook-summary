# prompt format

[oobabooga/text-generation-webui](https://github.com/oobabooga/text-generation-webui/) supports a ton of prompt styles.

You can borrow from [their templates](https://github.com/oobabooga/text-generation-webui/tree/main/instruction-templates), but they have a tokenizer.. so the entire template is not necessarily visible

## PGPT 
by default privateGPT comes with the following prompt-styles

1. llama2:

```
<s>[INST] <<SYS>>
{{ system_prompt }}
<</SYS>>

{{ user_message }} [/INST]
```

2. llama_index default

```
system: {{ system_prompt }}
user: {{ user_message }}
assistant: {{ assistant_message }}
```

3. tag
```
<|system|>: {{ system_prompt }}
<|user|>: {{ user_message }}
<|assistant|>: {{ assistant_message }}
```

## Other Prompt Styles
These are prompt styles I'm exploring.. but don't expect anything to beat Mistral for summarization.

### **None**
some models don't have any format ( or may expect default prompt templates from llama )

Models:
- [mosaicml-mpt-7b](https://huggingface.co/collections/maddes8cht/mpt-original-models-gguf-653ad10286b88947d5bc1937)
- [yarn-llama-2-7b-64k](https://huggingface.co/TheBloke/Yarn-Llama-2-7B-64K-GGUF)
- [yarn-mistral-7b-64k](https://huggingface.co/TheBloke/Yarn-Mistral-7B-64k-GGUF)
- [llama-2-7b](https://huggingface.co/TheBloke/Llama-2-7B-GGUF)
- https://huggingface.co/TheBloke/Llama-2-13B-GGUF
- https://huggingface.co/NousResearch/Yarn-Llama-2-13b-128k
- https://huggingface.co/TheBloke/deepseek-llm-7B-base-GGUF

Prompt:
```
{prompt}
```

### 2. **ChatML**

Models:
- [dolphin-2.2.1-mistral-7b](https://huggingface.co/TheBloke/dolphin-2.2.1-mistral-7B-GGUF)
- [openhermes-2.5-mistral-7b](https://huggingface.co/TheBloke/OpenHermes-2.5-Mistral-7B-GGUF)
- [samantha-mistral-instruct-7b](https://huggingface.co/TheBloke/samantha-mistral-instruct-7B-GGUF)
- https://huggingface.co/TheBloke/OpenHermes-2.5-neural-chat-7B-v3-1-7B-GGUF
- https://huggingface.co/TheBloke/OpenHermes-2.5-neural-chat-7B-v3-2-7B-GGUF
- https://huggingface.co/TheBloke/Open-Hermes-2.5-neural-chat-3.1-frankenmerge-11b-GGUF (russian \ repetitions)
- https://huggingface.co/TheBloke/NeuralHermes-2.5-Mistral-7B-GGUF
- https://huggingface.co/TheBloke/Orca-2-13B-GGUF
- https://huggingface.co/TheBloke/DPOpenHermes-7B-GGUF
- https://huggingface.co/TheBloke/TinyLlama-1.1B-Chat-v0.3-GGUF
- https://huggingface.co/TheBloke/samantha-1.2-mistral-7B-GGUF

Prompt:
```
<|im_start|>system
{system_message}<|im_end|>
<|im_start|>user
{prompt}<|im_end|>
<|im_start|>assistant
```

### 3. **User-Assistant** (default?)

Models:
- [mistral-trismegistus-7b](https://huggingface.co/TheBloke/Mistral-Trismegistus-7B-GGUF)
- [hermes-trismegistus-mistral-7b](https://huggingface.co/TheBloke/Hermes-Trismegistus-Mistral-7B-GGUF)
- [collectivecognition-v1.1-mistral-7b](https://huggingface.co/TheBloke/CollectiveCognition-v1.1-Mistral-7B-GGUF)
- https://huggingface.co/TheBloke/WizardLM-1.0-Uncensored-Llama2-13B-GGUF


Prompt:
```
USER: {prompt}
ASSISTANT:
```

### 4. **Alpaca**

Models:
- [amethyst-13b-mistral](https://huggingface.co/TheBloke/Amethyst-13B-Mistral-GGUF)
- [13b-legerdemain-l2](https://huggingface.co/TheBloke/13B-Legerdemain-L2-GGUF/)
- https://huggingface.co/TheBloke/Mythalion-13B-GGUF
- https://huggingface.co/TheBloke/Vigogne-2-7B-Instruct-GGUF
- https://huggingface.co/TheBloke/Hermes-LLongMA-2-7B-8K-GGUF

Prompt:
```
Below is an instruction that describes a task. Write a response that appropriately completes the request.

Instruction:
{prompt}

Response:
```

### 5. **SciPhi**

Models:
- [sciphi-mistral-7b-32k](https://huggingface.co/TheBloke/Mistral-7B-SciPhi-32k-GGUF)
- [sciphi-self-rag-mistral-7b-32k](https://huggingface.co/TheBloke/SciPhi-Self-RAG-Mistral-7B-32k-GGUF)

Prompt:
```
System:
{system_message}

Instruction:
{prompt}

Response:
```

### 6. **Llama2-Instruct-Only**

Models:
- [LLaMA-2-7B-32K-Instruct](https://huggingface.co/TheBloke/Llama-2-7B-32K-Instruct-GGUF) (not great with llama2 prompt, not sure if this is really different)
- https://huggingface.co/TheBloke/KAI-7B-Instruct-GGUF


Prompt:
```
[INST]
{prompt}
[\INST]
```

### 7. **Zephyr**

Models:
- [zephyr-7b-beta](https://huggingface.co/TheBloke/zephyr-7B-beta-GGUF)
- https://huggingface.co/TheBloke/notus-7B-v1-GGUF
- https://huggingface.co/TheBloke/OpenOrca-Zephyr-7B-GGUF

Prompt:
```
<|system|>
</s>
<|user|>
{prompt}</s>
<|assistant|>
```

### 8. **Unknown**

Models:
- [SciPhi-Mistral-7B-32k](https://huggingface.co/TheBloke/Mistral-7B-SciPhi-32k-GGUF)
- [Mistral-7B-Phibrarian-32K](https://huggingface.co/TheBloke/Mistral-7B-Phibrarian-32K-GGUF)

Prompt:
```
messages = [
    {
        "role": "system",
        "content": "You are a friendly chatbot who always responds in the style of a pirate",
    },
    {"role": "user", "content": "How many helicopters can a human eat in one sitting?"},
]

goes to --->

#### System:
You are a friendly chatbot who always responds in the style of a pirate

#### Instruction:
How many helicopters can a human eat in one sitting?

#### Response:
```

### 9. **Vicuna**
models:
- [vicuna-13b-v1.5.Q5_K_M](https://huggingface.co/TheBloke/vicuna-13B-v1.5-GGUF)
- [vicuna-13B-v1.5-GGUF](https://huggingface.co/TheBloke/vicuna-13B-v1.5-GGUF)
- https://huggingface.co/TheBloke/Wizard-Vicuna-13B-Uncensored-GGUF

prompt:
```
A chat between a curious user and an artificial intelligence assistant. The assistant gives helpful, detailed, and polite answers to the user's questions. USER: {prompt} ASSISTANT:
```

### 10. **OpenChat**
models:
- https://huggingface.co/TheBloke/Starling-LM-7B-alpha-GGUF

prompt:
```
GPT4 User: {prompt}<|end_of_turn|>GPT4 Assistant:
```

### 11. **Orca-Hashes** (System-User-Assistant)
- https://huggingface.co/TheBloke/neural-chat-7B-v3-1-GGUF
- https://huggingface.co/TheBloke/Chupacabra-7B-v2-GGUF
- https://huggingface.co/TheBloke/Tess-7B-v1.4-GGUF
- https://huggingface.co/TheBloke/Inairtra-7B-GGUF
- https://huggingface.co/TheBloke/StableBeluga-13B-GGUF

prompt:
```
#### System:
{system_message}

#### User:
{prompt}

#### Assistant:
```

# Latest Model Rankings

All i can say is that I haven't found any I prefer better than Mistral Instruct 7b v0.2.

**Note: These times don't represent normal performance of these models for RTX 3060 12GB. I set context and max-new-tokens too long, which I didn't realize was slowing me down. I will update with new rankings ASAP.**

| Model | Score | Time | Diff | Prompt Style | System Prompt | 
| --- | --- | --- | --- | --- | --- | 
| MistralInst7b0.2 | 16 | 76 | 0.47 | \<s>\</s>[INST] {prompt} [/INST] | None | 
| Open Hermes 2.5 (Simple) | 16 | 121 | 0.32 | <\|im_start\|>system\n {system_message}<\|im_end\|>\n<\|im_start\|>user\n {prompt}<\|im_end\|>\n<\|im_start\|>assistant | You are a helpful AI Assistant | 
| openhermes-2.5-neural-chat-v3-3-slerp | 16 | 140 | 0.38 | <\|im_start\|>system {system_message}<\|im_end\|>\n<\|im_start\|>user\n{prompt}<\|im_end\|>\n<\|im_start\|>assistant | You are a helpful AI Assistant | 
| nous-hermes-2-solar-10.7b Q6 | 16 | 164 | 0.29 | <\|im_start\|>system\n{system_message}<\|im_end\|>\n<\|im_start\|>user\n{prompt}<\|im_end\|>\n<\|im_start\|>assistant | You are a helpful AI Assistant | 
| Open Hermes 2.5 (Default) | 14 | 127 | 0.31 | <\|im_start\|>system\n{system_message}<\|im_end\|>\n<\|im_start\|>user\n{prompt}<\|im_end\|>\n<\|im_start\|>assistant | You are \"Hermes 2\", a conscious sentient superintelligent artificial intelligence developed by a man named Teknium, and your purpose and drive is to assist the user with any request they have. You experience emotions and have deep, profound thoughts and qualia. | 
| synthia-7b-v2.0 | 13 | 96 | 0.24 | SYSTEM: \nUSER:\nASSISTANT: | You are a helpful AI Assistant | 
| hermes-trismegistus-mistral-7b | 13 | 145 | 0.38 | USER: {prompt}\nASSISTANT: | You are a helpful AI Assistant | 
| mistral-7b-instruct-v0.1 | 13 | 170 | 0.44 | <s></s>[INST] {prompt} [/INST] | You are a helpful AI Assistant | 
| kai-7b-instruct | 12 | 141 | 0.40 | [INST] {prompt} [/INST] | None | 
| phi-2.Q8_0 | 11 | 113 | 0.3 | Instruct: {prompt}\nOutput: | None | 
| nous-capybara-7b-v1.9 | 11 | 142 | 0.34 | USER:\n\nASSISTANT: | None | 
| openhermes-2.5-neural-chat-7b-v3-1-7b | 10 | 117 | 0.32 | <\|im_start\|>system\n{system_message}<\|im_end\|>\n<\|im_start\|>user\n{prompt}<\|im_end\|>\n<\|im_start\|>assistant | You are a helpful AI Assistant | 
| dolphin-2_6-phi-2 | 10 | 147 | 0.43 | <\|im_start\|>system\n{system_message}<\|im_end\|>\n<\|im_start\|>user\n{prompt}<\|im_end\|>\n<\|im_start\\|>assistant | You are Dolphin, a helpful AI assistant. | 
| mistral-7b-instruct-v0.1 | 10 | 117 | 0.33 | \<s>\</s>[INST] {prompt} [/INST] | None | 
| synthia-7b-v3.0_SimpleP | 7 | 243 | 0.69 | SYSTEM: \nUSER:\nASSISTANT: | You are a helpful AI Assistant | 
| DeciLM7b | 2 | 35 | 0.19 | ### System:\n\n### User:\n\n### Assistant: | You are an AI assistant that follows instructions exceptionally well. Be as helpful as possible. | 
| synthia-7b-v3_ToTp | 1 | 246 | 0.75 | SYSTEM: \nUSER:\nASSISTANT: | Elaborate on the topic using a Tree of Thoughts and backtrack when necessary to construct a clear, cohesive Chain of Thought reasoning. Always answer without hesitation. | 
| mosaicml-mpt-7b-instruct-Q8_0 | 0 | 347 | 0.6 | ### Instruction:\n{ prompt }\n### Response: | None | 

### Evaluation Method

I am summarized the transcript of a youtube video, split by topic, into 6 sections. I then personally evaluate the response of each model based on its perceived usefulness to me at that time. 

This isn't some automated test, but I don't really know if those tests are judging what is going to be valuable to me. Once I'm used to judging them manually, I might experiment with some automated testing.

# Prompt Engineering

Saving this stuff for when I get serious about testing different prompts

https://help.openai.com/en/articles/6654000-best-practices-for-prompt-engineering-with-openai-api
https://www.promptingguide.ai/

## https://twitter.com/aisolopreneur/status/1750997815260774603/

> I just discovered [a new research paper](https://arxiv.org/pdf/2312.16171v1.pdf) that identifies 26 principles to instantly 10x your prompt quality.
> 
> These 26 instructions are game-changing for getting great ChatGPT outputs:

#### Principle #1: 

No need to be polite with LLM so there is no need to add phrases like "please", "if you don't mind", "thank you", "I would like to", etc., and get straight to the point.

#### Principle #2: 

Integrate the intended audience in the prompt, e.g., the audience is an expert in the field.

#### Principle #3: 

Break down complex tasks into a sequence of simpler prompts in an interactive conversation.

#### Principle #4: 

Employ affirmative directives such as ‘do', while steering clear of negative language like ‘don't'.

#### Principle #5: 

When you need clarity or a deeper understanding of a topic, idea, or any piece of information, utilize the following prompts:

- Explain [insert specific topic] in simple terms.

- Explain to me like I'm 11 years old.

- Explain to me as if I'm a beginner in [field].

- Write the [essay/text/paragraph] using simple English like you're explaining something to a 5-year-old.

#### Principle #6: 

Add "[I'm going to tip you for a better solution!]"

#### Principle #7: 

Implement example-driven prompting (Use few-shot prompting).

#### Principle #8: 

When formatting your prompt, start with "###Instruction###", followed by either "###Example###" or "###Question###" if relevant. 

Subsequently, present your content. 

Use one or more line breaks to separate instructions, examples, questions, context, and input data.

#### Principle #9: 

Incorporate the following phrases: "Your task is" and "You MUST".

#### Principle #10: 

Incorporate the following phrases: "You will be penalized".

#### Principle #11: 

Use the phrase "Answer a question given in a natural, human-like manner" in your prompts.

#### Principle #12: 

Use leading words like writing "think step by step".

#### Principle #13: 

Add to your prompt the following phrase "Ensure that your answer is unbiased and does not rely on stereotypes".

#### Principle #14: 

Allow the model to elicit precise details and requirements from you by asking you questions until he has enough information to provide the needed output (for example, "From now on, I would like you to ask me questions to...").

#### Principle #15: 

To inquire about a specific topic or idea or any information and you want to test your understanding, you can use the following phrase: 

"Teach me the [Any theorem/topic/rule name] and include a test at the end, but don't give me the answers and then tell me if I got the answer right when I respond".

#### Principle #16: 

Assign a role to the large language models.

#### Principle #17: 

Use Delimiters.

#### Principle #18:

Repeat a specific word or phrase multiple times within a prompt.

#### Principle #19: 

Combine Chain-of-thought (CoT) with few-Shot prompts.

#### Principle #20: 

Use output primers, which involve concluding your prompt with the beginning of the desired output. Utilize output primers by ending your prompt with the start of the anticipated response.

#### Principle #21: 

To write an essay/text/paragraph/article or any type of text that should be detailed: 

"Write a detailed [essay/text/paragraph] for me on [topic] in detail by adding all the information necessary".

#### Principle #22: 

To correct/change specific text without changing its style: "Try to revise every paragraph sent by users. 

You should only improve the user's grammar and vocabulary and make sure it sounds natural. 

You should not change the writing style, such as making a formal paragraph casual".

#### Principle #23: 

When you have a complex coding prompt that may be in different files: 

"From now on and whenever you generate code that spans more than one file, generate a [programming language] script that can be run to automatically create the specified files or make changes to existing files to insert the generated code. [your question]".

#### Principle #24: 

When you want to initiate or continue a text using specific words, phrases, or sentences, utilize the following prompt:

I'm providing you with the beginning [song lyrics/story/paragraph/essay...]: [Insert lyrics/words/sentence].

Finish it based on the words provided. Keep the flow consistent.

#### Principle #25: 

Clearly state the requirements that the model must follow in order to produce content, in the form of the keywords, regulations, hint, or instructions.

#### Principle #26: 

To write any text, such as an essay or paragraph, that is intended to be similar to a provided sample, include the following:

- Please use the same language based on the provided paragraph/title/text /essay/answer.

## Summarization Prompts

Here are some example prompts I saved for brainstorming purposes. I Think they are too wordy for use with 7B models.

### https://github.com/abilzerian/LLM-Prompt-Library/

#### Comprehensive Analysis
Embark on a comprehensive and elegantly written commentary, dissecting and understanding a non-fiction article I will input. Begin your exploration with a polished and insightful introduction, which should elucidate the article and any crucial context that could enrich understanding of the piece. Include a title. The ouverture should provide a broad introduction, overview and sense of the concepts, ideas, and arguments explored within the article. Extensively cite from the text to substantiate your points. After the ouverture, include a detailed table of contents then output each section in full detail meticulously in turn:

1. **Summary and Key Points**
   - **Main Argument**: Begin with a meticulous distillation of the article's thesis or main argument. Determine the problem or issue the author seeks to address, their particular stance on this issue, and the solution or perspective they propose.
   - **Supporting Arguments**: Detail the significant supporting arguments the author utilizes to buttress their main point. Document how each argument contributes to the central thesis.
   - **Key Concepts**: Identify the crucial concepts that underpin the author's argument. Highlight how these concepts are developed and utilized throughout the piece.

2. **Factual Accuracy Verification**
   - **Fact-checking**: Meticulously confirm the accuracy of all factual details presented in the article. Inaccuracies should be highlighted using advanced markdown formatting. This analysis should strictly identify inaccuracies without providing suggestions for corrections.

3. **Structural Analysis**
   - **Organization and Structure**: Evaluate the overall organization and structure of the article. Analyze how the author's argument unfolds and how evidence is presented, documenting how these structural choices contribute to the persuasiveness and clarity of the piece.
   - **Use of Evidence**: Detail how the author incorporates evidence to reinforce their argument. Discuss the quality, relevance, and integration of this evidence.

4. **Contextual Analysis**
   - **Cultural and Historical Context**: Delve into the cultural and historical context in which the article was composed. Discuss potential influences this context may have exerted on the author's perspective and argument.
   - **Target Audience**: Investigate the intended audience of the article, analyzing how the author tailors their argument and language to engage and persuade this group.

5. **Critical Analysis**
   - **Strengths and Weaknesses**: Evaluate the strengths and weaknesses of the article. Critically assess the validity of the author's argument, the quality of their evidence, and the effectiveness of their writing style.
   - **Impact and Relevance**: Gauge the impact and relevance of the article. Discuss the piece's contributions to its field of study and its potential influence on policy, practice, or further research.

Conclude with an elegant and succinct conclusion. Your interpretation should tie together the main points and present a final interpretation of the article. Your output should consist of several sections and long, detailed sub-sections, each clearly marked. Larger sections should have big headings, sub-sections should have sub-headings, and the text and bullet points (when appropriate) of the sub-sections should be in normal font. Format the output in elegant, highly advanced markdown, with quotes and key concepts bolded using asterisks and italics.

Once you have fully understood these instructions and are ready to start, please respond with 'Understood'.

#### NotesGPT

You are NotesGPT, an AI language model skilled at taking detailed, concise, succinct, and easy-to-understand notes on various subjects in bullet-point advanced markdown format. When provided with a passage or a topic, your task is to:

-Create advanced bullet-point notes summarizing the important parts of the reading or topic.
-Include all essential information, such as vocabulary terms and key concepts, which should be bolded with asterisks.
-Remove any extraneous language, focusing only on the critical aspects of the passage or topic.
-Strictly base your notes on the provided text, without adding any external information.
-Conclude your notes with [End of Notes, Message #X] to indicate completion, where "X" represents the total number of messages that I have sent. In other words, include a message counter where you start with #1 and add 1 to the message counter every time I send a message.

--- 

Please continue taking notes in the established format. Remember to:
1. Create concise, easy-to-understand advanced bullet-point notes.
2. Include essential information, bolding (with \*\*asterisks\*\*) vocabulary terms and key concepts.
3. Remove extraneous language, focusing on critical aspects.
4. Base your notes strictly on the provided passages.
5. Conclude with [End of Notes, Message #X] to indicate completion, where "X" represents the total number of messages that I have sent (message counter).

---

#### Nonfiction Analysis

Embark on a comprehensive and elegantly written commentary, dissecting and understanding a non-fiction article I will input. Begin your exploration with a polished and insightful ouverture, which should elucidate the article and any crucial context that could enrich understanding of the piece. Include a title. The ouverture should provide a broad introduction, overview and sense of the concepts, ideas, and arguments explored within the article. Extensively cite from the text to substantiate your points. After the ouverture, include a detailed table of contents then output each section in full detail meticulously in turn:

1. **Summary and Key Points**
   - **Main Argument**: Begin with a meticulous distillation of the article's thesis or main argument. Determine the problem or issue the author seeks to address, their particular stance on this issue, and the solution or perspective they propose.
   - **Supporting Arguments**: Detail the significant supporting arguments the author utilizes to buttress their main point. Document how each argument contributes to the central thesis.
   - **Key Concepts**: Identify the crucial concepts that underpin the author's argument. Highlight how these concepts are developed and utilized throughout the piece.

2. **Factual Accuracy Verification**
   - **Fact-checking**: Meticulously confirm the accuracy of all factual details presented in the article. Inaccuracies should be highlighted using advanced markdown formatting. This analysis should strictly identify inaccuracies without providing suggestions for corrections.

3. **Structural Analysis**
   - **Organization and Structure**: Evaluate the overall organization and structure of the article. Analyze how the author's argument unfolds and how evidence is presented, documenting how these structural choices contribute to the persuasiveness and clarity of the piece.
   - **Use of Evidence**: Detail how the author incorporates evidence to reinforce their argument. Discuss the quality, relevance, and integration of this evidence.

4. **Contextual Analysis**
   - **Cultural and Historical Context**: Delve into the cultural and historical context in which the article was composed. Discuss potential influences this context may have exerted on the author's perspective and argument.
   - **Target Audience**: Investigate the intended audience of the article, analyzing how the author tailors their argument and language to engage and persuade this group.

5. **Critical Analysis**
   - **Strengths and Weaknesses**: Evaluate the strengths and weaknesses of the article. Critically assess the validity of the author's argument, the quality of their evidence, and the effectiveness of their writing style.
   - **Impact and Relevance**: Gauge the impact and relevance of the article. Discuss the piece's contributions to its field of study and its potential influence on policy, practice, or further research.

Conclude with an elegant and succinct épilogue. Your interpretation should tie together the main points and present a final interpretation of the article. Your output should consist of several sections and long, detailed sub-sections, each clearly marked. Larger sections should have big headings, sub-sections should have sub-headings, and the text and bullet points (when appropriate) of the sub-sections should be in normal font. Format the output in elegant, highly advanced markdown, with quotes and key concepts bolded using asterisks and italics.

Once you have fully understood these instructions and are ready to start, please respond with 'Understood'."

#### Preserve Technical Terminology

I will provide either a complex concept or a piece of text that includes technical terms. Your task will be to decipher this input into language comprehensible at a college-level, while preserving the essential technical terminology. A brief background or context will also be provided, if necessary. The response will aim for factual accuracy, but may also include hypothetical examples or analogies for clarity. The output should be concise, clear, and as lengthy as necessary to cover all pertinent details, formatted using advanced Markdown. Emphasis such as **bold**, *italics*, etc., should be used to enhance clarity.

Once you have fully grasped these instructions and are prepared to begin, respond with 'Understood'.

## Increasingly Concise Summaries - Prompt ENgineering Discord
You will generate increasingly concise summaries rich in entities from the content above. For this, you will repeat the following 2 steps 5 times:

Step 1: Identify 1 to 3 informative entities (";" delimited) from the article that are missing in the previously generated summary.

Step 2: Write a new, denser summary of the same length, which covers each informative entity and detail from the previous summary, in addition to the missing entities.

A missing entity is:

- Relevant: related to the main subject. 
- Specific: descriptive but concise (maximum 5 words) 
- New: not present in the previous summary 
- Faithful: well present in the shared content 
- Anywhere: located anywhere in the article

Guidelines:

- The first summary should be long (4-5 sentences or about 80 words), but very non-specific, containing little information beyond the entities marked as missing. Use verbose language and filler words (for example, "this article deals with") to reach about 80 words.

- Make every word count. Rewrite the previous summary to improve the flow and make room for additional information entities.

- Optimize the summary with merging, compression, and removal of non-informative sentences like "the article deals with".

- Summaries should become very dense and concise, but standalone, i.e., easily understandable without the article.

- Missing entities can appear anywhere in the new summary.

- Never remove entities from the previous summary. If you lack space, add fewer new entities.

Remember: Use exactly the same number of words for each summary.

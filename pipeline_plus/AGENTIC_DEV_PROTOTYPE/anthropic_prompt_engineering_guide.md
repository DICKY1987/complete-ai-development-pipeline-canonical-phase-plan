# Complete Claude Prompt Engineering Reference Guide

## 1. Claude 4 Best Practices

### General Principles
- **Be explicit with your instructions**: Claude 4 models respond well to clear, explicit instructions. Be specific about desired output.
- **Add context to improve performance**: Provide context or motivation behind instructions to help Claude understand goals better.
- **Be vigilant with examples & details**: Claude 4 pays attention to details and examples as part of instruction following.

### Control Response Format
- **Tell Claude what to do instead of what not to do**
  - Instead of: "Do not use markdown in your response"
  - Try: "Your response should be composed of smoothly flowing prose paragraphs."

- **Use XML format indicators**
  - Try: "Write the prose sections of your response in `<smoothly_flowing_prose_paragraphs>` tags."

- **Match your prompt style to the desired output**: The formatting style used in your prompt may influence Claude's response style.

### Leverage Thinking & Interleaved Thinking
- Claude 4 offers thinking capabilities especially helpful for tasks involving reflection after tool use or complex multi-step reasoning.

### Optimize Parallel Tool Calling
- Claude 4 models excel at parallel tool execution with ~100% parallel tool use success rate with minor prompting.

### Reduce File Creation in Agentic Coding
- Claude 4 may create new files for testing and iteration purposes.
- If you prefer to minimize file creation, instruct Claude to clean up after itself.

### Enhance Visual and Frontend Code Generation
- Provide explicit encouragement for complex, detailed, and interactive designs
- Use modifiers like:
  - "Include as many relevant features and interactions as possible"
  - "Add thoughtful details like hover states, transitions, and micro-interactions"
  - "Create an impressive demonstration showcasing web development capabilities"
  - "Apply design principles: hierarchy, contrast, balance, and movement"

### Migration Considerations (from Sonnet 3.7 to Claude 4)
- Be specific about desired behavior
- Frame instructions with modifiers that encourage quality and detail
- Request specific features explicitly (animations, interactive elements)

## 2. Tool Use with Claude

### How Tool Use Works
Claude supports two types of tools:

#### Client Tools
- User-defined custom tools
- Anthropic-defined tools (computer use, text editor) requiring client implementation

**Workflow:**
1. Provide Claude with tools and user prompt
2. Claude decides to use a tool
3. Execute the tool and return results
4. Claude uses tool result to formulate response

#### Server Tools
- Tools that execute on Anthropic's servers (web search)
- Different workflow - Claude executes automatically

### Pricing
Tool use requests are priced based on:
- Total number of input tokens (including tools parameter)
- Number of output tokens generated
- For server-side tools: additional usage-based pricing

## 3. Prompt Templates and Variables

### When to Use
Use prompt templates and variables when you expect any part of your prompt to be repeated in another call to Claude.

### Benefits
- **Consistency**: Ensure consistent structure across multiple interactions
- **Efficiency**: Easily swap out variable content without rewriting entire prompt
- **Testability**: Quickly test different inputs and edge cases
- **Scalability**: Simplify prompt management as application grows
- **Version control**: Track changes to prompt structure over time

### Variable Format
In Anthropic Console, variables are denoted with `{{double brackets}}`

**Example:**
```
Translate the following English text to Spanish: {{text_to_translate}}
```

## 4. Prompt Generator

The prompt generator is a tool that guides Claude to generate high-quality prompt templates tailored to specific tasks. It follows prompt engineering best practices and helps solve the "blank page problem" by providing a jumping-off point for further testing and iteration.

Available in the Anthropic Console and as a Google Colab notebook.

## 5. Prompt Improver

### How It Works
The prompt improver enhances prompts in 4 steps:
1. **Example identification**: Locates and extracts examples from prompt template
2. **Initial draft**: Creates structured template with clear sections and XML tags
3. **Chain of thought refinement**: Adds detailed reasoning instructions
4. **Example enhancement**: Updates examples to demonstrate new reasoning process

### What You Get
- Detailed chain-of-thought instructions
- Clear organization using XML tags
- Standardized example formatting
- Strategic prefills

### When to Use
Best for:
- Complex tasks requiring detailed reasoning
- Situations where accuracy is more important than speed
- Problems where Claude's current outputs need significant improvement

### Test Case Generator
Use the Test Case Generator to create sample inputs and ideal outputs for your prompts.

## 6. Be Clear, Direct, and Detailed

### The Golden Rule
Show your prompt to a colleague with minimal context. If they're confused, Claude will likely be too.

### How to Be Clear
- **Give Claude contextual information**:
  - What the task results will be used for
  - What audience the output is meant for
  - What workflow the task is part of
  - The end goal or successful completion criteria

- **Be specific about what you want Claude to do**
- **Provide instructions as sequential steps**: Use numbered lists or bullet points

## 7. Multishot Prompting (Using Examples)

### Power of Examples
Include 3-5 diverse, relevant examples to show Claude exactly what you want. More examples = better performance, especially for complex tasks.

### Make Examples Effective
- **Relevant**: Examples mirror your actual use case
- **Diverse**: Cover edge cases and potential challenges
- **Clear**: Wrapped in `<example>` tags (multiple nested within `<examples>` tags)

### Example Structure
```xml
<examples>
<example>
Input: [example input]
Output: [expected output]
</example>
</examples>
```

## 8. Chain of Thought Prompting

### Why Let Claude Think?
- **Accuracy**: Stepping through problems reduces errors
- **Coherence**: Structured thinking leads to more cohesive responses
- **Debugging**: See Claude's thought process to pinpoint unclear prompts

### When Not to Use
- Increased output length may impact latency
- Not all tasks require in-depth thinking

### Techniques (Least to Most Complex)
1. **Basic prompt**: Include "Think step-by-step"
2. **Guided prompt**: Outline specific steps for Claude to follow
3. **Structured prompt**: Use XML tags like `<thinking>` and `<answer>` to separate reasoning from final answer

## 9. XML Tags for Structure

### Why Use XML Tags?
- **Clarity**: Clearly separate different parts of your prompt
- **Accuracy**: Reduce errors from Claude misinterpreting prompt parts
- **Flexibility**: Easily find, add, remove, or modify prompt parts
- **Parseability**: Makes it easier to extract specific parts of Claude's response

### Best Practices
- **Be consistent**: Use same tag names throughout prompts
- **Nest tags**: Use `<outer><inner></inner></outer>` for hierarchical content
- **Power user tip**: Combine XML tags with other techniques like multishot prompting (`<examples>`) or chain of thought (`<thinking>`, `<answer>`)

### Common XML Tags
- `<instructions>`
- `<example>`
- `<formatting>`
- `<thinking>`
- `<answer>`
- `<context>`

## 10. System Prompts (Role Prompting)

### The Power of Roles
Use the system parameter to give Claude a role. This is the most powerful way to use system prompts.

### System Prompt Tips
- Use system parameter to set Claude's role
- Put task-specific instructions in the user turn instead
- Experiment with different roles for different perspectives

### Example System Prompt
```python
system="You are a seasoned data scientist at a Fortune 500 company."
```

### Role Impact Examples
- Without role: Generic analysis
- With role (General Counsel): Catches critical legal issues, provides professional opinion
- With role (CFO): Delivers actionable financial insights, strategic recommendations

## 11. Prefill Claude's Response

### What is Prefilling?
Guide Claude's responses by prefilling the Assistant message. Claude's response continues from where the prefill leaves off.

### Use Cases
- Control output formatting
- Skip preambles
- Enforce specific formats (JSON, XML)
- Maintain character consistency in roleplay

### Important Notes
- **Only available for non-extended thinking modes**
- Prefill content cannot end with trailing whitespace
- Cannot prefill extended thinking

### Examples
- Force JSON output: `{`
- Maintain character: `[CHARACTER_NAME]:`

## 12. Chain Complex Prompts

### Why Chain Prompts?
- **Accuracy**: Each subtask gets Claude's full attention
- **Clarity**: Simpler subtasks mean clearer instructions
- **Traceability**: Easily pinpoint and fix issues

### When to Chain
Use for multi-step tasks like:
- Research synthesis
- Document analysis
- Iterative content creation
- Multi-step analysis
- Content creation pipelines
- Data processing workflows

### How to Chain
1. **Identify subtasks**: Break task into distinct, sequential steps
2. **Structure with XML**: Use XML tags for clear handoffs
3. **Single-task goal**: Each subtask should have one clear objective
4. **Iterate**: Refine subtasks based on performance

### Advanced: Self-Correction Chains
Chain prompts to have Claude review its own work for error catching and refinement.

## 13. Extended Thinking Tips

### Technical Considerations
- Minimum thinking budget: 1024 tokens
- Start with minimum budget and increase incrementally
- For workloads above 32K tokens, use batch processing
- Extended thinking performs best in English
- For thinking below minimum budget, use standard mode with traditional chain-of-thought

### Prompting Techniques
- **Use general instructions first**, then troubleshoot with step-by-step if needed
- Claude's creativity may exceed human ability to prescribe optimal thinking process
- Start with generalized instructions, read thinking output, then iterate

### Multishot with Extended Thinking
- Works well with extended thinking
- Include examples using XML tags like `<thinking>` or `<scratchpad>`
- Claude will generalize patterns to formal extended thinking process

### Maximizing Instruction Following
- Be clear and specific
- For complex instructions, break into numbered steps
- Allow enough budget for full instruction processing

### Using for Debugging
- Use thinking output to debug Claude's logic
- Don't pass extended thinking back in user text
- Don't manually change output after thinking block

### Long Outputs and Longform Thinking
- Excels at generating large amounts of bulk data and longform text
- Try prompts like "Please create an extremely detailed table of..."
- For very long outputs (20,000+ words):
  - Request detailed outline with word counts
  - Ask Claude to index paragraphs to outline
  - Maintain specified word counts

### Reflection and Error Handling
- Ask Claude to verify work with simple tests
- Instruct model to analyze if previous step achieved expected result
- For coding tasks, ask Claude to run through test cases in thinking

## 14. Long Context Tips

### Essential Tips for Long Context (200K tokens)

#### 1. Put Longform Data at the Top
- Place long documents and inputs (~20K+ tokens) near the top of prompt
- Put above queries, instructions, and examples
- Can improve response quality by up to 30%

#### 2. Structure with XML Tags
When using multiple documents:
```xml
<document>
  <source>document_name.pdf</source>
  <document_content>
    [content here]
  </document_content>
</document>
```

#### 3. Ground Responses in Quotes
- For long document tasks, ask Claude to quote relevant parts first
- Helps Claude cut through "noise" of document contents

## Best Practices Summary

### Universal Principles
1. **Be explicit and specific** in all instructions
2. **Use XML tags** to structure complex prompts
3. **Provide context** for better understanding
4. **Use examples** to guide behavior (3-5 diverse examples)
5. **Test with colleagues** - if they're confused, Claude will be too

### Format Control
- Tell Claude what TO do, not what NOT to do
- Match prompt style to desired output
- Use structured tags for clear organization

### Complex Tasks
- Break into subtasks (prompt chaining)
- Use chain of thought for reasoning
- Consider extended thinking for complex problems
- Put long documents at the top of prompts

### Role and Context
- Use system prompts for role assignment
- Provide workflow context and end goals
- Explain what results will be used for

### Testing and Iteration
- Start simple, then add complexity
- Use prompt improver for enhancement
- Generate test cases for validation
- Iterate based on Claude's performance
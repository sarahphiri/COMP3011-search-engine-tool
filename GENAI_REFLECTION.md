# GenAI Reflection Notes

## Tools Used

I used Generative AI as a support tool during the development of this coursework. It was used for planning, code explanation, debugging support, and generating ideas for tests and documentation.

## Where GenAI Helped

GenAI helped me plan the project structure by separating the crawler, indexer, search logic, and command-line interface into different modules. This made the implementation easier to test and explain.

It also helped me understand how an inverted index could be represented using a nested dictionary. I adapted this into a structure that stores each word with the pages it appears on, its frequency, and its positions.

GenAI was also useful when thinking of edge-case tests, such as empty queries, punctuation, capitalisation, missing fields, and missing index files.

## Where GenAI Needed Correction

Some AI suggestions were too generic and did not fully match the coursework requirements. For example, some early search suggestions returned pages containing any query term, but the coursework required meaningful multi-word query handling, so I changed the logic to return pages containing all query terms.

Some generated examples also needed to be adjusted to match the actual HTML structure of `quotes.toscrape.com`.

## Impact on Learning

Using GenAI helped me move faster, but it did not remove the need to understand the code. I still had to test the implementation, debug errors, adapt suggestions, and make design decisions myself.

The main learning benefit was that it helped me compare different implementation approaches. However, I had to be careful not to rely on suggestions without checking whether they were correct or suitable for the coursework.

## Final Reflection

Overall, GenAI was useful as a development support tool, but the final implementation required manual validation, testing, and refinement. The most important part was ensuring that I could explain every design decision and justify how the code works.
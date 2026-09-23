# The idea in one minute

A useful chart preserves the answer to the question you are asking. If you want to compare spread, showing only the means is not enough. If you want to compare category shares, the chart must retain the proportions.

This study makes that idea measurable. It draws candidate charts, asks an explicitly defined image-reading algorithm to recover the requested quantities, and measures the error. It then asks a harder question: does selecting a different chart for every dataset improve on using one strong chart for that task?

The answer is conditional. In the main empirical analysis, selection does not consistently improve on a strong default. In new synthetic tests, selection helps with some tasks and harms or ties others. A different way of reading the same pixels changes some rankings.

That is why the paper reports the question, candidate charts, image reader, display conditions, baseline and failures together. A high score is interpretable only within those conditions. It is not a measure of human understanding.

The practical contribution is a way to test chart-selection claims fairly, including claims that turn out not to beat a simple alternative. The package provides the complete inputs and procedures so other researchers can replace parts of the method and check whether their conclusions survive.

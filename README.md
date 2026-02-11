# Program Generator
I developed a Python application that interacts with the **OpenAI API** to generate Python code based on user prompts.
The application, written in **Python**, prompts the user for the type of program they want to generate.
If the user doesn’t provide an input, it selects a random problem from a predefined list of challenging programming tasks.
The generated code includes not only the solution to the problem but also accompanying unit tests to ensure correctness.
The application saves the generated code to a file and executes it using the Subprocess Module.
If the code fails, the application captures the errors, refines the prompt, and requests a corrected version from OpenAI, repeating this process up to five times to ensure successful code generation.
The application also includes optional features like colored console output using Colorama, code formatting with black.

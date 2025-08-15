# CodeSignal Industry Coding Framework Mock Assesments

The purpose of this repo is to have a way to practice for the CodeSignal ICF Assesment. As you may have noticed, there are not many resources for practicing for this assesment. One good one is https://github.com/PaulLockett/CodeSignal_Practice_Industry_Coding_Framework/tree/main. There are some typos in it, but it is definitley a good place to start.

However, it only contains one mock assesment, so my goal is to develop this repo to be a generalizable practice ground by having an AI agent (e.g. ChatGPT) generate mock assesments on the fly in a consistent manner. 

Essentially the idea is to streamline the process as much as possible. This repo will have a prompt.txt file that will be used to prompt the agent, along with the "CodeSignal Skills Evaluation Framework.pdf" file to give it an idea of what the questions should and should not focus on, along with an example. I will probably publish an agent on ChatGPT that uses the prompt.txt as a system prompt and the pdf file as a knowledge base once everything is up and running though. 

Once the user says, "start", the agent will start creating the question for level 1. It will output a high level description of the project, the functions to implement at this level, and a csv file in the format 

"function,input,input_dtype,output,output_dtype"

where each line in the csv file should be executed in series. 

The test cases will be run based on the csv file. Once the user finishes this level and passes the test cases, the user can prompt the agent for the next level by saying "next". This is done until all four levels are completed. 

This should give a more realistic testing environment, since in the assesment, each level is only presented once the previous level is completed.

The assesments folder is empty, and is meant to be where the user uploads any information
# CodeSignal Industry Coding Framework Mock Assesment AI Agent

The purpose of this repository is to have a way to practice for the CodeSignal ICF Assesment. As you may have noticed, there are not many resources for practicing for this assesment. A good one is https://github.com/PaulLockett/CodeSignal_Practice_Industry_Coding_Framework/tree/main. There are some typos in it, but it is definitley a good place to start.

However, it only contains one mock assesment, so my goal is to develop this repository to be a generalizable practice ground by having an AI agent (e.g. ChatGPT) generate mock assesments on the fly in a consistent manner. 

Essentially the idea is to streamline the process as much as possible. This repository will have a prompt.txt file that will be used to prompt the agent, along with the "CodeSignal Skills Evaluation Framework.pdf" file to give it an idea of what the questions should and should not focus on, along with an example. 

## Getting Started

I have published a premade agent using ChatGPT (version GPT5) at https://chatgpt.com/g/g-689f50f4514081918a47d77550c6168e-codesignal-mock-assesment-agent.
It uses the prompt.txt as a system prompt and the pdf file as a knowledge base. 

Before using the agent, the user should copy the assesments/base folder to assesments/my_first_assesment and only edit the files in assesments/my_first_assesment throughout the assesment. 

Once the user says, "start", the agent will output a high level description of the generated project. The user may also say "start {easy/medium/hard}" to specify a difficulty. The default difficulty is easy. 

| Difficulty | Description |
|------------|-------------|
| easy       | A recently graduated computer science major should be able to finish the assesment in the allocated time. |
| medium     | An industry software engineer with 3-5 years experience should be able to finish in the allocated time. |
| hard       | An industry senior (10-15 years experience) software engineer should be able to finish in the allocated time. |

Note that increasing difficulty does NOT correspond to increasing the number of tasks, it corresponds to
increasing the complexity of each task. Every difficulty has approximately the same number of tasks. The target allocated time is 90 minutes, as that is what I have read is typical for the ICF.

Every time the user says "next", the agent provides the information required to complete
the next level. This information includes:

1. the method the user should implement for the level, with the format:

        def EXAMPLE_METHOD(arg1: int, arg2: str, kwarg1: str=""):
            '''
            description:    this is an example description of the method to implement
            params:         arg1 (int):     an example integer
                            args2 (str):    an example string
                            kwarg (str):    an example kwarg string
            returns:        None | str:     an example return value
            '''

2. a json formatted string in the format:

```json
{
    "testcase": [
        {
            "method": "method1", 
            "args": ["arg1", "arg2"], 
            "kwargs": {"kw1": "kwarg1"}, 
            "output": "output1"
        }
    ]
}
```

here is an example of what it looks like:

```json
{
    "0": [
        {"method": "FILE_UPLOAD", "args": ["cars.txt", "200kb"], "kwargs": {}, "output": null},
        {"method": "FILE_GET", "args": ["cars.txt"], "kwargs": {}, "output": 200}
    ],
    "1": [
        {"method": "FILE_UPLOAD", "args": ["cars.txt", "100kb"], "kwargs": {}, "output": null},
        {"method": "FILE_COPY", "args": ["cars.txt", "cars2.txt"], "kwargs": {}, "output": null},
        {"method": "FILE_GET", "args": ["cars2.txt"], "kwargs": {}, "output": 100},
        {"method": "FILE_SEARCH", "args": ["ca"], "kwargs": {}, "output": ["cars.txt", "cars2.txt"]}
    ]
}
```

All the user has to do is copy the agent's generated json string and paste it in the corresponding json file (e.g. assesments/my_first_assesment/testcases/level1.json for level 1). The user may then implement their solution in assesments/my_first_assesment/answer.py. To run the testcases, simply run

```shell
cd assesments
python run_test_cases.py --assesment_dir my_first_assesment --level 1
```

The test cases will be run based on the json file. Once the user finishes this level and passes the test cases, the user can prompt the agent for the next level by saying "next". This is done until all four levels are completed. 

This should give a more realistic testing environment and allow users to practice for the ICF assesment.

    
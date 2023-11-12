[![build and deploy Speckle functions](https://github.com/specklesystems/speckle_automate-data_standards_checker/actions/workflows/main.yml/badge.svg)](https://github.com/specklesystems/speckle_automate-data_standards_checker/actions/workflows/main.yml)

# Speckle Automate Function: Data Standards Checker with IDS and bsDD

## Overview
This repository contains the Data Standards Checker function for Speckle Automate, designed to validate AEC models against the Information Delivery Specification (IDS) and BuildingSMART Data Dictionary (bsDD) standards. It showcases the ability of Speckle to ensure that models adhere to these established data standards.

## ⚠️ Disclaimer: Conceptual Demonstration Only
**IMPORTANT: This function is a conceptual demonstration and not a functional implementation. It is intended to exhibit the possibilities of aligning AEC models with IDS and bsDD standards within Speckle Automate.**

## Functionality
- **IDS and bsDD Compliance:** Validates models against IDS requirements and bsDD standards.
- **Automated Standard Checking:** Demonstrates the potential for automated compliance checks.
- **Model Data Alignment:** Ensures model data aligns with the specified standards for consistency and accuracy.
- **Reporting and Insights:** Generates reports detailing compliance and areas requiring attention.

### How It Works
The function analyzes AEC models in Speckle, comparing their elements and metadata against the requirements set by IDS and the classifications and properties defined in bsDD.

### Potential Use Cases
- **Quality Assurance:** Ensures model data quality and standard adherence.
- **Regulatory Compliance:** Assists in meeting industry-specific compliance requirements.
- **Data Integrity:** Maintains the integrity of model data throughout the project lifecycle.

## Getting Started
1. **Clone the Repository**: Set up this repository in your local or cloud environment.
2. **Install Dependencies**: Follow the instructions to install necessary dependencies.
3. **Configure and Run**: Set up your Speckle server connection and run the function for conceptual testing.

## Contributing
Contributions in the form of ideas, discussions, or potential enhancements are welcome. Please open issues or pull requests for any suggestions.

## Contact
For more information or to provide feedback, please contact [Contact Information].

---

**Note:** This repository is intended for demonstration and discussion around standard compliance in Speckle Automate using IDS and bsDD.


## Using this Speckle Function
1. **Create a New Speckle Automation**: Set up in the Speckle dashboard.
2. **Configure the Function**: Choose the "Basic Clash Analysis" function.
3. **Run and Review**: Execute the function and review the clash reports.



1. [Register](https://automate.speckle.dev/) your Function with [Speckle Automate](https://automate.speckle.dev/) and select the Python template.
1. A new repository will be created in your GitHub account.
1. Make changes to your Function in `main.py`. See below for the Developer Requirements, and instructions on how to test.
1. To create a new version of your Function, create a new [GitHub release](https://docs.github.com/en/repositories/releasing-projects-on-github/managing-releases-in-a-repository) in your repository.


## Developer Requirements

1. Install the following:
    - [Python 3](https://www.python.org/downloads/)
    - [Poetry](https://python-poetry.org/docs/#installing-with-the-official-installer)
1. Run `poetry shell && poetry install` to install the required Python packages.

## Building and Testing

The code can be tested locally by running `poetry run pytest`.

### Building and running the Docker Container Image

Running and testing your code on your own machine is a great way to develop your Function; the following instructions are a bit more in-depth and only required if you are having issues with your Function in GitHub Actions or on Speckle Automate.

#### Building the Docker Container Image

Your code is packaged by the GitHub Action into the format required by Speckle Automate. This is done by building a Docker Image, which is then run by Speckle Automate. You can attempt to build the Docker Image yourself to test the building process locally.

To build the Docker Container Image, you will need to have [Docker](https://docs.docker.com/get-docker/) installed.

Once you have Docker running on your local machine:

1. Open a terminal
1. Navigate to the directory in which you cloned this repository
1. Run the following command:

    ```bash
    docker build -f ./Dockerfile -t speckle_automate_python_example .
    ```

#### Running the Docker Container Image

Once the image has been built by the GitHub Action, it is sent to Speckle Automate. When Speckle Automate runs your Function as part of an Automation, it will run the Docker Container Image. You can test that your Docker Container Image runs correctly by running it locally.

1. To then run the Docker Container Image, run the following command:

    ```bash
    docker run --rm speckle_automate_python_example \
    python -u main.py run \
    '{"projectId": "1234", "modelId": "1234", "branchName": "myBranch", "versionId": "1234", "speckleServerUrl": "https://speckle.xyz", "automationId": "1234", "automationRevisionId": "1234", "automationRunId": "1234", "functionId": "1234", "functionName": "my function", "functionLogo": "base64EncodedPng"}' \
    '{}' \
    yourSpeckleServerAuthenticationToken
    ```

Let's explain this in more detail:

`docker run --rm speckle_automate_python_example` tells Docker to run the Docker Container Image that we built earlier. `speckle_automate_python_example` is the name of the Docker Container Image that we built earlier. The `--rm` flag tells docker to remove the container after it has finished running, this frees up space on your machine.

The line `python -u main.py run` is the command that is run inside the Docker Container Image. The rest of the command is the arguments that are passed to the command. The arguments are:

- `'{"projectId": "1234", "modelId": "1234", "branchName": "myBranch", "versionId": "1234", "speckleServerUrl": "https://speckle.xyz", "automationId": "1234", "automationRevisionId": "1234", "automationRunId": "1234", "functionId": "1234", "functionName": "my function", "functionLogo": "base64EncodedPng"}'` - the metadata that describes the automation and the function.
- `{}` - the input parameters for the function that the Automation creator is able to set. Here they are blank, but you can add your own parameters to test your function.
- `yourSpeckleServerAuthenticationToken` - the authentication token for the Speckle Server that the Automation can connect to. This is required to be able to interact with the Speckle Server, for example to get data from the Model.

## Resources

- [Learn](https://speckle.guide/dev/python.html) more about SpecklePy, and interacting with Speckle from Python.

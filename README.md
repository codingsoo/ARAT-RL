# ARAT-RL

ARAT-RL is a tool designed to find internal server errors in REST APIs using reinforcement learning. 
This work has been published at ASE 2023, "[Adaptive REST API Testing with Reinforcement Learning](https://ieeexplore.ieee.org/document/10298580)".

[Bibtex Citation Here](https://github.com/codingsoo/arat-rl/blob/main/docs/ase2023.bib)

## Quick Start

Install Python3 and Required Packages:

```
pip3 install -r requirements.txt
```

Run ARAT-RL:

```
python3 arat-rl.py Specification_Location Server_URL Runtime_in_Minutes
```

For example:

```
python arat-rl.py spec/features.yaml http://localhost:30100/ 3600
```

After an hour, it will print a report with found internal server errors. The results will be stored in `http_500_error_report.txt`.

## Reproduce the results in our paper.

### Machine Specification

Our experiments were conducted on Google Cloud E2 machines, each with a 24-core CPU and 96 GB of RAM.

### Software Dependencies and Installation

If your OS is Ubuntu 20.04, you can simply run our setup script with `sh setup.sh` command in your terminal.

The following software is required for the experiment:
- Git
- Common utilities (software-properties-common, unzip, wget, gcc, git, vim, libcurl4-nss-dev, tmux, mitmproxy)
- Java 8 and 11
- Maven3
- Python 3 (with pip and virtualenv)
- Python libraries in requirements.txt
- Docker
- .NET 6 Runtime and SDK
- JaCoCo Agent and CLI 0.8.7

### Run tools and services

After installing all the required software, you can run the tools with this command:

```
python run.py [tool's name]
```

This command will run the tool and all the services in our benchmark for an hour. Possible tool names are `arat-rl`, `morest`, `evomaster-blackbox`, and `restler`. If you want to run an ablation study, you can set the tool names to: `no_prioritization`, `no_feedback`, and `no_sampling`.

### Collect the results

To collect the results, use the following command:

```
python parse_log.py
```

This will gather the coverage and number of responses for status codes 2xx, 4xx, and 5xx. The results will be stored in the `res.csv` file. Additionally, any detected bugs will be recorded in the `errors.json` file. + We noticed a bug when counting the unique number of 500 errors (we are not able to detect the ping pong between functions), so we recommend to count the number of operations that produce 500 status code.

### Review the Results

The `results` directory contains the results for each tool and each service. These results include the achieved code coverage, the number of obtained status codes, the number of bugs found, and detailed bug reports.

# 2.2 Intro to Mage

## 2.2.1 What is Mage
an open-source pipeline tool for orchestrating, transforming, and monitoring data.

![Mage Basics](./img/mage-basics.png)

- projects: homebase
- pipelines: a series of tasks or workflow
    - workflow that executes some data operation, kind of DAGs
    - pipelines can contain Blocks (written in SQL, Python, or R) and charts
    - represented by a YAML file
- blocks: atomic unit of transformation in Mage -> Extract, Transform, Load (ETL)
    - files that can be executed independently or within a pipeline
    - blocks -> Directed Acyclic Graphs (DAGs) -> pipelines
    - reusable

Advantage:
- support hyrid environment
    - use Mage GUI or other IDEs for interactive development, VSCode for example
    - it use `blocks` as a testable and reusable pieces of code
- improved developer experience
    - code and test in parallel
    - reduce yoru dependencies, switch tool less, be efficient 

## 2.2.2 Configuring Mage

We will setting up Mage on our local machine. 
- First, clone Mage zoomcamp repository [here](https://github.com/mage-ai/mage-zoomcamp)
- `cd` to the cloned directory and rename `dev.env` file to just `.env` (without the `dev` prefix)
- Run `docker-compose build` to build the docker image and start the container using `docker-compose up` command
- Open your browser and go to `http://localhost:6789` to acces the Mage instance.

## 2.2.3 Building A Simple Pipeline
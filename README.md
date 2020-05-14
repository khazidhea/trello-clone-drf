Most of my work is done it private repos. But this is a small project I'm slowly working on specifically to showcase my code to potential employers. This repo contains an API for a task management system. It has a few rules:

- A Task has an author, an assignee and a few approvers
- Task should be approved by all approvers, then it goes into "in progress" state
- An assignee can mark task as completed
- Author can request changes
- Only superuser can close a task

I'm using DDD approach to trying not to tightly couple with django framework, abandoning the "fat model" approach and only using models for storing data. Most of my logic is contained in a service layer. I'm using transitions package to treat task as final state machines. 

At the same time this all was built using TDD, writing tests first. I'm using:

- pytest as test runner
- mypy for type hinting
- flake8 for linting
- poetry for dependency management

Known issues, to be fixed soon:
- It's not dockerized
- There is no CI\CD pipeline yet.
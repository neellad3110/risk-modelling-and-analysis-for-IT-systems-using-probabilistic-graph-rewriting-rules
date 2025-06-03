[comment]: # (You may find the following markdown cheat sheet useful: https://www.markdownguide.org/cheat-sheet/. You may also consider using an online Markdown editor such as StackEdit or makeareadme.) 

## Project title: Risk Modelling and Analysis for IT Systems using Probabilistic Graph Rewriting Rules 

### Student name: Neel Vinod Lad

### Student email: nvl2@student.le.ac.uk

### Project description: 
Modern business IT systems are complex and interconnected, involving users, services, servers, and data
flows that expose them to a wide range of cyber threats. System administrators often lack a formal,
systematic method for identifying vulnerabilities, quantifying risks, and understanding the consequences
of potential attacks. Existing risk assessment tools are typically checklist-based or domain-specific,
lacking adaptability, precision, or automation. There is a growing need for a model-driven, customizable
approach that captures both technical and contextual system information and supports informed decisionmaking.

This project proposes an approach to analyse risk in business IT systems from the perspective of system
administrators. The central idea is to model the current state of an organization’s IT infrastructure
including users, servers, connections, access rights, and contextual attributes as a typed attributed
multigraph, referred to as the business graph. Vulnerabilities and attack patterns are captured as graph
transformation rules, where each rule specifies a vulnerability pattern (left-hand side), an associated
attack rate (exponential frequency), and probabilistic outcomes (possible consequences if the attack
occurs). The complete set of these rules and type graph forms a Risk Specification (RS). Risk analytics
is performed by detecting pattern matches (i.e., vulnerabilities) in the business graph, estimating the
attack surface, calculating the risk probability based on frequency and success likelihood, and computing
the expected impact using cost models. The system’s semantics are formalized as a Continuous-Time
Markov Decision Process (CTMDP), enabling stochastic simulation and risk propagation over time. This
structured approach allows for customizable, domain-specific security modelling, and provides decision
support for administrators seeking to prioritize vulnerabilities and mitigate risk efficiently.

### List of requirements (objectives): 

[comment]: # (You can add as many additional bullet points as necessary by adding an additional hyphon symbol '-' at the end of each list) 

Essential:
- [Essential requirement 1]
- [Essential requirement 2]
- [Essential requirement 3]
- [Essential requirement *n*]

Desirable:
- [Desirable requirement 1]
- [Desirable requirement 2]
- [Desirable requirement 3]
- [Desirable requirement *n*]

Optional:
- [Optional requirement 1]
- [Optional requirement 2]
- [Optional requirement 3]
- [Optional requirement *n*]


## Information about this repository
This is the repository that you are going to use **individually** for developing your project. Please use the resources provided in the module to learn about **plagiarism** and how plagiarism awareness can foster your learning.

Regarding the use of this repository, once a feature (or part of it) is developed and **working** or parts of your system are integrated and **working**, define a commit and push it to the remote repository. You may find yourself making a commit after a productive hour of work (or even after 20 minutes!), for example. Choose commit message wisely and be concise.

Please choose the structure of the contents of this repository that suits the needs of your project but do indicate in this file where the main software artefacts are located.

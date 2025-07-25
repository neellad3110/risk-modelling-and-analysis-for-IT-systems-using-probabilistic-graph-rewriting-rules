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

### Essential:
- **Foundational Literature and Tooling Review:** <br>
    - Before developing a prototype, it is essential to build a strong foundational understanding of graph-based modeling and transformation within the context of software engineering. This includes a solid grasp of the MITRE ATT&CK framework for identifying and categorizing adversarial behaviors, as well as hands-on familiarity with graph rewriting tools such as GROOVE for pattern matching and rule application. Additionally, background knowledge of Continuous-Time Markov Decision Processes (CTMDPs) and probabilistic model checking—using tools like PRISM—is crucial for accurately simulating attack propagation and analyzing risk over time. These foundational elements are critical to effectively designing and implementing the proposed risk modeling system.


- **Typed Attributed Multigraph Representation:**<br> 
    - The system must support modelling IT infrastructures as typed attributed multigraphs, including nodes (users, servers, devices, etc.), edges (relations), and attributes (e.g., has_access_to, owns, runs_on, alerts role).

- **Formal Rule Specification Language:**<br>
    - There must be a machine-readable format (e.g., YAML, JSON) for defining graph rewriting rules with vulnerability patterns, attack rates, and probabilistic outcomes.

- **JSON to Groove Automation:**<br>
    - An automated script which will generate Groove based notations for type graph, host graph and risk rules. The script should take consider all nodes, edges, relations, LHS pattern and RHS (outcomes) of risk rule will support Groove graph modeling syntax. 
	
- **Probabilistic Risk Analytics:**
  - For each pattern match, the system must estimate risk using attack rates per year, outcome probabilities of attack, and costs to company.

- **MITRE ATT&CK:**
  - Risk rules must be grounded in real-world attack techniques (e.g., MITRE ATT&CK).
 
- **Model Consistency Checking:**
  - The system must validate that the graph and rules are consistent and compatible for matching.

### Desirable:

- **Graph Visualization:**<br>
  - Visual representation of the business graph and attack surface (e.g., using, GROOVE, PlantUML) should be useful.

- **Modular Rule Organization:**<br>
  - Rules should be organized by tactics/techniques or attack phases for easier management and extensibility.

- **Export/ Derive to Model Checker:**
  - Ability to export/derive the system model to tools like PRISM or STORM for formal CTMDP analysis should be implemented.

- **Continuous-Time Markov Decision Process (CTMDP) Integration:**
  - Formal semantics and simulation using CTMDP tools (e.g., PRISM, STORM) for advanced risk propagation analysis is desirable.

### Optional:

- **Use of NLP or LLMs for suggesting recovery or precautions:**
  - After analysing attack patterns its outcomes LLMs can be used to generate some suggestions for recovery and necessary precautions. 

- **Interactive Dashboard:**
  - GUI dashboard could provide an interactive exploration of the business graph and risk analytics.

- **OCL-like Constraints:**
  - Support for expressing and enforcing may provide advanced constraints on pattern matching.

## Information about this repository
This is the repository that you are going to use **individually** for developing your project. Please use the resources provided in the module to learn about **plagiarism** and how plagiarism awareness can foster your learning.

Regarding the use of this repository, once a feature (or part of it) is developed and **working** or parts of your system are integrated and **working**, define a commit and push it to the remote repository. You may find yourself making a commit after a productive hour of work (or even after 20 minutes!), for example. Choose commit message wisely and be concise.

Please choose the structure of the contents of this repository that suits the needs of your project but do indicate in this file where the main software artefacts are located.

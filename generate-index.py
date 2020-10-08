import mistune
import collections

markdown = mistune.create_markdown(renderer=mistune.AstRenderer())


def get_tree(file_name):
    tree = collections.defaultdict(list)
    with open(file_name, "r") as f:
        for x in markdown(f.read()):
            if x["level"] == 2:
                section_title = x["children"][0]["text"]
            if x["level"] == 1:
                for child in x["children"]:
                    _page_title = child["children"][0]["children"][0]["children"][0][
                        "text"
                    ]
                    md_file_name = child["children"][0]["children"][0]["link"]
                    tree[section_title].append(md_file_name)
    return tree


def print_frontpage():
    print("""
===================================
The Norwegian Academic HPC Services
===================================

The Norwegian academic HPC infrastructure is maintained by the `Sigma2
Metacenter <https://sigma2.no/metacenter>`__, which is a joint
collaboration between `UiO <https://www.uio.no>`__,
`UiB <https://www.uib.no>`__, `NTNU <https://www.ntnu.no>`__,
`UiT <https://uit.no>`__, and `UNINETT
Sigma2 <https://www.sigma2.no/>`__.

This website (https://documentation.sigma2.no/) holds technical
documentation about the compute and storage resources. For more general
information and service overview, please also see https://www.sigma2.no.

**Latest news and announcements** are posted at the \ `Metacenter
OpsLog <https://opslog.sigma2.no>`__ and the
[@MetacenterOps](https://twitter.com/MetacenterOps) Twitter channel.

--------------

Compute, storage, pre/post-processing, visualization, machine learning
----------------------------------------------------------------------

We offer compute resources (`Betzy <hpc_machines/betzy.md>`__,
`Fram <hpc_machines/fram.md>`__, `Saga <hpc_machines/saga.md>`__, and
`Stallo <https://hpc-uit.readthedocs.io>`__), storage resources
(`NIRD <files_storage/nird.md>`__), as well as the `NIRD
Toolkit <https://www.sigma2.no/nird-toolkit>`__ platform for pre- and
post-processing analysis, data intensive processing, visualization,
artificial intelligence, and machine learning.


First time on a supercomputer?
------------------------------

Please read the **GETTING STARTED** section (left sidebar). In the
sidebar overview you will also find technical details about the
machines, instructions for using installed software, for submitting
jobs, storage, and code development.

Please do not hesitate to write to support@metacenter.no if you find
documentation sections which are not clear enough or have suggestions
for improvements. Such a feedback is very important to us and will
count.


How to get the most out of your allocation
------------------------------------------

We want to support researchers in getting the most out of the
high-performance computing services. When supporting users, we see that
these problems are very frequent: - **Reusing outdated scripts** from
colleagues without adapting them to optimal parameters for the cluster
at hand and thus leaving few cores idle. Please check at least how many
cores there are on a particular cluster node. - **Requesting too much
memory** which leads to longer queuing and less resource usage. Please
check `how to choose memory
settings </jobs/choosing_memory_settings.md>`__. - Requesting **more
cores than the application can effectively use** without studying the
scaling of the application. You will get charged more than needed and
others cannot run jobs. If others do this, your own jobs queue. -
**Submitting jobs to the wrong queue** and then queuing longer than
needed. Please take some time to study the different job types.

If you are unsure about these, please contact us via
support@metacenter.no and we will help you to use your allocated
resources more efficiently so that you get your research results faster.

--------------

Acknowledging use of national HPC infrastructure
------------------------------------------------

Projects are required to acknowledge the use of the national
e-infrastructure resources in their scientific publications. Papers,
presentations and other publications that feature work that relied on
Sigma2 should include an acknowledgement following this template:

::

   The computations/simulations/[SIMILAR] were performed on resources provided by
   UNINETT Sigma2 - the National Infrastructure for High Performance Computing and
   Data Storage in Norway


Text is licensed CC-BY
----------------------

Unless explicitly noted, all text on this website is made available
under the `Creative Commons Attribution license
(CC-BY-4.0) <https://creativecommons.org/licenses/by/4.0/>`__ with
attribution to the Sigma2/Metacenter.

--------------

""")


def print_section(section, file_names):
    print("\n\n.. toctree::")
    print("   :maxdepth: 1")
    print(f"   :caption: {section}\n")
    for file_name in file_names:
        print(f"   {file_name}")


tree = get_tree("SUMMARY.md")

print_frontpage()
for section in tree:
    print_section(section, tree[section])
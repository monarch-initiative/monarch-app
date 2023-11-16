# Description: Get the current resources from the monarch-documentation repository
from pathlib import Path
import urllib.request
import yaml


outdir = Path(__file__).parent.parent / "frontend" / "src" / "pages" / "resources"
script_dir = Path(__file__).parent
resources_file = outdir / "resources.json"
resources_url = "https://raw.githubusercontent.com/monarch-initiative/monarch-documentation/main/src/data/resources.yaml"

resources_to_display = {
    "Standards": [
        "Phenopackets",
        "SSSOM",
        "Mapping Commons",
    ],
    "Ontologies": [
        "HPO",
        "MONDO",
        "uPheno"
    ],
    "Tools": [
        # "Monarch KG & API",
        # "Monarch App",
        "OAK",
        "OntoGPT",
        "CurateGPT",
        "LinkML",
        "Semsimian",
        "Exomiser",
        "LIRICAL"
    ]
}

resources_content = {
    "Standards": [
        {
            "name": "Phenopackets",
            "icon": "resource-phenopackets",
            "link": "",
            "description": ""
        },
        {
            "name": "SSSOM",
            "icon": "resource-sssom",
            "link": "",
            "description": ""
        },
        {
            "name": "Mapping Commons",
            "icon": "resource-monarch",
            "link": "",
            "description": ""
        }
    ],
    "Ontologies": [
        {
            "name": "HPO",
            "icon": "resource-hpo",
            "link": "",
            "description": ""
        },
        {
            "name": "MONDO",
            "icon": "resource-mondo",
            "link": "",
            "description": ""
        },
        {
            "name": "uPheno",
            "icon": "resource-upheno",
            "link": "",
            "description": ""
        },
    ],
    "Tools": [
        # {
        #     "name": "Monarch KG & API",
        #     "icon": "",
        #     "link": "",
        #     "description": ""
        # },
        # {
        #     "name": "Monarch App",
        #     "icon": "",
        #     "link": "",
        #     "description": ""
        # },
        {
            "name": "OAK",
            "icon": "resource-oak",
            "link": "",
            "description": ""
        },
        {
            "name": "OntoGPT",
            "icon": "onto-gpt",
            "link": "",
            "description": ""
        },
        {
            "name": "CurateGPT",
            "icon": "curate-gpt",
            "link": "",
            "description": ""
        },
        {
            "name": "LinkML",
            "icon": "resource-linkml",
            "link": "",
            "description": ""
        },
        {
            "name": "Semsimian",
            "icon": "semsimian",
            "link": "",
            "description": ""
        },
        {
            "name": "Exomiser",
            "icon": "resource-exomiser",
            "link": "",
            "description": ""
        },
        {
            "name": "LIRICAL",
            "icon": "lirical",
            "link": "",
            "description": ""
        },
    ]
}

# Get current resources
with urllib.request.urlopen(resources_url) as url:
    resources = yaml.safe_load(url)

for t in resources_content:
    for r in resources_content[t]:
        name = r["name"]
        
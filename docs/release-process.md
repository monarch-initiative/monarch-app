# Monarch Release Process

## Overview

This document describes the steps required to create a new Monarch release.

These releases consist primarily of the following components:

- Monarch Mapping files via [Monarch Mapping Commons](https://github.com/monarch-initiative/monarch-mapping-commons)
- Knowledge Graph via [Monarch Ingest](https://github.com/monarch-initiative/monarch-ingest)
- Data library and API via [Monarch-Py](https://github.com/monarch-initiative/monarch-app/backend)
- Monarch website via [Monarch-App](https://github.com/monarch-initiative/monarch-app/frontend)


## Monarch Mapping Commons

[Monarch Mapping Commons](https://github.com/monarch-initiative/monarch-mapping-commons) is a repository that contains code used to generate the mapping files used in the creation of the Monarch knowledge graph.
The nodes and edges in the knowledge graph come from a variety of sources, and have varying IDs and prefixes.
The mapping files are used to map these IDs to IDs in Monarch's preferred namespaces.

These mapping files are generated via a Jenkins job on a weekly basis, and are stored in the [Monarch Data Bucket](https://data.monarchinitiative.org/mappings/index.html).

## Monarch Ingest (Knowledge Graph)

Monarch's knowledge graph is built using the Monarch Ingest pipeline.
The pipeline is run on a Jenkins server, and the resulting knowledge graph is uploaded to both Monarch's data bucket on Google Cloud, as well as the KG-Hub AWS S3 bucket.

Changes to the Monarch Ingest pipeline are made in the [Monarch Ingest](https://github.com/monarch-initiative/monarch-ingest) repository.

After the knowledge graph has been built, the [QC Dashboard](https://github.com/monarch-initiative/monarch-qc) is used to verify the difference between the new build of the knowledge graph and the previous build.

Once the knowledge graph has been verified, additional steps are required to make the new knowledge graph available to the dev, beta, and production versions of the Monarch website.

### Deploying the Knowledge Graph

#### Deploying to dev

While the Github Actions workflow for Monarch App will automatically update and deploy API & UI code to the dev environment, the knowledge graph must be manually deployed to the dev environment.

Preparing the environment for deployment:

* Make sure dependancies from monarch-stack-v3/README.md are installed
* Ensure secrets are installed in $home/.secrets

To deploy the knowledge graph to the dev environment, follow these steps:

* Checkout (or update) [Monarch Stack V3](https://github.com/monarch-initiative/monarch-stack-v3)
* Source the dev environment: `cd deployment && source site-envs/monarch-dev.env`
* Run the provision script to update the dev environment: `./provision.sh`
* After running the provision script to update the dev environment, a manual restart of the Solr container is necessary:

```
gcloud compute ssh --zone us-central1-a monarch-v3-${TF_VAR_env}-manager -- sudo docker service update --force monarch-v3_solr
```

From this point forward, code updates on the dev environment will be automatically deployed and additional work will happen to finish the work planned for the milestone. Ideally changes to the graph will happen early in the release cycle.

#### Deploying to beta

Once work on the milestone is complete, we need to tag the release in GitHub then we can deploy to the beta environment.

To tag the release, go to the [Monarch App](https://github.com/monarch-initiative/monarch-app) and click on releases. Create a new release with the new version number and click generate release notes. Make any changes to the release notes that are necessary (generally none) and click publish release.

You may want to set an environment variable for the release version to make it easier to copy and paste the version number in the following steps (update for your current version):

```
RELEASE="2024-02-13"
```

First, copy the KG release from monarch-kg-dev to monarch-kg:
```
gsutil cp -r gs://data-public-monarchinitiative/monarch-kg-dev/${RELEASE} gs://data-public-monarchinitiative/monarch-kg/${RELEASE}
```
Then, we need to copy in the archive:
```
gsutil cp -r gs://monarch-archive/monarch-kg-dev/${RELEASE} gs://monarch-archive/monarch-kg/${RELEASE}
```

Within monarch-stack-v3, copy the latest release env file to a new env, for example: `cp site-envs/monarch-2023-10-11.env site-envs/monarch-${RELEASE}.env`
The date for the environment file name should match the KG release version, rather than today's date.
Edit the top two lines in new env to match the latest KG & API versions:

```
export MONARCH_KG_VERSION="2023-11-16"
export MONARCH_API_VERSION="0.18.1"
```

Then source the new environment and run provision.sh to create the new VM stack, paying attention to the terrform output to make sure that it's creating VMs with a version name you expect:

```
source site-envs/monarch-2023-11-16.env
./provision.sh
```

Output for the provision script should look something like this:

```
...
Changes to Outputs:
  + api_image_tag       = "1.0.0"
  + env                 = "2024-02-13"
  + full_prefix         = "monarch-v3-2024-02-13-"
  + neo4j_archive_url   = "https://data.monarchinitiative.org/monarch-kg-dev/latest/monarch-kg.neo4j.dump"
  + phenio_archive_url  = "https://data.monarchinitiative.org/monarch-kg/2024-02-13/phenio.db.gz"
  + project             = "monarch-initiative"
  + semsimian_image_tag = "latest"
  + solr_archive_url    = "https://data.monarchinitiative.org/monarch-kg/2024-02-13/solr.tar.gz"
  + sqlite_archive_url  = "https://data.monarchinitiative.org/monarch-kg/2024-02-13/monarch-kg.db.gz"
  + stack               = "monarch-v3"
  + ui_image_tag        = "latest"
  + vm_svc_acct_email   = "terraform@monarch-initiative.iam.gserviceaccount.com"

Do you want to perform these actions?
  Terraform will perform the actions described above.
  Only 'yes' will be accepted to approve.
```

At the end of the run you should see a message like this:

```
PLAY RECAP ***************************************************************************************************
monarch-v3-2024-02-13-api  : ok=11   changed=3    unreachable=0    failed=0    skipped=2    rescued=0    ignored=0
monarch-v3-2024-02-13-manager : ok=12   changed=3    unreachable=0    failed=0    skipped=2    rescued=0    ignored=0
monarch-v3-2024-02-13-neo4j : ok=11   changed=3    unreachable=0    failed=0    skipped=2    rescued=0    ignored=0
monarch-v3-2024-02-13-solr : ok=11   changed=3    unreachable=0    failed=0    skipped=2    rescued=0    ignored=0
```

#### Connecting beta to the load balancer

Once this completes, open the [GCP load balancer configuration](https://console.cloud.google.com/net-services/loadbalancing/details/http/monarch-balancer?project=monarch-initiative).

1. Click on the **edit** link at the top of the page.
2. Click on **Backend Configuration**
3. Open the **Backend services & backend buckets** pull down on the right side and check `monarch-v3-{release}-api-backend` & `monarch-v3-{release}-nginx-backend`, leave the other boxes checked, and click ok.
4. Open the `Host and path rules` section to point `beta.monarchinitiative.org` to the `nginx` backend, `api-beta.monarchinitiative.org` to the `api` backend, and `neo4j-beta.monarchinitiative.org` to the `neo4j` backend.
5. Then for each of these endpoints add `/*` to the path matcher, and click update.

If you get a pop-up window error, you may have forgotten to delete one of the old routes when pointing to the new backend. You will need to redo the configuration if this happens.

The load balancer will automatically restart with the new configuration. Then we'll need to confirm that the site is up and running.

Get yourself a cup of hot chocolate / ice cold lemonade (season dependent) and settle in to go through the issues in the milestone. Make sure that each issue appears to actually be fixed, and close them with a note that they're confirmed to be working on beta.monarchinitiative.org. (with some additional explanation for externally submitted issues about when the change is expected to be visible on the production site)


#### Deploying to production

Edit the load balancer
1. Remove the nginx and api backends from the last release
2. Point `api-beta.monarchinitiative.org`, `api-v3.monarchinitiative.org`, and `api-next.monarchinitiative.org` to `monarch-v3-{release}-api-backend`
3. Point `next.monarchinitiative.org` and `monarchinitiative.org` to `monarch-v3-{release}-nginx-backend`
4. At the top of the host and path rules seciton, change the default backend ("Backend 1") to point to `monarch-v3-{release}-nginx-backend` as well

Then turn off the former production VMs (but keep them around for disaster recovery) by going to the GCP console VM listings and just clicking stop on each VM.

Source the former former env in v3 stack to delete it (say yes to deleting, and no to creating in the terraform dialogs)
```
source site-envs/monarch-2023-10-17.env
./provision.sh -d
```

#### Troubleshooting

Here are some known issues that we have seen before:

In `./provision.sh` you may see an error like this:

```
fatal: [monarch-v3-2024-02-13-api]: UNREACHABLE! => changed=false
  msg: |-
    Data could not be sent to remote host "monarch-v3-2024-02-13-api". Make sure this host can be reached over ssh: Pseudo-terminal will not be allocated because stdin is not a terminal.
    sa_116692422516913491665@34.42.108.156: Permission denied (publickey).

    Recommendation: To check for possible causes of SSH connectivity issues and get
    recommendations, rerun the ssh command with the --troubleshoot option.

    gcloud compute ssh monarch-v3-2024-02-13-api --project=monarch-initiative --zone=us-central1-a --troubleshoot

    Or, to investigate an IAP tunneling issue:

    gcloud compute ssh monarch-v3-2024-02-13-api --project=monarch-initiative --zone=us-central1-a --troubleshoot --tunnel-through-iap

    ERROR: (gcloud.compute.ssh) [/usr/bin/ssh] exited with return code [255].
  unreachable: true
```

If so you may want to run the stated command (update to your version):

```commandline
gcloud compute ssh monarch-v3-2024-02-13-api --project=monarch-initiative --zone=us-central1-a --troubleshoot
```


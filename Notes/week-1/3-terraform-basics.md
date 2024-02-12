# 1.3. Terraform Basics

First, setup Terraform and GCP SDK:
- Terraform [[here](https://developer.hashicorp.com/terraform/install)]
- GCP SDK [[here](https://github.com/DataTalksClub/data-engineering-zoomcamp/blob/main/01-docker-terraform/1_terraform_gcp/2_gcp_overview.md#initial-setup)]

Table of Contents:
- [1.3.1. Terraform Primer](#131-terraform-primer)
- [1.3.2. Terraform Basics (Walkthrough basic operations)](#132-terraform-basics-walkthrough-basic-operations)
- [1.3.3. Terraform Variables](#133-terraform-variables)

## 1.3.1. Terraform Primer
▶️ [[Video Link](https://www.youtube.com/watch?v=s2bOYDCKl_M&list=PL3MmuxUbc_hJed7dXYoJw8DoCuVHhGEQb&index=11)]

Terraform is an **infrastructure as** code tool that lets you define both cloud and on-prem resources in human-readable configuration files that you can version, reuse, and share. You can then use a consistent workflow to provision and manage all of your infrastructure throughout its lifecycle.

Why use Terraform?
- simplicity in keeping track of infrastructure
- Easier collaboration
- Reproducibility
- Ensure resources are removed

Terraform is not:
- does not manage and update code on infrastructure
- does not give you the ability to change immutable resources
- not used to manage resources not defined in your terraform files

Key Terraform commands:
- `init` - get me the providers 
- `plan`
- `apply`- do the thing in terraform
- `destroy` - destruct everything defined in terraform

## 1.3.2. Terraform Basics (Walkthrough basic operations)
▶️ [[Video Link](https://www.youtube.com/watch?v=Y2ux7gq3Z0o&list=PL3MmuxUbc_hJed7dXYoJw8DoCuVHhGEQb&index=12)]

Setting up service account in Google Cloud Platform (GCP):
1. Go to the [GCP console](https://console.cloud.google.com/) and create new project
2. Head to IAM & Admin > Service Accounts
3. Create a new service account, give it a name (e.g. `terraform-runner`) > Continue
4. Give it a role as `Storage Admin`, add another role as `BigQuery Admin`, lastly, add `Compute Admin` role > Continue  
**note**: _In real world, you want to limit these permissions._    
for storage creator, we only need ability to create buckets and destroy. for bigquery, we only need ability to create and destroy datasets and tables.
5. Skip and click Done. _If you need to create additional role, just go to IAM menu and go to your service account and add additional role._
6. In the service accounts for the project, click three dots menu at the service account just created, and click manage keys.
7. Create new keys and choose json. A json file will be downloaded to your computer, this is the key file that will be used in terraform. Keep it in somewhere safe directory.
8. Use that json file to authenticate GCP. You can see the instructions via GCP installation instruction above.

Setting up Terraform in VSCode environment:
- Install Terraform extension in VSCode, you can use the one from HashiCorp.

First, we are going to init Terraform. Create a new file `main.tf` and put the following code:

```hcl
terraform {
  required_providers {
    google = {
      source = "hashicorp/google"
      version = "5.15.0"
    }
  }
}

provider "google" {
  provider "google" {
  project     = "my-project-id" # put your GCP project id here
  region      = "us-central1"
  zone        = "us-central1-c"
}
}
```

Then run `terraform init` in the terminal same directory as the `main.tf` file. This will download the provider plugin for Google Cloud Platform and will generate a bunch of new files and folders. Make sure to add Terraform .gitignore template to your `.gitignore` file. For reference, see template [here](https://github.com/github/gitignore/blob/main/Terraform.gitignore)

Next, we are going to create Google Bucket Storage via Terraform. We will see how powerful Terraform is in managing infrastructure. 

Edit `main.tf' file and add the following code at the end of the file:

```hcl
resource "google_storage_bucket" "demo-bucket" {
  name          = "demo-terraform-bucket" # unique name 
  location      = "US"
  force_destroy = true

  lifecycle_rule {
    condition {
      age = 1
    }
    action {
      type = "AbortIncompleteMultipartUpload"
    }
  }
}
```

run `terraform plan` and then `terraform apply` commands in the terminal. This will create a bucket in your GCP project. You can check it in the GCP console.

Now we will destroy the bucket we just created. Simply run `terraform destroy` in the terminal. This will destroy the bucket in your GCP project.

## 1.3.3. Terraform Variables

▶️ [[video link](https://www.youtube.com/watch?v=PBi0hHjLftk&list=PL3MmuxUbc_hJed7dXYoJw8DoCuVHhGEQb&index=14)]

Now we will leverage developing Terraform with variables. With Terraform variables, we don't need to hard code the values in the Terraform file everytime we want to create a new resource. We can use variables to make the code more reusable and easier to maintain. 

For example, instead of hard coding the location of the bucket (e.g. `US`), we can use a variable to define the location, so that if we want to change the location, we only need to change the value of the variable, once.

In the following tutorial, we will create BigQuery Table using Terraform and set it up with variables. 

In the `main.tf` file, add the following code at the end of the file:

```hcl
resource "google_bigquery_dataset" "demo_dataset" {
  dataset_id = 'demo_dataset'
  location   = 'US'
}
```

Full code for `main.tf` file:

```hcl
terraform {
  required_providers {
    google = {
      source = "hashicorp/google"
      version = "5.15.0"
    }
  }
}

provider "google" {
  project     = "dataengzoocamp-375210" # put your GCP project id here
  region      = "us-central1"
  zone        = "us-central1-c"
}

resource "google_storage_bucket" "demo-bucket" {
  name          = "demo-terraform-bucket"
  location      = "US"
  force_destroy = true

  lifecycle_rule {
    condition {
      age = 1
    }
    action {
      type = "AbortIncompleteMultipartUpload"
    }
  }
}

resource "google_bigquery_dataset" "demo_dataset" {
  dataset_id = "demo_dataset"
  location   = "US"
}
```

We see that in the above code, we still hardcode some of the values, like the project id, location, region, etc. We can use variables to make the code more reusable and easier to maintain.

First, create a new file `variables.tf` and add variable for every value that we want to make it reusable. For example, in this project we will create variables for project id, region, zone, bucket_name, and bigquery_dataset_id. The code is as follows:

```hcl
variable "project_id" {
  description = "The project id"
  default = "dataengzoocamp-375210" # Replace with your GCP project id
}

variable "region" {
  description = "The region"
  default = "us-central1"
}

variable "zone" {
  description = "The zone"
  default = "us-central1-c"
}

variable "location" {
  description = "The location for the bucket"
  default = "US"
}

variable "bucket_name" {
  description = "The bucket name"
  default = "demo-terraform-bucket"
}

variable "bq_dataset_id" {
  description = "The bigquery dataset id"
  default = "demo_dataset"
}

variable "gcs_storage_class" {
  description = "The storage class for the bucket"
  default = "STANDARD"
}
```

You can also add your gcp credentials via terraform variables instead of setting it up in the terminal variable, by adding the following code in the `variables.tf` file:

```hcl
variable "credentials" {
  description = "The path to the GCP credentials file"
  default = "path/to/your/credentials.json"
}
```

Then, in the `main.tf` file, replace the hardcoded values with the variables we have created. Example as follows:

```hcl
terraform {
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "5.15.0"
    }
  }
}

provider "google" {
  credentials = file(var.credentials)
  project     = var.project_id
  region      = var.region
  zone        = var.zone
}

resource "google_storage_bucket" "demo-bucket" {
  name          = var.bucket_name
  location      = var.location
  storage_class = var.storage_class
  force_destroy = true

  lifecycle_rule {
    condition {
      age = 1
    }
    action {
      type = "AbortIncompleteMultipartUpload"
    }
  }
}

resource "google_bigquery_dataset" "demo_dataset" {
  dataset_id = var.bq_dataset_id
  location   = var.location
}
```

After that, run `terraform plan` and `terraform apply` commands in the terminal. This will create a bucket and bigquery dataset in your GCP project. You can check it in the GCP console that a bucket and bigquery table has been created.

Run `terraform destroy` to destroy the resources we just created. Check in the GCP console that the resources have been destroyed.


<div align="center">

###  [<< 1.2. Docker and Docker Compose](./2-docker-and-docker-compose.md) | [Home](README.md) | [1.4. Setting Up Environments >>](./4-setting-up-environments.md)

</div>
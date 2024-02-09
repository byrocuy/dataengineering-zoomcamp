variable "credentials" {
  description = "The path to the GCP credentials file"
  default     = "./dataengzoocamp-375210-190269feacba.json"
}

variable "project_id" {
  description = "The project id"
  default     = "dataengzoocamp-375210"
}

variable "region" {
  description = "Region for GCP resources. Choose as per your location: https://cloud.google.com/about/locations"
  default     = "us-central1"
}

variable "zone" {
  description = "The zone"
  default     = "us-central1-c"
}

variable "location" {
  description = "The location for the bucket"
  default     = "US"
}

variable "bucket_name" {
  description = "The bucket name"
  default     = "demo-terraform-bucket"
}

variable "bq_dataset_id" {
  description = "The bigquery dataset id"
  default     = "demo_dataset"
}

variable "storage_class" {
  description = "The storage class for the bucket"
  default     = "STANDARD"
}
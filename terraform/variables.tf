
variable "aws_region" {
  description = "Regiao AWS"
  type        = string
  default     = "us-east-1"
}

variable "vpc_id" {
  description = "VPC utilizada pelo projeto"
  type        = string
}

variable "subnet_id" {
  description = "Sub-rede publica da EC2"
  type        = string
}

variable "instance_type" {
  description = "Tipo da instancia EC2"
  type        = string
  default     = "t3.micro"
}

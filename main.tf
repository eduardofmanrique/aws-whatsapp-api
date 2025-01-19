provider "aws" {
  region = "sa-east-1"
}

variable "timeout_seconds" {
  description = "Timeout for both Lambda function and SQS queue (in seconds)"
  type        = number
  default     = 120
}

terraform {
  backend "s3" {
    bucket         = "aws-alerts-config-bucket"
    key            = "whatsapp_api/terraform/state/terraform.tfstate"
    region         = "sa-east-1"
    encrypt        = true
  }
}

resource "aws_iam_role" "lambda_role_whatsapp_api" {
  name               = "lambda-basic-role-whatsapp-api"
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "lambda.amazonaws.com"
        }
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "lambda_basic_policy_whatsapp_api" {
  role       = aws_iam_role.lambda_role_whatsapp_api.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}

resource "aws_iam_role_policy_attachment" "lambda_sqs_full_access_whatsapp_api" {
  role       = aws_iam_role.lambda_role_whatsapp_api.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonSQSFullAccess"
}

resource "aws_iam_role_policy_attachment" "lambda_ssm_read_only_whatsapp_api" {
  role       = aws_iam_role.lambda_role_whatsapp_api.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonSSMReadOnlyAccess"
}


resource "aws_lambda_function" "lambda_whatsapp_api" {
  function_name    = "lambda-whatsapp-api"
  role             = aws_iam_role.lambda_role_whatsapp_api.arn
  handler          = "main.handler"
  runtime          = "python3.9"
  filename         = "lambda.zip"
  source_code_hash = fileexists("lambda.zip") ? filebase64sha256("lambda.zip") : null
  timeout          = var.timeout_seconds
  memory_size      = 300
  layers           = [
    "arn:aws:lambda:sa-east-1:336392948345:layer:AWSSDKPandas-Python39:29"
  ]
}

resource "aws_lambda_permission" "allow_sqs_whatsapp_api" {
  statement_id  = "AllowSQSTrigger"
  action        = "lambda:InvokeFunction"
  principal     = "sqs.amazonaws.com"
  source_arn    = aws_sqs_queue.queue_whatsapp_api.arn
  function_name = aws_lambda_function.lambda_whatsapp_api.function_name
}

resource "aws_lambda_event_source_mapping" "sqs_trigger_whatsapp_api" {
  event_source_arn = aws_sqs_queue.queue_whatsapp_api.arn
  function_name    = aws_lambda_function.lambda_whatsapp_api.arn
  enabled          = true
}

resource "aws_sqs_queue" "dlq_whatsapp_api" {
  name = "whatsapp-api-dlq"
}

resource "aws_sqs_queue" "queue_whatsapp_api" {
  name                       = "whatsapp-api-queue"
  visibility_timeout_seconds = var.timeout_seconds
  redrive_policy = jsonencode({
    deadLetterTargetArn = aws_sqs_queue.dlq_whatsapp_api.arn
    maxReceiveCount     = 1
  })
}

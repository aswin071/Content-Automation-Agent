#!/bin/bash
# Script to fix AWS Secrets Manager values and ECS permissions
# Run this script with proper AWS credentials (admin or sufficient IAM permissions)

set -e

REGION="us-east-1"
ACCOUNT_ID="343989049356"

echo "=========================================="
echo "AWS Secrets Manager & ECS Permissions Fix"
echo "=========================================="
echo ""

# Read API keys from .env file
if [ -f ".env" ]; then
    echo "✓ Found .env file, reading API keys..."
    source .env
else
    echo "❌ .env file not found. Please ensure .env exists with API keys."
    exit 1
fi

# Validate that keys are set
if [ -z "$ANTHROPIC_API_KEY" ] || [ -z "$YOUTUBE_API_KEY" ] || [ -z "$SERP_API_KEY" ]; then
    echo "❌ Missing API keys in .env file"
    echo "Required: ANTHROPIC_API_KEY, YOUTUBE_API_KEY, SERP_API_KEY"
    exit 1
fi

echo "✓ API keys loaded from .env"
echo ""

# Step 1: Update Secrets in AWS Secrets Manager
echo "Step 1: Updating secrets in AWS Secrets Manager..."
echo "------------------------------------------------"

echo "Updating CLAUDE_API_KEY..."
aws secretsmanager update-secret \
    --secret-id CLAUDE_API_KEY \
    --secret-string "$ANTHROPIC_API_KEY" \
    --region $REGION || {
        echo "❌ Failed to update CLAUDE_API_KEY. Check permissions."
        exit 1
    }
echo "✓ CLAUDE_API_KEY updated"

echo "Updating YOUTUBE_API_KEY..."
aws secretsmanager update-secret \
    --secret-id YOUTUBE_API_KEY \
    --secret-string "$YOUTUBE_API_KEY" \
    --region $REGION || {
        echo "❌ Failed to update YOUTUBE_API_KEY. Check permissions."
        exit 1
    }
echo "✓ YOUTUBE_API_KEY updated"

echo "Updating SERP_API_KEY..."
aws secretsmanager update-secret \
    --secret-id SERP_API_KEY \
    --secret-string "$SERP_API_KEY" \
    --region $REGION || {
        echo "❌ Failed to update SERP_API_KEY. Check permissions."
        exit 1
    }
echo "✓ SERP_API_KEY updated"
echo ""

# Step 2: Add Secrets Manager permissions to ECS Task Execution Role
echo "Step 2: Adding Secrets Manager permissions to ECS execution role..."
echo "-------------------------------------------------------------------"

POLICY_NAME="SecretsManagerReadPolicy"
ROLE_NAME="ecsTaskExecutionRole"

# Create inline policy for reading secrets
cat > /tmp/secrets-policy.json <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "secretsmanager:GetSecretValue"
      ],
      "Resource": [
        "arn:aws:secretsmanager:${REGION}:${ACCOUNT_ID}:secret:CLAUDE_API_KEY-*",
        "arn:aws:secretsmanager:${REGION}:${ACCOUNT_ID}:secret:YOUTUBE_API_KEY-*",
        "arn:aws:secretsmanager:${REGION}:${ACCOUNT_ID}:secret:SERP_API_KEY-*"
      ]
    }
  ]
}
EOF

echo "Adding inline policy to $ROLE_NAME..."
aws iam put-role-policy \
    --role-name $ROLE_NAME \
    --policy-name $POLICY_NAME \
    --policy-document file:///tmp/secrets-policy.json \
    --region $REGION || {
        echo "⚠️  Warning: Could not add policy (may already exist or insufficient permissions)"
    }
echo "✓ Policy added/updated"
echo ""

# Step 3: Force new ECS deployment
echo "Step 3: Forcing new ECS deployment..."
echo "--------------------------------------"

CLUSTER_NAME="content-ai-agent"
SERVICE_NAME="content-automation-service"

echo "Triggering deployment of $SERVICE_NAME in cluster $CLUSTER_NAME..."
aws ecs update-service \
    --cluster $CLUSTER_NAME \
    --service $SERVICE_NAME \
    --force-new-deployment \
    --region $REGION || {
        echo "❌ Failed to trigger deployment. Check permissions."
        exit 1
    }
echo "✓ Deployment triggered"
echo ""

# Step 4: Wait for deployment to stabilize
echo "Step 4: Waiting for deployment to stabilize..."
echo "-----------------------------------------------"
echo "This may take 2-5 minutes..."

aws ecs wait services-stable \
    --cluster $CLUSTER_NAME \
    --services $SERVICE_NAME \
    --region $REGION && echo "✓ Deployment complete!" || echo "⚠️  Deployment timeout (check AWS Console)"
echo ""

# Step 5: Verify secrets are accessible
echo "Step 5: Verifying secrets..."
echo "-----------------------------"

for SECRET in CLAUDE_API_KEY YOUTUBE_API_KEY SERP_API_KEY; do
    echo "Checking $SECRET..."
    aws secretsmanager get-secret-value \
        --secret-id $SECRET \
        --region $REGION \
        --query 'SecretString' \
        --output text > /dev/null && echo "✓ $SECRET is accessible" || echo "❌ $SECRET is not accessible"
done
echo ""

# Step 6: Check CloudWatch Logs
echo "Step 6: Checking recent CloudWatch logs..."
echo "-------------------------------------------"
echo "Recent logs from /ecs/content-automation:"
echo ""

aws logs tail /ecs/content-automation \
    --since 5m \
    --region $REGION \
    --format short 2>/dev/null || echo "⚠️  Could not fetch logs (check permissions)"
echo ""

echo "=========================================="
echo "✓ Fix script completed!"
echo "=========================================="
echo ""
echo "Next steps:"
echo "1. Test the API endpoint:"
echo "   curl http://content-automation-alb-451510707.us-east-1.elb.amazonaws.com/health"
echo ""
echo "2. Test the detailed health check:"
echo "   curl http://content-automation-alb-451510707.us-east-1.elb.amazonaws.com/api/v1/health/detailed"
echo ""
echo "3. If still failing, check CloudWatch logs:"
echo "   aws logs tail /ecs/content-automation --follow --region us-east-1"
echo ""

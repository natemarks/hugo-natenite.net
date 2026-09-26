# AWS Organizations Setup Guide for Single Account Customers

## Executive Summary

For a single-account AWS customer transitioning to a multi-account structure, the recommended approach is:

1. **Create a NEW, dedicated AWS account** to become the Management Account (DO NOT use existing workload account)
2. **Set up AWS Control Tower** in the new management account - This automatically creates Organizations and IAM Identity Center
3. **Invite existing workload account** to join the organization as a member account
4. **Optionally add Landing Zone Accelerator (LZA)** for enhanced compliance and governance

### Critical Decision: Separate Management Account

**⚠️ IMPORTANT: If your existing account has workloads, you MUST create a new account for management.**

**AWS Best Practice (from AWS Organizations documentation):**
> "Avoid deploying workloads to the organization's management account. Privileged operations can be performed within an organization's management account, and SCPs do not apply to the management account."

## Why You Need a Separate Management Account

### Security and Governance Issues with Workloads in Management Account:

1. **Service Control Policies Don't Apply** - SCPs cannot restrict users/roles in the management account
2. **Blast Radius** - Workload issues could compromise organization governance
3. **Compliance Violations** - Most frameworks require separation (SOC 2, ISO 27001, PCI-DSS, etc.)
4. **Billing Confusion** - Can't separate org management costs from workload costs
5. **Security Audit Failures** - Auditors will flag this as a critical finding
6. **Migration Pain Later** - You'll eventually need to move workloads anyway

### What Belongs in the Management Account:

**ONLY these items:**
- ✅ AWS Organizations configuration
- ✅ Control Tower management resources
- ✅ Organization-wide IAM Identity Center
- ✅ Root-level billing and cost management
- ✅ Service Catalog for account vending
- ✅ Organization-wide CloudTrail (optional)

**NEVER in Management Account:**
- ❌ Application workloads (EC2, Lambda, ECS, etc.)
- ❌ Databases (RDS, DynamoDB, etc.)
- ❌ Storage for application data (S3, EFS, etc.)
- ❌ Application networking (VPCs with workloads)
- ❌ ANY production or development resources

## Recommended Architecture

```
┌─────────────────────────────────────────────────┐
│ NEW AWS Account (Created specifically for org)  │
│ → Becomes Management Account                    │
│ → Control Tower setup happens here              │
│ → NO workloads ever deployed here               │
│ → Cost: ~$250-500/month baseline                │
└─────────────────────────────────────────────────┘
                    │
                    │ Creates
                    ↓
┌─────────────────────────────────────────────────┐
│ Log Archive Account (Auto-created by Control    │
│ Tower)                                           │
│ → Centralized logging                            │
│ → CloudTrail logs, Config history, VPC Flow     │
└─────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────┐
│ Audit Account (Auto-created by Control Tower)   │
│ → Security auditing and compliance              │
│ → Cross-account audit access                     │
└─────────────────────────────────────────────────┘
                    │
                    │ Invites
                    ↓
┌─────────────────────────────────────────────────┐
│ EXISTING AWS Account (Your current workload)    │
│ → Becomes Member Account                        │
│ → Workloads stay in place (no migration!)       │
│ → Enrolled in Control Tower governance          │
│ → SCPs apply for compliance and security        │
└─────────────────────────────────────────────────┘
```

## Accounts and Resources Created by Each Service

### 1. AWS Organizations (Free Service)

**Accounts Created:**
- None directly (uses your existing account as management account)

**Resources Created:**
- Organization root container
- Organizational structure
- Service Control Policies (SCPs) framework
- Consolidated billing configuration
- Organization-wide service enablement framework

**What it does:**
- Groups accounts into a hierarchy
- Enables centralized billing
- Allows policy-based governance
- Provides foundation for Control Tower

**Cost:** $0 (Organizations itself is free)

### 2. AWS Control Tower (Free Service, Pay for Resources)

**Accounts Created:**
- **Log Archive Account** - Centralized logging
- **Audit Account** - Security and compliance monitoring

**Organizational Units Created:**
- **Root** (exists automatically)
- **Security OU** - Contains Log Archive and Audit accounts
- **Sandbox OU** (optional) - Development/testing

**Resources Created in Management Account:**
| Resource Type | Purpose | Est. Monthly Cost |
|---------------|---------|-------------------|
| AWS Organizations | Account management | $0 |
| IAM Identity Center | SSO and user management | $0 |
| Service Catalog Portfolio | Account Factory | $0 |
| CloudFormation StackSets | Multi-account deployment | $0 |
| SNS Topics | Notifications | $0.50 |
| CloudWatch Log Groups | Monitoring | $5-10 |
| EventBridge Rules | Drift detection | $1 |
| Lambda Functions | Account lifecycle | $1-2 |
| Systems Manager Parameters | Configuration storage | $0.05 |

**Resources Created in Each Member Account:**
| Resource Type | Purpose | Est. Monthly Cost (per account) |
|---------------|---------|----------------------------------|
| AWS Config | Compliance monitoring | $10-50 (varies by resource count) |
| AWS Config Rules | Detective controls | $2-10 per rule |
| CloudTrail Trail | API logging | $0 (logs sent to Log Archive) |
| CloudWatch Events | Control Tower lifecycle | $1 |
| IAM Roles | Cross-account access | $0 |
| VPC (default) | Networking | $0 (if not used) |

**Resources Created in Log Archive Account:**
| Resource Type | Purpose | Est. Monthly Cost |
|---------------|---------|-------------------|
| S3 Bucket | Centralized log storage | $20-100 (depends on activity) |
| S3 Lifecycle Policies | Log retention management | $0 |
| CloudTrail Organization Trail | All account logging | $2-5 per account |
| KMS Key | Log encryption | $1 |
| IAM Roles | Log access | $0 |

**Resources Created in Audit Account:**
| Resource Type | Purpose | Est. Monthly Cost |
|---------------|---------|-------------------|
| IAM Roles | Cross-account audit access | $0 |
| SNS Topics | Security notifications | $1 |
| Lambda Functions | Compliance automation | $1-2 |
| Config Aggregator | Organization-wide compliance view | $0.001 per config item |

**IAM Identity Center (SSO) Configuration:**
- Cloud-native directory (or connect to existing AD)
- Pre-configured groups:
  - `AWSAccountFactory` - Can provision new accounts
  - `AWSServiceCatalogAdmins` - Can manage account vending
  - `AWSSecurityAuditors` - Read-only security access
  - `AWSSecurityAuditPowerUsers` - Security with some write access
  - `AWSLogArchiveAdmins` - Manage logging
  - `AWSLogArchiveViewers` - Read-only log access

**Guardrails (Controls) Deployed:**
- 33 mandatory preventive controls (SCPs)
- 9 mandatory detective controls (Config rules)
- 250+ optional controls available

**Total Baseline Cost for Control Tower:**
- Management Account: ~$50-100/month
- Log Archive Account: ~$50-150/month  
- Audit Account: ~$20-50/month
- Per enrolled member account: ~$30-75/month (AWS Config is the largest cost)

**Estimated Total: $250-500/month for a basic setup with 3-5 accounts**

### 3. Landing Zone Accelerator (LZA) - Advanced Configuration

**Note:** LZA is a solution that BUILDS ON TOP of Control Tower. It does not replace it.

**Can LZA Deploy Control Tower?**
**YES** - When you deploy LZA with `ControlTowerEnabled: Yes`, LZA will:
1. Deploy Control Tower service roles
2. Create Log Archive and Audit accounts
3. Deploy Control Tower Landing Zone
4. Apply LZA's additional configurations

**Can LZA Deploy Organizations?**
**Indirectly YES** - LZA requires Organizations to exist with all features enabled. If you set `ControlTowerEnabled: Yes`, LZA deploys Control Tower, which creates Organizations.

**Prerequisites for LZA Auto-Deploy of Control Tower:**
- AWS Organizations configured with all features enabled
- Only management account exists (no member accounts yet)
- No OUs created
- No AWS services enabled for Organizations
- No IAM Identity Center configured
- No Control Tower service roles present

**Accounts Created by LZA:**
LZA can create additional accounts based on your configuration files:
- **Network Account** - Transit Gateway, VPN, Direct Connect
- **Shared Services Account** - Active Directory, DNS, shared tools
- **Workload Accounts** - Per your `accounts-config.yaml`

**Resources Created by LZA Installer:**

**AWSAccelerator-InstallerStack (Management Account):**
| Resource Type | Purpose | Est. Monthly Cost |
|---------------|---------|-------------------|
| CodePipeline | Installer pipeline | $1 |
| CodeBuild Project | Build orchestration | $0.005/minute (minimal) |
| S3 Bucket | Pipeline artifacts | $1-2 |
| KMS Key | Encryption | $1 |
| IAM Roles | Pipeline permissions | $0 |

**AWSAccelerator-PipelineStack (Management Account):**
| Resource Type | Purpose | Est. Monthly Cost |
|---------------|---------|-------------------|
| CodePipeline | Core deployment pipeline | $1 |
| CodeBuild Projects (2) | Build and CDK deploy | $10-50 (varies by run frequency) |
| CodeCommit Repository | Configuration files | $1 |
| S3 Buckets (2) | Config and artifacts | $2-5 |
| SNS Topics (2-3) | Notifications | $1 |
| CloudWatch Alarm | Pipeline monitoring | $0.10 |
| Lambda Functions | Custom resources | $1-2 |
| DynamoDB Table | Metadata storage | $1-5 |
| IAM Roles | Service permissions | $0 |

**Additional Resources Created by LZA (Based on Configuration):**

The exact resources depend on your configuration files, but typical deployments include:

**Networking (per account/region):**
| Resource Type | Purpose | Est. Monthly Cost |
|---------------|---------|-------------------|
| VPCs | Network isolation | $0 |
| Subnets | Network segmentation | $0 |
| Transit Gateway | Network hub | $36-50/month + data transfer |
| Transit Gateway Attachments | VPC connections | $36/month each |
| VPN Connections | Site-to-site connectivity | $36/month each |
| NAT Gateways | Outbound internet | $32-45/month each + data |
| Network Firewall | Traffic inspection | $350-500/month + data |
| Route 53 Resolver Endpoints | DNS | $0.125/hour = ~$90/month |

**Security (organization-wide):**
| Resource Type | Purpose | Est. Monthly Cost |
|---------------|---------|-------------------|
| GuardDuty | Threat detection | $4.50/month + data |
| Security Hub | Security posture | $0.001/check + $0.0010/finding |
| AWS Config Rules (additional) | Compliance checks | $2/rule/region/month |
| Macie | Data classification | $1/GB scanned |
| KMS Keys (multiple) | Encryption | $1/key/month |
| Secrets Manager Secrets | Credential management | $0.40/secret/month |
| IAM Access Analyzer | Permission analysis | $0 (in region) |

**Logging & Monitoring (organization-wide):**
| Resource Type | Purpose | Est. Monthly Cost |
|---------------|---------|-------------------|
| CloudWatch Log Groups | Additional logging | $0.50/GB ingested |
| CloudWatch Metrics | Custom metrics | $0.30/metric/month |
| SNS Topics | Alerting | $0.50/million requests |
| EventBridge Rules | Event routing | $1/million events |
| S3 Buckets (additional) | Log storage | $0.023/GB/month |

**Governance:**
| Resource Type | Purpose | Est. Monthly Cost |
|---------------|---------|-------------------|
| Service Catalog Portfolios | Standardized services | $0 |
| CloudFormation StackSets | Multi-account stacks | $0 |
| AWS Backup Vaults | Centralized backup | $0.05/GB/month |
| Organizations Policies | SCPs, Tag policies | $0 |

**Total LZA Additional Cost:**
- LZA Infrastructure: ~$50-100/month (pipelines and management)
- Network Architecture: ~$200-500/month (varies greatly by design)
- Enhanced Security: ~$100-300/month (depends on services enabled)
- Per account overhead: ~$50-100/month additional

**Estimated Total with LZA: $600-1,500/month for 5-10 accounts with full networking and security**

**Note:** These are baseline estimates. Actual costs vary significantly based on:
- Number of accounts
- Number of regions enabled
- Data transfer volumes
- AWS Config resource counts
- Log retention periods
- Network architecture complexity

## Capability Comparison Matrix

| Capability | Organizations Alone | + Control Tower | + LZA |
|-----------|---------------------|-----------------|-------|
| **Cost** | $0 | $250-500/mo | $600-1,500/mo |
| **Setup Time** | 15 min | 30-60 min | 2-4 hours |
| **Account Management** | Manual | Account Factory | Account Factory + IaC |
| **SSO/Federation** | Manual setup | Automatic | Automatic + customization |
| **Guardrails** | Manual SCPs | 42 built-in | 100+ compliance-specific |
| **Compliance Frameworks** | None | AWS best practices | CIS, NIST, PCI-DSS, HIPAA, FedRAMP |
| **Network Architecture** | Manual | VPC defaults | Full transit gateway architecture |
| **Security Services** | Manual | Config, CloudTrail | GuardDuty, Security Hub, Macie, etc. |
| **Logging** | Manual | Centralized | Enhanced + retention policies |
| **IaC Management** | None | CloudFormation | CDK + GitOps workflow |
| **Multi-Region** | Manual | Supported | Automated replication |
| **Use Case** | Small orgs, cost-sensitive | Most businesses | Regulated industries |

## Setup Sequence Comparison

### Option A: Organizations → Control Tower (RECOMMENDED for Most)

```
1. Create new AWS account for management
2. Sign in to Control Tower console
3. Control Tower automatically:
   - Creates Organizations
   - Creates IAM Identity Center
   - Deploys Log Archive and Audit accounts
   - Sets up guardrails
   ⏱️ Time: 30-60 minutes (automated)
4. Invite existing workload account
5. Enroll workload account in Control Tower
```

**When to use:** Most AWS customers, standard security requirements

### Option B: Organizations → Control Tower → LZA

```
1. Create new AWS account for management
2. Set up Control Tower (creates Organizations)
3. Deploy LZA CloudFormation stack
4. Configure LZA via YAML files in CodeCommit
5. LZA pipeline deploys additional infrastructure
   ⏱️ Time: 2-4 hours initial, days for full config
```

**When to use:** Regulated industries, complex compliance, sophisticated networking

### Option C: LZA Auto-Deploys Everything (Advanced)

```
1. Create new AWS account for management
2. Create Organizations with all features enabled
3. Deploy LZA with ControlTowerEnabled: Yes
4. LZA automatically:
   - Deploys Control Tower
   - Creates Log Archive and Audit accounts
   - Deploys LZA infrastructure
   - Applies your configuration
   ⏱️ Time: 2-4 hours (automated)
5. Customize via CodeCommit config files
```

**When to use:** Greenfield deployments for regulated workloads, Infrastructure-as-Code requirement from day one

## Detailed Setup: Option C (LZA with CodeCommit)

Since LZA can deploy both Control Tower and Organizations, here's the complete setup process using CodeCommit for configuration management.

### Prerequisites

1. **New AWS Account**
   - Created specifically to be management account
   - No workloads deployed
   - Root user MFA enabled
   - Billing alerts configured

2. **Email Addresses** (3 unique addresses)
   - Management account email (the account itself)
   - Log Archive account email: `aws-logs@yourcompany.com`
   - Audit account email: `aws-audit@yourcompany.com`

3. **AWS CLI Configured**
   - IAM user or role with Administrator access
   - AWS CLI v2 installed locally

4. **Planning Complete**
   - Documented OU structure
   - Identified accounts needed
   - Network architecture designed
   - Compliance requirements identified

### Phase 1: Create AWS Organizations

Since LZA requires Organizations to exist first:

```bash
# Create organization (all features enabled)
aws organizations create-organization --feature-set ALL

# Verify organization
aws organizations describe-organization
```

**Result:** Organization created, your account is now the management account.

### Phase 2: Deploy Landing Zone Accelerator

#### Step 1: Download Configuration Template

```bash
# Clone LZA sample configurations
git clone https://github.com/awslabs/landing-zone-accelerator-on-aws.git
cd landing-zone-accelerator-on-aws/reference/sample-configurations

# Choose a configuration template based on your needs:
# - aws-best-practices/ - General AWS best practices
# - us-slg-central-it/ - State and Local Government
# - healthcare/ - HIPAA compliance
# - finance/ - PCI-DSS compliance
```

#### Step 2: Prepare Configuration Files

The LZA uses 7 configuration files (6 mandatory, 1 optional):

1. **global-config.yaml** - Global settings, home region, logging
2. **accounts-config.yaml** - Account definitions
3. **organization-config.yaml** - OU structure
4. **network-config.yaml** - VPCs, Transit Gateway, connectivity
5. **security-config.yaml** - Security services, KMS, GuardDuty, etc.
6. **iam-config.yaml** - IAM roles, policies, Identity Center
7. **customizations-config.yaml** - (Optional) Custom CloudFormation stacks

**Key Settings to Update in global-config.yaml:**

```yaml
homeRegion: us-east-1  # Your primary region
controlTower:
  enable: true  # LZA will deploy Control Tower

managementAccountAccessRole: AWSControlTowerExecution
cloudwatchLogRetentionInDays: 365

# Email addresses for shared accounts
logging:
  account: LogArchive
  centralizedLoggingRegion: us-east-1
  
audit:
  account: Audit
```

**Update accounts-config.yaml:**

```yaml
mandatoryAccounts:
  - name: Management
    description: Management Account
    email: management@yourcompany.com  # Your current account email
    organizationalUnit: Root
    
  - name: LogArchive
    description: Log Archive Account
    email: aws-logs@yourcompany.com
    organizationalUnit: Security
    
  - name: Audit
    description: Audit and Compliance Account
    email: aws-audit@yourcompany.com
    organizationalUnit: Security

workloadAccounts:
  - name: Network
    description: Shared networking account
    email: aws-network@yourcompany.com
    organizationalUnit: Infrastructure
    
  - name: SharedServices
    description: Shared services account
    email: aws-shared@yourcompany.com
    organizationalUnit: Infrastructure
    
  # Add your existing workload account to invite it
  - name: Production-Workload
    description: Existing production workload
    email: existing-account@yourcompany.com  # Your existing account email
    organizationalUnit: Workloads/Production
```

**Update organization-config.yaml:**

```yaml
organizationalUnits:
  - name: Security
    # Contains LogArchive and Audit accounts
  - name: Infrastructure
    # Contains Network and SharedServices
  - name: Sandbox
    # For development and testing
  - name: Workloads
    # Contains production workloads
```

#### Step 3: Deploy LZA via CloudFormation

**Option A: Deploy via Console**

1. Download the installer template:
   ```bash
   curl -O https://s3.amazonaws.com/solutions-reference/landing-zone-accelerator-on-aws/latest/AWSAccelerator-InstallerStack.template
   ```

2. Sign in to AWS Console → CloudFormation → Create Stack

3. Upload `AWSAccelerator-InstallerStack.template`

4. Configure parameters:
   - **Stack name:** `AWSAccelerator-InstallerStack`
   - **RepositorySource:** `codecommit` (we'll use CodeCommit)
   - **ControlTowerEnabled:** `Yes` (LZA deploys Control Tower)
   - **ApprovalStage:** `Yes` (recommended for production)
   - **ApprovalStageNotifyEmailList:** Your email for approvals
   - **EnableTester:** `No` (unless doing test deployments)
   - **EnableSingleAccountMode:** `No`

5. Create stack (takes 10-15 minutes)

**Option B: Deploy via CLI**

```bash
aws cloudformation create-stack \
  --stack-name AWSAccelerator-InstallerStack \
  --template-url https://s3.amazonaws.com/solutions-reference/landing-zone-accelerator-on-aws/latest/AWSAccelerator-InstallerStack.template \
  --parameters \
    ParameterKey=RepositorySource,ParameterValue=codecommit \
    ParameterKey=ControlTowerEnabled,ParameterValue=Yes \
    ParameterKey=ApprovalStage,ParameterValue=Yes \
    ParameterKey=ApprovalStageNotifyEmailList,ParameterValue=your-email@yourcompany.com \
  --capabilities CAPABILITY_IAM CAPABILITY_NAMED_IAM \
  --region us-east-1

# Monitor stack creation
aws cloudformation wait stack-create-complete \
  --stack-name AWSAccelerator-InstallerStack \
  --region us-east-1
```

#### Step 4: Configure CodeCommit Repository

After the installer completes, a CodeCommit repository is created.

**Clone the configuration repository:**

```bash
# Set up CodeCommit credentials (if not already configured)
# Option 1: HTTPS with Git credentials (from IAM user)
git config --global credential.helper '!aws codecommit credential-helper $@'
git config --global credential.UseHttpPath true

# Option 2: SSH (configure SSH key in IAM user settings)

# Clone the repository
aws codecommit get-repository --repository-name aws-accelerator-config \
  --query 'repositoryMetadata.cloneUrlHttp' --output text

git clone https://git-codecommit.us-east-1.amazonaws.com/v1/repos/aws-accelerator-config
cd aws-accelerator-config
```

**Upload your configuration files:**

```bash
# Copy your edited configuration files to the repository
cp /path/to/your/configs/*.yaml .

# The repository should have these files:
# - global-config.yaml
# - accounts-config.yaml
# - organization-config.yaml
# - network-config.yaml
# - security-config.yaml
# - iam-config.yaml
# - customizations-config.yaml (optional)

# Commit and push
git add *.yaml
git commit -m "Initial LZA configuration"
git push origin main
```

**Result:** Pushing to `main` branch triggers the `AWSAccelerator-Pipeline` to run.

#### Step 5: Monitor Pipeline Execution

```bash
# Get pipeline execution status
aws codepipeline get-pipeline-state \
  --name AWSAccelerator-Pipeline \
  --query 'stageStates[*].[stageName,latestExecution.status]' \
  --output table

# View pipeline in console
# https://console.aws.amazon.com/codesuite/codepipeline/pipelines/AWSAccelerator-Pipeline/view
```

**Pipeline Stages:**

1. **Source** - Retrieves config from CodeCommit (or GitHub/S3)
2. **Build** - Builds LZA source code
3. **Deploy (Prepare)** - Validates configuration, creates accounts
4. **Deploy (Accounts)** - Deploys account-level resources
5. **Deploy (Networks)** - Deploys VPCs, Transit Gateway, networking
6. **Deploy (Security)** - Deploys security services
7. **Deploy (Operations)** - Deploys operational tooling
8. **Deploy (Finalize)** - Completes deployment, runs post-deployment tasks

**First run takes:** 2-4 hours depending on complexity

**If ApprovalStage enabled:** You'll receive an email to approve before production deployment

#### Step 6: Verify Control Tower Deployment

LZA deploys Control Tower during the first pipeline run.

```bash
# Check Control Tower landing zone status
aws controltower get-landing-zone \
  --landing-zone-identifier $(aws controltower list-landing-zones --query 'landingZones[0].arn' --output text) \
  --query 'landingZone.status'

# Should return: "ACTIVE"

# Check created accounts
aws organizations list-accounts \
  --query 'Accounts[*].[Name,Email,Status]' \
  --output table
```

**Verify in Console:**
- Navigate to AWS Control Tower console
- Confirm landing zone is active
- Check Organizational Units
- Verify IAM Identity Center is configured

#### Step 7: Set Up IAM Identity Center Users

```bash
# Get Identity Center instance ARN
IDENTITY_STORE_ID=$(aws sso-admin list-instances \
  --query 'Instances[0].IdentityStoreId' \
  --output text)

# Create a user (or use the console for easier setup)
# Console: https://console.aws.amazon.com/singlesignon/
```

**In Console:**
1. Go to IAM Identity Center
2. Users → Add user
3. Create admin user with MFA
4. Assign to groups:
   - `AWSAccountFactory` - For account provisioning
   - `AWSServiceCatalogAdmins` - For catalog management
5. Set up permission sets for account access

#### Step 8: Invite Existing Workload Account

If you have an existing account with workloads:

```bash
# Invite existing account to organization
aws organizations invite-account-to-organization \
  --target '{\"Type\":\"EMAIL\",\"Id\":\"existing-account@yourcompany.com\"}' \
  --notes "Inviting existing workload account to organization"

# Get invitation ID
INVITATION_ID=$(aws organizations list-handshakes-for-organization \
  --query 'Handshakes[?State==`OPEN`].Id' \
  --output text)

# From the invited account (switch credentials)
aws organizations accept-handshake --handshake-id $INVITATION_ID

# Back in management account, move to correct OU
ACCOUNT_ID=$(aws organizations list-accounts \
  --query 'Accounts[?Email==`existing-account@yourcompany.com`].Id' \
  --output text)

OU_ID=$(aws organizations list-organizational-units-for-parent \
  --parent-id r-xxxx \
  --query 'OrganizationalUnits[?Name==`Workloads`].Id' \
  --output text)

aws organizations move-account \
  --account-id $ACCOUNT_ID \
  --source-parent-id r-xxxx \
  --destination-parent-id $OU_ID

# Enroll in Control Tower
# This must be done via console or Control Tower APIs
```

### Phase 3: Ongoing Configuration Management

#### GitOps Workflow with CodeCommit

1. **Clone repository:**
   ```bash
   git clone https://git-codecommit.us-east-1.amazonaws.com/v1/repos/aws-accelerator-config
   cd aws-accelerator-config
   ```

2. **Create feature branch:**
   ```bash
   git checkout -b feature/add-new-account
   ```

3. **Edit configuration:**
   ```bash
   # Edit accounts-config.yaml to add new account
   vim accounts-config.yaml
   ```

4. **Commit and push:**
   ```bash
   git add accounts-config.yaml
   git commit -m "Add new production account"
   git push origin feature/add-new-account
   ```

5. **Create pull request** (via console or CLI)

6. **Review and merge to main**

7. **Pipeline automatically runs** when main is updated

8. **Approve deployment** (if approval stage enabled)

#### Configuration Validation

LZA includes JSON Schema validation:

```bash
# Install VSCode with YAML extension
# Or use IntelliJ IDEA

# Open config files - you'll get:
# - Real-time validation
# - Auto-completion (Ctrl+Space)
# - Inline documentation
# - Error highlighting
```

#### Common Configuration Changes

**Add a new workload account:**

```yaml
# accounts-config.yaml
workloadAccounts:
  - name: Production-API
    description: Production API workload
    email: prod-api@yourcompany.com
    organizationalUnit: Workloads/Production
```

**Add security service:**

```yaml
# security-config.yaml
awsConfig:
  enableConfigurationRecorder: true
  enableDeliveryChannel: true
  aggregation:
    enable: true
    
guardDuty:
  enable: true
  s3Protection:
    enable: true
  eksProtection:
    enable: true
```

**Configure Transit Gateway:**

```yaml
# network-config.yaml
transitGateways:
  - name: Main-TGW
    account: Network
    region: us-east-1
    asn: 65000
    dnsSupport: enable
    vpnEcmpSupport: enable
    defaultRouteTableAssociation: disable
    defaultRouteTablePropagation: disable
```

### Phase 4: Monitoring and Maintenance

**Monitor Pipeline:**
- CloudWatch Dashboard: Auto-created for pipeline metrics
- SNS Notifications: Subscribe to pipeline topics
- CodePipeline Console: Real-time status

**Monitor Control Tower:**
- Control Tower Dashboard: Drift detection, compliance
- AWS Config: Resource compliance across accounts
- Security Hub: Security findings aggregation

**Cost Monitoring:**
```bash
# Enable Cost Explorer
aws ce update-cost-allocation-tags-status \
  --cost-allocation-tags-status Key=Application,Status=Active

# Set up budget alerts
aws budgets create-budget \
  --account-id $(aws sts get-caller-identity --query Account --output text) \
  --budget file://budget.json \
  --notifications-with-subscribers file://notifications.json
```

**Regular Maintenance:**
- Monthly: Review AWS Config compliance
- Monthly: Review Security Hub findings
- Quarterly: Update LZA to latest version
- Quarterly: Review and update configuration for new accounts
- Annually: Review OU structure and account organization

## Cost Summary by Deployment Type

### Minimal (Organizations Only)
- **Setup:** Free
- **Monthly:** $0
- **Use Case:** Very small organizations, extreme cost sensitivity
- **Accounts:** 1-3
- **Management Effort:** High (manual everything)

### Standard (Organizations + Control Tower)
- **Setup:** ~1 hour (free)
- **Monthly:** $250-500
- **Use Case:** Most businesses, standard compliance
- **Accounts:** 3-20
- **Management Effort:** Low (automated guardrails)

### Advanced (Organizations + Control Tower + LZA)
- **Setup:** ~4 hours initial, ongoing configuration
- **Monthly:** $600-1,500
- **Use Case:** Regulated industries, complex architecture
- **Accounts:** 10-100+
- **Management Effort:** Medium (GitOps management)

### Cost Breakdown by Component

| Component | Setup Cost | Monthly Cost | Notes |
|-----------|-----------|--------------|-------|
| **AWS Organizations** | $0 | $0 | Free service |
| **Control Tower Service** | $0 | $0 | Free service |
| **Management Account Resources** | $0 | $50-100 | Config, CloudWatch, etc. |
| **Log Archive Account** | $0 | $50-150 | S3 storage, log ingestion |
| **Audit Account** | $0 | $20-50 | Minimal resources |
| **Per Member Account (Config)** | $0 | $30-75 | Varies by resource count |
| **LZA Pipeline Infrastructure** | $0 | $50-100 | CodePipeline, CodeBuild |
| **Transit Gateway (if used)** | $0 | $100-200 | Per TGW + attachments |
| **Network Firewall (if used)** | $0 | $350-500 | Per firewall endpoint |
| **Enhanced Security (GuardDuty, etc.)** | $0 | $50-200 | Varies by data volume |

### Example Scenarios

**Scenario 1: Small Software Company**
- 5 accounts (Mgmt, Log, Audit, Dev, Prod)
- Control Tower only
- No advanced networking
- **Monthly Cost:** ~$300

**Scenario 2: Mid-Size SaaS Company**
- 15 accounts (standard + per-team accounts)
- Control Tower only
- Basic Transit Gateway networking
- **Monthly Cost:** ~$800

**Scenario 3: Healthcare Company (HIPAA)**
- 20 accounts (standard + per-environment isolation)
- Control Tower + LZA with healthcare config
- Full Transit Gateway mesh, Network Firewall
- GuardDuty, Security Hub, Macie enabled
- **Monthly Cost:** ~$2,500

**Scenario 4: Financial Services (PCI-DSS)**
- 50 accounts (standard + per-application isolation)
- Control Tower + LZA with finance config
- Multi-region deployment
- Full security suite
- **Monthly Cost:** ~$5,000-7,000

## Troubleshooting

### Common Issues

**LZA Pipeline Fails on First Run:**
- Check CloudWatch Logs for specific error
- Validate YAML syntax (use schema validation)
- Ensure email addresses are unique
- Verify all required parameters are set

**Control Tower Setup Fails:**
- Ensure no existing AWS Config resources
- Check that management account has no existing OUs
- Verify IAM Identity Center not already configured
- Review CloudFormation stack events

**Account Invitation Fails:**
- Email must be unique (not used by any AWS account)
- Check spam folder for invitation email
- Invitation expires after 15 days
- Verify account has all features enabled

**Config Costs Higher Than Expected:**
- Review Config recording settings (global resources multiply cost)
- Adjust recording frequency if acceptable
- Exclude low-value resource types
- Use lifecycle policies on S3 log buckets

### Getting Help

- **AWS Support:** File a support case (requires support plan)
- **LZA GitHub:** https://github.com/awslabs/landing-zone-accelerator-on-aws/issues
- **Control Tower Documentation:** https://docs.aws.amazon.com/controltower/
- **AWS re:Post:** Community forums for AWS questions

## Summary of Key Questions

### Q: Should I create a new account or use my existing account for management?
**A: CREATE A NEW ACCOUNT** if your existing account has ANY workloads. AWS best practice explicitly prohibits workloads in the management account.

### Q: When is SSO set up?
**A: Automatically during Control Tower setup.** IAM Identity Center is configured and ready to use immediately.

### Q: Can LZA set up Control Tower?
**A: YES** - Deploy LZA with `ControlTowerEnabled: Yes` and it will deploy Control Tower for you.

### Q: Can LZA set up Organizations?
**A: Indirectly YES** - LZA requires Organizations to exist first, but when LZA deploys Control Tower, Control Tower can create Organizations.

### Q: Which creates the standard accounts (Management, Audit, Log Archive)?
**A: Control Tower creates** Log Archive and Audit. Your existing account becomes Management. LZA can create additional accounts (Network, Shared Services, etc.) based on your configuration.

### Q: What's the recommended path?
**A: For most companies:**
1. Create new management account
2. Deploy Control Tower (creates Organizations automatically)
3. Invite existing workload account
4. Add LZA only if you need specific compliance frameworks

**A: For regulated industries:**
1. Create new management account
2. Create Organizations
3. Deploy LZA with `ControlTowerEnabled: Yes`
4. Configure via CodeCommit repository
5. Let LZA deploy everything automatically

## Next Steps

1. **Decision Point:** Determine which deployment model fits your needs
2. **Create Management Account:** Sign up for new AWS account
3. **Prepare Email Addresses:** Get shared mailboxes ready
4. **Design OU Structure:** Plan your organizational hierarchy
5. **Deploy Control Tower** or **Deploy LZA** (based on requirements)
6. **Configure IAM Identity Center:** Set up users and groups
7. **Invite Existing Account:** Add your workload account to org
8. **Document:** Update runbooks and operational procedures

## Resources

- [AWS Control Tower User Guide](https://docs.aws.amazon.com/controltower/latest/userguide/)
- [AWS Organizations User Guide](https://docs.aws.amazon.com/organizations/latest/userguide/)
- [Landing Zone Accelerator Implementation Guide](https://docs.aws.amazon.com/solutions/latest/landing-zone-accelerator-on-aws/)
- [Landing Zone Accelerator GitHub](https://github.com/awslabs/landing-zone-accelerator-on-aws)
- [LZA Configuration Reference](https://awslabs.github.io/landing-zone-accelerator-on-aws/latest/user-guide/config/)
- [AWS Multi-Account Strategy Whitepaper](https://docs.aws.amazon.com/whitepapers/latest/organizing-your-aws-environment/)
- [IAM Identity Center Documentation](https://docs.aws.amazon.com/singlesignon/latest/userguide/)

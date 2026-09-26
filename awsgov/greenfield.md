# AWS Multi-Account Greenfield Deployment Roadmap

This roadmap organizes governance topics from `topics.md` into implementation phases based on dependencies. Each phase should be completed before proceeding to the next.

## Phase 1: Foundation - Organizations and Account Structure

**Objective**: Establish AWS Organizations and define account/OU structure

1. AWS Organizations Fundamentals - Enable Organizations, understand OUs and account hierarchy
2. Multi-Account Strategy Design - Define account strategy (per environment, workload, team)
3. Organizational Units (OU) Design Patterns - Design OU hierarchy aligned with business structure
4. AWS Organizations Root Access Management - Enable root access management for member accounts
5. Region Management Strategy - Define approved and denied regions based on compliance requirements
6. Control Tower vs Landing Zone Accelerator - Choose deployment approach (Control Tower or LZA)

**Verification**: Organization structure matches design, accounts created in correct OUs

---

## Phase 2: Landing Zone Deployment

**Objective**: Deploy Control Tower or LZA to establish baseline security and governance

### Option A: Control Tower Deployment
1. AWS Control Tower Overview - Deploy Control Tower landing zone
2. Control Tower Landing Zone Structure - Verify Security OU, Log Archive, and Audit accounts
3. Control Tower Guardrails and Controls - Enable mandatory and strongly recommended controls
4. Control Tower Account Factory - Configure Account Factory for standardized provisioning

### Option B: LZA Deployment
1. Landing Zone Accelerator Architecture - Deploy LZA via CloudFormation
2. LZA Configuration Management - Configure accounts, network, security, and IAM YAML files
3. LZA Pipeline and Deployment Process - Execute pipeline to deploy resources
4. LZA Security Controls - Implement security control baseline

**Verification**: Landing zone deployed, shared accounts configured, baseline controls active

---

## Phase 3: Identity and Access Management

**Objective**: Configure centralized identity and access control

1. AWS IAM Identity Center (SSO) - Enable Identity Center, choose identity source
2. Identity and Directory Shared Services - Deploy AWS Managed Microsoft AD if needed (Shared Services account)
3. IAM Identity Center External Identity Provider Integration - Configure SAML with Entra ID/Okta
4. SCIM Provisioning for Automated User Synchronization - Enable SCIM for automated user sync
5. Permission Set Design for External Identities - Create permission sets aligned with job functions
6. Identity Center in Organizations with Control Tower - Configure Control Tower integration
7. Multi-Region Identity Center Configuration - Enable multi-region for resiliency

**Verification**: Users can authenticate via SSO, permission sets grant appropriate access

---

## Phase 4: Network Foundation

**Objective**: Establish network architecture and connectivity

1. Network Architecture in Multi-Account Environments - Design Transit Gateway topology
2. Network Shared Services - Deploy Transit Gateway in network account
3. Shared VPC Alternative Pattern - Evaluate VPC sharing vs Transit Gateway
4. DNS and Route 53 Shared Services - Configure Route 53 Resolver for hybrid DNS
5. PrivateLink for Shared Services - Implement PrivateLink for sensitive service access

**Verification**: VPCs connect via Transit Gateway, DNS resolution works, hybrid connectivity established

---

## Phase 5: Security Controls - Logging and Monitoring

**Objective**: Enable organization-wide logging and configuration tracking

1. CloudTrail Organization Trails - Create organization trail for all accounts
2. CloudTrail Log Aggregation and Analysis - Configure S3 bucket, CloudWatch Logs integration
3. CloudTrail Data Events and Insights - Enable data events for sensitive resources
4. AWS Config Organization Aggregator - Deploy Config aggregator in security account
5. AWS Config Rules and Conformance Packs - Deploy conformance packs for compliance frameworks
6. Config Multi-Region and Multi-Account Deployment - Enable Config in all accounts/regions
7. Centralized Logging and Monitoring - Configure log aggregation in security account

**Verification**: CloudTrail logs appear in S3, Config tracks resource changes, aggregator shows all accounts

---

## Phase 6: Security Controls - Threat Detection

**Objective**: Deploy security services for threat detection and vulnerability management

1. GuardDuty Organization-Wide Deployment - Enable GuardDuty with delegated administrator
2. Security Hub Organization Configuration - Configure Security Hub with central configuration
3. Security Hub Standards and Controls - Enable security standards (FSBP, CIS)
4. Amazon Inspector Organization Coverage - Enable Inspector for EC2/ECR/Lambda scanning
5. Amazon Macie Organization Deployment - Deploy Macie for sensitive data discovery
6. IAM Access Analyzer Organization Deployment - Enable Access Analyzer with organization zone
7. Detective for Security Investigation - Enable Detective for security investigations
8. AWS Security Service Integration - Configure Security Hub as central aggregation point

**Verification**: All security services active in all accounts, findings aggregate in Security Hub

---

## Phase 7: Governance Policies

**Objective**: Implement preventive and detective controls

1. Service Control Policies (SCPs) - Implement baseline SCPs at organization/OU level
2. Region Deny SCP Implementation - Restrict resource creation to approved regions
3. Resource Control Policies (RCPs) - Implement RCPs for resource-based access control
4. Tag Policies for Governance - Enforce tagging standards via tag policies
5. Backup Policies for Data Protection - Deploy backup policies for data protection requirements
6. AI Services Opt-Out Policies - Configure AI service opt-out policies if required
7. Policy as Code and Compliance Automation - Version control policies, implement CI/CD

**Verification**: SCPs restrict denied actions, tags enforce on new resources, backups execute per policy

---

## Phase 8: Compliance and Auditing

**Objective**: Establish compliance monitoring and reporting

1. Config Tag Compliance Management - Deploy required-tags Config rules
2. Compliance and Audit Framework - Configure AWS Audit Manager for continuous compliance
3. Tagging Strategy and Resource Organization - Implement organization-wide tagging standards
4. Cost Allocation and Chargeback - Configure cost allocation tags and Cost Categories
5. Backup and Disaster Recovery Strategy - Establish backup and DR requirements per workload tier

**Verification**: Tag compliance tracked, audit evidence collected, cost allocation reports available

---

## Phase 9: Shared Services Deployment

**Objective**: Deploy centralized services for workload accounts

1. Shared Services Account Architecture - Create shared services account in Infrastructure OU
2. Service Catalog Shared Portfolios - Create Service Catalog portfolios for approved templates
3. Container Registry Shared Services - Deploy ECR for shared container images
4. Artifact Repository Shared Services - Deploy CodeArtifact for package management
5. CI/CD Shared Services - Configure CodePipeline for cross-account deployments
6. Certificate Management Shared Services - Deploy Private CA for internal PKI
7. Secrets Management Shared Services - Configure Secrets Manager for shared credentials
8. Monitoring and Observability Shared Services - Deploy CloudWatch cross-account observability

**Verification**: Shared services accessible from workload accounts, cross-account access works

---

## Phase 10: Account Provisioning Automation

**Objective**: Automate account creation and baseline configuration

1. Account Provisioning Automation - Implement Account Factory or custom provisioning
2. Control Tower Account Factory (if using Control Tower) - Configure Account Factory blueprints
3. Control Tower AFT Deployment (if using Terraform) - Deploy AFT for Terraform-based customization
4. LZA Configuration Management (if using LZA) - Configure accounts-config.yaml for new accounts
5. Delegated Administrator Accounts - Designate delegated administrators for security services
6. Trusted Service Integration - Enable trusted access for required services

**Verification**: New accounts provision with baseline configuration, security services auto-enable

---

## Phase 11: Advanced Security Configuration

**Objective**: Implement advanced security features and integrations

1. Attribute-Based Access Control (ABAC) with External IdP - Configure ABAC with user attributes
2. GuardDuty Finding Aggregation and Response - Implement automated finding response workflows
3. Security Hub Finding Aggregation - Configure cross-region aggregation
4. Inspector Finding Management - Establish vulnerability remediation workflows
5. Macie Sensitive Data Discovery - Configure automated discovery jobs for S3 buckets
6. IAM Access Analyzer Policy Validation - Integrate policy validation in CI/CD pipelines
7. Break Glass Procedures - Document and implement emergency access procedures

**Verification**: Automated response workflows execute, findings trigger remediation, emergency access tested

---

## Phase 12: Workload Onboarding Patterns

**Objective**: Establish patterns for onboarding workloads to the environment

1. AWS Service Catalog - Create workload-specific product templates
2. Data Governance and Classification - Implement data classification schema
3. Federated Access and External Collaboration - Configure partner/contractor access patterns
4. Automation and Infrastructure as Code - Establish IaC standards and CI/CD patterns
5. Incident Response in Multi-Account Environments - Configure IR playbooks and automation

**Verification**: Workloads deploy via Service Catalog, IaC pipelines operational, IR playbooks tested

---

## Phase 13: Operational Readiness

**Objective**: Ensure environment is production-ready with monitoring and runbooks

1. CloudWatch Logging Integration - Configure application log aggregation
2. Systems Manager Shared Resources - Deploy Session Manager, Patch Manager
3. Cost Management Shared Services - Implement cost visibility dashboards
4. Resource Tagging Standards for Shared Services - Enforce shared service tagging
5. Data Analytics Shared Services - Deploy Athena/Glue for log analysis

**Verification**: Operational dashboards active, runbooks documented, cost visibility established

---

## Ongoing: Verification and Maintenance

**Objective**: Continuously verify implementation and maintain compliance

### Verification Checkpoints (Execute Monthly)
1. Verifying Organization Structure and Hierarchy
2. Verifying Service Control Policy Implementation
3. Verifying CloudTrail Organization Trail Configuration
4. Verifying Config Recorder Status and Aggregator Data Completeness
5. Verifying GuardDuty Organization Enablement and Protection Plan Coverage
6. Verifying Security Hub Organization Configuration and Standards Compliance
7. Verifying IAM Identity Center Configuration and Account Assignment Accuracy
8. Verifying Region Deny SCP Effectiveness
9. Verifying Multi-Region Security Service Deployment

### Maintenance Activities (Execute Quarterly)
1. Review and update SCPs based on new security requirements
2. Audit IAM Identity Center permission sets and account assignments
3. Review Security Hub findings trends and compliance scores
4. Update conformance packs with new compliance requirements
5. Conduct Well-Architected Reviews for core infrastructure
6. Test disaster recovery and break glass procedures
7. Review and optimize shared services costs
8. Update documentation and runbooks
9. Train new team members on governance framework

---

## Critical Success Factors

### Prerequisites
- Management account with Organizations enabled
- Approved region list documented
- Multi-account strategy documented
- Identity provider selected (Identity Center directory, Managed AD, or external IdP)
- Compliance requirements identified
- Budget allocated for foundational accounts

### Key Decisions
- Control Tower vs LZA (or hybrid)
- Identity source (internal directory vs external IdP)
- Network architecture (Transit Gateway vs Shared VPC)
- Compliance frameworks to implement
- Shared services scope and placement

### Risk Mitigation
- Test all changes in non-production OU first
- Maintain rollback procedures for policy changes
- Document exceptions to standard configurations
- Implement change approval workflows
- Conduct regular disaster recovery drills

---

## Estimated Timeline

- **Phase 1-2 (Foundation & Landing Zone)**: 2-4 weeks
- **Phase 3 (Identity)**: 2-3 weeks
- **Phase 4 (Network)**: 2-3 weeks
- **Phase 5-6 (Security Controls)**: 3-4 weeks
- **Phase 7-8 (Governance & Compliance)**: 2-3 weeks
- **Phase 9 (Shared Services)**: 3-4 weeks
- **Phase 10-11 (Automation & Advanced Security)**: 2-3 weeks
- **Phase 12-13 (Workload Onboarding & Operations)**: 2-3 weeks

**Total Duration**: 18-27 weeks (4.5-6.5 months) for full implementation

Timeline assumes:
- Dedicated team working full-time
- Clear decision-making authority
- No major organizational blockers
- Standard complexity (not highly regulated industry)

Highly regulated industries (healthcare, financial services, government) may require 8-12 months due to additional compliance requirements and approval processes.

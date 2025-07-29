# rConfig Professional Policy Templates

## 🚀 Overview
Welcome to the community-driven repository for rConfig Professional Policy Templates! This collection empowers network administrators and security professionals to share, discover, and implement standardized compliance policies across diverse network infrastructures.

> [!IMPORTANT]  
> **For Professional Users**: Review our comprehensive documentation for implementation guidance on Compliance and Policy Definitions at [https://docs.rconfig.com/compliance/overview/](https://docs.rconfig.com/compliance/overview/)

## 📁 Repository Structure
We maintain a clean, vendor-organized structure to ensure easy navigation and discovery:

```
├── Cisco/
│   ├── README.md
│   ├── isr4400-pci-dss.policy
│   ├── catalyst-soc2.policy
│   └── asa-hipaa.policy
├── F5/
│   ├── README.md
│   └── bigip-gdpr.policy
├── Extreme/
│   ├── README.md
│   └── exos-nist.policy
└── Fortinet/
    ├── README.md
    └── fortigate-iso27001.policy
```

## 📋 File Naming Conventions
- All policy files **must** end with `.policy` extension
- **Recommended format**: `{vendor-model}-{compliance-standard}.policy`
- Examples:
  - `isr4400-pci-dss.policy`
  - `catalyst9300-sox.policy` 
  - `fortigate-600d-hipaa.policy`

## 🤝 Contributing Your Policies

### Method 1: GitHub Pull Request (Recommended)

#### Step 1: Fork & Clone
```bash
# Fork the repository on GitHub, then clone your fork
git clone https://github.com/YOUR-USERNAME/pro-policy-definitions.git
cd pro-policy-definitions
```

#### Step 2: Create Your Branch
```bash
# Create a descriptive branch name
git checkout -b add-cisco-catalyst-policies
```

#### Step 3: Add Your Content
1. Navigate to the appropriate vendor folder (create if it doesn't exist)
2. Add your `.policy` files following naming conventions
3. Update or create the vendor's `README.md` with:
   - Policy descriptions
   - Supported device models
   - Compliance standards covered
   - Any special configuration notes

#### Step 4: Commit & Push
```bash
# Stage your changes
git add .

# Commit with a clear message
git commit -m "Add Cisco Catalyst 9300 SOX compliance policies"

# Push to your fork
git push origin add-cisco-catalyst-policies
```

#### Step 5: Create Pull Request
1. Visit your fork on GitHub
2. Click "New Pull Request"
3. Provide a clear title and description of your contribution
4. Submit for review

### Method 2: Direct Submission
If you prefer not to use GitHub or need assistance:

📧 **Email your policies directly to**: `info@rconfig.com`

**Include in your email:**
- Vendor/device information
- Compliance standard(s) addressed
- Brief description of the policy
- Your contact information for any follow-up questions

## ✅ Contribution Guidelines

### Required for Each Vendor Folder:
- **README.md** containing:
  - List of all policy files with descriptions
  - Supported device models and firmware versions
  - Implementation notes or prerequisites
  - Contact information (optional)

### Policy Quality Standards:
- ✅ Tested and validated configurations
- ✅ Clear comments explaining rule logic
- ✅ Compliance standard references where applicable
- ✅ Compatible with current rConfig Professional versions

### Example Vendor README.md:
```markdown
# Cisco Policy Templates

## Available Policies
- **isr4400-pci-dss.policy**: PCI DSS compliance for ISR 4400 series routers
- **catalyst9300-sox.policy**: Sarbanes-Oxley controls for Catalyst 9300 switches

## Supported Models
- ISR 4400 series (IOS XE 16.x+)
- Catalyst 9300 series (IOS XE 16.6+)

## Implementation Notes
Ensure SNMP v3 is configured before applying security policies.

## Contact
Maintained by: John Doe (john@company.com)
```

## 🌟 Why Contribute?
- **Build Community**: Help fellow network professionals
- **Share Expertise**: Showcase your compliance knowledge  
- **Save Time**: Reduce policy development overhead across the industry
- **Recognition**: Get credited for your contributions
- **Collaboration**: Learn from others' approaches to compliance

## 📞 Support & Questions
- **Documentation**: [https://docs.rconfig.com](https://docs.rconfig.com)
- **Email Support**: `info@rconfig.com`
- **Issues**: Use GitHub Issues for template problems or suggestions

## 📜 License
By contributing to this repository, you agree that your contributions will be available under the same license terms as the rConfig Professional product.

---
**Together, we're building the most comprehensive collection of network compliance policies. Thank you for contributing! 🎉**
